# Link-preview images (1200x630, shown when a page link is texted or emailed) and the site icon.
import asyncio, pathlib, base64
from playwright.async_api import async_playwright

OUT = pathlib.Path('/home/claude/web/share'); OUT.mkdir(parents=True, exist_ok=True)
F = '/home/claude/fontsrc/package/files/montserrat-latin-{w}-{s}.woff2'
FACES = ''.join(f"@font-face{{font-family:'Montserrat';font-weight:{w};font-style:{s};src:url('file://{F.format(w=w, s=s)}') format('woff2')}}"
                for w in (500, 600, 700, 800) for s in ('normal', 'italic'))
DOCS = [('rutledge', 'Dr. Joseph Rutledge'), ('hom', 'Dr. Brian Hom'), ('gordon', 'Dr. David Gordon'), ('cook', 'Dr. Andrew Cook'),
        ('kowlowitz', 'Dr. Edward Kowlowitz'), ('oberhelman', 'Dr. Forrest Oberhelman'), ('dorwart', 'Dr. Michael Dorwart'), ('kim', 'Dr. Scott Kim')]
POSTER = '/home/claude/web/poster_hd.jpg'   # full-quality frame (2:56), eyes open
PLAY = ('<svg width="96" height="96" viewBox="0 0 96 96"><circle cx="48" cy="48" r="46" fill="rgba(255,255,255,0.95)"/>'
        '<path d="M39 30 L68 48 L39 66 Z" fill="#1F2735"/></svg>')

def card(full=None, key=None):
    doc = ''
    if full:
        doc = f'''<div class="doc"><img src="file:///home/claude/handout/up/dr_{key}.jpg"><div><div class="k">Physician Spotlight</div><div class="n">{full}</div></div></div>'''
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>{FACES}
    html,body{{margin:0}} body{{width:1200px;height:630px;display:flex;font-family:Montserrat;background:#293242;overflow:hidden}}
    .pic{{width:560px;height:630px;position:relative;background:#000 url('file://{POSTER}') 14% center/cover}}
    .pic .pl{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%)}}
    .txt{{flex:1;position:relative;padding:58px 52px 0 52px;color:#fff;display:flex;flex-direction:column;gap:14px;
          background:radial-gradient(circle at 85% 10%,rgba(43,196,199,0.22),rgba(43,196,199,0) 55%),#293242}}
    .txt::before{{content:"";position:absolute;left:0;right:0;top:0;height:10px;background:#EB9F25}}
    .e{{font-size:22px;font-weight:800;letter-spacing:.16em;text-transform:uppercase;color:#33C5C8}}
    h1{{margin:0;font-size:56px;line-height:1.08;font-weight:800;font-style:italic}} h1 span{{color:#F7B538}}
    .s{{font-size:26px;font-weight:600;font-style:italic;color:#DDE7EA}}
    .doc{{margin-top:auto;margin-bottom:44px;display:flex;align-items:center;gap:20px}}
    .doc img{{width:104px;height:104px;border-radius:16px;border:4px solid #F2B43A;background:#fff;padding:4px;object-fit:cover;
              box-shadow:0 0 0 6px rgba(242,180,58,.2),0 0 26px 6px rgba(242,180,58,.38)}}
    .k{{font-size:18px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#F7B538}}
    .n{{font-size:34px;font-weight:800;font-style:italic;line-height:1.15}}
    .foot{{margin-top:auto;margin-bottom:44px;font-size:22px;font-weight:700;color:#C9D3DB}}
    </style></head><body><div class="pic"><div class="pl">{PLAY}</div></div><div class="txt">
    <div class="e">Patient Testimonial</div><h1>Hear From a<br><span>Center for Pain</span> Patient</h1>
    <div class="s">Listen to her story.</div>
    {doc or '<div class="foot">Center for Pain Management</div>'}</div></body></html>'''

ICON = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#293242"/>
<rect y="0" width="64" height="5" rx="2" fill="#EB9F25"/><circle cx="32" cy="34" r="19" fill="#00B7BA"/>
<path d="M27 24.5 L42 34 L27 43.5 Z" fill="#FFFFFF"/></svg>'''

async def main():
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=sorted(pathlib.Path('/opt/pw-browsers').glob('chromium-*/chrome-linux/chrome'))[0].as_posix())
        pg = await br.new_page(viewport={'width': 1200, 'height': 630})
        for key, full in DOCS + [('root', None)]:
            tmp = OUT / f'_{key}.html'; tmp.write_text(card(full, key))
            await pg.goto('file://' + str(tmp)); await pg.wait_for_load_state('networkidle'); await pg.evaluate('document.fonts.ready')
            await pg.screenshot(path=str(OUT / f'{key}.jpg'), type='jpeg', quality=86); tmp.unlink()
        (OUT / 'favicon.svg').write_text(ICON)
        pg2 = await br.new_page(viewport={'width': 180, 'height': 180})
        await pg2.set_content(f'<html><body style="margin:0;background:#293242">{ICON.replace("<svg ", "<svg width=\"180\" height=\"180\" ")}</body></html>')
        await pg2.screenshot(path=str(OUT / 'apple-touch-icon.png'))
        await br.close()
    print(sorted(x.name for x in OUT.iterdir()))
asyncio.run(main())
