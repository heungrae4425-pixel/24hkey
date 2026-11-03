"""블로그 생성기.

_posts/<slug>.txt 원고를 읽어 blog/<slug>.html, blog/index.html, 썸네일을 만든다.

원고 형식
  머리말 (--- 위)
    title / date / place(썸네일 맨 위 동네 이름) / region(지역 페이지 slug) / photo(배경 사진 번호 1~20) / desc
  본문 (--- 아래)
    # 소제목            → H2 (번호 자동)
    문장 / 문장         → 문단 (/ 마다 줄바꿈)
    - 항목              → 목록
    ? 질문 | 답         → 자주 묻는 질문
"""
import os, html
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

import build
from build import head, foot, page_top, side, write, e, ROOT, TEL, NAME, CITIES

HERE = os.path.dirname(os.path.abspath(__file__))
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
MINT = "#3fdca4"


def parse(path):
    raw = open(path, encoding="utf-8").read()
    meta_txt, body = raw.split("\n---\n", 1)
    meta = dict(l.split(": ", 1) for l in meta_txt.strip().splitlines())
    meta["slug"] = os.path.basename(path)[:-4]
    meta["photo"] = int(meta.get("photo", 1))
    meta["body"] = body
    return meta


def render(body):
    out, lst, faq, n = [], [], [], 0

    def flush():
        nonlocal lst, faq
        if lst:
            out.append('<ul class="list">' + "".join(f"<li>{e(i)}</li>" for i in lst) + "</ul>")
            lst = []
        if faq:
            out.append('<div class="qa">' + "".join(
                f'<div><p class="q">{e(q)}</p><p class="a">{e(a)}</p></div>' for q, a in faq) + "</div>")
            faq = []

    for line in body.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("# "):
            flush()
            n += 1
            out.append(f"<h2>{n}. {e(line[2:])}</h2>")
        elif line.startswith("- "):
            lst.append(line[2:])
        elif line.startswith("? "):
            q, a = line[2:].split(" | ", 1)
            faq.append((q, a))
        else:
            flush()
            out.append("<p>" + "<br>".join(e(s.strip()) for s in line.split(" / ")) + "</p>")
    flush()
    return "\n".join(out)


# ── 썸네일 ───────────────────────────────────────────────
def _font(size):
    return ImageFont.truetype(FONT, size, index=1)


def _fit(d, text, size, max_w):
    f = _font(size)
    while d.textlength(text, font=f) > max_w and size > 40:
        size -= 6
        f = _font(size)
    return f


def thumb(out, place, photo, w, h, sizes):
    bg = Image.open(os.path.join(HERE, "thumb_bg", f"bg{photo:02d}.jpg")).convert("RGB")
    s = max(w / bg.width, h / bg.height)
    bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1), Image.LANCZOS)
    l, t = (bg.width - w) // 2, (bg.height - h) // 2
    im = ImageEnhance.Brightness(bg.crop((l, t, l + w, t + h))).enhance(0.62)
    d = ImageDraw.Draw(im)
    lines = [(place, sizes[0], MINT, sizes[0] // 11), ("24시 출장열쇠", sizes[1], "#ffffff", sizes[1] // 13),
             (TEL, sizes[2], "#ffffff", sizes[2] // 13)]
    fonts = [_fit(d, t, sz, w - 80) for t, sz, _, _ in lines]
    hs = [f.getbbox(t)[3] - f.getbbox(t)[1] for (t, *_), f in zip(lines, fonts)]
    gap = int(h * 0.045)
    y = (h - sum(hs) - gap * 2) // 2
    for (text, _, color, stroke), f, hh in zip(lines, fonts, hs):
        bb = f.getbbox(text)
        x = (w - (bb[2] - bb[0])) // 2 - bb[0]
        d.text((x, y - bb[1]), text, font=f, fill=color, stroke_width=stroke, stroke_fill="#0d0d0d")
        y += hh + gap
    im.save(out, quality=84, optimize=True)


# ── 페이지 ───────────────────────────────────────────────
def with_base(page):
    # blog/ 폴더 안 페이지도 루트 기준으로 링크가 맞도록
    return page.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<base href="/">', 1)


def build_post(p):
    city = next((c for c in CITIES if c["slug"] == p["region"]), None)
    path = f"blog/{p['slug']}.html"
    page = head(f"{p['title']} | {NAME}", p["desc"], path.replace(".html", ""), f"blog/img/{p['slug']}-og.jpg")
    crumb = '<a href="./">홈</a> › <a href="blog/">블로그</a>'
    if city:
        crumb += f' › <a href="{city["slug"]}.html">{city["name"]}</a>'
    page += page_top(crumb, e(p["title"]), p["date"].replace("-", ". ") + ".")
    page += f"""
<div class="wrap content">
  <article class="article post">
    <img class="post-cover" src="blog/img/{p['slug']}.jpg" alt="{e(p['place'])} 출장열쇠 {TEL}" width="810" height="1080">
    {render(p['body'])}
  </article>
  {side(city['slug'] if city else None, city['prov'] if city else None)}
</div>
"""
    write(path, with_base(page + foot()))


def build_index(posts):
    cards = "".join(
        f'<a class="post-card" href="blog/{p["slug"]}"><img src="blog/img/{p["slug"]}.jpg" alt="" loading="lazy" width="810" height="1080">'
        f'<b>{e(p["title"])}</b><span>{p["date"]}</span></a>' for p in posts)
    page = head(f"블로그 | {NAME}", "출장열쇠, 현관문 개문, 도어락 이야기를 동네별로 적어 둡니다.", "blog/")
    page += page_top('<a href="./">홈</a> › 블로그', "블로그", "동네별 출장 이야기와 도어락 관리 요령을 적어 둡니다.")
    page += f'<div class="wrap" style="padding-block:36px"><div class="post-grid">{cards}</div></div>'
    write("blog/index.html", with_base(page + foot()))


def main():
    os.makedirs(os.path.join(ROOT, "blog", "img"), exist_ok=True)
    pdir = os.path.join(ROOT, "_posts")
    posts = sorted((parse(os.path.join(pdir, f)) for f in os.listdir(pdir) if f.endswith(".txt")),
                   key=lambda p: (p["date"], p["slug"]), reverse=True)
    for p in posts:
        img = os.path.join(ROOT, "blog", "img")
        thumb(os.path.join(img, f"{p['slug']}.jpg"), p["place"], p["photo"], 810, 1080, (230, 150, 128))
        thumb(os.path.join(img, f"{p['slug']}-og.jpg"), p["place"], p["photo"], 1200, 630, (170, 104, 96))
        build_post(p)
    build_index(posts)
    return posts


if __name__ == "__main__":
    print([p["slug"] for p in main()])
