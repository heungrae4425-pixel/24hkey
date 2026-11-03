"""지도 경계로 맞닿은 지역(이웃) 계산. 한 번만 실행.
python3 _tools/make_neighbors.py <skorea_municipalities_geo_simple.json> → _tools/neighbors.json
"""
import json, os, re, sys
from shapely.geometry import shape
from shapely.ops import unary_union
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regions import all_regions
src = json.load(open(sys.argv[1], encoding="utf-8"))
by_name = {(r["prov"], r["name"]): r["slug"] for r in all_regions()}
groups = {}
for f in src["features"]:
    c, n = f["properties"]["code"], f["properties"]["name"]
    if c[:2] == "11": k = ("서울", n)
    elif c[:2] == "31": k = ("경기", re.sub(r"^(.+?시).+구$", r"\1", n))
    else: continue
    groups.setdefault(by_name[k], []).append(shape(f["geometry"]))
g = {s: unary_union(v).buffer(0.003) for s, v in groups.items()}
out = {}
for s, a in g.items():
    out[s] = sorted((t for t, b in g.items() if t != s and a.intersects(b)),
                    key=lambda t: -a.intersection(g[t]).area)
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "neighbors.json")
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print({k: len(v) for k, v in out.items()})
