"""글 하나가 다른 글과 문장이 얼마나 겹치는지 확인 (8글자 단위, 공백 제외).
사용: python3 _tools/overlap_check.py _posts/글.txt [...]   → 겹침이 큰 상대 글 5개를 보여준다.
기준: 0.35 이하가 되게 쓴다."""
import glob, re, sys

def grams(p):
    s = re.sub(r"\s", "", open(p, encoding="utf-8").read().split("---", 1)[1])
    return {s[i:i + 8] for i in range(len(s) - 7)}

files = sorted(glob.glob("_posts/*.txt"))
G = {f: grams(f) for f in files}
for t in sys.argv[1:]:
    t = t if t.startswith("_posts/") else "_posts/" + t
    g = G.get(t) or grams(t)
    r = sorted(((len(g & G[f]) / min(len(g), len(G[f])), f) for f in files if f != t), reverse=True)[:5]
    print(t, " | ".join(f"{s:.2f} {f[7:-4]}" for s, f in r))
