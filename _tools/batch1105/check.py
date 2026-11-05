"""2026-11-05 배치 검수: 형식·분량·금지어·겹침.
사용: python3 _tools/batch1105/check.py  (저장소 루트에서)"""
import glob, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(ROOT)
plan = json.load(open("_tools/batch1105/plan.json", encoding="utf-8"))
want = {x["slug"]: x for x in plan}

def body_of(t):
    return t.split("\n---\n", 1)[1] if "\n---\n" in t else ""

def grams(s):
    s = re.sub(r"\s", "", s)
    return {s[i:i + 8] for i in range(len(s) - 7)}

all_files = sorted(glob.glob("_posts/*.txt"))
G = {f: grams(body_of(open(f, encoding="utf-8").read())) for f in all_files}

rows, bad = [], []
missing = [s for s in want if not os.path.exists(f"_posts/{s}.txt")]
for s, x in want.items():
    f = f"_posts/{s}.txt"
    if not os.path.exists(f):
        continue
    t = open(f, encoding="utf-8").read()
    head, body = (t.split("\n---\n", 1) + [""])[:2]
    meta = dict(l.split(": ", 1) for l in head.strip().splitlines() if ": " in l)
    n = len(re.sub(r"\s", "", body))
    h2 = len(re.findall(r"^# ", body, re.M))
    pics = len(re.findall(r"^@ ", body, re.M))
    faq = len(re.findall(r"^\? .+ \| .+", body, re.M))
    links = len(re.findall(r"\]\([a-z0-9-]+\.html\)", body))
    issues = []
    for k, v in (("date", "2026-11-05"), ("place", x["place"]), ("region", x["region"]), ("imgset", "region")):
        if meta.get(k) != v: issues.append(f"{k}={meta.get(k)}")
    if not meta.get("title") or x["place"] not in meta.get("title", ""): issues.append("제목에 동네 없음")
    if not (70 <= len(meta.get("desc", "")) <= 130): issues.append(f"desc {len(meta.get('desc',''))}자")
    if not (2600 <= n <= 3500): issues.append(f"분량 {n}")
    if not (12 <= h2 <= 16): issues.append(f"소제목 {h2}")
    if pics != 4: issues.append(f"사진 {pics}")
    if faq != 5: issues.append(f"FAQ {faq}")
    if links < 5: issues.append(f"링크 {links}")
    if f"{x['region']}.html" not in body: issues.append("지역 링크 없음")
    if "010-3664-5455" not in body: issues.append("전화 없음")
    if re.search(r"\d[\d,]*\s*(원|만원|만 원)", t): issues.append("가격 숫자")
    if "만능" in t: issues.append("만능 표기")
    g = G[f]
    top = max(((len(g & G[o]) / max(1, min(len(g), len(G[o]))), o) for o in all_files if o != f), default=(0, ""))
    if top[0] > 0.35: issues.append(f"겹침 {top[0]:.2f} {top[1][7:-4]}")
    rows.append((s, n, round(top[0], 2)))
    if issues: bad.append((s, issues))

print(f"작성됨 {len(rows)}/{len(want)}, 미작성 {len(missing)}, 문제 {len(bad)}")
if rows:
    ns = [r[1] for r in rows]; ov = [r[2] for r in rows]
    print(f"분량 최소 {min(ns)} 평균 {sum(ns)//len(ns)} 최대 {max(ns)} | 겹침 최대 {max(ov)} 평균 {sum(ov)/len(ov):.2f}")
for s, i in bad[:60]:
    print(" ", s, "→", ", ".join(i))
if "-v" in sys.argv and missing:
    print("미작성:", " ".join(missing))
