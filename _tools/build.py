#!/usr/bin/env python3
"""24시출장열쇠 사이트 생성기.

python3 _tools/build.py  → 저장소 루트에 모든 페이지를 만든다.
DRAFT = True 인 동안에는 모든 페이지에 noindex 가 붙어 검색에 노출되지 않는다.
공개할 때 DRAFT = False 로 바꾸고 다시 실행.
"""
import os, html, json

DRAFT = True
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://xn--24-ji5jp6afzih4cnup.kr"   # 24시출장열쇠.kr
NAME = "24시출장열쇠"
TEL = "010-3664-5455"
TEL_RAW = "01036645455"
VER = "2"

def w(n):
    return f"assets/work/w{n:02d}.jpg"

# ── 서비스 ───────────────────────────────────────────────
SERVICES = [
  dict(slug="key-call", name="출장 열쇠", pics=[9, 1, 10], short="어디 계시든 갑니다. 밤이든 새벽이든.",
       title="출장 열쇠",
       lead="열쇠를 잃어버렸거나 문이 잠겼을 때 전화 주시면 계신 곳으로 갑니다. 24시간 받습니다.",
       body=[
         ("이럴 때 전화 주세요", None, ["외출했다 왔는데 현관문이 안 열릴 때", "열쇠를 잃어버렸거나 집 안에 두고 나왔을 때",
                                    "도어락 배터리가 다 돼서 번호판이 안 켜질 때", "늦은 밤이라 다른 데 연락이 안 될 때"]),
         ("전화로 먼저 여쭤봅니다", "문 종류랑 도어락 상태를 먼저 여쭤봅니다.\n그래야 필요한 장비를 챙겨서 한 번에 끝낼 수 있습니다.", None),
         ("비용은 작업 전에 말씀드립니다", "도착해서 상태를 보고 얼마인지 먼저 말씀드립니다.\n괜찮다고 하시면 그때 시작합니다. 못 열면 돈 안 받습니다.", None),
       ]),
  dict(slug="door-open", name="현관문 개문", pics=[6, 2, 7], short="문 최대한 안 상하게 엽니다.",
       title="현관문 개문",
       lead="잠긴 현관문, 문하고 도어락이 최대한 안 상하는 방법부터 해봅니다. 못 열면 돈 안 받습니다.",
       body=[
         ("문이 안 열리는 흔한 이유", None, ["도어락 배터리가 다 돼서 번호판이 꺼진 경우", "비밀번호가 기억 안 나는 경우",
                                         "모터 소리만 나고 걸쇠가 안 빠지는 경우", "안쪽 보조키가 걸려 버린 경우"]),
         ("상하지 않게 여는 게 먼저", "문을 여는 방법은 여러 가지가 있습니다.\n문과 도어락이 덜 상하는 방법부터 차례로 해봅니다.", None),
         ("열고 나서 확인까지", "열고 나면 도어락이 제대로 잠기고 열리는지 같이 확인합니다.\n고쳐서 쓸 수 있으면 교체는 권하지 않습니다.", None),
       ]),
  dict(slug="doorlock-install", name="도어락 설치", pics=[5, 3, 4], short="문 보고 맞는 제품으로 달아드립니다.",
       title="도어락 설치",
       lead="새 집, 상가, 사무실 출입문. 문 재질하고 두께를 보고 맞는 제품으로 답니다.",
       body=[
         ("설치 전에 보는 것", None, ["문 재질과 두께 (철문, 방화문, 나무문)", "원래 뚫려 있는 구멍 위치와 크기",
                                   "문이 닫힐 때 틀어지지 않는지", "번호키, 지문, 카드 중 어떤 걸 원하시는지"]),
         ("문에 맞는 걸로", "같은 도어락이라도 문에 따라 안 맞는 경우가 있습니다.\n문을 직접 보고 맞는 제품을 말씀드립니다.", None),
         ("다 달고 나서", "비밀번호, 지문, 카드 등록하는 법이랑 배터리 바꾸는 법까지 알려드립니다.", None),
       ]),
  dict(slug="doorlock-replace", name="도어락 교체", pics=[13, 8, 11], short="있던 구멍 그대로 살려서 바꿉니다.",
       title="도어락 교체",
       lead="이사 오셨거나 오래돼서 자꾸 말썽일 때. 원래 구멍을 최대한 살려서 바꿉니다.",
       body=[
         ("이럴 때 많이 바꾸십니다", None, ["이사 왔는데 전에 살던 분 도어락을 그대로 쓰는 경우", "버튼이 잘 안 눌리거나 오작동이 잦은 경우",
                                         "번호키를 지문이나 카드로 바꾸고 싶은 경우", "부품을 구하기 어려운 오래된 제품"]),
         ("문에 새 구멍 안 내도록", "가능하면 원래 구멍 그대로 맞는 제품으로 바꿉니다.\n안 맞으면 미리 말씀드리고 괜찮다고 하실 때 작업합니다.", None),
         ("고칠 수 있으면 고칩니다", "교체 문의로 오셨어도 고쳐서 될 것 같으면 수리를 먼저 말씀드립니다.", None),
       ]),
  dict(slug="doorlock-repair", name="도어락 수리", pics=[17, 12, 15], short="고칠 수 있으면 고칩니다. 교체 안 권합니다.",
       title="도어락 수리",
       lead="번호판이 안 켜지거나, 안 잠기거나, 삑삑 소리가 계속 날 때. 원인 찾아서 고칩니다.",
       body=[
         ("자주 오는 고장", None, ["번호판이 안 켜지거나 몇 개 버튼만 눌릴 때", "문 닫아도 자동으로 안 잠길 때",
                                 "경고음이 계속 울릴 때", "지문이나 카드를 잘 못 알아볼 때", "모터 소리만 나고 안 열릴 때"]),
         ("먼저 해보셔도 되는 것", "배터리가 약하면 이런저런 증상이 같이 나옵니다.\n배터리를 전부 새 걸로 바꿔 보시고, 그래도 똑같으면 전화 주세요.", None),
         ("세게 당기거나 두드리지 마세요", "안 열린다고 손잡이를 세게 당기거나 두드리면 더 망가질 수 있습니다.\n그대로 두고 전화 주시면 됩니다.", None),
       ]),
]

# ── 지역 ─────────────────────────────────────────────────
CITIES = [
  dict(slug="suwon", name="수원", full="수원시",
       intro="영통, 광교 아파트부터 권선, 장안 주택가, 인계동 상가까지 수원 어디든 갑니다.",
       dongs=["영통동","매탄동","원천동","망포동","광교동","이의동","인계동","권선동","세류동","곡선동","정자동","조원동",
              "율전동","천천동","화서동","호매실동","금곡동","우만동","파장동","연무동","송죽동","매교동","고등동","행궁동"]),
  dict(slug="hwaseong", name="화성", full="화성시",
       intro="동탄 아파트 단지, 병점, 봉담, 향남 주택가, 남양까지 화성 어디든 갑니다.",
       dongs=["동탄 반송동","동탄 능동","동탄 청계동","동탄 영천동","동탄 오산동","동탄 목동","동탄 산척동","동탄 장지동",
              "병점동","진안동","기배동","새솔동","봉담읍","향남읍","남양읍","송산동","화산동"]),
  dict(slug="yongin", name="용인", full="용인시",
       intro="수지, 기흥 아파트 단지부터 처인구 주택가, 상가까지 용인 어디든 갑니다.",
       dongs=["풍덕천동","상현동","성복동","죽전동","동천동","신봉동","구갈동","보정동","동백동","영덕동","서농동",
              "상갈동","마북동","신갈동","역북동","김량장동","고림동","유림동","포곡읍","모현읍","남사읍"]),
  dict(slug="osan", name="오산", full="오산시",
       intro="세교 아파트부터 오산동, 원동 주택가와 상가까지 오산 어디든 갑니다.",
       dongs=["오산동","원동","궐동","세교동","신장동","대원동","남촌동","초평동","수청동","갈곶동","누읍동","부산동"]),
  dict(slug="seongnam", name="성남", full="성남시",
       intro="분당, 판교 아파트와 사무실, 수정구, 중원구 주택가, 위례까지 성남 어디든 갑니다.",
       dongs=["분당 정자동","서현동","수내동","야탑동","이매동","금곡동","구미동","판교 백현동","삼평동","운중동",
              "태평동","신흥동","단대동","위례동","금광동","은행동","상대원동","도촌동"]),
]

STEPS = [("전화", "어디인지, 어떤 상황인지"), ("확인", "문 종류와 증상을 여쭤봅니다"),
         ("출동", "도착 전에 전화드립니다"), ("비용 안내", "작업 전에 먼저 말씀드립니다"),
         ("작업", "끝나고 잘 되는지 같이 봅니다")]

FAQ = [
  ("문 못 열면 돈 내야 하나요?", "안 받습니다. 그리고 작업 전에 얼마인지 먼저 말씀드리고, 괜찮다고 하시면 시작합니다."),
  ("새벽에도 오시나요?", "24시간 받습니다. 시간 상관없이 전화 주세요."),
  ("어디까지 오시나요?", "서울, 경기 다 갑니다. 수원, 화성, 용인, 오산, 성남은 아래에 동네별로 적어 뒀습니다."),
  ("문이나 도어락이 망가지진 않나요?", "덜 상하는 방법부터 해봅니다. 부품을 바꿔야 할 때는 미리 말씀드립니다."),
  ("집주인 아니어도 열어주나요?", "사시는 분이 맞는지 신분증이나 우편물로 확인하고 엽니다."),
  ("고장 나면 무조건 바꿔야 하나요?", "아닙니다. 고쳐서 될 것 같으면 수리를 먼저 말씀드립니다."),
]

NAV = [("key-call", "출장 열쇠"), ("door-open", "현관문 개문"), ("doorlock-install", "도어락 설치"),
       ("doorlock-replace", "도어락 교체"), ("doorlock-repair", "도어락 수리"), ("area", "출장 지역"), ("guide", "이용안내")]

e = html.escape


def href(slug):
    return "./#area" if slug == "area" else f"{slug}.html"


def head(title, desc, path, img="assets/work/w09.jpg"):
    url = SITE + "/" + path
    robots = '<meta name="robots" content="noindex, nofollow">\n' if DRAFT else ""
    ld = json.dumps({"@context": "https://schema.org", "@type": "Locksmith", "name": NAME, "url": SITE,
                     "telephone": TEL, "areaServed": ["서울특별시", "경기도"], "openingHours": "Mo-Su 00:00-24:00"},
                    ensure_ascii=False)
    nav = "".join(f'<a href="{href(s)}"{" aria-current=page" if path == s + ".html" else ""}>{n}</a>' for s, n in NAV)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
{robots}<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{NAME}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/{img}">
<meta name="theme-color" content="#ffd400">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css">
<link rel="stylesheet" href="assets/style.css?v={VER}">
<script type="application/ld+json">{ld}</script>
</head>
<body>
{'<div class="draft-flag">초안</div>' if DRAFT else ''}
<header class="site-header"><div class="wrap">
  <a class="logo" href="./"><em>24시</em>출장열쇠</a>
  <a class="h-call" href="tel:{TEL_RAW}">{TEL}</a>
</div></header>
<nav class="nav" aria-label="메뉴"><div class="wrap">{nav}</div></nav>
<main>
"""


def foot():
    svc = "".join(f'<a href="{s["slug"]}.html">{s["name"]}</a>' for s in SERVICES)
    area = "".join(f'<a href="{c["slug"]}.html">{c["name"]}</a>' for c in CITIES)
    return f"""</main>
<footer><div class="wrap">
  <div class="name">{NAME}</div>
  <div>전화 <b>{TEL}</b> · 24시간 · 서울, 경기 출장</div>
  <div class="links">{svc}<a href="guide.html">이용안내</a></div>
  <div class="links">출장 지역: {area}</div>
  <div>문 못 열면 돈 안 받습니다. 비용은 작업 전에 먼저 말씀드립니다.</div>
</div></footer>
<div class="callbar"><a class="main" href="tel:{TEL_RAW}">전화 {TEL}</a><a class="sub" href="./#area">지역</a></div>
</body>
</html>
"""


def tel_box(label="24시간 바로 받습니다"):
    return f'<a class="tel-box" href="tel:{TEL_RAW}"><small>{label}</small><b>{TEL}</b></a>'


def flow():
    return '<ol class="flow">' + "".join(
        f"<li><em>{i}</em><div><b>{a}</b><span>{b}</span></div></li>" for i, (a, b) in enumerate(STEPS, 1)) + "</ol>"


def qa(items):
    return '<div class="qa">' + "".join(
        f'<div><p class="q">{e(q)}</p><p class="a">{e(a)}</p></div>' for q, a in items) + "</div>"


def side(current=None):
    s = "".join(f'<li><a href="{x["slug"]}.html">{x["name"]}</a></li>' for x in SERVICES if x["slug"] != current)
    c = "".join(f'<li><a href="{x["slug"]}.html">{x["name"]} 출장열쇠</a></li>' for x in CITIES if x["slug"] != current)
    return f"""<aside class="side">
  <div class="call">24시간 받습니다<a href="tel:{TEL_RAW}">{TEL}</a>못 열면 돈 안 받습니다</div>
  <div class="box"><h3>하는 일</h3><ul>{s}</ul></div>
  <div class="box"><h3>지역</h3><ul>{c}</ul></div>
</aside>"""


def body_html(blocks):
    out = []
    for h, para, items in blocks:
        out.append(f"<h2>{e(h)}</h2>")
        if para:
            out += [f"<p>{e(line)}</p>" for line in para.split("\n")]
        if items:
            out.append('<ul class="list">' + "".join(f"<li>{e(i)}</li>" for i in items) + "</ul>")
    return "\n".join(out)


def write(path, content):
    with open(os.path.join(ROOT, path), "w", encoding="utf-8") as f:
        f.write(content)


def page_top(crumb, h1, lead):
    return f"""<section class="page-top"><div class="wrap">
  <div class="crumb">{crumb}</div>
  <h1>{h1}</h1><p>{e(lead)}</p>{tel_box()}
</div></section>"""


# ── 홈 ───────────────────────────────────────────────────
def build_home():
    hero_pics = "".join(f'<img src="{w(n)}" alt="설치한 도어락" width="240" height="240">' for n in (9, 6, 13, 17))
    menu = "".join(f'<a href="{s["slug"]}.html"><img src="{w(s["pics"][0])}" alt="{s["name"]}" loading="lazy">'
                   f'<div><b>{s["name"]}</b><span>{s["short"]}</span></div><i>→</i></a>' for s in SERVICES)
    photos = "".join(f'<img src="{w(n)}" alt="작업한 도어락" loading="lazy" width="200" height="200">' for n in range(1, 21))
    area = "".join(f'<a href="{c["slug"]}.html"><b>{c["name"]}</b><span>{", ".join(c["dongs"][:5])} …</span><i>동네 보기</i></a>'
                   for c in CITIES)
    page = head("24시출장열쇠 · 현관문 개문 · 도어락 수리",
                "문 안 열리면 전화 주세요. 24시간 출장열쇠, 현관문 개문, 도어락 설치·교체·수리. 서울·경기 출장, 못 열면 비용 없음.", "")
    page += f"""
<section class="hero"><div class="wrap">
  <div>
    <h1>문 안 열리면<br><span>전화 주세요</span></h1>
    <p class="sub">현관문 개문 · 출장 열쇠 · 도어락 설치, 교체, 수리<br>서울, 경기 어디든 24시간 갑니다.</p>
    {tel_box()}
    <ul class="facts"><li>못 열면 돈 안 받습니다</li><li>비용은 작업 전에 먼저 말씀드립니다</li><li>도어락 일만 30년 했습니다</li></ul>
  </div>
  <div class="hero-photos">{hero_pics}</div>
</div></section>

<section class="sec" id="services"><div class="wrap">
  <h2>이런 일 합니다</h2>
  <p class="note">눌러 보시면 자세히 적어 뒀습니다.</p>
  <div class="menu">{menu}</div>
</div></section>

<section class="sec paper"><div class="wrap">
  <h2>전화 주시면 이렇게 합니다</h2>
  <p class="note">비용은 꼭 작업 전에 말씀드립니다.</p>
  {flow()}
</div></section>

<section class="sec"><div class="wrap">
  <h2>직접 달고 고친 도어락</h2>
  <p class="note">전부 현장에서 찍은 사진입니다.</p>
  <div class="photos">{photos}</div>
</div></section>

<section class="sec paper" id="area"><div class="wrap">
  <h2>출장 지역</h2>
  <p class="note">지역을 누르면 동네가 나옵니다.</p>
  <div class="area">{area}</div>
  <p class="area-more">여기 없는 곳도 서울, 경기면 갑니다. 전화로 위치만 말씀해 주세요.</p>
</div></section>

<section class="sec"><div class="wrap">
  <h2>많이 물어보시는 것</h2>
  {qa(FAQ)}
</div></section>

<section class="cta"><div class="wrap">
  <h2>문 앞에서 기다리지 마시고<br>바로 전화 주세요</h2>
  <p>출동 되는지 바로 알려드립니다.</p>
  {tel_box()}
</div></section>
"""
    write("index.html", page + foot())


def build_service(s):
    pics = "".join(f'<img src="{w(n)}" alt="{s["name"]} 작업 사진" loading="lazy">' for n in s["pics"])
    page = head(f"{s['title']} | {NAME}", s["lead"][:80], f"{s['slug']}.html", w(s["pics"][0]))
    page += page_top(f'<a href="./">홈</a> › {s["name"]}', s["title"], s["lead"])
    page += f"""
<div class="wrap content">
  <article class="article">
    <div class="pics">{pics}</div>
    {body_html(s['body'])}
    <h2>진행 순서</h2>
    {flow()}
    <h2>많이 물어보시는 것</h2>
    {qa(FAQ[:4])}
  </article>
  {side(s['slug'])}
</div>
"""
    write(f"{s['slug']}.html", page + foot())


def build_city(c):
    dongs = "".join(f"<li>{d}</li>" for d in c["dongs"])
    svc = "".join(f'<li><a href="{s["slug"]}.html">{s["name"]}</a> — {s["short"]}</li>' for s in SERVICES)
    page = head(f"{c['name']} 출장열쇠 · 현관문 개문 · 도어락 수리 | {NAME}",
                f"{c['full']} 24시간 출장열쇠. {c['intro']}"[:80], f"{c['slug']}.html")
    page += page_top(f'<a href="./">홈</a> › <a href="./#area">출장 지역</a> › {c["name"]}', f"{c['name']} 출장열쇠", c["intro"])
    page += f"""
<div class="wrap content">
  <article class="article">
    <h2>{c['name']} 이런 동네 다닙니다</h2>
    <ul class="dongs">{dongs}</ul>
    <p>적혀 있지 않아도 {c['full']}이면 다 갑니다.</p>
    <h2>{c['name']}에서 하는 일</h2>
    <ul class="list">{svc}</ul>
    <h2>전화하실 때 알려주시면 빨라요</h2>
    <ul class="list"><li>주소와 건물 이름 (아파트면 동, 호수)</li><li>문 종류, 번호판이 켜지는지</li>
      <li>사시는 걸 확인할 신분증이나 우편물이 있는지</li></ul>
    <h2>진행 순서</h2>
    {flow()}
    <h2>많이 물어보시는 것</h2>
    {qa([FAQ[0], FAQ[1], FAQ[4]])}
  </article>
  {side(c['slug'])}
</div>
"""
    write(f"{c['slug']}.html", page + foot())


def build_guide():
    page = head(f"이용안내 | {NAME}", "24시출장열쇠 진행 순서, 비용 안내 방법, 거주 확인 방법.", "guide.html")
    page += page_top('<a href="./">홈</a> › 이용안내', "이용안내", "전화 주신 뒤부터 작업 끝날 때까지 어떻게 하는지 적어 뒀습니다.")
    page += f"""
<div class="wrap content">
  <article class="article">
    <h2>진행 순서</h2>
    {flow()}
    <h2>비용</h2>
    <ul class="list"><li>현장에서 상태를 보고 작업 전에 얼마인지 말씀드립니다.</li><li>괜찮다고 하셔야 시작합니다.</li>
      <li>못 열면 돈 안 받습니다.</li><li>고쳐서 되면 교체 권하지 않습니다.</li></ul>
    <h2>사시는 분 확인</h2>
    <p>문을 여는 일이라 사시는 분이 맞는지 확인하고 엽니다.</p>
    <p>신분증, 주소 나온 우편물, 관리사무소 확인 중 하나면 됩니다.</p>
    <h2>출장 지역</h2>
    <p>서울, 경기 다 갑니다. 수원, 화성, 용인, 오산, 성남은 지역 페이지에 동네를 적어 뒀습니다.</p>
    <h2>많이 물어보시는 것</h2>
    {qa(FAQ)}
  </article>
  {side()}
</div>
"""
    write("guide.html", page + foot())


def build_misc():
    write("assets/favicon.svg", '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#ffd400"/>'
          '<rect x="2" y="2" width="60" height="60" fill="none" stroke="#141414" stroke-width="4"/>'
          '<circle cx="24" cy="32" r="10" fill="none" stroke="#e3120b" stroke-width="6"/><path d="M33 32h21M47 32v9M54 32v6" stroke="#e3120b" stroke-width="6"/></svg>')
    pages = [""] + [f"{s['slug']}.html" for s in SERVICES] + [f"{c['slug']}.html" for c in CITIES] + ["guide.html"]
    write("robots.txt", "User-agent: *\nDisallow: /\n" if DRAFT else f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    urls = "".join(f"<url><loc>{SITE}/{p.replace('.html', '')}</loc></url>" for p in pages)
    write("sitemap.xml", f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    write("404.html", head(f"페이지가 없습니다 | {NAME}", "찾으시는 페이지가 없습니다.", "404.html")
          + page_top('<a href="./">홈</a>', "페이지가 없습니다", "급하시면 바로 전화 주세요.") + foot())


if __name__ == "__main__":
    build_home()
    for s in SERVICES:
        build_service(s)
    for c in CITIES:
        build_city(c)
    build_guide()
    build_misc()
    print("done")
