"""예약 글(날짜가 아직 안 된 글)의 썸네일·공유 이미지를 미리 만든다.

매일 아침 자동 공개(GitHub Actions)에서는 글 페이지만 새로 쓰고 사진은 이미 있는 것을 쓰므로,
예약 글을 올린 뒤 한 번 실행해 두면 된다. 이미 있는 이미지는 건너뛴다.
사용: cd _tools && python3 prerender_images.py
"""
import os
import blog
from blog import card, parse, ROOT

img = os.path.join(ROOT, "blog", "img")
pdir = os.path.join(ROOT, "_posts")
n = 0
for f in sorted(os.listdir(pdir)):
    if not f.endswith(".txt"):
        continue
    p = parse(os.path.join(pdir, f))
    if p["date"] <= blog.TODAY:
        continue
    for name, w, h in ((f"{p['slug']}.jpg", 810, 1080), (f"{p['slug']}-og.jpg", 1200, 630)):
        out = os.path.join(img, name)
        if not os.path.exists(out):
            card(out, p["place"], p["photo"], w, h); n += 1
    if p.get("imgset") != "region":
        print("경고: 예약 글에 imgset: region 이 없어 본문 사진이 공개 날 새로 그려집니다:", p["slug"])
print("새로 만든 이미지", n)
