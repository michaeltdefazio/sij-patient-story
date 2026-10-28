# Final deliverables: one PRINT (HP glossy) and one EMAIL PDF per physician.
# PRINT  = print-tuned HTML (brochure print teal #4BDEBC, footer lifted for the HP's borderless trim,
#          no glow behind text on white), rendered at 300 dpi, untagged RGB like the brochure print file.
# EMAIL  = the approved design as-is (regular teal, normal footer, glows), rendered at 300 dpi, sRGB-tagged.
# Both are flattened to one image per page so glows can't print as dark rectangles on anyone's printer.
import asyncio, pathlib, io, sys, img2pdf
from PIL import Image, ImageCms
from playwright.async_api import async_playwright
sys.argv = ['x']
src = open('/home/claude/scripts/build_print.py').read()
exec(src[:src.index('def jpeg(')])          # reuse print_tune / palette / PRINT_SAFE definitions

PDF = pathlib.Path('/home/claude/handout/pdf')
FINAL = pathlib.Path('/home/claude/handout/final'); (FINAL / 'PRINT').mkdir(parents=True, exist_ok=True); (FINAL / 'EMAIL').mkdir(exist_ok=True)
DOCS = [('rutledge', 'Dr. Joseph Rutledge'), ('hom', 'Dr. Brian Hom'), ('gordon', 'Dr. David Gordon'), ('cook', 'Dr. Andrew Cook'),
        ('kowlowitz', 'Dr. Edward Kowlowitz'), ('oberhelman', 'Dr. Forrest Oberhelman'), ('dorwart', 'Dr. Michael Dorwart'), ('kim', 'Dr. Scott Kim'),
        ('tolbert', 'Dr. Ashley Tolbert'), ('bush', 'Dr. Jocelyn Bush')]
SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
LAYOUT = img2pdf.get_layout_fun((img2pdf.in_to_pt(8.5), img2pdf.in_to_pt(11)))

# EMAIL teal = the Now Offering EMAIL brochures' teal (#00B7BA: footer band, headings, icons). The handout design
# used a deeper #007F82 / #00777B, which reads green next to the brochures on screen. PRINT files are untouched.
EMAIL_TEAL = {'#007F82': '#00B7BA', '#00777B': '#00B7BA',
              '#4FD3D6': '#33C5C8', 'rgba(79,211,214,': 'rgba(51,197,200,'}   # brochure teal on navy = #33C5C8
# The teal headings' glows were tuned for the deeper teal. On the brighter brochure teal a same-color glow blurs the
# letters, so the email version adds a fine deeper-teal edge and keeps a distinct teal-then-gold halo.
EMAIL_GLOW = [
    ('color: #00B7BA; text-shadow: 0 0 12px rgba(0,183,186,0.68), 0 0 22px rgba(247,181,56,0.48)">SCAN TO WATCH',
     'color: #00B7BA; text-shadow: 0 0 1px rgba(0,112,115,0.55), 0 0 10px rgba(0,183,186,0.50), 0 0 22px rgba(247,181,56,0.58)">SCAN TO WATCH'),
    ('text-shadow: 0 0 10px rgba(0,183,186,0.40), 0 0 22px rgba(0,183,186,0.30)">AFTER YOUR',
     'text-shadow: 0 0 1px rgba(0,112,115,0.45), 0 0 10px rgba(0,183,186,0.34), 0 0 22px rgba(0,183,186,0.22)">AFTER YOUR'),
]
def email_tune(html):
    head, body = html.split('<body>', 1)
    for a, b in EMAIL_TEAL.items():
        body = body.replace(a, b).replace(a.lower(), b)
    for a, b in EMAIL_GLOW:
        if a.split('">')[1] in body:
            assert body.count(a) == 1, a[-20:]; body = body.replace(a, b)
    return head + '<body>' + body

def jpg(png, tagged):
    im = Image.open(io.BytesIO(png)).convert('RGB'); assert im.size == (2550, 3300), im.size
    b = io.BytesIO(); kw = {'icc_profile': SRGB} if tagged else {}
    im.save(b, 'JPEG', quality=95, subsampling=0, dpi=(300, 300), **kw); return b.getvalue()

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=sorted(pathlib.Path('/opt/pw-browsers').glob('chromium-*/chrome-linux/chrome'))[0].as_posix())
        pg = await br.new_page(viewport={'width': 816, 'height': 1056}, device_scale_factor=300 / 96)
        async def shot(name, mode):
            html = (PDF / name).read_text()
            path = PDF / f'{mode}_{name}'
            path.write_text(print_tune(html) if mode == 'print' else email_tune(html))
            await pg.goto('file://' + str(path)); await pg.wait_for_load_state('networkidle'); await pg.evaluate('document.fonts.ready')
            # Both versions untagged DeviceRGB, exactly like the Now Offering brochures' own colors, so any viewer
            # shows the handout teal and the brochure teal identically (an sRGB tag made some viewers render it lighter).
            return jpg(await pg.screenshot(clip={'x': 0, 'y': 0, 'width': 816, 'height': 1056}), tagged=False)
        backs = {m: await shot('back.html', m) for m in ('print', 'email')}
        for key, full in DOCS:
            for mode, folder, label in (('print', 'PRINT', 'PRINT (HP glossy)'), ('email', 'EMAIL', 'EMAIL')):
                front = await shot(f'{key}.html', mode)
                out = FINAL / folder / f'{full} - SIJ Patient Story Handout - {label}.pdf'
                out.write_bytes(img2pdf.convert([front, backs[mode]], layout_fun=LAYOUT,
                                                title=f'{full} - SIJ Fusion Patient Story Handout ({label})',
                                                author='Impact Surgical', creator='Impact Surgical'))
                print('wrote', out)
        await br.close()
asyncio.run(main())
