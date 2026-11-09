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

GSK_NOTE = ('Real photos and records come first; where none exist, the video uses AI-generated reenactment illustrations (ChatGPT) with no real faces. '
            'Licences are as stated on the source pages. Victims are shown only through photos their families or agencies made public.')
GSK_PROD = ['Korean narration: Google Gemini text-to-speech (voice Leda)', 'Reenactment illustrations: generated with ChatGPT', 'Maps, timelines and title cards: made by Jinju Archive']

C, MX = 'https://commons.wikimedia.org/wiki/File:', 'https://mixkit.co/free-stock-video/'
PD, ML = 'Public domain', 'Mixkit Stock Video Free License'
PH = {
  'slug': 'patty-hearst', 'no': '002', 'title': 'Patty Hearst', 'ko': '패티 허스트',
  'note': ('Real photos and records come first; mood scenes use Mixkit stock footage, which is illustrative and does not show the actual events. '
           'Licences are as stated on the source pages.'),
  'visuals': [  # (what, licence, author, url), in the order of credits.txt
    ('Hibernia Bank robbery, security camera frame (Donald DeFreeze)', PD, 'FBI', C + 'SLA-DonaldD-Hibernia(300).jpg'),
    ('Hibernia Bank robbery, security camera frame (April 1974)', PD, 'Closed circuit security camera', C + 'Patty_Hearst_takes_part_in_the_April_1974_Hiberna_bank_raid_with_other_SLA_members.jpg'),
    ('Hibernia Bank robbery, security camera frame', PD, "Hibernia Bank's security camera", C + 'Hearst-hibernia-yell.jpg'),
    ('Hibernia Bank robbery, security camera frame', PD, 'Closed circuit security camera', C + 'Patty_Hearst-_Hibernia_bank_robbery.jpg'),
    ('FBI wanted poster', PD, 'Federal Bureau of Investigation', C + 'Patty_Hearst_FBI_poster.jpg'),
    ('FBI wanted poster (crop)', PD, 'United States Government, Federal Bureau of Investigation', C + 'Patti_Hearst_et._al._wanted_poster_01.jpg'),
    ('Stock video: shed in the forest closed with a padlock', ML, 'matthiasgroeneveld', MX + 'shed-in-the-forest-closed-with-a-padlock-2501/'),
    ('Stock video: street lamps at night', ML, 'jibaroartz', MX + 'street-lamps-at-night-3526/'),
    ('William Randolph Hearst', PD, 'Harris & Ewing, photographer', C + 'HEARST,_WILLIAM_RANDOLPH_LCCN2016858735.jpg'),
    ('Randolph A. Hearst (1940)', PD, 'Unknown, dedicated to Bettmann Archive', C + 'Randolph_A._Hearst_1940_(cropped).jpg'),
    ('Stock video: dancer in the dark, back view', ML, 'edgarfernandez', MX + 'dancer-in-the-dark-back-view-1038/'),
    ('Stock video: point of view driving across a road', ML, 'marcolopez', MX + 'point-of-view-driving-across-a-road-44650/'),
    ('Stock video: police car lights flashing', ML, 'Mixkit', MX + 'police-car-lights-flashing-17376/'),
    ('Symbionese Liberation Army congressional report cover', PD, 'A product of the United States Government', C + 'Symbionese_Liberation_Army_congressional_report_cover_01.jpg'),
    ('Symbionese Liberation Army flag', PD, 'Wikimedia Commons', C + 'Symbionese_Liberation_Army_flag.png'),
    ('Donald DeFreeze mugshot (1973)', PD, 'FBI', C + 'Donald_David_DeFreeze_mugshot_1973.jpg'),
    ('Stock video: flipping through a newspaper', ML, 'mixkit', MX + 'pov-flipping-through-a-newspaper-41192/'),
    ('Hearst Building, San Francisco (2013)', 'CC BY-SA 3.0', 'Wikimedia Commons', C + 'Hearst_Building,_San_Francisco_(2013)_-_1.JPG'),
    ('Stock video: young adult reading the newspaper', ML, 'm0de0n', MX + 'young-adult-reading-the-newspaper-34190/'),
    ('Stock video: man reading the newspaper with a cup of coffee', ML, 'mixkit', MX + 'intellectual-man-reading-the-newspaper-with-a-cup-of-coffee-41191/'),
    ('Stock video: candle lighting in the dark', ML, 'edgarfernandez', MX + 'candle-lighting-in-the-dark-3458/'),
    ('Stock video: reel-to-reel tape recorder, close-up', ML, 'mixkit', MX + 'the-camera-gets-closer-to-vintage-reel-to-reel-tape-recorder-placed-52198/'),
    ('Stock video: vinyl records and a reel-to-reel tape recorder', ML, 'mixkit', MX + 'the-camera-pans-on-a-vintage-vinyl-records-and-a-52199/'),
    ('Stock video: blurry lights form a police car', ML, 'ivz', MX + 'blurry-lights-form-a-police-car-47491/'),
    ('Stock video: a calm street in Paris', ML, 'dubassy', MX + 'a-calm-street-in-paris-4348/'),
    ('Emily Harris', PD, 'Wikimedia Commons', C + 'Emily_Harris_(SLA).jpg'),
    ('Stock video: couple getting off a van in a parking lot', ML, 'rubenvelasco', MX + 'romantic-couple-getting-off-a-van-in-a-parking-lot-45380/'),
    ('Stock video: glass bottle breaking in slow motion', ML, 'Mixkit', MX + 'glass-bottle-breaking-in-slow-motion-28413/'),
    ('Stock video: road trip aboard a van', ML, 'mixkit', MX + 'road-trip-as-a-couple-aboard-a-van-41582/'),
    ('Stock video: car driving on an empty country road', ML, 'Mixkit', MX + 'car-driving-on-an-empty-road-in-the-countryside-28777/'),
    ('Stock video: wood burning in a fireplace', ML, 'kovalrk', MX + 'wood-burning-in-a-fireplace-1242/'),
    ('Stock video: people walking in front of a building', ML, 'dubassy', MX + 'people-walking-in-front-of-a-building-4169/'),
    ('Patty Hearst (1975)', PD, 'Wikimedia Commons', C + '1975_Patty_Hearst.jpg'),
    ('Patty Hearst booking photo', PD, 'Wikimedia Commons', C + 'PattyHearstmug.jpg'),
    ('Patty Hearst escorted by marshals', 'CC BY 4.0', 'Wikimedia Commons', C + 'Patty_Hearst_escorted_by_marshals.jpg'),
    ('Stock video: judge pronounces sentence in court', ML, 'ivz', MX + 'judge-pronounces-sentence-in-court-46820/'),
    ('F. Lee Bailey', 'CC BY-SA 2.0', 'Wikimedia Commons', C + 'F._Lee_Bailey.jpg'),
    ('Stock video: judge shows money on table', ML, 'ivz', MX + 'judge-shows-money-on-table-46117/'),
    ('Jimmy Carter, official portrait (1977)', PD, 'The White House', C + 'Official_Portrait_of_Jimmy_Carter_(1977).jpg'),
    ('Patty Hearst and Bernard Shaw (1979)', 'CC BY 4.0', 'Rick Meyer, Los Angeles Times', C + 'Patty_Hearst_and_Bernard_Shaw,_1979.jpg'),
    ('Bill Clinton, official portrait', PD, 'Wikimedia Commons', C + 'Official_Portrait_of_President_William_Jefferson_Clinton_(3x4_cropped).jpg'),
    ('Stock video: houses in the suburbs from above', ML, 'marcolopez', MX + 'view-from-above-to-houses-in-the-suburbs-3420/'),
  ],
  'facts': [
    ('Wikipedia: Patty Hearst (overview, cross-checked)', 'https://en.wikipedia.org/wiki/Patty_Hearst'),
    ('History.com: Patty Hearst kidnapped', 'https://www.history.com/this-day-in-history/february-4/patty-hearst-kidnapped'),
    ('Britannica: Patty Hearst', 'https://www.britannica.com/biography/Patty-Hearst'),
    ('Encyclopedia.com: Hearst, Patty', 'https://encyclopedia.com/law/encyclopedias-almanacs-transcripts-and-maps/hearst-patty'),
    ('Famous Trials: chronology', 'https://famous-trials.com/pattyhearst/2198-chronology'),
    ('Crime Magazine: LAPD raid leaves six SLA members dead (1974)', 'https://crimemagazine.com/lapd-raid-leaves-six-sla-members-dead-1974'),
    ('PBS NewsHour: Jeffrey Toobin on the Patty Hearst story', 'https://www.pbs.org/newshour/show/victim-becomes-criminal-fresh-look-story-patty-hearst'),
    ('Wikipedia: Sara Jane Olson', 'https://en.wikipedia.org/wiki/Sara_Jane_Olson'),
    ('PBS American Experience: Myrna Opsahl', 'https://www.pbs.org/wgbh/americanexperience/features/guerrilla-myrna-opsahl'),
    ('UPI (2002): Hearst ready for SLA trial showdown', 'https://www.upi.com/Top_News/2002/01/23/Hearst-ready-for-SLA-trial-showdown/66661011818959/'),
    ('KQED: 40 years ago today, Patty Hearst kidnapped in Berkeley', 'https://www.kqed.org/news/125209/40-years-ago-today-patty-hearst-kidnapped-in-berkeley'),
    ('Crime+Investigation: the arrest', 'https://www.crimeandinvestigation.co.uk/crime-files/sla-kidnap-of-patty-hearst/arrest'),
    ('Wikipedia: Symbionese Liberation Army', 'https://en.wikipedia.org/wiki/Symbionese_Liberation_Army'),
    ('Slate (2002): What is the Symbionese Liberation Army?', 'https://www.slate.com/articles/news_and_politics/explainer/2002/01/what_is_the_symbionese_liberation_army.html'),
    ('PBS American Experience: rise and fall of the SLA', 'https://www.pbs.org/wgbh/americanexperience/features/guerrilla-rise-and-fall-symbionese-liberation-army/'),
    ('The Michigan Daily archive (trial coverage)', 'https://digital.bentley.umich.edu/midaily/mdp.39015071754548/576'),
    ('UC Berkeley Library digital collections (trial coverage)', 'https://digicoll.lib.berkeley.edu/record/117527'),
    ('SF State DIVA: KPIX film after the Hibernia robbery', 'https://diva.sfsu.edu/bundles/239874'),
    ('CBS LA: SWAT officers on the biggest shootout in LA history', 'https://www.cbsnews.com/losangeles/news/swat-officers-talk-exclusively-to-cbs2s-pat-harvey-about-biggest-shootout-in-las-history/'),
    ('CBS SF: husband of Patty Hearst dies at 68', 'https://cbsnews.com/sanfrancisco/news/husband-of-patty-hearst-dies-at-68'),
  ],
  'prod': [  # raw HTML, written here
    'Korean narration: AI voice',
    'Mood scenes: Mixkit stock footage, illustrative only',
    'Music: "Lightless Dawn" by Kevin MacLeod (<a href="https://incompetech.com">incompetech.com</a>), licensed under <a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons: By Attribution 4.0</a>',
    'Maps, timelines and title cards: made by Jinju Archive',
  ],
}

HS = {
  'slug': 'robert-hanssen', 'no': '003', 'title': 'Robert Hanssen', 'ko': '로버트 핸슨',
  'note': ('Real photos, FBI evidence photos and court records come first; news stills (CBS 60 Minutes, press photos) are used for commentary. '
           'Mood scenes use Mixkit stock footage, which is illustrative and does not show the actual events. Licences are as stated on the source pages.'),
  'visuals': [[w, l.replace('Press photo, used for commentary', 'Used for commentary') , a, u] for w, l, a, u in json.load(open('hs_visuals.json', encoding='utf-8'))],
  'facts': [
    ('FBI affidavit in support of the criminal complaint, U.S. v. Robert Philip Hanssen (2001)', 'https://www.fbi.gov/file-repository/counterintelligence/hanssen-affidavit.pdf'),
    ('U.S. DOJ Office of the Inspector General: review of the FBI and Robert Hanssen (2003)', 'https://oig.justice.gov/special/0308/index.htm'),
    ('Commission for the Review of FBI Security Programs (Webster report, 2002)', 'https://irp.fas.org/agency/doj/fbi/websterreport.html'),
    ('FAS: Hanssen case photos and documents', 'https://irp.fas.org/ops/ci/hanssenphotos.htm'),
    ('CBS News 60 Minutes: Robert Hanssen (2001)', 'https://www.youtube.com/watch?v=FYWZczIUJaI'),
    ('CBS News: To Catch a Spy (Brian Kelley, 2003)', 'https://www.cbsnews.com/news/to-catch-a-spy-21-08-2003/'),
    ('Wikipedia: Robert Hanssen (overview, cross-checked)', 'https://en.wikipedia.org/wiki/Robert_Hanssen'),
    ('Wikipedia: Brian Kelley (CIA officer)', 'https://en.wikipedia.org/wiki/Brian_Kelley_(CIA_officer)'),
    ('Wikipedia: Boris Yuzhin', 'https://en.wikipedia.org/wiki/Boris_Yuzhin'),
    ("Wikipedia: Eric O'Neill", 'https://en.wikipedia.org/wiki/Eric_O%27Neill'),
    ("International Spy Museum: Robert Hanssen's PalmPilot", 'https://www.spymuseum.org/exhibition-experiences/about-the-collection/collection-highlights/robert-hanssen-s-palmpilot/'),
    ('ABC News: Spycatcher, bringing down Robert Hanssen', 'https://abcnews.go.com/2020/story?id=123776'),
    ('Washington Post (2001): book says FBI was told in 1990 Hanssen might be a spy', 'https://www.washingtonpost.com/archive/politics/2001/12/16/book-says-fbi-was-told-in-90-hanssen-might-be-spy/bf02236d-7b30-4763-b800-59d8adb5906e/'),
    ('The Harvard Crimson (2003): Opening the doors of Opus Dei', 'https://www.thecrimson.com/article/2003/4/10/opening-the-doors-of-opus-dei/'),
    ('Washington Times (2011): Brian Kelley, veteran counterspy, dies at 68', 'https://m.washingtontimes.com/news/2011/sep/20/brian-kelley-veteran-counterspy-dies-at-68/'),
    ('Tampa Bay Times (2001): a spy tells of life in shadows (Boris Yuzhin)', 'https://www.tampabay.com/archive/2001/06/09/danger-deceit-a-spy-tells-of-life-in-shadows/'),
  ],
  'prod': [
    'Korean narration: AI voice; English subtitles translated by Jinju Archive',
    'Mood scenes: Mixkit stock footage, illustrative only',
    'Outro illustration and thumbnail: generated with ChatGPT (thumbnail uses the real FBI portrait and booking photo)',
    'Music: "Lightless Dawn" by Kevin MacLeod (<a href="https://incompetech.com">incompetech.com</a>), licensed under <a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons: By Attribution 4.0</a>',
    'Timelines, maps and title cards: made by Jinju Archive',
  ],
}

ET = {
  'slug': 'emmett-till', 'no': '004', 'title': 'Emmett Till', 'ko': '에밋 틸',
  'note': ('Real photos and documents come first: 1955 Jet magazine photos (public domain, copyright never renewed), the FBI 2006 report and '
           'U.S. government photos. Name tags were added to two photos. Mood scenes use Mixkit stock footage, which is illustrative and does not show the actual events. '
           'Licences are as stated on the source pages.'),
  'visuals': json.load(open('et_visuals.json', encoding='utf-8')),
  'facts': [
    ('FBI Prosecutive Report of Investigation Concerning Emmett Till (2006), FBI Vault', 'https://vault.fbi.gov/Emmett%20Till%20'),
    ('PBS American Experience: The Murder of Emmett Till, timeline', 'https://www.pbs.org/wgbh/americanexperience/features/till-timeline/'),
    ('PBS American Experience: The trial of J.W. Milam and Roy Bryant', 'https://www.pbs.org/wgbh/americanexperience/features/emmett-trial-jw-milam-and-roy-bryant'),
    ('PBS American Experience: Roy and Carolyn Bryant and J.W. Milam', 'https://www.pbs.org/wgbh/americanexperience/features/emmett-biography-roy-carolyn-bryant-and-jw-milam'),
    ('PBS American Experience: Moses and Elizabeth Wright', 'https://www.pbs.org/wgbh/americanexperience/features/emmett-biography-moses-and-elizabeth-wright'),
    ('PBS American Experience: Sheriff Clarence Strider', 'https://www.pbs.org/wgbh/americanexperience/features/emmett-biography-sheriff-clarence-strider'),
    ('Famous Trials (UMKC Law): the abduction', 'https://famous-trials.com/emmetttill/1754-abduction'),
    ('Mississippi Today (2024): Moses Wright identified Emmett Till\'s killers', 'https://mississippitoday.org/2024/09/21/on-this-day-in-1955-moses-wright-identified-emmett-till-killers-2/'),
    ('Emmett Till Interpretive Center: Till app', 'https://tillapp.emmett-till.org/items/show/3'),
    ('AP via KSAT (2022): 1955 warrant in Emmett Till case found', 'https://www.ksat.com/news/national/2022/06/29/1955-warrant-in-emmett-till-case-found-family-seeks-arrest/'),
    ('Axios (2022): grand jury declines to indict Carolyn Bryant Donham', 'https://www.axios.com/2022/08/09/emmett-till-accuser-grand-jury'),
    ('AP via KAXE (2023): Carolyn Bryant Donham dies at 88', 'https://www.kaxe.org/news/2023-04-27/carolyn-bryant-donham-who-accused-emmett-till-before-he-was-lynched-dies-at-age-88'),
    ('Zinn Education Project: Rosa Parks and Emmett Till', 'https://www.zinnedproject.org/news/tdih/rosa-parks-emmett-till/'),
    ('Smithsonian Magazine (2009): museum to receive Emmett Till\'s casket', 'https://www.smithsonianmag.com/smithsonian-institution/african-american-history-museum-to-receive-emmett-tills-casket-15807840/'),
    ('The Root: Emmett Till memorial, vandalized for more than 10 years, is now bulletproof', 'https://www.theroot.com/emmett-till-memorial-marred-by-vandalism-for-more-than-10-years-is-now-bullet-proof'),
    ('The Root (2017): Simeon Wright dies at 74', 'https://www.theroot.com/simeon-wright-cousin-who-witnessed-emmett-tills-kidnap-1799939564'),
    ('Wikipedia: Emmett Till (overview, cross-checked)', 'https://en.wikipedia.org/wiki/Emmett_Till'),
  ],
  'prod': [
    'Korean narration: AI voice; English subtitles translated by Jinju Archive',
    'Mood scenes: Mixkit stock footage, illustrative only',
    'Verdict card: a newspaper-style graphic made by Jinju Archive, not a real front page',
    'Outro illustration: generated with ChatGPT',
    'Music: "Lightless Dawn" by Kevin MacLeod (<a href="https://incompetech.com">incompetech.com</a>), licensed under <a href="http://creativecommons.org/licenses/by/4.0/">Creative Commons: By Attribution 4.0</a>',
  ],
}

def episode(ep):
    rows = []
    for c in (json.load(open(ep['commons'])) if 'commons' in ep else []):
        f = c['file']; lic, credit, title = c['license'], c['artist'] or c['credit'], 'File:' + f
        if f in ep['fill']: lic, credit, title = ep['fill'][f]
        url = 'https://commons.wikimedia.org/wiki/' + urllib.parse.quote(title.replace(' ', '_'))
        rows.append(f'<tr><td>{E(ep["what"].get(f, f))}</td><td>{E(lic)}</td><td>{E(credit)}</td><td class="f"><a href="{url}">{E(title[5:])}</a></td></tr>')
    for what, lic, credit, url in ep.get('visuals', []):
        name = urllib.parse.unquote(url.split('File:')[1]).replace('_', ' ') if 'File:' in url else url.split('/')[2]
        rows.append(f'<tr><td>{E(what)}</td><td>{E(lic)}</td><td>{E(credit)}</td><td class="f"><a href="{E(url)}">{E(name)}</a></td></tr>')
    for what, lic, url in ep.get('other', []):
        rows.append(f'<tr><td>{E(what)}</td><td>{E(lic)}</td><td></td><td class="f"><a href="{url}">{E(url.split("/")[2])}</a></td></tr>')
    facts = ''.join(f'<li><a href="{u}">{E(t)}</a></li>' for t, u in ep['facts'])
    prod = ''.join(f'<li>{p}</li>' for p in ep.get('prod', GSK_PROD))
    body = (f'<h2>Photos, documents and footage</h2><p class="note">{E(ep.get("note", GSK_NOTE))}</p>'
            f'<table><thead><tr><th>Shown</th><th>Licence</th><th>Author / source</th><th>Source page</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'
            f'<h2>Fact sources</h2><p class="note">Facts in the narration were cross-checked against at least two sources wherever possible; a few details rest on a single report. Where sources disagree, the narration uses the safer wording.</p><ul>{facts}</ul>'
            f'<h2>Production</h2><ul>{prod}</ul>')
    os.makedirs(ep['slug'], exist_ok=True)
    open(os.path.join(ep['slug'], 'index.html'), 'w', encoding='utf-8').write(
        page(f'{ep["no"]} {ep["title"]}', 'JINJU ARCHIVE · SOURCES', f'{ep["ko"]} · 출처와 자료 목록', body))
    return f'<li><a href="{ep["slug"]}/">{E(ep["no"])} {E(ep["title"])}</a> · {E(ep["ko"])}</li>'

items = ''.join(episode(ep) for ep in (GSK, PH, HS, ET))
open('index.html', 'w', encoding='utf-8').write(page('Jinju Archive', 'SOURCES', '진주 아카이브 영상의 출처와 자료 목록',
    f'<h2>Episodes</h2><ul>{items}</ul><p class="note">Each page lists the photos, documents, footage and articles used in that video.</p>'))
print('built')
