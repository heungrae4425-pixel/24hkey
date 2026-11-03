#!/usr/bin/env python3
"""24시출장열쇠.kr 사이트 생성기.

python3 _tools/build.py  → 저장소 루트에 모든 페이지를 만든다.
DRAFT = True 인 동안에는 모든 페이지에 noindex 가 붙어 검색에 노출되지 않는다.
공개할 때 DRAFT = False 로 바꾸고 다시 실행.
"""
import os, html, json

DRAFT = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://xn--24-ji5jp6afzih4cnup.kr"   # 24시출장열쇠.kr
NAME = "만능 24시 도어락"
TEL = "010-3664-5455"
TEL_RAW = "01036645455"
VER = "1"

PHONE_SVG = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" '
             'stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 '
             '19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 '
             '2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>')

# ── 서비스 ───────────────────────────────────────────────
SERVICES = [
  dict(slug="key-call", name="출장 열쇠", photo="photo-open", short="부르시면 계신 곳으로 바로 갑니다",
       title="출장 열쇠 24시 · 밤낮 없이 바로 출동",
       lead="문이 잠겨 들어가지 못할 때, 열쇠나 도어락 문제로 급할 때 전화 한 통이면 계신 곳으로 출동합니다.",
       body=[
         ("이럴 때 부르세요", None, ["외출했다 돌아왔는데 현관문이 열리지 않을 때", "열쇠를 잃어버리거나 집 안에 두고 나왔을 때",
                                  "도어락 배터리가 다 되어 번호판이 켜지지 않을 때", "늦은 밤이나 새벽이라 다른 곳에 연락이 닿지 않을 때"]),
         ("출동 전에 전화로 확인합니다", "전화를 주시면 문 종류와 잠금장치 상태를 먼저 여쭙니다.\n현장 상황을 미리 알면 필요한 장비를 챙겨 한 번에 해결할 수 있습니다.", None),
         ("작업 전에 비용을 먼저 안내합니다", "현장에 도착해 상태를 확인한 뒤 작업 방법과 비용을 먼저 말씀드립니다.\n동의하신 뒤에만 작업을 시작하며, 도어락 개방에 실패하면 비용을 받지 않습니다.", None),
         ("거주 확인 후 작업합니다", "문을 여는 일인 만큼 신분증이나 우편물 등으로 거주 여부를 확인한 뒤 작업합니다.\n손님과 이웃 모두의 안전을 위한 절차이니 양해 부탁드립니다.", None),
       ]),
  dict(slug="door-open", name="현관문 개문", photo="photo-hero", short="문과 잠금장치를 최대한 상하지 않게",
       title="현관문 개문 · 문이 안 열릴 때",
       lead="잠긴 현관문을 문과 잠금장치 손상을 최소화하는 방법부터 시도해 엽니다. 개방에 실패하면 비용을 받지 않습니다.",
       body=[
         ("문이 안 열리는 흔한 원인", None, ["도어락 배터리 방전으로 번호판이 꺼진 경우", "비밀번호를 잊었거나 바뀐 줄 모르는 경우",
                                         "모터나 걸쇠가 고장 나 소리만 나고 열리지 않는 경우", "보조키·걸쇠가 안쪽에서 걸린 경우"]),
         ("손상이 적은 방법부터", "개문은 문과 잠금장치를 상하지 않게 여는 것이 가장 중요합니다.\n상태를 확인해 손상이 적은 방법부터 차례로 시도합니다.", None),
         ("열고 난 뒤 점검까지", "문을 연 뒤에는 도어락이 다시 정상으로 잠기고 열리는지 확인합니다.\n수리로 해결되면 교체를 권하지 않으며, 필요한 경우에만 교체를 안내합니다.", None),
         ("기다리시는 동안", "추운 날이나 비 오는 날에는 가까운 건물 안에서 기다리셔도 됩니다.\n도착이 가까워지면 전화로 미리 알려드립니다.", None),
       ]),
  dict(slug="doorlock-install", name="도어락 설치", photo="photo-install", short="문 재질과 구조에 맞춰 설치",
       title="도어락 설치 · 새 집, 상가, 사무실",
       lead="현관문 재질과 두께, 기존 타공 상태를 보고 맞는 제품을 골라 설치합니다.",
       body=[
         ("설치 전에 확인하는 것", None, ["현관문 재질과 두께(철문, 방화문, 목문 등)", "기존 타공 위치와 크기",
                                       "문이 닫힐 때 틀어짐이 없는지", "번호키·지문·카드 등 원하시는 사용 방식"]),
         ("문에 맞는 제품 안내", "같은 도어락이라도 문 구조에 따라 맞지 않는 경우가 있습니다.\n현장에서 문을 확인한 뒤 맞는 제품과 설치 방법을 안내합니다.", None),
         ("설치 후 사용법 안내", "설치가 끝나면 비밀번호 등록, 지문·카드 등록, 배터리 교체 방법을 알려드립니다.\n처음 쓰시는 분도 바로 사용하실 수 있게 함께 확인합니다.", None),
       ]),
  dict(slug="doorlock-replace", name="도어락 교체", photo="photo-replace", short="이사 후, 오래된 도어락 교체",
       title="도어락 교체 · 이사 후, 오래된 도어락",
       lead="이사 후 보안이 걱정될 때, 오래되어 자주 고장 날 때 기존 타공을 살려 깔끔하게 교체합니다.",
       body=[
         ("교체를 고민할 때", None, ["이사 와서 전에 살던 분이 쓰던 도어락을 그대로 쓰는 경우", "버튼 반응이 늦거나 오작동이 잦은 경우",
                                    "번호키를 지문·카드 방식으로 바꾸고 싶은 경우", "부품을 구하기 어려운 오래된 제품인 경우"]),
         ("기존 타공을 최대한 활용", "가능하면 기존 구멍을 그대로 쓰는 제품으로 교체해 문에 새 구멍을 내지 않습니다.\n맞지 않을 때는 미리 설명드리고 동의를 받은 뒤 작업합니다.", None),
         ("수리로 되면 수리를 권합니다", "교체 문의를 주셔도 점검해 보고 간단한 수리로 해결되면 수리를 먼저 안내합니다.\n불필요한 교체를 권하지 않습니다.", None),
       ]),
  dict(slug="doorlock-repair", name="도어락 수리", photo="photo-repair", short="번호판·모터·지문 인식 불량",
       title="도어락 수리 · 고장 증상별 점검",
       lead="번호판이 안 켜지거나, 문이 안 잠기거나, 경고음이 계속 울릴 때 원인을 찾아 수리합니다.",
       body=[
         ("자주 들어오는 고장 증상", None, ["번호판이 켜지지 않거나 일부 버튼만 반응할 때", "문을 닫아도 자동으로 잠기지 않을 때",
                                         "경고음이 계속 울리거나 오작동할 때", "지문·카드 인식이 잘 안 될 때", "모터 소리만 나고 열리지 않을 때"]),
         ("먼저 해보셔도 되는 것", "배터리가 약하면 여러 증상이 함께 나타납니다.\n배터리를 새것으로 모두 바꿔 보시고, 그래도 같으면 연락 주세요.", None),
         ("억지로 열거나 두드리지 마세요", "문이 안 열린다고 손잡이를 세게 당기거나 도어락을 두드리면 고장이 커질 수 있습니다.\n그 상태 그대로 두고 전화 주시면 됩니다.", None),
       ]),
]

# ── 지역 ─────────────────────────────────────────────────
CITIES = [
  dict(slug="suwon", name="수원", full="수원시", photo="photo-area",
       intro="영통·광교의 아파트 단지부터 권선·장안의 주택가와 인계동 상가까지 수원 전 지역으로 출동합니다.",
       dongs=["영통동","매탄동","원천동","망포동","광교동","이의동","인계동","권선동","세류동","곡선동","정자동","조원동",
              "율전동","천천동","화서동","호매실동","금곡동","우만동","파장동","연무동","송죽동","매교동","고등동","행궁동"]),
  dict(slug="hwaseong", name="화성", full="화성시", photo="photo-area",
       intro="동탄 신도시 아파트와 병점·봉담·향남의 주택가, 남양 일대까지 화성 전 지역으로 출동합니다.",
       dongs=["동탄 반송동","동탄 능동","동탄 청계동","동탄 영천동","동탄 오산동","동탄 목동","동탄 산척동","동탄 장지동",
              "병점동","진안동","기배동","새솔동","봉담읍","향남읍","남양읍","송산동","화산동"]),
  dict(slug="yongin", name="용인", full="용인시", photo="photo-area",
       intro="수지·기흥의 아파트 단지와 처인구 주택가·상가까지 용인 전 지역으로 출동합니다.",
       dongs=["풍덕천동","상현동","성복동","죽전동","동천동","신봉동","구갈동","보정동","동백동","영덕동","서농동",
              "상갈동","마북동","신갈동","역북동","김량장동","고림동","유림동","포곡읍","모현읍","남사읍"]),
  dict(slug="osan", name="오산", full="오산시", photo="photo-area",
       intro="세교 신도시 아파트부터 오산동·원동 구도심 주택가와 상가까지 오산 전 지역으로 출동합니다.",
       dongs=["오산동","원동","궐동","세교동","신장동","대원동","남촌동","초평동","수청동","갈곶동","누읍동","부산동"]),
  dict(slug="seongnam", name="성남", full="성남시", photo="photo-area",
       intro="분당·판교의 아파트와 오피스, 수정·중원구 주택가와 위례까지 성남 전 지역으로 출동합니다.",
       dongs=["분당 정자동","서현동","수내동","야탑동","이매동","금곡동","구미동","판교 백현동","삼평동","운중동",
              "태평동","신흥동","단대동","위례동","금광동","은행동","상대원동","도촌동"]),
]

STEPS = [("전화 상담", "상황과 위치를 말씀해 주세요"), ("상황 확인", "문 종류와 증상을 먼저 확인합니다"),
         ("현장 출동", "도착 전 미리 연락드립니다"), ("비용 안내·동의", "작업 전 비용을 먼저 안내합니다"),
         ("작업·점검", "작업 후 정상 작동을 확인합니다")]

FAQ = [
  ("문을 끝내 못 열면 비용을 내야 하나요?", "도어락 개방에 실패하면 비용을 받지 않습니다. 작업 전에 비용을 먼저 안내하고, 동의하신 뒤에 시작합니다."),
  ("밤늦게나 새벽에도 출동하나요?", "24시간 운영합니다. 늦은 시간이어도 전화 주시면 바로 출동 가능 여부를 알려드립니다."),
  ("출동 지역은 어디까지인가요?", "서울·경기 전 지역으로 출장합니다. 수원·화성·용인·오산·성남은 동네별로 따로 안내하고 있습니다."),
  ("문을 열 때 문이나 도어락이 망가지지 않나요?", "손상이 적은 방법부터 차례로 시도합니다. 부득이하게 부품을 바꿔야 할 때는 미리 설명드리고 동의를 받습니다."),
  ("집주인이 아니어도 문을 열어 주나요?", "거주하시는 분이 맞는지 신분증이나 우편물 등으로 확인한 뒤 작업합니다. 확인이 어려우면 작업이 제한될 수 있습니다."),
  ("고장 났는데 무조건 교체해야 하나요?", "아닙니다. 점검해 보고 수리로 해결되면 수리를 먼저 안내합니다."),
]

NAV = [("key-call", "출장 열쇠"), ("door-open", "현관문 개문"), ("doorlock-install", "도어락 설치"),
       ("doorlock-replace", "도어락 교체"), ("doorlock-repair", "도어락 수리"), ("area", "출장 지역"), ("guide", "이용안내")]

e = html.escape


def head(title, desc, path, img="assets/scenes/photo-hero.jpg"):
    url = SITE + "/" + path
    robots = '<meta name="robots" content="noindex, nofollow">\n' if DRAFT else ""
    ld = json.dumps({"@context": "https://schema.org", "@type": "Locksmith", "name": NAME, "url": SITE,
                     "telephone": TEL, "areaServed": ["서울특별시", "경기도"], "openingHours": "Mo-Su 00:00-24:00"},
                    ensure_ascii=False)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="24시출장열쇠 · {NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/{img}">
<meta name="theme-color" content="#111216">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="assets/style.css?v={VER}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
{'<div class="draft-flag">초안</div>' if DRAFT else ''}
<div class="top-band">24시간 연중무휴<span class="opt"> · 서울·경기 전 지역 출장</span> · 개방 실패 시 비용 없음</div>
<header class="site-header">
  <div class="wrap">
    <a class="logo" href="./" aria-label="24시출장열쇠 홈"><b><em>24시</em>출장열쇠</b><span>{NAME}</span></a>
    <nav class="nav" aria-label="주 메뉴">{''.join(f'<a href="{href(s)}"{cur(s, path)}>{n}</a>' for s, n in NAV)}</nav>
    <a class="h-call" href="tel:{TEL_RAW}">{PHONE_SVG}{TEL}</a>
    <button class="menu-btn" aria-label="메뉴" aria-expanded="false" onclick="var m=document.getElementById('mnav');m.classList.toggle('open');this.setAttribute('aria-expanded',m.classList.contains('open'))"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 6h16M4 12h16M4 18h16"/></svg></button>
  </div>
  <nav class="m-nav" id="mnav" aria-label="모바일 메뉴">{''.join(f'<a href="{href(s)}">{n}</a>' for s, n in NAV)}</nav>
</header>
<main>
"""


def href(slug):
    return "./#area" if slug == "area" else f"{slug}.html"


def cur(slug, path):
    return ' aria-current="page"' if path == f"{slug}.html" else ""


def foot():
    svc = "".join(f'<a href="{s["slug"]}.html">{s["name"]}</a>' for s in SERVICES)
    area = "".join(f'<a href="{c["slug"]}.html">{c["name"]} 출장열쇠</a>' for c in CITIES)
    return f"""</main>
<footer>
  <div class="wrap">
    <b>24시출장열쇠 · {NAME}</b><br>
    전화 <a href="tel:{TEL_RAW}"><b>{TEL}</b></a> · 24시간 운영 · 서울·경기 전 지역 출장
    <div class="f-links">{svc}<a href="guide.html">이용안내</a></div>
    <div class="f-links">{area}</div>
    <div>도어락 개방 실패 시 비용을 받지 않습니다. 작업 전 비용을 먼저 안내합니다.</div>
  </div>
</footer>
<div class="callbar"><a class="main" href="tel:{TEL_RAW}">{PHONE_SVG}{TEL}</a><a href="./#area">출장 지역</a></div>
</body>
</html>
"""


def bigtel():
    return f'<a class="big-tel" href="tel:{TEL_RAW}">{PHONE_SVG}{TEL}</a>'


def faq_html(items):
    return '<div class="faq">' + "".join(
        f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in items) + "</div>"


def steps_html():
    return '<ol class="steps">' + "".join(f"<li><b>{a}</b><span>{b}</span></li>" for a, b in STEPS) + "</ol>"


def side(current=None):
    s = "".join(f'<li><a href="{x["slug"]}.html">{x["name"]}</a></li>' for x in SERVICES if x["slug"] != current)
    c = "".join(f'<li><a href="{x["slug"]}.html">{x["name"]} 출장열쇠</a></li>' for x in CITIES if x["slug"] != current)
    return f"""<aside class="side">
  <div class="box dark">24시간 바로 연결<a class="tel" href="tel:{TEL_RAW}">{TEL}</a><small>개방 실패 시 비용 없음</small></div>
  <div class="box"><h3>서비스</h3><ul>{s}</ul></div>
  <div class="box"><h3>지역별 안내</h3><ul>{c}</ul></div>
</aside>"""


def body_html(blocks):
    out = []
    for h, para, items in blocks:
        out.append(f"<h2>{e(h)}</h2>")
        if para:
            for line in para.split("\n"):
                out.append(f"<p>{e(line)}</p>")
        if items:
            out.append('<ul class="check">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>")
    return "\n".join(out)


def write(path, content):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f:
        f.write(content)


# ── 홈 ───────────────────────────────────────────────────
def build_home():
    works = [f"assets/work/w{i:02d}.jpg" for i in range(1, 21)]
    imgs = "".join(f'<img src="{w}" alt="도어락 작업 사진" loading="lazy" width="180" height="180">' for w in works)
    svc_cards = "".join(
        f'<a class="svc" href="{s["slug"]}.html" style="background-image:url(assets/scenes/{s["photo"]}.jpg)">'
        f'<h3>{s["name"]}</h3><p>{s["short"]}</p><span class="more">자세히 보기 →</span></a>' for s in SERVICES)
    svc_cards += f'<a class="svc call" href="tel:{TEL_RAW}"><span>지금 바로 전화</span><b>{TEL}</b><span>24시간 연결</span></a>'
    cities = "".join(f'<a class="city" href="{c["slug"]}.html"><b>{c["name"]}</b><span>{len(c["dongs"])}개 동 안내 →</span></a>'
                     for c in CITIES)
    page = head("24시출장열쇠 · 현관문 개문 · 도어락 수리 | " + NAME,
                "문이 안 열릴 때 24시간 출장열쇠. 현관문 개문, 도어락 설치·교체·수리, 서울·경기 전 지역 출장. 개방 실패 시 비용 없음.",
                "")
    page += f"""
<section class="hero" style="background-image:url(assets/scenes/photo-hero.jpg)">
  <div class="wrap">
    <span class="tag">24시간 긴급 출동</span>
    <h1>문이 안 열릴 땐<br><em>24시 출장열쇠</em></h1>
    <p class="lead">현관문 개문, 출장 열쇠, 도어락 설치·교체·수리까지.<br>서울·경기 전 지역, 밤낮없이 전화 한 통이면 출동합니다.</p>
    <div class="hero-btns">{bigtel()}<a class="ghost" href="#area">우리 동네 보기</a></div>
    <ul class="badges"><li class="y">개방 실패 시 비용 없음</li><li>작업 전 비용 안내</li><li>거주 확인 후 작업</li><li>도어락 경력 30년</li></ul>
  </div>
</section>
<div class="strip"><div class="wrap"><ul>
  <li><b>24시간</b>연중무휴 운영</li><li><b>30년</b>도어락 경력</li><li><b>서울·경기</b>전 지역 출장</li><li><b>비용 0원</b>개방 실패 시</li>
</ul></div></div>

<section class="sec" id="services">
  <div class="wrap">
    <div class="sec-head"><div class="kicker">SERVICE</div><h2>어떤 일로 부르시나요?</h2><p>상황에 맞는 서비스를 눌러 자세한 안내를 확인하세요.</p></div>
    <div class="svc-grid">{svc_cards}</div>
  </div>
</section>

<section class="sec alt">
  <div class="wrap">
    <div class="sec-head"><div class="kicker">PROCESS</div><h2>이렇게 진행합니다</h2><p>작업 전에 비용을 먼저 안내하고, 동의하신 뒤에 시작합니다.</p></div>
    {steps_html()}
  </div>
</section>

<section class="sec">
  <div class="wrap"><div class="sec-head"><div class="kicker">WORK</div><h2>직접 작업한 현장</h2><p>사진은 실제 작업 현장에서 찍은 것입니다.</p></div></div>
  <div class="marquee"><div class="track">{imgs}{imgs}</div></div>
</section>

<section class="sec alt" id="area">
  <div class="wrap">
    <div class="sec-head"><div class="kicker">AREA</div><h2>지역별 출장 안내</h2><p>지역을 누르면 동네별 안내를 볼 수 있습니다.</p></div>
    <div class="city-grid">{cities}</div>
    <p class="area-note">안내된 지역 외에도 서울·경기 전 지역으로 출장합니다. 위치를 말씀해 주시면 바로 확인해 드립니다.</p>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec-head"><div class="kicker">FAQ</div><h2>자주 묻는 질문</h2></div>
    {faq_html(FAQ)}
  </div>
</section>

<section class="cta" style="background-image:url(assets/scenes/photo-end.jpg)">
  <div class="wrap"><h2>문 앞에서 기다리지 마세요</h2><p>지금 전화 주시면 출동 가능 여부를 바로 알려드립니다.</p>{bigtel()}</div>
</section>
"""
    page += foot()
    write("index.html", page)


def build_service(s):
    page = head(f"{s['title']} | 24시출장열쇠", s["lead"][:80], f"{s['slug']}.html", f"assets/scenes/{s['photo']}.jpg")
    page += f"""
<section class="page-hero"><div class="wrap">
  <div class="crumb"><a href="./">홈</a> › 서비스 › {s['name']}</div>
  <h1>{e(s['title'])}</h1><p>{e(s['lead'])}</p>{bigtel()}
</div></section>
<section class="sec"><div class="wrap content">
  <article class="article">
    <img class="photo" src="assets/scenes/{s['photo']}.jpg" alt="{s['name']} 작업 사진">
    {body_html(s['body'])}
    <h2>진행 순서</h2>
    {steps_html()}
    <h2>자주 묻는 질문</h2>
    {faq_html(FAQ[:4])}
  </article>
  {side(s['slug'])}
</div></section>
"""
    page += foot()
    write(f"{s['slug']}.html", page)


def build_city(c):
    dongs = "".join(f"<li>{d}</li>" for d in c["dongs"])
    svc = "".join(f'<li>{s["name"]} — {s["short"]}</li>' for s in SERVICES)
    title = f"{c['name']} 출장열쇠 · 현관문 개문 · 도어락 수리"
    page = head(f"{title} | 24시출장열쇠", f"{c['full']} 전 지역 24시 출장열쇠. {c['intro']}"[:80], f"{c['slug']}.html")
    page += f"""
<section class="page-hero"><div class="wrap">
  <div class="crumb"><a href="./">홈</a> › <a href="./#area">출장 지역</a> › {c['name']}</div>
  <h1>{c['name']} 출장열쇠 24시</h1><p>{e(c['intro'])}</p>{bigtel()}
</div></section>
<section class="sec"><div class="wrap content">
  <article class="article">
    <h2>{c['name']} 출장 가능 동네</h2>
    <p>아래 동네를 포함해 {c['full']} 전 지역으로 출동합니다.</p>
    <ul class="dongs">{dongs}</ul>
    <h2>{c['name']}에서 할 수 있는 작업</h2>
    <ul class="check">{svc}</ul>
    <h2>부르기 전에 알려주시면 좋은 것</h2>
    <ul class="check"><li>정확한 주소와 건물 이름(아파트 동·호수)</li><li>문 종류와 도어락 상태(번호판이 켜지는지 등)</li>
      <li>거주를 확인할 수 있는 신분증이나 우편물이 있는지</li></ul>
    <h2>진행 순서</h2>
    {steps_html()}
    <h2>자주 묻는 질문</h2>
    {faq_html([FAQ[0], FAQ[1], FAQ[4]])}
  </article>
  {side(c['slug'])}
</div></section>
"""
    page += foot()
    write(f"{c['slug']}.html", page)


def build_guide():
    page = head("이용안내 | 24시출장열쇠", "24시출장열쇠 이용 방법, 진행 순서, 비용 안내 원칙과 거주 확인 절차를 안내합니다.", "guide.html")
    page += f"""
<section class="page-hero"><div class="wrap">
  <div class="crumb"><a href="./">홈</a> › 이용안내</div>
  <h1>이용안내</h1><p>전화 상담부터 작업 후 점검까지, 진행 방법과 원칙을 안내합니다.</p>{bigtel()}
</div></section>
<section class="sec"><div class="wrap content">
  <article class="article">
    <h2>진행 순서</h2>
    {steps_html()}
    <h2>비용 안내 원칙</h2>
    <ul class="check"><li>현장 상태를 확인한 뒤 작업 전에 비용을 먼저 안내합니다.</li><li>동의하신 뒤에만 작업을 시작합니다.</li>
      <li>도어락 개방에 실패하면 비용을 받지 않습니다.</li><li>수리로 해결되면 교체를 권하지 않습니다.</li></ul>
    <h2>거주 확인 절차</h2>
    <p>문을 여는 작업은 거주하시는 분이 맞는지 확인한 뒤 진행합니다.</p>
    <p>신분증, 주소가 적힌 우편물, 관리사무소 확인 등으로 확인할 수 있습니다.</p>
    <h2>출장 지역</h2>
    <p>서울·경기 전 지역으로 출장합니다. 수원·화성·용인·오산·성남은 지역별 페이지에서 동네를 확인하실 수 있습니다.</p>
    <h2>자주 묻는 질문</h2>
    {faq_html(FAQ)}
  </article>
  {side()}
</div></section>
"""
    page += foot()
    write("guide.html", page)


def build_misc():
    write("assets/favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#d7261e"/>'
          '<circle cx="24" cy="32" r="11" fill="none" stroke="#fff" stroke-width="6"/><path d="M34 32h22M48 32v9M55 32v6" stroke="#fff" stroke-width="6" stroke-linecap="round"/></svg>')
    pages = [""] + [f"{s['slug']}.html" for s in SERVICES] + [f"{c['slug']}.html" for c in CITIES] + ["guide.html"]
    if DRAFT:
        write("robots.txt", "User-agent: *\nDisallow: /\n")
    else:
        write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    urls = "".join(f"<url><loc>{SITE}/{p.replace('.html', '')}</loc></url>" for p in pages)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    write("404.html", head("페이지를 찾을 수 없습니다 | 24시출장열쇠", "요청하신 페이지를 찾을 수 없습니다.", "404.html")
          + f'<section class="page-hero"><div class="wrap"><h1>페이지를 찾을 수 없습니다</h1><p>급하시면 바로 전화 주세요.</p>{bigtel()}</div></section>' + foot())


if __name__ == "__main__":
    build_home()
    for s in SERVICES:
        build_service(s)
    for c in CITIES:
        build_city(c)
    build_guide()
    build_misc()
    print("done:", sorted(f for f in os.listdir(ROOT) if f.endswith(".html")))
