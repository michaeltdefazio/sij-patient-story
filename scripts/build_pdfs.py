import re, json, asyncio, pathlib
from playwright.async_api import async_playwright
T = open('/home/claude/handout/design/Handout.dc.html').read()
body = T[T.index('</helmet>') + len('</helmet>'):T.index('</x-dc>')]
# keep the QR image branch, drop the placeholder branch
body = re.sub(r'<sc-if value="\{\{noQr\}\}"[^>]*>.*?</sc-if>', '', body, flags=re.S)
body = re.sub(r'<sc-if value="\{\{(hasQr|hasPhoto)\}\}"[^>]*>(.*?)</sc-if>', r'\2', body, flags=re.S)
LOC_RE = r'<sc-if value="\{\{hasLoc\}\}"[^>]*>(.*?)</sc-if>'
F = '/home/claude/fontsrc/package/files/montserrat-latin-{w}-{s}.woff2'
faces = ''.join(f"@font-face{{font-family:'Montserrat';font-weight:{w};font-style:{s};src:url('file://{F.format(w=w, s=s)}') format('woff2')}}"
                for w in (400, 500, 600, 700, 800) for s in ('normal', 'italic'))
DOCS = [  # file name, full name, short, location, photo, qr
 ('Rutledge', 'Dr. Joseph Rutledge', 'Dr. Rutledge', 'Lafayette'),
 ('Hom', 'Dr. Brian Hom', 'Dr. Hom', 'Kokomo'),
 ('Gordon', 'Dr. David Gordon', 'Dr. Gordon', 'Greenwood | Carmel'),
 ('Cook', 'Dr. Andrew Cook', 'Dr. Cook', 'Indianapolis | Brownsburg | Avon | Greenwood'),
 ('Kowlowitz', 'Dr. Edward Kowlowitz', 'Dr. Kowlowitz', '8805 N. Meridian St., Indianapolis'),
 ('Oberhelman', 'Dr. Forrest Oberhelman', 'Dr. Oberhelman', 'Kokomo | Indianapolis | Greenwood'),
 ('Dorwart', 'Dr. Michael Dorwart', 'Dr. Dorwart', 'Downtown Indianapolis'),
 ('Kim', 'Dr. Scott Kim', 'Dr. Kim', 'Greenwood'),
 ('Tolbert', 'Dr. Ashley Tolbert', 'Dr. Tolbert', 'Indianapolis | Greenwood'),
 ('Bush', 'Dr. Jocelyn Bush', 'Dr. Bush', '8805 N. Meridian St., Indianapolis')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=sorted(pathlib.Path('/opt/pw-browsers').glob('chromium-*/chrome-linux/chrome'))[0].as_posix())
        pg = await b.new_page(viewport={'width': 816, 'height': 1056})
        for key, full, short, loc in DOCS:
            k = key.lower()
            h = re.sub(LOC_RE, (r'\1' if loc else ''), body, flags=re.S)
            h = h.replace('{{dr}}', full).replace('{{drShort}}', short).replace('{{loc}}', loc.replace(' | ', '\u00a0\u00b7 '))
            h = h.replace('{{photo}}', f'file:///home/claude/handout/up/dr_{k}.jpg').replace('{{qr}}', f'file:///home/claude/handout/qr/qr_{k}.png')
            h = h.replace('/_blob/86ee2e1c30b955a7174b69074d58a175', 'file:///home/claude/handout/up/patient_story_still_crop4.jpg')
            # Scheduling line as printed on each doctor's Now Offering brochure (Dr. Rutledge: Lafayette office).
            if key == 'Rutledge': h = h.replace('317-706-7246', '765-807-2780')
            assert '{{' not in h and 'sc-if' not in h, key
            html = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><style>{faces}@page{{size:8.5in 11in;margin:0}}html,body{{margin:0;padding:0}}</style></head><body>{h}</body></html>"
            src = f'/home/claude/handout/pdf/{k}.html'; open(src, 'w').write(html)
            await pg.goto('file://' + src); await pg.wait_for_load_state('networkidle')
            await pg.evaluate('document.fonts.ready')
            out = f'/home/claude/handout/pdf/_front_{k}.pdf'
            await pg.pdf(path=out, width='8.5in', height='11in', print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}, page_ranges='1')
            await pg.screenshot(path=f'/home/claude/handout/pdf/{k}.png')
        BK = open('/home/claude/handout/design/Back.dc.html').read()
        bk = BK[BK.index('</helmet>') + len('</helmet>'):BK.index('</x-dc>')]
        assert '{{' not in bk and 'sc-if' not in bk
        html = f"<!doctype html><html lang='en'><head><meta charset='utf-8'><style>{faces}@page{{size:8.5in 11in;margin:0}}html,body{{margin:0;padding:0}}</style></head><body>{bk}</body></html>"
        src = '/home/claude/handout/pdf/back.html'; open(src, 'w').write(html)
        await pg.goto('file://' + src); await pg.wait_for_load_state('networkidle'); await pg.evaluate('document.fonts.ready')
        await pg.pdf(path='/home/claude/handout/pdf/_back.pdf', width='8.5in', height='11in', print_background=True, margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'}, page_ranges='1')
        await pg.screenshot(path='/home/claude/handout/pdf/back.png')
        await b.close()
    from pypdf import PdfReader, PdfWriter
    for key, *_ in DOCS:
        w = PdfWriter()
        w.add_page(PdfReader(f'/home/claude/handout/pdf/_front_{key.lower()}.pdf').pages[0])
        w.add_page(PdfReader('/home/claude/handout/pdf/_back.pdf').pages[0])
        out = f'/home/claude/handout/pdf/SIJ_Patient_Story_Handout_Dr_{key}.pdf'
        with open(out, 'wb') as fh: w.write(fh)
        print('wrote', out)
asyncio.run(main())
