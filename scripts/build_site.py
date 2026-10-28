# Branded patient-story site for GitHub Pages: one page per physician (/<id>/) playing that physician's video
# (hosted on the site, no YouTube branding), plus a chooser at the root. QR codes on the printed handouts point to
# https://michaeltdefazio.github.io/sij-patient-story/<id>/  -- never rename the repo or the doctor folders.
# v2 upgrades: physician card with headshot + locations + official profile link, on/off captions, tappable chapters,
# share button, "save contact" for Mike, sticky call bar on phones, link-preview images, site icon, chooser with photos.
import pathlib, shutil, html, os, glob
from PIL import Image

OUT = pathlib.Path('/home/claude/web/gh/sij-patient-story')
SITE = 'https://michaeltdefazio.github.io/sij-patient-story/'
APC = 'https://www.americanpainconsortium.com/find-a-provider/'
# id, full name, short, locations (same as the printed handout / Now Offering brochure), official profile slug
DOCS = [
    ('rutledge', 'Dr. Joseph Rutledge', 'Dr. Rutledge', 'Lafayette', 'joseph-c-rutledge-md'),
    ('hom', 'Dr. Brian Hom', 'Dr. Hom', 'Kokomo', 'brian-hom-md'),
    ('gordon', 'Dr. David Gordon', 'Dr. Gordon', 'Greenwood | Carmel', 'david-gordon-md'),
    ('cook', 'Dr. Andrew Cook', 'Dr. Cook', 'Indianapolis | Brownsburg | Avon | Greenwood', 'andrew-cook-md'),
    ('kowlowitz', 'Dr. Edward Kowlowitz', 'Dr. Kowlowitz', '8805 N. Meridian St., Indianapolis', 'edward-kowlowitz-md'),
    ('oberhelman', 'Dr. Forrest Oberhelman', 'Dr. Oberhelman', 'Kokomo | Indianapolis | Greenwood', 'forrest-oberhelman-do'),
    ('dorwart', 'Dr. Michael Dorwart', 'Dr. Dorwart', 'Downtown Indianapolis', 'michael-r-dorwart-md'),
    ('kim', 'Dr. Scott Kim', 'Dr. Kim', 'Greenwood', 'scott-kim-md'),
    ('tolbert', 'Dr. Ashley Tolbert', 'Dr. Tolbert', 'Indianapolis | Greenwood', 'ashley-tolbert-md'),
    ('bush', 'Dr. Jocelyn Bush', 'Dr. Bush', '8805 N. Meridian St., Indianapolis', 'jocelyn-bush-md'),
]
# Same five topics as the printed handout. Times are where each topic's on-screen question appears in the video
# (all eight videos share the same interview timing).
CHAPTERS = [('Her symptoms', 'Low back pain that became burning leg pain', 17.2),
            ('Daily life', 'Years of pain that limited her walking', 44.8),
            ('Finding the source', 'How her SI joint was confirmed as the cause', 91.0),
            ('The procedure', 'What treatment and recovery were like', 127.5),
            ('Life after', 'The everyday activities she’s back to doing', 182.4)]

CHECK = ('<svg width="22" height="22" viewBox="0 0 20 20" aria-hidden="true"><circle cx="10" cy="10" r="10" fill="#00B7BA"/>'
         '<path d="M5.5 10.2 L8.6 13.2 L14.5 7.2" fill="none" stroke="#FFFFFF" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>')
PHONE = ('<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.1 15.1 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25'
         'c1.1.37 2.3.57 3.6.57a1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.57a1 1 0 0 1-.25 1z" fill="currentColor"/></svg>')
PIN = ('<svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5.25 7 13 7 13s7-7.75 7-13a7 7 0 0 0-7-7zm0 9.5'
       'a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5z" fill="currentColor"/></svg>')
SHARE = ('<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v12M7 8l5-5 5 5M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6" fill="none" '
         'stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>')
CC = ('<svg width="20" height="18" viewBox="0 0 24 20" aria-hidden="true"><rect x="1" y="1" width="22" height="18" rx="4" fill="none" stroke="currentColor" stroke-width="2"/>'
      '<path d="M10.5 7.6a3 3 0 1 0 0 4.8M18.5 7.6a3 3 0 1 0 0 4.8" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')
CONTACT = ('<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8" r="4" fill="none" stroke="currentColor" stroke-width="2.2"/>'
           '<path d="M4 21c1-4 4.5-6 8-6s7 2 8 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>')
DOC_ICON = ('<svg width="24" height="24" viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z" '
            'fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linejoin="round"/><path d="M14 3v5h5M9 13h6M9 17h6" fill="none" stroke="#FFFFFF" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>')

CSS = """
  :root { --navy:#293242; --navy-2:#1F2735; --orange:#EB9F25; --gold:#F7B538; --teal:#00B7BA; --teal-bright:#00B7BA; --paper:#FFFFFF;
          --soft:#F3F5F7; --ink:#293242; --muted:#5A6270; --on-navy:#FFFFFF; --teal-on-navy:#4FD3D6;
          --font:'Montserrat','Segoe UI',Arial,Helvetica,sans-serif; color-scheme: light; --bar: 0px; }
  * { box-sizing: border-box; }
  html { -webkit-text-size-adjust: 100%; scroll-behavior: smooth; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: var(--font); font-size: 16px; line-height: 1.5; }
  .wrap { max-width: 760px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left)); padding-right: max(16px, env(safe-area-inset-right)); }
  .band { background: var(--navy); color: var(--on-navy); position: relative; }
  .obar { background: var(--orange); }
  .obar .wrap { padding-block: 14px 16px; display: flex; flex-direction: column; gap: 3px; }
  .obar .ot { margin: 0; font-size: clamp(18px, 4.9vw, 22px); font-weight: 800; font-style: italic; line-height: 1.2; color: var(--navy-2); text-wrap: balance; }
  .nw { white-space: nowrap; }
  .obar .os { margin: 0; font-size: 14.5px; font-weight: 600; line-height: 1.4; color: var(--navy); text-wrap: balance; }
  .band .wrap { padding-block: 26px 30px; display: flex; flex-direction: column; gap: 6px; }
  .eyebrow { font-size: 13.5px; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; color: #33C5C8; }
  h1 { margin: 0; font-size: clamp(25px, 7vw, 40px); font-weight: 800; font-style: italic; line-height: 1.1; text-wrap: balance; }
  h1 .cfp { color: var(--gold); }
  .sub { margin: 2px 0 0; font-size: 17px; font-weight: 600; font-style: italic; color: #DDE7EA; }
  main .wrap { padding-block: 22px 8px; display: flex; flex-direction: column; gap: 28px; }
  h2 { margin: 0 0 10px; font-size: 21px; font-weight: 800; line-height: 1.2; color: var(--navy); text-wrap: balance; padding-left: 12px; border-left: 5px solid var(--teal-bright); }
  .solution h2, .ask-mike h2 { padding-left: 0; border-left: 0; }
  p, li, dd { text-wrap: pretty; }
  .next .phone, .ask-mike p, .tile b, .tile span, ul.ticks li, .edu-note { text-wrap: balance; }
  a:focus-visible, button:focus-visible { outline: 3px solid var(--orange); outline-offset: 3px; }

  .player { display: flex; flex-direction: column; gap: 10px; scroll-margin-top: 12px; }
  .frame { position: relative; width: 100%; aspect-ratio: 16 / 9; background: #000; border-radius: 12px; overflow: hidden; }
  .playover { position: absolute; inset: 0; z-index: 2; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 12px;
              border: 0; padding: 0; cursor: pointer; background: linear-gradient(180deg, rgba(15,20,30,0) 35%, rgba(15,20,30,0.55) 100%); }
  .playover[hidden] { display: none; }
  .playover .pi { width: 68px; height: 68px; border-radius: 50%; background: rgba(255,255,255,0.95); display: flex; align-items: center; justify-content: center;
                  padding-left: 4px; box-shadow: 0 6px 22px rgba(0,0,0,0.35); }
  .playover .pt { font: 800 13.5px/1 var(--font); letter-spacing: .12em; text-transform: uppercase; color: var(--navy-2); background: #F2B43A;
                  border-radius: 8px; padding: 9px 14px; box-shadow: 0 4px 14px rgba(0,0,0,0.3); }
  .playover:hover .pi, .playover:focus-visible .pi { transform: scale(1.06); }
  .frame video, .frame iframe { position: absolute; inset: 0; width: 100%; height: 100%; display: block; border: 0; background: #000; object-fit: contain; }
  video::cue { font-family: var(--font); font-weight: 600; background: rgba(15,20,30,0.82); color: #FFFFFF; line-height: 1.35; }
  .tools { display: flex; flex-wrap: wrap; gap: 8px; }
  .tools .chip { flex: 1 1 auto; justify-content: center; }
  .tools .toast { flex-basis: 100%; }
  .toast:empty { display: none; }
  .chip { display: inline-flex; align-items: center; gap: 8px; min-height: 46px; padding: 8px 14px; border-radius: 999px; border: 2px solid #D5DAE0;
          background: #FFFFFF; color: var(--ink); font: 700 15px/1 var(--font); cursor: pointer; text-decoration: none; white-space: nowrap; }
  .chip[aria-pressed="true"] { background: var(--navy); border-color: var(--navy); color: #FFFFFF; }
  .chip .st { font-weight: 600; color: var(--muted); }
  .chip[aria-pressed="true"] .st { color: var(--teal-on-navy); }
  .toast { font-size: 14px; font-weight: 600; color: var(--teal); align-self: center; }

  .doc { position: relative; overflow: hidden; display: flex; align-items: center; gap: 18px; padding: 20px; border-radius: 16px; color: #FFFFFF;
         background: radial-gradient(circle at 92% 0%, rgba(43,196,199,0.22), rgba(43,196,199,0) 55%), var(--navy-2); }
  .doc::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 4px; background: var(--orange); }
  .doc img { width: 112px; height: 112px; flex-shrink: 0; object-fit: cover; border-radius: 16px; border: 3px solid #F2B43A; background: #FFFFFF; padding: 4px;
             box-shadow: 0 0 0 5px rgba(242,180,58,0.18), 0 0 22px 4px rgba(242,180,58,0.34); }
  .doc .k { font-size: 12.5px; font-weight: 800; letter-spacing: .14em; text-transform: uppercase; color: var(--gold); }
  .doc .n { margin: 2px 0 2px; font-size: clamp(21px, 5.6vw, 27px); font-weight: 800; font-style: italic; line-height: 1.15; color: #FFFFFF; }
  .doc .ti { font-size: 14px; font-weight: 600; color: var(--teal-on-navy); }
  .doc .lo { margin-top: 6px; display: flex; gap: 6px; align-items: flex-start; font-size: 14px; font-weight: 600; color: #DDE7EA; }
  .doc .lo svg { flex-shrink: 0; margin-top: 2px; color: var(--gold); }
  .doc .pf { display: inline-block; margin-top: 10px; font-size: 14px; font-weight: 700; color: #FFFFFF; text-decoration: underline; text-decoration-color: var(--gold);
             text-underline-offset: 4px; text-decoration-thickness: 2px; }
  @media (max-width: 400px) { .doc { gap: 14px; padding: 18px 16px; } .doc img { width: 92px; height: 92px; } }

  .hint { margin: -4px 0 12px; font-size: 14.5px; color: var(--muted); font-weight: 500; }
  ol.chap { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 8px; }
  ol.chap button, ol.chap .row { width: 100%; display: flex; gap: 12px; align-items: center; text-align: left; padding: 12px 14px; border-radius: 12px;
         border: 2px solid transparent; background: var(--soft); color: var(--ink); font: inherit; cursor: pointer; }
  ol.chap .row { cursor: default; }
  ol.chap button:hover { border-color: var(--teal-bright); }
  ol.chap button.now { border-color: var(--teal-bright); background: #E3F6F6; }
  ol.chap svg { flex-shrink: 0; }
  ol.chap .tx { flex: 1; display: flex; flex-direction: column; }
  ol.chap b { color: var(--teal); font-size: 16px; font-weight: 800; }
  ol.chap .d { font-size: 15.5px; font-weight: 500; }
  ol.chap .tm { flex-shrink: 0; display: inline-flex; align-items: center; gap: 5px; font-size: 13.5px; font-weight: 800; color: var(--navy);
         background: #FFFFFF; border: 1.5px solid #D5DAE0; border-radius: 999px; padding: 4px 10px; font-variant-numeric: tabular-nums; }

  .next { background: var(--soft); border-radius: 14px; padding: 20px; display: flex; flex-direction: column; gap: 6px; }
  .next .label { font-size: 13px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--teal); }
  .next .ask { font-size: 20px; font-weight: 800; line-height: 1.3; }
  .next .phone a { color: var(--ink); font-weight: 800; }
  .btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 48px; padding: 12px 20px; border-radius: 12px;
         font: 800 16px/1.1 var(--font); text-decoration: none; }
  .btn.call { background: var(--orange); color: var(--navy-2); }
  .next .btn { align-self: flex-start; margin-top: 8px; }

  .ask-mike { position: relative; overflow: hidden; background: var(--navy-2); color: #FFFFFF; border-radius: 16px; padding: 24px 20px; display: flex;
              flex-direction: column; align-items: center; gap: 6px; text-align: center; box-shadow: 0 0 0 4px rgba(242,180,58,0.14), 0 0 26px 4px rgba(242,180,58,0.22); }
  .ask-mike::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 4px; background: var(--orange); }
  .ask-mike .k { font-size: 13px; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: var(--teal-on-navy); text-wrap: balance; }
  .ask-mike .q { margin: 0; font-size: 22px; font-weight: 800; line-height: 1.25; color: var(--gold); text-wrap: balance; }
  .ask-mike .num { font-size: clamp(32px, 9vw, 44px); font-weight: 800; letter-spacing: .01em; color: #FFFFFF; text-decoration: none; line-height: 1.1; margin-top: 4px; }
  .ask-mike .who { font-size: 15px; font-weight: 600; color: #C9D3DB; text-wrap: balance; }
  .ask-mike .who b { color: #FFFFFF; }
  .ask-mike .role { white-space: nowrap; }
  @media (max-width: 480px) { .ask-mike .who b { display: block; } .ask-mike .sep { display: none; } }
  .ask-mike .em { font-size: 16px; font-weight: 700; color: var(--teal-on-navy); }
  .ask-mike p { margin: 8px 0 0; font-size: 15px; font-weight: 500; line-height: 1.5; color: #DDE7EA; max-width: 520px; }
  .ask-mike .btns { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 14px; }
  .ask-mike .btn.out { background: transparent; color: #FFFFFF; border: 2px solid var(--teal-on-navy); }

  .dl { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 260px), 1fr)); gap: 12px; }
  .dl a { display: flex; gap: 14px; align-items: center; padding: 16px; border-radius: 12px; background: var(--soft); color: var(--ink); text-decoration: none; border: 2px solid transparent; }
  .dl a:hover, .dl a:focus-visible { border-color: var(--teal-bright); outline: none; }
  .dl .th { width: 62px; height: 80px; flex-shrink: 0; border-radius: 6px; object-fit: cover; box-shadow: 0 2px 8px rgba(31,39,53,0.22); background: #FFFFFF; }
  .dl .ic { width: 44px; height: 44px; border-radius: 10px; background: var(--teal-bright); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .dl .t { font-weight: 800; line-height: 1.25; }
  .dl .s { font-size: 13.5px; font-weight: 500; color: var(--muted); }
  .edu { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr)); gap: 14px; }
  .edu figure { margin: 0; display: flex; flex-direction: column; gap: 8px; }
  .edu figcaption { font-size: 15px; font-weight: 700; }
  .edu-note { margin: 0 0 12px; font-size: 15px; color: var(--muted); }

  .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 230px), 1fr)); gap: 10px; }
  .grid a { display: flex; align-items: center; gap: 12px; padding: 10px 14px 10px 10px; border-radius: 12px; background: var(--soft); color: var(--ink);
            font-weight: 800; text-decoration: none; border: 2px solid transparent; }
  .grid a img { width: 56px; height: 56px; border-radius: 10px; object-fit: cover; border: 2px solid #F2B43A; background: #FFFFFF; }
  .grid a:hover, .grid a:focus-visible { border-color: var(--teal-bright); outline: none; }

  .vh { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
  h3 { margin: 0 0 8px; font-size: 17px; font-weight: 800; color: var(--teal-bright); }
  .learn { display: flex; flex-direction: column; gap: 14px; }
  .learn h2 { margin: 0; }
  .learn .lead { margin: 0; font-size: 18px; font-weight: 700; line-height: 1.4; color: var(--navy); text-wrap: pretty; }
  .about { background: var(--soft); border-radius: 14px; padding: 16px 18px; border-left: 5px solid var(--teal-bright); }
  .about p { margin: 0; font-size: 16px; font-weight: 500; line-height: 1.55; text-wrap: pretty; }
  .signs { display: flex; gap: 16px; align-items: flex-start; padding: 4px 2px; }
  .signs .leg { width: 64px; height: auto; flex-shrink: 0; margin-top: 4px; }
  ul.ticks { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: 1fr; gap: 7px 22px; }
  ul.ticks li { display: flex; gap: 8px; align-items: flex-start; font-size: 16px; font-weight: 500; line-height: 1.35; }
  ul.ticks svg { flex-shrink: 0; margin-top: 1px; }
  .learn-grid { display: grid; grid-template-columns: 1fr; gap: 14px; }
  @media (min-width: 620px) { .learn-grid { grid-template-columns: 1.25fr 1fr; gap: 30px; align-items: start; }
  }
  .conv { background: var(--soft); border-radius: 14px; padding: 16px 18px; }
  .solution { position: relative; overflow: hidden; border-radius: 16px; padding: 22px 20px 20px; color: #FFFFFF;
              background: radial-gradient(circle at 92% 0%, rgba(51,197,200,0.20), rgba(51,197,200,0) 55%), var(--navy-2); }
  .solution::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 4px; background: var(--orange); }
  .solution .k { font-size: 13px; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; color: var(--gold); }
  .solution h2 { margin: 2px 0 8px; font-size: clamp(22px, 5.8vw, 28px); font-style: italic; color: #33C5C8; }
  .solution p { margin: 0 0 16px; font-size: 16px; font-weight: 500; line-height: 1.55; color: #E3EAEE; text-wrap: pretty; }
  .tiles { display: grid; grid-template-columns: 1fr; gap: 10px; }
  @media (min-width: 620px) { .tiles { grid-template-columns: 1fr 1fr 1fr; } }
  .tile { display: flex; flex-direction: column; gap: 4px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12);
          border-radius: 12px; padding: 14px 16px; }
  .tile b { font-size: 16px; font-weight: 800; color: #33C5C8; }
  .tile span { font-size: 14.5px; font-weight: 500; color: #DDE7EA; line-height: 1.45; }
  .tile.dime { flex-direction: row; align-items: center; gap: 14px; }
  .tile.dime img { width: 58px; height: 58px; flex-shrink: 0; }
  .tile.dime div { display: flex; flex-direction: column; gap: 2px; }
  .tile .big { font-size: 26px !important; font-weight: 800 !important; color: #FFFFFF !important; line-height: 1.1 !important; }
  .meet { display: flex; flex-direction: column; gap: 14px; }
  ul.badges { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(3, 1fr); background: var(--soft); border-radius: 14px;
              border-top: 3px solid var(--teal-bright); overflow: hidden; }
  ul.badges li { display: flex; flex-direction: column; gap: 3px; padding: 12px 14px; border-left: 1px solid #DCE1E6; }
  ul.badges li:first-child { border-left: 0; }
  .bl { font-size: 11px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: var(--orange); line-height: 1.25; }
  .bv { font-size: 14px; font-weight: 700; color: var(--navy); line-height: 1.3; }
  @media (max-width: 480px) { ul.badges { grid-template-columns: 1fr; } ul.badges li { flex-direction: row; justify-content: space-between; align-items: baseline; gap: 10px;
    border-left: 0; border-top: 1px solid #DCE1E6; padding: 11px 14px; } ul.badges li:first-child { border-top: 0; } .bv { text-align: right; } }
  .bio p { margin: 0 0 10px; font-size: 16px; font-weight: 500; line-height: 1.6; text-wrap: pretty; }
  .bio p:last-child { margin-bottom: 0; }
  .edu-list { background: var(--soft); border-radius: 12px; }
  .edu-list summary { list-style: none; cursor: pointer; display: flex; align-items: center; justify-content: space-between; gap: 10px; padding: 13px 16px;
                      font-size: 16px; font-weight: 800; color: var(--navy); }
  .edu-list summary::-webkit-details-marker { display: none; }
  .edu-list summary::after { content: ""; width: 9px; height: 9px; border-right: 2.5px solid var(--teal-bright); border-bottom: 2.5px solid var(--teal-bright);
                             transform: rotate(45deg); margin: -4px 4px 0 0; transition: transform .15s; }
  .edu-list[open] summary::after { transform: rotate(-135deg); margin-top: 4px; }
  .edu-list dl { padding: 2px 16px 16px; }
  .edu-list dl { margin: 0; display: flex; flex-direction: column; gap: 8px; }
  .edu-list dl > div { display: flex; flex-direction: column; padding-left: 12px; border-left: 3px solid #D5DAE0; }
  .edu-list dt { font-size: 14px; font-weight: 800; color: var(--teal-bright); }
  .edu-list dd { margin: 0; font-size: 15px; font-weight: 500; line-height: 1.45; }
  ul.expect { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 10px; }
  ul.expect li { display: flex; gap: 10px; align-items: flex-start; font-size: 16px; font-weight: 500; line-height: 1.45; }
  ul.expect svg { flex-shrink: 0; margin-top: 1px; }
  ul.expect b { color: var(--teal-bright); font-weight: 800; }
  .fine { margin: 0; font-size: 12.5px; color: var(--muted); line-height: 1.45; }
  footer { margin-top: 26px; background: var(--teal); color: var(--on-navy); }
  footer .wrap { padding-block: 18px calc(22px + var(--bar)); display: flex; flex-wrap: wrap; gap: 8px 28px; align-items: center; justify-content: space-between; font-weight: 700; }
  footer a { color: var(--on-navy); text-underline-offset: 3px; }
  .loc { font-weight: 500; white-space: nowrap; }
  @media (max-width: 480px) { footer .loc { display: block; margin-top: 2px; } footer .dot { display: none; } }

  .callbar { display: none; }
  @media (max-width: 820px) {
    :root { --bar: calc(70px + env(safe-area-inset-bottom)); }
    .callbar { display: flex; gap: 8px; position: fixed; left: 0; right: 0; bottom: 0; z-index: 10; background: rgba(255,255,255,0.97);
               padding: 10px max(12px, env(safe-area-inset-left)) calc(10px + env(safe-area-inset-bottom)); box-shadow: 0 -4px 18px rgba(31,39,53,0.16); }
    .callbar a { flex: 1; min-height: 50px; display: flex; flex-direction: column; align-items: center; justify-content: center; border-radius: 12px;
                 text-decoration: none; font: 800 15px/1.15 var(--font); text-align: center; }
    .callbar a small { font-size: 12px; font-weight: 600; }
    .callbar .a { background: var(--orange); color: var(--navy-2); }
    .callbar .b { background: var(--navy-2); color: #FFFFFF; }
    .callbar .b small { color: var(--teal-on-navy); }
  }
  @media (max-width: 430px) { .chip { font-size: 14.5px; padding: 8px 11px; gap: 6px; } .tools { gap: 6px; } }
  @media (max-width: 380px) { .callbar a { font-size: 13.5px; } }
"""

JS = """
(function () {
  var v = document.querySelector('video'); if (!v) return;
  var tr = v.textTracks && v.textTracks[0];
  var cc = document.getElementById('cc');
  function syncCC() { if (!cc || !tr) return; var on = tr.mode === 'showing'; cc.setAttribute('aria-pressed', on); cc.querySelector('.st').textContent = on ? 'On' : 'Off'; }
  if (cc && tr) {
    tr.mode = 'hidden';
    cc.addEventListener('click', function () { tr.mode = (tr.mode === 'showing') ? 'hidden' : 'showing'; syncCC(); });
    v.textTracks.addEventListener && v.textTracks.addEventListener('change', syncCC);
    syncCC();
  } else if (cc) { cc.hidden = true; }

  var po = document.getElementById('playover');
  if (po) {
    v.controls = false;   // clean poster with one big button; the player's own controls appear once it starts
    po.addEventListener('click', function () { v.play().catch(function () {}); });
    v.addEventListener('play', function () { po.hidden = true; v.controls = true; });
    v.addEventListener('ended', function () { po.hidden = false; v.controls = false; });
  }
  var chaps = [].slice.call(document.querySelectorAll('[data-t]'));
  function seek(t) {
    document.getElementById('watch').scrollIntoView({ block: 'start' });
    if (v.readyState >= 1) { v.currentTime = t; v.play().catch(function () {}); }
    else { v.addEventListener('loadedmetadata', function () { v.currentTime = t; }, { once: true }); v.play().catch(function () {}); }
  }
  chaps.forEach(function (b) { b.addEventListener('click', function () { seek(parseFloat(b.dataset.t)); }); });
  v.addEventListener('timeupdate', function () {
    var t = v.currentTime, cur = null;
    chaps.forEach(function (b) { if (t >= parseFloat(b.dataset.t) - 0.5) cur = b; });
    chaps.forEach(function (b) { b.classList.toggle('now', b === cur && !v.paused); });
  });

  var sh = document.getElementById('share'), toast = document.getElementById('toast');
  if (sh) sh.addEventListener('click', function () {
    var url = location.href.split('#')[0];
    var data = { title: document.title, text: "Hear a Center for Pain Management patient share her SI joint fusion story.", url: url };
    if (navigator.share) { navigator.share(data).catch(function () {}); return; }
    var done = function (msg) { toast.textContent = msg; setTimeout(function () { toast.textContent = ''; }, 4000); };
    if (navigator.clipboard) navigator.clipboard.writeText(url).then(function () { done('Link copied. Paste it in a text or email.'); }, function () { done(url); });
    else done(url);
  });
})();
"""

# Scheduling line per doctor, as printed on each Now Offering brochure (Dr. Rutledge's lists the Lafayette office).
PHONES = {'rutledge': '765-807-2780'}
def tel(n): return 'tel:+1' + n.replace('-', '')

def page(title, body, rel, desc, og_img, og_url, callbar=True, script=True, phone='317-706-7246'):
    bar = (f'''<nav class="callbar" aria-label="Call">
  <a class="a" href="{tel(phone)}">Call to Schedule<small>{phone}</small></a>
  <a class="b" href="tel:+13173400342">Questions? Ask Mike<small>317-340-0342</small></a>
</nav>''' if callbar else '')
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex, nofollow">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:url" content="{og_url}">
<meta property="og:image" content="{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Hear From a Center for Pain Patient: her SI joint fusion story">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#293242">
<link rel="icon" href="{rel}favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{rel}apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,500;0,600;0,700;0,800;1,600;1,800&display=swap">
<style>{CSS}</style>
</head>
<body>
<header class="band"><div class="wrap">
  <div class="eyebrow">Patient Testimonial</div>
  <h1>Hear From a<br><span class="cfp">Center for Pain</span> Patient</h1>
  <p class="sub">Listen to her story.</p>
</div></header>
<div class="obar"><div class="wrap">
  <p class="ot"><span class="nw">Considering SI joint fusion?</span> <span class="nw">Watch this first.</span></p>
  <p class="os">Know what to expect from diagnosis to recovery, and come ready with your questions.</p>
</div></div>
<main><div class="wrap">
{body}
  <p class="fine">Patient testimonial. Individual results vary, and this patient’s experience may not be typical. Talk with your physician about the benefits and risks of any procedure. This video is for general information and is not medical advice.</p>
</div></main>
<footer><div class="wrap">
  <div>Center for Pain Management <span class="loc"><span class="dot">&middot; </span><a href="{tel(phone)}">{phone}</a></span></div>
  <a href="https://www.indypain.com" target="_blank" rel="noopener">www.IndyPain.com</a>
</div></footer>
{bar}
{('<script>' + JS + '</script>') if script else ''}
</body>
</html>
"""

def fmt(t):
    t = int(round(t)); return f'{t // 60}:{t % 60:02d}'

def chapters(interactive):
    if interactive:
        lis = '\n'.join(f'      <li><button type="button" data-t="{t}">{CHECK}<span class="tx"><b>{h}</b><span class="d">{html.escape(d)}</span></span>'
                        f'<span class="tm" aria-label="Plays from {fmt(t)}">&#9654; {fmt(t)}</span></button></li>' for h, d, t in CHAPTERS)
        hint = '\n    <p class="hint">Tap a topic to jump to that part of her story.</p>'
    else:
        lis = '\n'.join(f'      <li><div class="row">{CHECK}<span class="tx"><b>{h}</b><span class="d">{html.escape(d)}</span></span></div></li>' for h, d, t in CHAPTERS)
        hint = ''
    return f'''  <section aria-labelledby="hear">
    <h2 id="hear">What you’ll hear</h2>{hint}
    <ol class="chap">
{lis}
    </ol>
  </section>'''

# ---- Patient education content: Mike's approved wording, copied exactly from the Now Offering brochures ----
# Page 1 is identical in all seven brochures; page 2 (bio, education, badges) is per doctor (scripts/extract_bios.py).
import json
BIOS = json.load(open('/home/claude/web/brochure_bios.json'))
LEAD = 'Studies show the SI joint is the source of pain for roughly 15–30% of patients with persistent low back pain.'
ABOUT = ('The SI joints absorb movement between the spine and pelvis. Aging, arthritis, injury, or pregnancy can leave the '
         'bones rubbing together — pain that often mimics a lower back or disc problem.')
SIGNS = ['Lower back pain', 'Isolated pain in one SI joint', 'Sciatic-like pain in buttocks or leg', 'Hip/pelvis/groin pain',
         'Reduced range of motion', 'Pain climbing stairs or running', 'Pain lying on one side', 'Leg numbness or weakness',
         'Disrupted sitting patterns', 'Difficulty moving from sitting to standing', 'Sleep disturbances due to pain']
CONV = ['Physical therapy', 'Chiropractic care', 'Medication', 'Therapeutic injections', 'Radiofrequency ablation (RFA)']
NOW_OFFER = ('There’s good news! We now offer Minimally Invasive SIJ Fusion, a procedure that gets you back to life faster. '
             'It minimizes discomfort and recovery time, helping you regain control of your pain and get back to the activities you love.')
SOLUTION = [('Safe Posterior Approach', 'Designed to avoid vital anatomy such as nerves and muscles'),
            ('Incision as small as a dime', '2 cm'),
            ('Easier Recovery', 'Allows patients to have less procedure soreness and a quicker recovery')]
EXPECT = [('Compassionate Care', 'Care focused on your comfort and well-being.'),
          ('Thorough Evaluation', 'We review your history and symptoms to tailor your plan.'),
          ('Clear Communication', 'We explain your diagnosis and treatment options.'),
          ('Collaborative Approach', 'Your input shapes your plan and health goals.'),
          ('Supportive Environment', 'Your needs come first, every step of the way.')]
TICK = ('<svg width="18" height="18" viewBox="0 0 20 20" aria-hidden="true"><path d="M4 10.5 L8.2 14.5 L16 6" fill="none" stroke="#00B7BA" '
        'stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>')

def learn():
    signs = '\n'.join(f'          <li>{TICK}<span>{s}</span></li>' for s in SIGNS)
    conv = '\n'.join(f'        <li>{TICK}<span>{c}</span></li>' for c in CONV)
    return f'''  <section class="learn" aria-labelledby="learnh">
    <h2 id="learnh">Understanding SI joint pain</h2>
    <p class="lead">{LEAD}</p>
    <div class="about">
      <h3>About the SI joint</h3>
      <p>{ABOUT}</p>
    </div>
    <div class="learn-grid">
    <div class="signs">
      <img class="leg" src="../img/leg.png" alt="Leg illustration showing where SI joint pain is often felt: the buttock, back of the thigh and down the leg" width="64" height="328">
      <div>
        <h3>Common signs of SI joint pain</h3>
        <ul class="ticks">
{signs}
        </ul>
      </div>
    </div>
    <div class="conv">
      <h3>Conventional care not working?</h3>
      <ul class="ticks">
{conv}
      </ul>
    </div>
    </div>
  </section>'''

def solution():
    tiles = []
    for t, d in SOLUTION:
        if t.startswith('Incision'):
            tiles.append(f'''      <div class="tile dime"><img src="../img/dime.png" alt="" width="64" height="64"><div><b>{t}</b><span class="big">{d}</span></div></div>''')
        else:
            tiles.append(f'''      <div class="tile"><b>{t}</b><span>{d}</span></div>''')
    tiles = '\n'.join(tiles)
    return f'''  <section class="solution" aria-labelledby="solh">
    <div class="k">Now Offering</div>
    <h2 id="solh">Minimally Invasive SIJ Fusion</h2>
    <p>{NOW_OFFER}</p>
    <div class="tiles">
{tiles}
    </div>
  </section>'''

def meet(key, full, short, loc, slug):
    locs = (f'<div class="lo">{PIN}<span>{html.escape(loc).replace(" | ", "&nbsp;&middot; ")}</span></div>' if loc else '')
    b = BIOS.get(key)
    extra = ''
    if b:
        badges = '\n'.join(f'        <li><span class="bl">{html.escape(l)}</span><span class="bv">{html.escape(v)}</span></li>' for l, v in b['badges'])
        bio = '\n'.join(f'    <p>{html.escape(p)}</p>' for p in b['bio'])
        edu = '\n'.join(f'        <div><dt>{html.escape(l)}</dt><dd>{html.escape(v)}</dd></div>' for l, v in b['education'])
        extra = f'''
    <ul class="badges">
{badges}
    </ul>
    <div class="bio">
{bio}
    </div>
    <details class="edu-list">
      <summary>Education &amp; training</summary>
      <dl>
{edu}
      </dl>
    </details>'''
    return f'''  <section class="meet" aria-labelledby="meeth">
    <h2 id="meeth" class="vh">Meet {short}</h2>
    <div class="doc">
      <img src="photo.jpg" alt="{full}" width="112" height="112">
      <div>
        <div class="k">Physician Spotlight</div>
        <div class="n">{full}</div>
        <div class="ti">Pain Management Specialist &middot; Center for Pain Management</div>
        {locs}
        <a class="pf" href="{APC}{slug}/" target="_blank" rel="noopener">View {short}’s profile</a>
      </div>
    </div>{extra}
  </section>'''

def expectations():
    lis = '\n'.join(f'      <li>{CHECK}<span><b>{t}:</b> {d}</span></li>' for t, d in EXPECT)
    return f'''  <section aria-labelledby="exph">
    <h2 id="exph">Patient expectations</h2>
    <ul class="expect">
{lis}
    </ul>
  </section>'''

def ask_mike():
    return f'''  <section class="ask-mike" aria-labelledby="askq">
    <div class="k">After your Center for Pain appointment</div>
    <h2 id="askq" class="q">Have questions? Speak with someone who can answer them.</h2>
    <a class="num" href="tel:+13173400342">317-340-0342</a>
    <div class="who"><b>Mike DeFazio</b><span class="sep"> &middot; </span><span class="role">Manufacturer’s Representative</span></div>
    <a class="em" href="mailto:Mike@Impact-Surgical.com">Mike@Impact-Surgical.com</a>
    <p>Call or email with any questions you or your family have about the procedure, your pain diagnosis, recovery or what to expect. We can also connect you with a local patient.</p>
    <div class="btns">
      <a class="btn call" href="tel:+13173400342">{PHONE} Call Mike</a>
      <a class="btn out" href="mailto:Mike@Impact-Surgical.com">Email Mike</a>
      <a class="btn out" href="../mike-defazio.vcf" download="Mike DeFazio.vcf">{CONTACT} Save Contact</a>
    </div>
  </section>'''

BROCHURES = '/home/claude/handout/brochures'
HANDOUTS = '/home/claude/handout/final/EMAIL'

def thumb(pdf, out):
    import subprocess, tempfile
    with tempfile.TemporaryDirectory() as t:
        subprocess.run(['pdftoppm', '-r', '40', '-f', '1', '-l', '1', '-png', str(pdf), t + '/p'], check=True)
        im = Image.open(glob.glob(t + '/p*.png')[0]).convert('RGB')
    im.thumbnail((186, 240), Image.LANCZOS); im.save(out, quality=84, optimize=True)

def downloads(key, full, d):
    items = []
    last = full.split()[-1]
    br = [f for f in glob.glob(BROCHURES + '/*Brochure*.pdf') if f'_{last}_' in f.replace(' ', '_')]
    if br:
        shutil.copy(br[0], d / 'now-offering-brochure.pdf')
        items.append(('now-offering-brochure.pdf', f'{full} &middot; Now Offering Brochure', 'SI joint fusion at Center for Pain Management (PDF)'))
    ho = glob.glob(f'{HANDOUTS}/{full} - SIJ Patient Story Handout - EMAIL.pdf')
    if ho:
        shutil.copy(ho[0], d / 'patient-story-handout.pdf')
        items.append(('patient-story-handout.pdf', 'Patient Testimonial Handout', 'Her story and how to reach us (PDF)'))
    if not items:
        return ''
    for f, *_ in items: thumb(d / f, d / (f.replace('.pdf', '') + '-thumb.jpg'))
    cards = '\n'.join(f'      <a href="{f}" target="_blank" rel="noopener"><img class="th" src="{f.replace(".pdf", "")}-thumb.jpg" alt="" width="62" height="80">'
                      f'<span><span class="t">{t}</span><br><span class="s">{sub}</span></span></a>' for f, t, sub in items)
    return f'''  <section aria-labelledby="dlh">
    <h2 id="dlh">Brochures to view or share</h2>
    <div class="dl">
{cards}
    </div>
  </section>'''

# The two general SI-joint education videos linked by the QR codes on every Now Offering brochure.
EDU = [('moFgtJDI0w0', 'SI Joint Patient Education &middot; Part 1'), ('EsVReai9C5w', 'SI Joint Patient Education &middot; Part 2')]

def edu_videos():
    figs = '\n'.join(f'''      <figure>
        <div class="frame"><iframe src="https://www.youtube-nocookie.com/embed/{v}?rel=0&amp;playsinline=1" title="{t}" loading="lazy"
          allow="accelerometer; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
          referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe></div>
        <figcaption>{t}</figcaption>
      </figure>''' for v, t in EDU)
    return f'''  <section aria-labelledby="eduh">
    <h2 id="eduh">Patient educational videos</h2>
    <p class="edu-note">General information about SI joint pain and treatment. These are the same videos the QR codes on the Now Offering brochure open.</p>
    <div class="edu">
{figs}
    </div>
  </section>'''

VCARD = """BEGIN:VCARD\r
VERSION:3.0\r
N:DeFazio;Mike;;;\r
FN:Mike DeFazio\r
ORG:Impact Surgical\r
TITLE:Manufacturer's Representative\r
TEL;TYPE=CELL,VOICE:+1-317-340-0342\r
EMAIL;TYPE=INTERNET:Mike@Impact-Surgical.com\r
NOTE:SI joint fusion questions for Center for Pain Management patients and families.\r
END:VCARD\r
"""

def photo(key, dest, size):
    im = Image.open(f'/home/claude/handout/up/dr_{key}.jpg').convert('RGB').resize((size, size), Image.LANCZOS)
    im.save(dest, quality=86, optimize=True, progressive=True)

def chooser(base):
    links = '\n'.join(f'      <a href="{base}{k}/"><img src="{base}{k}/thumb.jpg" alt="" width="56" height="56">{f}</a>' for k, f, *_ in DOCS)
    return f'''  <section aria-labelledby="pickq">
    <h2 id="pickq">Which Center for Pain doctor did you see?</h2>
    <p style="margin:0 0 12px;font-weight:600">Choose your doctor to watch her story.</p>
    <div class="grid">
{links}
    </div>
  </section>
{chapters(False)}'''

def build():
    if OUT.exists(): shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    shutil.copy('/home/claude/web/poster_hd.jpg', OUT / 'poster.jpg')   # 1280x720 frame from the full-quality video
    shutil.copy('/home/claude/web/captions.vtt', OUT / 'captions.vtt')
    shutil.copytree('/home/claude/web/img', OUT / 'img')
    for f in ('favicon.svg', 'apple-touch-icon.png'):
        shutil.copy(f'/home/claude/web/share/{f}', OUT / f)
    shutil.copy('/home/claude/web/share/root.jpg', OUT / 'share.jpg')
    (OUT / 'mike-defazio.vcf').write_bytes(VCARD.encode())
    (OUT / '.nojekyll').write_text('')
    (OUT / 'robots.txt').write_text('User-agent: *\nDisallow: /\n')
    desc = 'Hear from a Center for Pain Management patient about her SI joint fusion.'
    for key, full, short, loc, slug in DOCS:
        phone = PHONES.get(key, '317-706-7246')
        d = OUT / key; d.mkdir()
        photo(key, d / 'photo.jpg', 360); photo(key, d / 'thumb.jpg', 168)
        # The patient in the video is Dr. Rutledge's patient. Only his page pairs a physician with the video in the
        # texted-link preview; every other page uses the general preview image and a neutral title.
        own = key == 'rutledge'
        if own: shutil.copy(f'/home/claude/web/share/{key}.jpg', d / 'share.jpg')
        # Video is served from this site (GitHub Pages supports byte-range streaming, so iPhones play it).
        body = f'''  <section class="player" id="watch" aria-label="Patient story video">
    <div class="frame"><video controls playsinline preload="metadata" poster="../poster.jpg" title="Patient story: SI joint fusion">
      <source src="../videos/{key}.mp4" type="video/mp4">
      <track kind="captions" src="../captions.vtt" srclang="en" label="English">
      Your browser can’t play this video.
    </video>
      <button type="button" class="playover" id="playover" aria-label="Play her story, 4 minutes"><span class="pi"><svg width="30" height="30" viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5 L19 12 L8 18.5 Z" fill="#1F2735"/></svg></span><span class="pt">Watch her story &middot; 4 min</span></button>
    </div>
    <div class="tools">
      <button type="button" class="chip" id="cc" aria-pressed="false">{CC} Captions <span class="st">Off</span></button>
      <button type="button" class="chip" id="share">{SHARE} Share with family</button>
      <span class="toast" id="toast" role="status" aria-live="polite"></span>
    </div>
  </section>
{chapters(True)}
{learn()}
{solution()}
{edu_videos()}
{meet(key, full, short, loc, slug)}
{expectations()}
  <section class="next" aria-labelledby="nextlabel">
    <div class="label" id="nextlabel">Your next step</div>
    <div class="ask">Ask {short} whether SI joint fusion is right for you.</div>
    <div class="phone">Call to schedule an evaluation.</div>
    <a class="btn call" href="{tel(phone)}">{PHONE} Call {phone}</a>
  </section>
{ask_mike()}
{downloads(key, full, d)}'''
        title = f'Patient Story · {full} · Center for Pain Management' if own else 'SI Joint Fusion Patient Story · Center for Pain Management'
        (d / 'index.html').write_text(page(title, body, '../', desc, f'{SITE}{key}/share.jpg' if own else f'{SITE}share.jpg', f'{SITE}{key}/', phone=phone))
    (OUT / 'index.html').write_text(page('Patient Story · Center for Pain Management', chooser(''), '', desc,
                                         f'{SITE}share.jpg', SITE, callbar=True, script=False))
    base = '/' + os.environ.get('SITE_REPO', 'sij-patient-story') + '/'
    (OUT / '404.html').write_text(page('Patient Story · Center for Pain Management', chooser(base), base, desc,
                                       f'{SITE}share.jpg', SITE, callbar=True, script=False))
    print('built', sorted(p.relative_to(OUT).as_posix() for p in OUT.rglob('*') if p.is_file()))

build()
