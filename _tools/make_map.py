"""출장 지역 지도용 SVG 경로 만들기 (한 번만 실행).

원본: southkorea-maps (KOSTAT 2013 시군구 경계, 간략화본)
  https://github.com/southkorea/southkorea-maps
python3 _tools/make_map.py <skorea_municipalities_geo_simple.json>
→ _tools/map_paths.json  (build.py 가 이 파일만 읽는다. shapely 필요 없음)
"""
import json, math, os, re, sys
from shapely.geometry import shape, mapping
from shapely.ops import unary_union

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from regions import all_regions

src = json.load(open(sys.argv[1], encoding="utf-8"))
regions = all_regions()
by_name = {(r["prov"], r["name"]): r["slug"] for r in regions}

groups = {}
for f in src["features"]:
    code, name = f["properties"]["code"], f["properties"]["name"]
    if code[:2] == "11":
        key = ("서울", name)
    elif code[:2] == "31":
        key = ("경기", re.sub(r"^(.+?시).+구$", r"\1", name))
    else:
        continue
    groups.setdefault(key, []).append(shape(f["geometry"]))

geoms = {k: unary_union(v) for k, v in groups.items()}
missing = [k for k in by_name if k not in geoms]
assert not missing, missing


def project(geom_list, width):
    minx = min(g.bounds[0] for g in geom_list); miny = min(g.bounds[1] for g in geom_list)
    maxx = max(g.bounds[2] for g in geom_list); maxy = max(g.bounds[3] for g in geom_list)
    k = math.cos(math.radians((miny + maxy) / 2))
    sx = width / ((maxx - minx) * k)
    height = (maxy - miny) * sx
    return (lambda x, y: ((x - minx) * k * sx, (maxy - y) * sx)), round(height)


def path_of(geom, P, tol):
    g = geom.simplify(tol, preserve_topology=True)
    polys = [g] if g.geom_type == "Polygon" else list(g.geoms)
    parts = []
    for poly in polys:
        for ring in [poly.exterior] + list(poly.interiors):
            pts = [P(x, y) for x, y in ring.coords]
            if len(pts) < 4:
                continue
            parts.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + "Z")
    return "".join(parts)


def label_pt(geom, P):
    p = geom.representative_point()
    x, y = P(p.x, p.y)
    return round(x, 1), round(y, 1)


out = {}
# 경기 지도: 31개 시·군 + 서울 전체(한 덩어리)
gg = {k: v for k, v in geoms.items() if k[0] == "경기"}
seoul_all = unary_union([v for k, v in geoms.items() if k[0] == "서울"])
P, H = project(list(gg.values()), 800)
out["gyeonggi"] = {"w": 800, "h": H, "seoul": {"d": path_of(seoul_all, P, 0.002), "pt": label_pt(seoul_all, P)},
                   "items": [{"slug": by_name[k], "d": path_of(g, P, 0.002), "pt": label_pt(g, P)} for k, g in gg.items()]}
# 서울 지도: 25개 구
se = {k: v for k, v in geoms.items() if k[0] == "서울"}
P, H = project(list(se.values()), 800)
out["seoul"] = {"w": 800, "h": H,
                "items": [{"slug": by_name[k], "d": path_of(g, P, 0.0006), "pt": label_pt(g, P)} for k, g in se.items()]}

dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "map_paths.json")
json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False)
print(dst, os.path.getsize(dst), "bytes", out["gyeonggi"]["h"], out["seoul"]["h"])
