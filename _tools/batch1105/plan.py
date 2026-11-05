"""2026-11-05 배치: 서울 25개 구 x 12 = 300, 경기 글 적은 23개 시·군 동네 200."""
import os, re, sys, json, random, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import regions
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
spec = open(os.path.join(ROOT, "_tools", "POST_SPEC.md"), encoding="utf-8").read()
TOPICS = re.findall(r"^(\d+) ([a-z-]+): (.+)$", spec, re.M)
TOPICS = [(k, d) for _, k, d in TOPICS]
TKEYS = [k for k, _ in TOPICS]

# 개정 로마자 표기 (간단판)
CHO = ["g","kk","n","d","tt","r","m","b","pp","s","ss","","j","jj","ch","k","t","p","h"]
JUNG = ["a","ae","ya","yae","eo","e","yeo","ye","o","wa","wae","oe","yo","u","wo","we","wi","yu","eu","ui","i"]
JONG = ["","k","k","k","n","n","n","t","l","k","m","l","l","l","p","l","m","p","p","t","t","ng","t","t","k","t","p","t"]
def rom(word):
    out = []
    syl = [ord(c) - 0xAC00 for c in word if 0xAC00 <= ord(c) <= 0xD7A3]
    for i, s in enumerate(syl):
        c, j, f = s // 588, (s % 588) // 28, s % 28
        ini = CHO[c]
        if i == 0 and c == 5: ini = "r"
        if i > 0:
            pf = syl[i-1] % 28
            if c == 5 and JONG[pf] in ("l","n"): ini = "l"
        fin = JONG[f]
        if i + 1 < len(syl) and syl[i+1] // 588 == 11 and f:   # 받침 + 모음 연음
            fin = {"k":"g","t":"d","p":"b","l":"r"}.get(fin, fin) if fin != "ng" else "ng"
        if i + 1 < len(syl) and syl[i+1] // 588 == 5 and fin == "n": fin = "l"
        out.append(ini + JUNG[j] + fin)
    return "".join(out)
def stem(d):
    return re.sub(r"(동|읍|면)$", "", d) if len(d) > 2 else d[:-1] if d.endswith("동") else d

posts = []
for f in os.listdir(os.path.join(ROOT, "_posts")):
    if f.endswith(".txt"):
        h = open(os.path.join(ROOT, "_posts", f), encoding="utf-8").read().split("---", 1)[0]
        m = dict(l.split(": ", 1) for l in h.strip().splitlines() if ": " in l); m["slug"] = f[:-4]
        m["topic"] = next((k for k in sorted(TKEYS, key=len, reverse=True) if m["slug"].endswith("-" + k)), "")
        posts.append(m)
used = collections.defaultdict(set)          # (region, place) -> topics
slugroot = {}                                # (region, place) -> romanized
for p in posts:
    used[(p["region"], p["place"])].add(p["topic"])
    if p["topic"]:
        slugroot[(p["region"], p["place"])] = p["slug"][len(p["region"]) + 1: -len(p["topic"]) - 1]

R = regions.all_regions()
random.seed(1105)
plan = []
topic_count = collections.Counter()
def pick(region, place, avoid):
    cands = [k for k in TKEYS if k not in used[(region, place)] and k not in avoid]
    random.shuffle(cands)
    cands.sort(key=lambda k: topic_count[k])
    k = cands[0]; topic_count[k] += 1; used[(region, place)].add(k); return k

THIN = [r for r in R if r["prov"] == "경기" and r["slug"] not in
        ("suwon","yongin","seongnam","hwaseong","anyang","pyeongtaek","gunpo","osan")]
for r in R:
    if r["prov"] != "서울": continue
    ds = r["dongs"]; region_topics = set()
    for i in range(12):
        d = ds[i % len(ds)].split()[-1]
        k = pick(r["slug"], d, region_topics if len(region_topics) < 40 else set()); region_topics.add(k)
        plan.append((r, d, k))
g = []
for r in THIN:
    for d in r["dongs"]:
        d = d.split()[-1]; g.append((r, d, 0 if not used[(r["slug"], d)] else 1))
g.sort(key=lambda x: x[2])
drop = len(g) - 200
# 인구 적은 곳부터 넘치는 만큼 제외
small = ["yeoncheon","gapyeong","dongducheon","yangpyeong","yeoju","pocheon","anseong"]
cut = []
for s in small:
    for x in g[::-1]:
        if len(cut) >= drop: break
        if x[0]["slug"] == s and x[2] == 1 and x not in cut: cut.append(x); break
g = [x for x in g if x not in cut]
extra = {"goyang": ["화정동", "일산동"], "bucheon": ["중동"], "ansan": ["고잔동"], "namyangju": ["다산동"]}
for r in THIN:
    for d in extra.get(r["slug"], []):
        if len(g) < 200: g.append((r, d, 1))
for r, d, _ in g:
    region_topics = {k for (rg, pl), ks in used.items() if rg == r["slug"] for k in ks}
    plan.append((r, d, pick(r["slug"], d, set())))

rows, seen = [], set()
photo = collections.Counter()
for r, d, k in plan:
    root = slugroot.get((r["slug"], d)) or rom(stem(d))
    slug = f"{r['slug']}-{root}-{k}"
    n = 2
    while slug in seen or os.path.exists(os.path.join(ROOT, "_posts", slug + ".txt")):
        slug = f"{r['slug']}-{root}-{k}-{n}"; n += 1
    seen.add(slug)
    photo[r["slug"]] += 1
    ph = (photo[r["slug"]] * 7 + len(r["slug"])) % 20 + 1
    rows.append({"slug": slug, "region": r["slug"], "city": r["name"], "short": r["short"], "place": d,
                 "topic": k, "topic_desc": dict(TOPICS)[k], "photo": ph,
                 "existing_same_place": sorted(t for t in used[(r["slug"], d)] if t != k)})
json.dump(rows, open(os.path.join(os.path.dirname(__file__), "plan.json"), "w"), ensure_ascii=False, indent=1)
print(len(rows), collections.Counter(x["region"].startswith("seoul") for x in rows), len(TKEYS))
print(topic_count.most_common(3), topic_count.most_common()[-3:])
for x in rows[:5] + rows[300:304]: print(x["slug"], x["place"], x["topic"], x["photo"])
print([x["slug"] for x in rows if re.search(r"[^a-z0-9-]", x["slug"])])
