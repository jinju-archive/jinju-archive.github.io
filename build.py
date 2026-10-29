# Builds the Jinju Archive sources site (GitHub Pages): index.html + one folder per episode.
# Episode data lives in this file; Commons licence data comes from <ep>_commons.json (fetched from the Commons API).
import html, json, os, urllib.parse
E = html.escape
CSS = """:root{--ink:#13101f;--text:#1a1726;--muted:#5b6070;--line:#e4e1ee;--accent:#4a3aa0;--amber:#f5a524;--bg:#fff}
@media (prefers-color-scheme:dark){:root{--text:#ece9f5;--muted:#a7a3b8;--line:#2e2a40;--accent:#b7adf2;--bg:#13101f}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:16px/1.6 -apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif}
header{background:var(--ink);color:#fff;padding:40px 16px 32px}header .w,main{max-width:960px;margin:0 auto}
.k{color:var(--amber);font-size:13px;font-weight:700;letter-spacing:.2em}h1{margin:6px 0 4px;font-size:30px}header p{margin:0;color:#c9c2ee}
main{padding:24px 16px 64px}h2{font-size:20px;margin:36px 0 8px}p.note{color:var(--muted);margin:0 0 12px}
table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;padding:8px 6px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600}a{color:var(--accent)}td.f{word-break:break-word}
@media (max-width:640px){table,tbody,tr,td{display:block}thead{display:none}tr{border-bottom:1px solid var(--line);padding:8px 0}td{border:0;padding:2px 0}}
ul{padding-left:20px}li{margin:4px 0}footer{color:var(--muted);font-size:13px;margin-top:48px}"""

def page(title, kicker, sub, body):
    return (f'<!doctype html><html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{E(title)}</title><style>{CSS}</style><header><div class="w"><div class="k">{E(kicker)}</div><h1>{E(title)}</h1><p>{E(sub)}</p></div></header>'
            f'<main>{body}<footer>Jinju Archive · 진주 아카이브. Corrections and takedown requests: please leave a comment on the video.</footer></main></html>')

GSK = {
  'slug': 'golden-state-killer', 'no': '001', 'title': 'The Golden State Killer', 'ko': '골든 스테이트 킬러',
  'commons': 'gsk_commons.json',
  'what': {  # what each file shows, in the video
    'Visalia Ransacker.jpg': 'Visalia Ransacker composite sketch (1975)', 'Joseph James DeAngelo.jpg': 'Joseph DeAngelo, Exeter police photo (1973)',
    'Joseph DeAngelo mugshot.jpg': 'Booking photo (2018)', 'ONS composites.jpg': 'Original Night Stalker composites',
    'EAR-ONS-Punishment map.png': 'Hand-drawn "Punishment" map attributed to the offender', 'EAR-ONS-Mad is the Word Front.jpg': '"Mad is the Word" handwritten poem attributed to the offender',
    'EAR-ONS Maggiore Suspects 1978.jpg': '1978 suspect flyer, Maggiore case', 'Home Ransacked by the East Area Rapist.jpg': 'Ransacked victim home',
    'Ski Masks Worn by East Area Rapist.jpg': 'Ski masks', 'Shoelace as Evidence in the East Area Rapist Case.jpg': 'Shoelace evidence, Maggiore case',
    'Keeping Tabs on the Case.jpg': 'Case records', 'Rapist Turns to Murder.jpg': 'FBI case material', 'Evidence (East Area Rapist).jpg': 'Evidence',
    'The Evidence Room.jpg': 'Evidence room', 'Golden State Killer police sketch vs mugshot.png': 'Composite sketch beside the 2018 booking photo',
    'Location of Some Escapes by the East Area Rapist.jpg': 'Escape routes map', 'East Area Rapist Attacks Map.jpg': 'Attacks map',
    'East Area Rapist Press Conference 2018 04 25.webm': '2018 arrest press conference (video)', 'Clues Sought in Unsolved East Area Rapist Case.webm': 'FBI 2016 appeal for tips (video)',
    'P v DeAngelo Redacted Search Warrant Final.pdf': 'Redacted search warrant affidavit', 'Sketch of the East Area Rapist Suspect.jpg': 'East Area Rapist composite sketch',
  },
  'fill': {  # Commons pages with no machine-readable licence
    'EAR-ONS-Punishment map.png': ('Public domain (per Commons)', 'Sacramento Police Department', 'File:EAR-ONS-Back of "Punishment" map.png'),
    'EAR-ONS-Mad is the Word Front.jpg': ('Public domain (per Commons)', 'Sacramento Police Department', 'File:EAR-ONS-"Mad is the Word" Front.jpg'),
  },
  'other': [
    ('Katie and Brian Maggiore', 'FBI, public domain (U.S. federal government work)', 'https://www.fbi.gov/image-repository/katie_brian_maggiore.jpg/view'),
    ('Paul Holes at CrimeCon 2019', 'Photo by Michelle Callahan, CC BY 2.0', 'https://commons.wikimedia.org/wiki/File:Paul_Holes_-_at_Crime_Con_2019_New_Orleans.jpg'),
  ],
  'facts': [
    ('Ventura County District Attorney, joint release on sentencing (2020-08-21)', 'https://da.venturacounty.gov/2020/08/august-21-2020'),
    ('Orange County District Attorney, charges media advisory', 'https://ocdistrictattorney.gov/?p=24339'),
    ('Fox LA: pleads guilty to 13 murders, including 4 OC slayings', 'https://www.foxla.com/news/golden-state-killer-pleads-guilty-to-13-murders-including-4-oc-slayings'),
    ('ABC30: Visalia detective came face to face with serial killer in 1975', 'https://abc30.com/post/visalia-detective-came-face-to-face-with-serial-killer-in-1975/3393359/'),
    ('TheWrap: Was the Golden State Killer also the Visalia Ransacker?', 'https://www.thewrap.com/ill-be-gone-in-the-dark-state-killer-visalia-ransacker/'),
    ('Sun-Gazette: former Exeter officer charged with the 1975 murder of Claude Snelling', 'https://thesungazette.com/article/news/2018/08/15/former-exeter-police-officer-joseph-james-deangelo-jr-charged-with-the-1975-murder-of-claude-snelling-in-visalia'),
    ('CBS13: Who is Joseph DeAngelo?', 'https://www.cbsnews.com/sacramento/news/who-is-joseph-deangelo/'),
    ('WRAL/AP archive', 'https://www.wral.com/archive/17513400/'),
    ('NBC Bay Area/AP: victims voice relief after arrest', 'https://www.nbcbayarea.com/news/local/victims-voice-relief-after-arrest-in-golden-state-killer-case/2031280/'),
    ('ABC10: honoring the homicide victims', 'https://abc10.com/article/news/local/honoring-the-golden-state-killer-homicide-victims/103-546280255'),
    ('CBS SF / FBI renews efforts (2016)', 'https://www.cbsnews.com/sanfrancisco/news/fbi-renews-efforts-to-track-down-infamous-serial-killer/'),
    ('NPR: Paul Holes interview (2023)', 'https://www.npr.org/2023/10/06/1203897830/after-a-career-of-cracking-cold-cases-investigator-paul-holes-opens-up'),
    ('KTVU: genealogist in the case speaks out', 'https://ktvu.com/news/critical-genealogist-in-golden-state-killer-case-speaks-out-about-her-role'),
    ('ABC15: DNA collected from his car while he shopped', 'https://www.abc15.com/news/national/golden-state-killer-dna-that-led-to-suspects-arrest-was-collect-from-his-car-while-he-shopped'),
    ('CNN: the brother who pushed the DNA database law', 'https://edition.cnn.com/2018/04/26/us/golden-state-killer-dna-database-trnd'),
    ('UC Berkeley Journalism: Proposition 69 (2004)', 'https://projects.journalism.berkeley.edu/election2004/archives/2004/11/dna_fingerprint.html'),
    ('Forensic Magazine: cases solved with forensic genetic genealogy', 'https://www.forensicmag.com/594940-How-Many-Cases-Have-Been-Solved-with-Forensic-Genetic-Genealogy/'),
    ('KSL: how a Utah case upended GEDmatch', 'https://www.ksl.com/article/46560537/how-a-utah-assault-case-upended-the-cutting-edge-dna-website-that-caught-the-golden-state-killer'),
    ('Scripps/10News: DOJ policy on genealogy searches', 'https://www.10news.com/news/national/new-doj-policy-limits-how-authorities-can-use-genealogy-services-to-solve-crimes'),
    ('ABC30: sentencing hearing', 'https://abc30.com/golden-state-killer-sentencing-sacramento-joseph-deangelo-hearing/6381802/'),
    ('NBC News: sentenced to life without parole', 'https://www.nbcnews.com/news/us-news/golden-state-killer-joseph-deangelo-sentenced-life-without-possibility-parole-n1237670'),
    ('ABC News: why he stopped (Paul Holes)', 'https://abcnews.com/US/golden-state-killer-stopped-murder-spree-investigator/story?id=54906116'),
    ('A&E: prosecutor doubts he stopped in 1986', 'https://www.aetv.com/articles/golden-state-killer-prosecutor-doesnt-think-joseph-deangelo-stopped-killing-in-1986'),
    ('Fox 32/AP: "inner person" Jerry', 'https://www.fox32chicago.com/news/golden-state-killer-pleads-guilty-to-murders-said-inner-person-drove-him'),
    ('Wikipedia: Joseph James DeAngelo (overview, cross-checked)', 'https://en.wikipedia.org/wiki/Joseph_James_DeAngelo'),
  ],
}

def episode(ep):
    rows = []
    for c in json.load(open(ep['commons'])):
        f = c['file']; lic, credit, title = c['license'], c['artist'] or c['credit'], 'File:' + f
        if f in ep['fill']: lic, credit, title = ep['fill'][f]
        url = 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(title.replace(' ', '_'))
        rows.append(f'<tr><td>{E(ep["what"].get(f, f))}</td><td>{E(lic)}</td><td>{E(credit)}</td><td class="f"><a href="{url}">{E(title[5:])}</a></td></tr>')
    for what, lic, url in ep['other']:
        rows.append(f'<tr><td>{E(what)}</td><td>{E(lic)}</td><td></td><td class="f"><a href="{url}">{E(url.split("/")[2])}</a></td></tr>')
    facts = ''.join(f'<li><a href="{u}">{E(t)}</a></li>' for t, u in ep['facts'])
    body = (f'<h2>Photos, documents and footage</h2><p class="note">Real photos and records come first; where none exist, the video uses AI-generated reenactment illustrations (ChatGPT) with no real faces. '
            f'Licences are as stated on the source pages. Victims are shown only through photos their families or agencies made public.</p>'
            f'<table><thead><tr><th>Shown</th><th>Licence</th><th>Author / source</th><th>Source page</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
            f'<h2>Fact sources</h2><p class="note">Facts in the narration were cross-checked against at least two sources wherever possible; a few details rest on a single report. Where sources disagree, the narration uses the safer wording.</p><ul>{facts}</ul>'
            f'<h2>Production</h2><ul><li>Korean narration: Google Gemini text-to-speech (voice Leda)</li><li>Reenactment illustrations: generated with ChatGPT</li><li>Maps, timelines and title cards: made by Jinju Archive</li></ul>')
    os.makedirs(ep['slug'], exist_ok=True)
    open(os.path.join(ep['slug'], 'index.html'), 'w', encoding='utf-8').write(
        page(f'{ep["no"]} {ep["title"]}', 'JINJU ARCHIVE · SOURCES', f'{ep["ko"]} · 출처와 자료 목록', body))
    return f'<li><a href="{ep["slug"]}/">{E(ep["no"])} {E(ep["title"])}</a> · {E(ep["ko"])}</li>'

items = episode(GSK)
open('index.html', 'w', encoding='utf-8').write(page('Jinju Archive', 'SOURCES', '진주 아카이브 영상의 출처와 자료 목록',
    f'<h2>Episodes</h2><ul>{items}</ul><p class="note">Each page lists the photos, documents, footage and articles used in that video.</p>'))
print('built')
