"""2026-11-06~11-30 예약 배치: 서울 25개 구 x 10 = 250, 경기 글 적은 23개 시·군 250. 하루 20편씩 날짜 배정."""
import os, sys, json, random, collections, datetime
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "batch1105"))
sys.argv = [sys.argv[0]]
import importlib.util
spec = importlib.util.spec_from_file_location("p1", os.path.join(HERE, "..", "batch1105", "plan.py"))
# 1차 계획 모듈의 로마자·주제 도구만 재사용 (실행 시 plan.json 을 다시 쓰므로 소스를 잘라 읽음)
src = open(os.path.join(HERE, "..", "batch1105", "plan.py"), encoding="utf-8").read().split("R = regions.all_regions()")[0]
ns = {"__file__": os.path.join(HERE, "..", "batch1105", "plan.py")}
exec(src, ns)
TKEYS, TOPICS, used, slugroot, rom, stem, ROOT = ns["TKEYS"], ns["TOPICS"], ns["used"], ns["slugroot"], ns["rom"], ns["stem"], ns["ROOT"]
import regions
R = regions.all_regions()
random.seed(1106)
tc = collections.Counter()
def pick(region, place):
    c = [k for k in TKEYS if k not in used[(region, place)]]
    random.shuffle(c); c.sort(key=lambda k: tc[k])
    k = c[0]; tc[k] += 1; used[(region, place)].add(k); return k

plan = []
for r in R:
    if r["prov"] != "서울": continue
    ds = r["dongs"]
    # 1차에서 덜 쓴 동네부터
    order = sorted(ds, key=lambda d: (len(used[(r["slug"], d.split()[-1])]), ds.index(d)))
    for i in range(10):
        d = order[i % len(order)].split()[-1]
        plan.append((r, d, pick(r["slug"], d)))
BIG = ["goyang","bucheon","ansan","namyangju","siheung","paju","uijeongbu","gimpo","gwangju","hanam","guri","gwangmyeong","icheon","yangju"]
THIN = [r for r in R if r["prov"] == "경기" and r["slug"] not in ("suwon","yongin","seongnam","hwaseong","anyang","pyeongtaek","gunpo","osan")]
g = [(r, d.split()[-1]) for r in THIN for d in r["dongs"]]
g.sort(key=lambda x: len(used[(x[0]["slug"], x[1])]))
gg = g[:]
extra = [(r, d.split()[-1]) for s in BIG for r in THIN if r["slug"] == s for d in r["dongs"]]
i = 0
while len(gg) < 250:
    gg.append(extra[i % len(extra)]); i += 1
gg = gg[:250]
for r, d in gg:
    plan.append((r, d, pick(r["slug"], d)))

rows, seen, photo = [], set(), collections.Counter()
for r, d, k in plan:
    root = slugroot.get((r["slug"], d)) or rom(stem(d))
    slug = f"{r['slug']}-{root}-{k}"; n = 2
    while slug in seen or os.path.exists(os.path.join(ROOT, "_posts", slug + ".txt")):
        slug = f"{r['slug']}-{root}-{k}-{n}"; n += 1
    seen.add(slug); photo[r["slug"]] += 1
    rows.append({"slug": slug, "region": r["slug"], "city": r["name"], "short": r["short"], "place": d,
                 "topic": k, "topic_desc": dict(TOPICS)[k], "photo": (photo[r["slug"]] * 7 + len(r["slug"]) + 3) % 20 + 1,
                 "existing_same_place": sorted(t for t in used[(r["slug"], d)] if t != k)})
# 날짜: 서울·경기를 섞어 하루 20편씩, 같은 날 한 지역에 몰리지 않게 지역별로 번갈아
by = collections.defaultdict(list)
for x in rows: by[x["region"]].append(x)
queue = []
while any(by.values()):
    for k in sorted(by, key=lambda k: -len(by[k])):
        if by[k]: queue.append(by[k].pop(0))
start = datetime.date(2026, 11, 6)
for i, x in enumerate(queue):
    x["date"] = (start + datetime.timedelta(days=i // 20)).isoformat()
json.dump(queue, open(os.path.join(HERE, "plan.json"), "w"), ensure_ascii=False, indent=1)
print(len(queue), len({x["slug"] for x in queue}), collections.Counter(x["region"].startswith("seoul") for x in queue), queue[0]["date"], queue[-1]["date"])
print(tc.most_common(2), tc.most_common()[-2:])
print([x["slug"] for x in queue if x["slug"][-2:-1] == "-"][:5])
