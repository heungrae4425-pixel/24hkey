"""지역별 검색·공유 썸네일 (og:image) 생성.

실제 작업 사진을 어둡게 깔고 가운데에
  지역 이름 (노랑, 검정 테두리)
  24시 출장열쇠 (흰색, 검정 테두리)
  전화번호 (흰색, 검정 테두리)
를 크게 넣는다. 1200x630 (구글·네이버·카카오 공유 표준 크기).
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
W, H = 1200, 630
HERE = os.path.dirname(os.path.abspath(__file__))


def font(size):
    return ImageFont.truetype(FONT, size, index=1)  # index 1 = 한국어


def fit(draw, text, size, max_w):
    f = font(size)
    while draw.textlength(text, font=f) > max_w and size > 40:
        size -= 6
        f = font(size)
    return f


def make(out, title, tel, bg_no):
    bg = Image.open(os.path.join(HERE, "thumb_bg", f"bg{bg_no:02d}.jpg")).convert("RGB")
    s = W / bg.width
    bg = bg.resize((W, int(bg.height * s)), Image.LANCZOS)
    top = (bg.height - H) // 2
    im = ImageEnhance.Brightness(bg.crop((0, top, W, top + H))).enhance(0.48)
    d = ImageDraw.Draw(im)
    lines = [(title, 168, "#ffd400", 12), ("24시 출장열쇠", 104, "#ffffff", 9), (tel, 112, "#ffffff", 9)]
    fonts = [fit(d, t, sz, W - 120) for t, sz, _, _ in lines]
    heights = [f.getbbox(t)[3] - f.getbbox(t)[1] for (t, *_), f in zip(lines, fonts)]
    gap = 34
    y = (H - sum(heights) - gap * 2) // 2
    for (text, _, color, stroke), f, h in zip(lines, fonts, heights):
        bb = f.getbbox(text)
        x = (W - (bb[2] - bb[0])) // 2 - bb[0]
        d.text((x, y - bb[1]), text, font=f, fill=color, stroke_width=stroke, stroke_fill="#111111")
        y += h + gap
    im.save(out, quality=82, optimize=True)


def make_all(root, regions, tel):
    od = os.path.join(root, "assets", "og")
    os.makedirs(od, exist_ok=True)
    make(os.path.join(od, "home.jpg"), "서울·경기", tel, 9)
    for i, r in enumerate(regions):
        make(os.path.join(od, f"{r['slug']}.jpg"), r["name"], tel, i % 20 + 1)
