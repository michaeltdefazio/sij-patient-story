# SIJ Patient Story: project source (backup)

This branch holds everything used to build the patient story handouts and the website.
It is **not** part of the website: GitHub Pages serves only the `main` branch.
(The repository is public, so this branch can be seen on github.com; it holds nothing that isn't already on the site or the handouts.)

## Live website
https://michaeltdefazio.github.io/sij-patient-story/<doctor>/
Doctors: rutledge, hom, gordon, cook, kowlowitz, oberhelman, dorwart, kim, tolbert, bush

**Do not** rename or delete the repository, change the GitHub username, turn off Pages, or rename a doctor folder.
Every printed QR code depends on these addresses.

## What's here
| Folder | Contents |
|---|---|
| `scripts/` | `build_pdfs.py` (handout HTML/PDF), `build_print.py` (HP print tuning, used by build_final), `build_final.py` (PRINT + EMAIL PDFs), `build_site.py` (website), `build_share.py` (link-preview images, icon), `extract_bios.py` (doctor bios from brochures) |
| `design/` | Handout front (`Handout.dc.html`) and back (`Back.dc.html`) design |
| `brochures/` | Each doctor's Now Offering brochure (EMAIL version) |
| `assets/` | Headshots (reframed), QR codes (PNG/SVG + map), Montserrat fonts |
| `web/` | Captions, doctor bios, page images, link-preview images, video poster |
| `print/` | Final PRINT (HP glossy) handouts for all ten doctors. EMAIL versions are on the site in each doctor folder. |

Website videos live on `main` in `videos/`.

## Rebuild
```
bash restore.sh
python3 -I /home/claude/scripts/build_pdfs.py && python3 -I /home/claude/scripts/build_final.py
SITE_REPO=sij-patient-story python3 -I /home/claude/scripts/build_site.py
```
Publish: copy `/home/claude/web/gh/sij-patient-story/` over a clone of `main` (keep `videos/`), commit, push.

## Settings to keep
- **PRINT files**: brochure print teal #4BDEBC, footer lifted for HP borderless trim, no text glow on white, untagged RGB.
  Print from Acrobat with "Let printer determine colors", preset Borderless / HP Glossy Brochure / Best.
- **EMAIL files**: Now Offering brochure teal #00B7BA (#33C5C8 on navy), untagged RGB.
- **Dr. Rutledge**: Lafayette office line 765-807-2780 (all others 317-706-7246).
- Patient's words are never changed. The interview is Dr. Rutledge's patient. No other doctor is paired with the video in link previews.

## Open items
- **Old Dr. Rutledge QR (10 early copies):** points to the old claude.ai page. Before finalizing, offer to turn that page into a "tap here for the updated page" link to /rutledge/. Keep that claude.ai page shared until then.
- Optional: visit counter per doctor page (needs a free analytics account).
- Optional: real titles for the two brochure education videos (currently "SI Joint Patient Education · Part 1/2").
