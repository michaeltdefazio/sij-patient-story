# Print masters: each page rendered once at 300 dpi and saved as a single RGB image per page,
# so glows and shadows can't be split into separate transparent patches that printers blend unevenly.
import asyncio, pathlib, io, img2pdf
from PIL import Image, ImageCms
from playwright.async_api import async_playwright

PDF = pathlib.Path('/home/claude/handout/pdf')
OUT = PDF / 'print'; OUT.mkdir(exist_ok=True)
KEYS = ['Rutledge', 'Hom', 'Gordon', 'Cook', 'Kowlowitz', 'Oberhelman', 'Dorwart', 'Kim']
SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
SCALE = 300 / 96  # 816x1056 css px -> 2550x3300 px = 8.5x11 in at 300 dpi

# Print tuning (from the printed color test): this printer renders our teal as blue, so every teal is
# rotated 10 degrees toward green (row 3); pale teal tints print as gray, so they get more color; text glows
# on white paper print as a fuzzy halo, so those two are removed (glows on dark panels stay).
import re, colorsys
NO_GLOW = [
    ('color: #007F82; text-shadow: 0 0 12px rgba(0,183,186,0.68), 0 0 22px rgba(247,181,56,0.48)">SCAN TO WATCH',
     'color: #007F82">SCAN TO WATCH'),
    ('; text-shadow: 0 0 10px rgba(0,183,186,0.40), 0 0 22px rgba(0,183,186,0.30)">AFTER YOUR <span style="color: #1F2735; text-shadow: 0 0 12px rgba(242,180,58,0.50)">CENTER FOR PAIN</span>',
     '">AFTER YOUR <span style="color: #1F2735">CENTER FOR PAIN</span>'),
]
# Final print palette = the exact teals in the approved Rutledge "PRINT (HP glossy)" brochure, which prints
# correctly on Mike's HP Smart Tank with "Let printer determine colors" checked in Acrobat:
#   one main teal for every fill, heading, check and footer (#4BDEBC), a lighter teal only for teal text
#   on the dark navy panels (#65EBCB, the brochure's "Now Offering..." shade), and a pale tint at the same hue.
MAIN, ACCENT, TINT = (75, 222, 188), (101, 235, 203), (215, 244, 237)
ON_NAVY_TEALS = {(79, 211, 214)}          # #4FD3D6: teal text and glows on navy
def _tune(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    if not (172 <= h * 360 <= 188 and s >= 0.3):
        return None
    if (r, g, b) in ON_NAVY_TEALS:
        return ACCENT
    if l >= 0.9:
        return TINT
    return MAIN
# Borderless printing on the HP enlarges the page slightly and trims ~0.1 in (about 10 px) off the bottom
# (measured from the printed back page). Teal bands still run to the edge, but footer content is lifted so it
# sits centered in the part that actually prints.
PRINT_SAFE = [
    ('<div style="height: 64px; background: #007F82; box-sizing: border-box; padding: 0 48px; display: flex;',
     '<div style="height: 70px; background: #007F82; box-sizing: border-box; padding: 0 48px 12px 48px; display: flex;'),
    ('<div style="flex: 1 1 auto; background: #007F82; box-sizing: border-box; padding: 0 40px; display: flex;',
     '<div style="flex: 1 1 auto; background: #007F82; box-sizing: border-box; padding: 0 40px 12px 40px; display: flex;'),
]
def print_tune(html):
    for a, b in NO_GLOW:
        if a in html:
            assert html.count(a) == 1; html = html.replace(a, b)
    for a, b in PRINT_SAFE:
        if a in html:
            assert html.count(a) == 1; html = html.replace(a, b)
    def hexsub(m):
        c = m.group(0); t = _tune(int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16))
        return c if t is None else '#%02X%02X%02X' % t
    def rgbasub(m):
        r, g, b = (int(m.group(i)) for i in (1, 2, 3)); t = _tune(r, g, b)
        return m.group(0) if t is None else f'rgba({t[0]},{t[1]},{t[2]},{m.group(4)})'
    head, body = html.split('<body>', 1)
    body = re.sub(r'#[0-9A-Fa-f]{6}\b', hexsub, body)
    body = re.sub(r'rgba\((\d+),(\d+),(\d+),([\d.]+)\)', rgbasub, body)
    return head + '<body>' + body

def jpeg(png_bytes):
    im = Image.open(io.BytesIO(png_bytes)).convert('RGB')
    assert im.size == (2550, 3300), im.size
    buf = io.BytesIO()
    im.save(buf, 'JPEG', quality=95, subsampling=0, dpi=(300, 300))  # untagged DeviceRGB, like the brochure's colors
    return buf.getvalue()

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=sorted(pathlib.Path('/opt/pw-browsers').glob('chromium-*/chrome-linux/chrome'))[0].as_posix())
        pg = await b.new_page(viewport={'width': 816, 'height': 1056}, device_scale_factor=SCALE)
        async def shot(html):
            tuned = PDF / ('print_' + html)
            tuned.write_text(print_tune((PDF / html).read_text()))
            await pg.goto('file://' + str(tuned)); await pg.wait_for_load_state('networkidle')
            await pg.evaluate('document.fonts.ready')
            return jpeg(await pg.screenshot(clip={'x': 0, 'y': 0, 'width': 816, 'height': 1056}))
        back = await shot('back.html')
        for key in KEYS:
            front = await shot(f'{key.lower()}.html')
            out = OUT / f'SIJ_Patient_Story_Handout_Dr_{key}_PRINT.pdf'
            layout = img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))
            out.write_bytes(img2pdf.convert([front, back], layout_fun=layout))
            print('wrote', out)
        await b.close()
asyncio.run(main())
