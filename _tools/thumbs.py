"""지역별 검색·공유 썸네일과 지역 페이지 본문 사진.

블로그 썸네일과 같은 스타일 (지역 이름 민트 / 24시 출장열쇠 / 굵은 전화번호).
- assets/og/<slug>.jpg       1200x630  검색·카톡 공유용
- assets/og/<slug>-card.jpg   600x760  지역 페이지 본문 사진
메타 정보 없이 저장 (blog.save_clean).
"""
import os


def make_all(root, regions, tel):
    from blog import card
    od = os.path.join(root, "assets", "og")
    os.makedirs(od, exist_ok=True)
    card(os.path.join(od, "home.jpg"), "서울·경기", 9, 1200, 630)
    for i, r in enumerate(regions):
        label = r["short"]
        card(os.path.join(od, f"{r['slug']}.jpg"), label, i % 20 + 1, 1200, 630)
        card(os.path.join(od, f"{r['slug']}-card.jpg"), label, (i + 7) % 20 + 1, 600, 760,
             shift=(0.3, 0.7, 0.5)[i % 3], bright=(0.6, 0.64, 0.58)[i % 3])
