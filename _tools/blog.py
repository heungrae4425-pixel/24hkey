"""블로그 생성기.

_posts/<slug>.txt 원고를 읽어 blog/<slug>.html, blog/index.html, 썸네일·본문 사진을 만든다.

원고 형식
  머리말 (--- 위)
    title / date / place(썸네일 맨 위 동네 이름) / region(지역 페이지 slug) / photo(배경 사진 번호 1~20) / desc
  본문 (--- 아래)
    # 소제목            → H2 (번호·목차 자동)
    문장 / 문장         → 문단 (/ 마다 줄바꿈)
    [글자](주소)        → 링크 (사이트 안 페이지)
    - 항목              → 목록
    ? 질문 | 답         → 자주 묻는 질문
    @ 사진 설명         → 본문 사진 (썸네일과 같은 문구, 크기·배경 사진은 매번 다름)

사진은 모두 EXIF·ICC 같은 메타 정보 없이 저장한다.
"""
import os, re, json, sys, datetime

# 예약 공개: date 가 오늘(한국 시간)보다 뒤인 글은 빌드에서 빼 둔다.
# 매일 아침 GitHub Actions(.github/workflows/daily-publish.yml)가 다시 빌드하면 그날 글이 공개된다.
TODAY = os.environ.get("PUBLISH_DATE") or (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).strftime("%Y-%m-%d")
# 이미 있는 사진은 다시 그리지 않는다 (--force-images 로 전부 다시 그림)
FORCE_IMAGES = "--force-images" in sys.argv
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

from build import head, foot, page_top, side, write, e, ROOT, TEL, NAME, CITIES, SITE

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
MINT = "#3fdca4"
# 본문 사진 크기 (돌아가며 사용)
BODY_SIZES = [(800, 800), (800, 450), (720, 960), (800, 600), (760, 760)]


def parse(path):
    raw = open(path, encoding="utf-8").read()
    meta_txt, body = raw.split("\n---\n", 1)
    meta = dict(l.split(": ", 1) for l in meta_txt.strip().splitlines())
    meta["slug"] = os.path.basename(path)[:-4]
    meta["photo"] = (int(meta.get("photo", 1)) - 1) % 20 + 1   # 1~20 밖의 번호는 순환
    meta["body"] = body
    return meta


def inline(text):
    """문장 안의 [글자](주소) 를 링크로 바꾼다."""
    out, pos = [], 0
    for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
        out.append(e(text[pos:m.start()]))
        out.append(f'<a href="{e(m.group(2))}">{e(m.group(1))}</a>')
        pos = m.end()
    out.append(e(text[pos:]))
    return "".join(out)


def strip_links(text):
    return re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)


def render(p):
    out, lst, faq, toc, n, img_no = [], [], [], [], 0, 0
    slug = p["slug"]

    def flush():
        nonlocal lst, faq
        if lst:
            out.append('<ul class="list">' + "".join(f"<li>{inline(i)}</li>" for i in lst) + "</ul>")
            lst = []
        if faq:
            out.append('<div class="qa">' + "".join(
                f'<div><p class="q">{e(q)}</p><p class="a">{inline(a)}</p></div>' for q, a in faq) + "</div>")
            faq = []

    images = []
    for line in p["body"].strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            flush()
            n += 1
            title = line[2:]
            toc.append((n, title))
            out.append(f'<h2 id="s{n}">{n}. {e(title)}</h2>')
        elif line.startswith("- "):
            lst.append(line[2:])
        elif line.startswith("? "):
            q, a = line[2:].split(" | ", 1)
            faq.append((q, a))
        elif line.startswith("@"):
            flush()
            img_no += 1
            alt = line[1:].strip() or f"{p['place']} 출장열쇠"
            w, h = BODY_SIZES[(img_no - 1) % len(BODY_SIZES)]
            # imgset: region → 본문 사진을 지역(구·시)별 공용 사진으로 재사용 (파일 수 절약)
            name = (f"r-{p['region']}-{img_no}.jpg" if p.get("imgset") == "region" else f"{slug}-{img_no}.jpg")
            images.append((name, w, h, img_no))
            out.append(f'<figure class="post-img"><img src="blog/img/{name}" alt="{e(alt)}" width="{w}" height="{h}" loading="lazy"></figure>')
        else:
            flush()
            out.append("<p>" + "<br>".join(inline(s.strip()) for s in line.split(" / ")) + "</p>")
    flush()
    toc_html = ('<nav class="toc" aria-label="목차"><b>목차</b><ol>' +
                "".join(f'<li><a href="blog/{slug}#s{i}">{e(t)}</a></li>' for i, t in toc) + "</ol></nav>")
    return toc_html, "\n".join(out), images


# ── 사진 ─────────────────────────────────────────────────
def _font(size):
    return ImageFont.truetype(FONT, size, index=1)


def _fit(d, text, size, max_w):
    f = _font(size)
    while d.textlength(text, font=f) > max_w and size > 30:
        size -= 4
        f = _font(size)
    return f


def save_clean(im, path, quality):
    # 메타 정보(EXIF, ICC, 주석) 없이 새 이미지로 저장
    clean = Image.new("RGB", im.size)
    clean.paste(im)
    # 용량을 줄이기 위해 화질을 12 낮춰 저장 (눈으로는 거의 차이 없음)
    clean.save(path, "JPEG", quality=max(60, quality - 12), optimize=True, progressive=True)


def card(out, place, photo, w, h, shift=0.5, bright=0.62, quality=84, tags=()):
    if not FORCE_IMAGES and os.path.exists(out):
        return
    """동네 이름 / 24시 출장열쇠 / 전화번호 를 실제 사진 위에 얹는다. tags 가 있으면 아래에 빨간 띠로 추가."""
    bg = Image.open(os.path.join(HERE, "thumb_bg", f"bg{photo:02d}.jpg")).convert("RGB")
    s = max(w / bg.width, h / bg.height) * 1.08
    bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1), Image.LANCZOS)
    l = int((bg.width - w) * shift)
    t = int((bg.height - h) * (1 - shift))
    im = ImageEnhance.Brightness(bg.crop((l, t, l + w, t + h))).enhance(bright)
    d = ImageDraw.Draw(im)
    base = min(w, h * 0.95) * (0.84 if tags else 1)
    lines = [(place, base * 0.284, MINT, 0.09), ("24시 출장열쇠", base * 0.185, "#ffffff", 0.08),
             (TEL, base * 0.172, "#ffffff", 0.09)]
    fonts = [_fit(d, t, int(sz), w - int(w * 0.09)) for t, sz, _, _ in lines]
    hs = [f.getbbox(t)[3] - f.getbbox(t)[1] for (t, *_), f in zip(lines, fonts)]
    gap = int(h * 0.045)
    tf = _font(int(base * 0.1)) if tags else None
    pad_x, pad_y = int(base * 0.035), int(base * 0.022)
    tag_hs = [tf.getbbox(t)[3] - tf.getbbox(t)[1] + pad_y * 2 for t in tags]
    tag_gap = int(h * 0.02)
    total = sum(hs) + gap * 2 + (gap + sum(tag_hs) + tag_gap * (len(tags) - 1) if tags else 0)
    y = (h - total) // 2
    for i, ((text, _, color, sk), f, hh) in enumerate(zip(lines, fonts, hs)):
        bb = f.getbbox(text)
        x = (w - (bb[2] - bb[0])) // 2 - bb[0]
        stroke = max(3, int(f.size * sk))
        d.text((x, y - bb[1]), text, font=f, fill=color, stroke_width=stroke, stroke_fill="#0b0b0b")
        if i == 2:  # 전화번호는 한 번 더 굵게
            d.text((x, y - bb[1]), text, font=f, fill=color, stroke_width=max(2, f.size // 28), stroke_fill=color)
        y += hh + gap
    for t, th in zip(tags, tag_hs):
        bb = tf.getbbox(t)
        tw = bb[2] - bb[0]
        bw = tw + pad_x * 2
        x0 = (w - bw) // 2
        d.rectangle((x0, y, x0 + bw, y + th), fill="#e3120b", outline="#0b0b0b", width=max(3, int(base * 0.008)))
        d.text((x0 + pad_x - bb[0], y + pad_y - bb[1]), t, font=tf, fill="#ffffff")
        y += th + tag_gap
    save_clean(im, out, quality)


# ── 페이지 ───────────────────────────────────────────────
def with_base(page):
    # blog/ 폴더 안 페이지도 루트 기준으로 링크가 맞도록
    return page.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="/">', 1)


def article_ld(p):
    return json.dumps({
        "@context": "https://schema.org", "@type": "BlogPosting",
        "headline": p["title"], "description": p["desc"],
        "datePublished": p["date"], "dateModified": p["date"],
        "image": f"{SITE}/blog/img/{p['slug']}-og.jpg",
        "mainEntityOfPage": f"{SITE}/blog/{p['slug']}",
        "author": {"@type": "Organization", "name": NAME, "url": SITE},
        "publisher": {"@type": "Organization", "name": NAME, "url": SITE},
    }, ensure_ascii=False)


def build_post(p, posts):
    city = next((c for c in CITIES if c["slug"] == p["region"]), None)
    path = f"blog/{p['slug']}.html"
    toc, body, images = render(p)
    page = head(f"{p['title']} | {NAME}", p["desc"], path.replace(".html", ""), f"blog/img/{p['slug']}-og.jpg")
    page = page.replace('<meta property="og:type" content="website">', '<meta property="og:type" content="article">')
    page = page.replace("</head>", f'<script type="application/ld+json">{article_ld(p)}</script>\n</head>', 1)
    crumb = '<a href="./">홈</a> › <a href="blog/">블로그</a>'
    if city:
        crumb += f' › <a href="{city["slug"]}.html">{city["name"]}</a>'
    page += page_top(crumb, e(p["title"]), p["date"].replace("-", ". ") + ".")
    others = [o for o in posts if o["slug"] != p["slug"]][:4]
    more = ""
    if others:
        more = '<h2>다른 글</h2><div class="post-grid">' + "".join(
            f'<a class="post-card" href="blog/{o["slug"]}"><img src="blog/img/{o["slug"]}.jpg" alt="" loading="lazy" width="810" height="1080"><b>{e(o["title"])}</b></a>'
            for o in others) + "</div>"
    page += f"""
<div class="wrap content">
  <article class="article post">
    <img class="post-cover" src="blog/img/{p['slug']}.jpg" alt="{e(p['place'])} 24시 출장열쇠 {TEL}" width="810" height="1080">
    {toc}
    {body}
    {more}
  </article>
  {side(city['slug'] if city else None, city['prov'] if city else None)}
</div>
"""
    write(path, with_base(page + foot()))
    return images


PER_PAGE = 20


def page_url(n):
    return "blog/" if n == 1 else f"blog/page/{n}"


def pager(n, total):
    if total <= 1:
        return ""
    items = []
    if n > 1:
        items.append(f'<a href="{page_url(n - 1)}" rel="prev">이전</a>')
    for i in range(1, total + 1):
        items.append(f'<b aria-current="page">{i}</b>' if i == n else f'<a href="{page_url(i)}">{i}</a>')
    if n < total:
        items.append(f'<a href="{page_url(n + 1)}" rel="next">다음</a>')
    return '<nav class="pager" aria-label="블로그 페이지">' + "".join(items) + "</nav>"


def build_index(posts):
    import math, shutil
    total = max(1, math.ceil(len(posts) / PER_PAGE))
    shutil.rmtree(os.path.join(ROOT, "blog", "page"), ignore_errors=True)
    for n in range(1, total + 1):
        chunk = posts[(n - 1) * PER_PAGE: n * PER_PAGE]
        start = (n - 1) * PER_PAGE
        toc = "".join(
            f'<li><a href="blog/{p["slug"]}"><i>{start + k + 1}</i><span>{e(p["title"])}</span><em>{e(p["place"])}</em></a></li>'
            for k, p in enumerate(chunk))
        cards = "".join(
            f'<a class="post-card" href="blog/{p["slug"]}"><img src="blog/img/{p["slug"]}.jpg" alt="" loading="lazy" width="810" height="1080">'
            f'<b>{e(p["title"])}</b><span>{p["date"]}</span></a>' for p in chunk)
        suffix = "" if n == 1 else f" {n}페이지"
        page = head(f"블로그{suffix} | {NAME}", "출장열쇠, 현관문 개문, 도어락 이야기를 동네별로 적어 둡니다.", page_url(n))
        extra = ""
        if n > 1:
            extra += f'<link rel="prev" href="{SITE}/{page_url(n - 1)}">'
        if n < total:
            extra += f'<link rel="next" href="{SITE}/{page_url(n + 1)}">'
        if extra:
            page = page.replace("</head>", extra + "\n</head>", 1)
        lead = f"동네별 출장 이야기와 도어락 관리 요령을 적어 둡니다. 전체 {len(posts)}개 글 중 {start + 1}~{start + len(chunk)}번째입니다."
        page += page_top('<a href="./">홈</a> › 블로그' + (f" › {n}페이지" if n > 1 else ""), "블로그", lead)
        page += (f'<div class="wrap" style="padding-block:36px">'
                 f'<h2 class="toc-h">목차 <small>{n} / {total} 페이지</small></h2><ol class="blog-toc">{toc}</ol>'
                 f'<div class="post-grid">{cards}</div>{pager(n, total)}</div>')
        out = "blog/index.html" if n == 1 else f"blog/page/{n}.html"
        write(out, with_base(page + foot()))


def add_to_sitemap(posts):
    path = os.path.join(ROOT, "sitemap.xml")
    sm = open(path, encoding="utf-8").read()
    urls = [f"{SITE}/blog/"] + [f"{SITE}/{page_url(n)}" for n in range(2, max(1, -(-len(posts) // PER_PAGE)) + 1)] + [f"{SITE}/blog/{p['slug']}" for p in posts]
    add = "".join(f"<url><loc>{u}</loc></url>" for u in urls if f"<loc>{u}</loc>" not in sm)
    write("sitemap.xml", sm.replace("</urlset>", add + "</urlset>"))


def load_posts():
    pdir = os.path.join(ROOT, "_posts")
    posts = (parse(os.path.join(pdir, f)) for f in os.listdir(pdir) if f.endswith(".txt"))
    return sorted((p for p in posts if p["date"] <= TODAY),
                  key=lambda p: (p["date"], p["slug"]), reverse=True)


def main():
    img = os.path.join(ROOT, "blog", "img")
    os.makedirs(img, exist_ok=True)
    posts = load_posts()
    shared_done = set()
    city_name = {c["slug"]: c["name"] for c in CITIES}
    for p in posts:
        card(os.path.join(img, f"{p['slug']}.jpg"), p["place"], p["photo"], 810, 1080)
        card(os.path.join(img, f"{p['slug']}-og.jpg"), p["place"], p["photo"], 1200, 630, shift=0.5)
        for name, w, h, k in build_post(p, posts):
            shared = p.get("imgset") == "region"
            if shared:
                if name in shared_done:
                    continue
                shared_done.add(name)
            ph = ((len(p["region"]) * 5 if shared else p["photo"]) + k * 3 - 1) % 20 + 1   # 사진마다 다른 배경
            card(os.path.join(img, name), city_name.get(p["region"], p["place"]) if shared else p["place"], ph, w, h,
                 shift=(0.2, 0.8, 0.35, 0.65, 0.5)[k % 5], bright=(0.58, 0.64, 0.6, 0.66, 0.62)[k % 5],
                 quality=(82, 86, 80, 84, 83)[k % 5], tags=("비파손 개방 전문", "개방 실패시 무료"))
    build_index(posts)
    add_to_sitemap(posts)
    # 관리자 화면용 글 목록 (서버에서만 읽음, 외부 접근은 차단)
    write("blog/posts.json", json.dumps({
        "posts": [{k: p[k] for k in ("slug", "title", "date", "region", "place")} for p in posts],
        "regions": [{"slug": c["slug"], "name": c["name"], "prov": c["prov"]} for c in CITIES],
    }, ensure_ascii=False))
    return posts


if __name__ == "__main__":
    print([p["slug"] for p in main()])
