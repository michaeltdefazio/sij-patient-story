# Pull each doctor's bio, education and credential badges from page 2 of their Now Offering EMAIL brochure
# (Mike's approved wording), for the doctor section of the patient landing pages.
import re, glob, json, subprocess, html
ATT = '/home/claude/handout/brochures'
out = {}
for f in sorted(glob.glob(ATT + '/*Brochure*.pdf')):
    key = re.search(r'Dr\._[A-Za-z]+_([A-Za-z]+)_-', f).group(1).lower()
    x = subprocess.run(['pdftotext', '-f', '2', '-l', '2', '-bbox-layout', f, '-'], capture_output=True, text=True).stdout
    blocks = []
    for m in re.finditer(r'<block xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</block>', x, re.S):
        lines = [' '.join(html.unescape(w) for w in re.findall(r'>([^<]+)</word>', ln)) for ln in re.findall(r'<line.*?</line>', m.group(5), re.S)]
        blocks.append((float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), lines))
    ed = next(b for b in blocks if b[4] and b[4][0].startswith('Education'))
    badge_y = min(b[1] for b in blocks if b[4] and b[4][0].isupper() and len(b[4][0]) > 6 and b[1] > ed[1] + 50 and 'PATIENT' not in b[4][0])
    bio_blocks = [b for b in sorted(blocks, key=lambda b: b[1]) if b[0] < 300 and ed[1] - 10 <= b[1] < badge_y - 5]
    bio = []; last = None   # merge line-blocks that belong to one paragraph (gap under 6 pt)
    for b in bio_blocks:
        t = ' '.join(b[4])
        if bio and last is not None and b[1] - last < 6: bio[-1] += ' ' + t
        else: bio.append(t)
        last = b[3]
    edu = []
    for b in sorted(blocks, key=lambda b: b[1]):
        if b[0] > 300 and ed[1] + 5 < b[1] < badge_y - 5:
            edu.append((b[4][0], ' '.join(b[4][1:])))
    labels = sorted([b for b in blocks if abs(b[1] - badge_y) < 3], key=lambda b: b[0])
    vals = sorted([b for b in blocks if 8 < b[1] - badge_y < 20], key=lambda b: b[0])
    badges = [(l[4][0], v[4][0]) for l, v in zip(labels, vals)]
    foot = [b for b in blocks if b[1] > 730 and 'Center for Pain' in ' '.join(b[4])]
    out[key] = {'bio': bio, 'education': edu, 'badges': badges, 'footer': foot[0][4] if foot else []}
json.dump(out, open('/home/claude/web/brochure_bios.json', 'w'), indent=1, ensure_ascii=False)
for k, v in out.items():
    print('==', k); print('  BIO:', ' || '.join(v['bio'])); print('  EDU:', v['education']); print('  BADGES:', v['badges']); print('  FOOT:', v['footer'])
