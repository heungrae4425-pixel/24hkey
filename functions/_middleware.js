// 24시출장열쇠 서버 기능 (Cloudflare Pages Functions)
// - /admin : 아이디·비밀번호 로그인, 방문 통계, 블로그 글 수
// - 모든 페이지 : 방문 기록(D1), 내부 파일 차단
//
// Cloudflare 설정 (Pages 프로젝트 24hkey → 설정):
//   바인딩   D1 데이터베이스  변수 이름 DB
//   변수     ADMIN_USER (아이디), ADMIN_PASS (비밀번호, "암호화" 선택)
// 아이디·비밀번호는 코드에 넣지 않는다 (저장소가 공개라서).

const BLOCKED = [/^\/_posts(\/|$)/, /^\/_tools(\/|$)/, /^\/functions(\/|$)/, /^\/blog\/posts\.json$/];
const COOKIE = "hk_admin";
const SESSION_DAYS = 7;

export async function onRequest(ctx) {
  const { request, env } = ctx;
  const url = new URL(request.url);
  const path = url.pathname;

  if (path === "/admin" || path.startsWith("/admin/")) return admin(ctx, url);
  if (path === "/api/event" && request.method === "POST") return recordEvent(ctx, request);
  if (BLOCKED.some((r) => r.test(path))) return notFound(ctx, url);

  const res = await ctx.next();
  const type = res.headers.get("content-type") || "";
  if (type.includes("text/html") && request.method === "GET" && res.status === 200 && !(await authed(request, env))) {
    ctx.waitUntil(logHit(env, request, url));
  }
  return res;
}

// ---------------- 공통 ----------------
async function notFound(ctx, url) {
  const r = await ctx.env.ASSETS.fetch(new URL("/404.html", url));
  return new Response(r.body, { status: 404, headers: { "content-type": "text/html; charset=utf-8" } });
}

function kstDay(offsetDays = 0) {
  const d = new Date(Date.now() + 9 * 3600e3 - offsetDays * 86400e3);
  return d.toISOString().slice(0, 10);
}

let schemaReady = false;
async function db(env) {
  if (!env.DB) return null;
  if (!schemaReady) {
    await env.DB.batch([
      env.DB.prepare("CREATE TABLE IF NOT EXISTS hits (day TEXT, path TEXT, n INTEGER, PRIMARY KEY(day, path))"),
      env.DB.prepare("CREATE TABLE IF NOT EXISTS visits (day TEXT, vid TEXT, hour INTEGER, country TEXT, region TEXT, city TEXT, device TEXT, ref TEXT, landing TEXT, kind TEXT, org TEXT, PRIMARY KEY(day, vid))"),
      env.DB.prepare("CREATE TABLE IF NOT EXISTS events (day TEXT, kind TEXT, page TEXT, label TEXT, n INTEGER, PRIMARY KEY(day, kind, page, label))"),
      env.DB.prepare("CREATE TABLE IF NOT EXISTS keywords (day TEXT, kw TEXT, n INTEGER, PRIMARY KEY(day, kw))"),
    ]);
    // 해외 접속은 손님이 아니므로 방문자에서 뺀다 (이전 기록도 같이 정리)
    try { await env.DB.prepare("UPDATE visits SET kind = 'foreign' WHERE kind = 'person' AND country != '' AND country != 'KR'").run(); } catch {}
    schemaReady = true;
  }
  return env.DB;
}

async function sha(text) {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

// ---------------- 방문 기록 ----------------
const REGION_KO = { "Seoul": "서울", "Gyeonggi-do": "경기", "Incheon": "인천", "Busan": "부산", "Daegu": "대구", "Daejeon": "대전",
  "Gwangju": "광주", "Ulsan": "울산", "Sejong": "세종", "Gangwon-do": "강원", "Gangwon": "강원", "Chungcheongbuk-do": "충북",
  "Chungcheongnam-do": "충남", "Jeollabuk-do": "전북", "Jeonbuk": "전북", "Jeollanam-do": "전남", "Gyeongsangbuk-do": "경북",
  "Gyeongsangnam-do": "경남", "Jeju-do": "제주" };
const CITY_KO = { "Seoul": "서울", "Suwon": "수원", "Seongnam": "성남", "Goyang": "고양", "Yongin": "용인", "Bucheon": "부천", "Ansan": "안산",
  "Anyang": "안양", "Namyangju": "남양주", "Hwaseong": "화성", "Pyeongtaek": "평택", "Uijeongbu": "의정부", "Siheung": "시흥", "Paju": "파주",
  "Gimpo": "김포", "Gwangmyeong": "광명", "Gwangju": "광주", "Hanam": "하남", "Gunpo": "군포", "Osan": "오산", "Icheon": "이천", "Yangju": "양주",
  "Guri": "구리", "Anseong": "안성", "Pocheon": "포천", "Uiwang": "의왕", "Yeoju": "여주", "Dongducheon": "동두천", "Gwacheon": "과천",
  "Incheon": "인천", "Ilsan": "일산", "Bundang": "분당", "Gangnam-gu": "강남구", "Songpa-gu": "송파구", "Mapo-gu": "마포구" };

function device(ua) {
  if (/iPad|Tablet|Tab/i.test(ua)) return "태블릿";
  if (/Mobi|Android|iPhone/i.test(ua)) return "휴대폰";
  return "PC";
}

function keyword(ref) {
  try {
    const u = new URL(ref), h = u.host;
    const q = /naver\./.test(h) ? u.searchParams.get("query") : /daum\.|kakao/.test(h) ? u.searchParams.get("q") : /bing\.|google\./.test(h) ? u.searchParams.get("q") : null;
    return q ? q.trim().slice(0, 60) : null;
  } catch { return null; }
}

const BOT_UA = /bot|crawl|spider|slurp|preview|monitor|curl|wget|python|httpx|okhttp|java\/|go-http|node-fetch|axios|scrapy|headless|phantom|puppeteer|playwright|lighthouse|yeti|daumoa|facebookexternalhit|bingpreview|ahrefs|semrush|mj12|dotbot|petalbot|bytespider|gptbot|claudebot|ccbot|perplexity/i;
const DC_ORG = /amazon|aws|google|microsoft|azure|digitalocean|ovh|hetzner|linode|akamai|alibaba|aliyun|tencent|oracle|vultr|choopa|contabo|leaseweb|m247|datacamp|cdn77|scaleway|ionos|hostinger|colocrossing|psychz|servers\.com|g-core|gcore|cloudflare|fastly|hostwinds|kamatera|zenlayer|cogent|ucloud|huawei|baidu|byteplus|bytedance|data ?cent|hosting|server|cloud|vps/i;
function botName(ua) {
  const m = ua.match(/([A-Za-z][\w.-]*?(?:bot|crawler|spider))\b/i) || ua.match(/(Yeti|Daumoa|facebookexternalhit|HeadlessChrome|python-requests|curl|Wget|Go-http-client|okhttp|Lighthouse)/i);
  return m ? m[1] : "기타 자동 프로그램";
}
function classify(ua, cf) {
  if (!ua || BOT_UA.test(ua)) return { kind: "bot", org: ua ? botName(ua) : "UA 없음" };
  const org = String(cf.asOrganization || "");
  if (DC_ORG.test(org)) return { kind: "bot", org: org.slice(0, 60) };
  return { kind: "person", org: org.slice(0, 60) };
}

function refName(ref, host) {
  if (!ref) return "직접 방문";
  let h;
  try { h = new URL(ref).host.replace(/^www\./, ""); } catch { return null; }
  if (h === host || h.endsWith("xn--24-ji5jp6afzih4cnup.kr") || h.endsWith("pages.dev")) return null;
  if (/naver\./.test(h)) return "네이버";
  if (/google\./.test(h)) return "구글";
  if (/daum\.|kakao/.test(h)) return "다음·카카오";
  if (/bing\./.test(h)) return "빙";
  if (/instagram|facebook|fb\./.test(h)) return "인스타그램·페이스북";
  return h;
}

async function logHit(env, request, url) {
  try {
    const ua = request.headers.get("user-agent") || "";
    const d = await db(env);
    if (!d) return;
    const day = kstDay();
    const hour = new Date(Date.now() + 9 * 3600e3).getUTCHours();
    let path = url.pathname.replace(/\.html$/, "").replace(/\/index$/, "/");
    try { path = decodeURIComponent(path); } catch {}
    const ip = request.headers.get("cf-connecting-ip") || "";
    const vid = (await sha(ip + "|" + ua + "|" + day)).slice(0, 20);
    const cf = request.cf || {};
    let { kind, org } = classify(ua, cf);
    // 출장 지역 손님은 한국에만 있으므로 해외 접속은 방문자·조회·검색어 집계에서 뺀다
    if (kind === "person" && cf.country && cf.country !== "KR") kind = "foreign";
    const refHdr = request.headers.get("referer");
    const ref = refName(refHdr, url.host);
    const visit = d.prepare("INSERT OR IGNORE INTO visits (day, vid, hour, country, region, city, device, ref, landing, kind, org) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")
      .bind(day, vid, hour, cf.country || "", REGION_KO[cf.region] || cf.region || "", CITY_KO[cf.city] || cf.city || "", device(ua), ref || "사이트 내 이동", path, kind, org);
    if (kind !== "person") { await visit.run(); return; }
    const stmts = [
      d.prepare("INSERT INTO hits (day, path, n) VALUES (?, ?, 1) ON CONFLICT(day, path) DO UPDATE SET n = n + 1").bind(day, path),
      visit,
    ];
    const kw = refHdr ? keyword(refHdr) : null;
    if (kw) stmts.push(d.prepare("INSERT INTO keywords (day, kw, n) VALUES (?, ?, 1) ON CONFLICT(day, kw) DO UPDATE SET n = n + 1").bind(day, kw));
    await d.batch(stmts);
  } catch {}
}

// 전화 버튼 클릭 기록 (assets/main.js 에서 전송)
async function recordEvent(ctx, request) {
  try {
    if (await authed(request, ctx.env)) return new Response(null, { status: 204 });
    const body = await request.json();
    if (body.kind !== "call") return new Response(null, { status: 204 });
    let page = String(body.page || "").slice(0, 200).replace(/\.html$/, "");
    try { page = decodeURIComponent(page); } catch {}
    const label = String(body.label || "기타").slice(0, 40);
    const d = await db(ctx.env);
    if (d) await d.prepare("INSERT INTO events (day, kind, page, label, n) VALUES (?, 'call', ?, ?, 1) ON CONFLICT(day, kind, page, label) DO UPDATE SET n = n + 1")
      .bind(kstDay(), page, label).run();
  } catch {}
  return new Response(null, { status: 204 });
}

// ---------------- 로그인 ----------------
async function sign(value, env) {
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode("hk24|" + (env.ADMIN_USER || "") + "|" + (env.ADMIN_PASS || "")),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(value));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function authed(request, env) {
  if (!env.ADMIN_PASS) return false;
  const c = (request.headers.get("cookie") || "").match(new RegExp(COOKIE + "=([^;]+)"));
  if (!c) return false;
  const [exp, sig] = decodeURIComponent(c[1]).split(".");
  if (!exp || !sig || Number(exp) < Date.now()) return false;
  return (await sign(exp, env)) === sig;
}

function same(a, b) {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

// ---------------- 관리자 ----------------
async function admin(ctx, url) {
  const { request, env } = ctx;
  const path = url.pathname.replace(/\/$/, "") || "/admin";
  const headers = { "content-type": "text/html; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex" };

  if (!env.ADMIN_PASS || !env.ADMIN_USER) {
    return new Response(page("설정 필요", `<div class="card"><h2>관리자 설정이 아직 안 되었습니다</h2>
      <p>Cloudflare Pages 프로젝트(24hkey) → 설정 → 변수 및 비밀에 <b>ADMIN_USER</b>, <b>ADMIN_PASS</b>를 추가한 뒤 다시 배포하세요.</p></div>`), { headers });
  }

  if (path === "/admin/login" && request.method === "POST") {
    const f = await request.formData();
    const ok = same(String(f.get("id") || ""), env.ADMIN_USER) && same(String(f.get("pw") || ""), env.ADMIN_PASS);
    if (!ok) {
      await new Promise((r) => setTimeout(r, 800));
      return new Response(loginPage("아이디 또는 비밀번호가 맞지 않습니다."), { status: 401, headers });
    }
    const exp = String(Date.now() + SESSION_DAYS * 86400e3);
    const val = encodeURIComponent(exp + "." + (await sign(exp, env)));
    return new Response(null, { status: 303, headers: {
      location: "/admin", "set-cookie": `${COOKIE}=${val}; Path=/; Max-Age=${SESSION_DAYS * 86400}; HttpOnly; Secure; SameSite=Strict`,
    } });
  }
  if (path === "/admin/logout") {
    return new Response(null, { status: 303, headers: { location: "/admin", "set-cookie": `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Strict` } });
  }
  if (!(await authed(request, env))) return new Response(loginPage(""), { headers });

  const d = await db(env).catch(() => null);
  return new Response(await dashboard(ctx, url, d), { headers });
}

function esc(s) { return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c])); }

function table(rows, cols, empty = "아직 기록이 없습니다") {
  if (!rows.length) return `<p class="muted">${empty}</p>`;
  const head = `<tr>${cols.map((c) => `<th class="${c.n ? "n" : ""}">${c.t}</th>`).join("")}</tr>`;
  return `<table>${head}${rows.map((r) => `<tr>${cols.map((c) => `<td class="${c.n ? "n" : ""}">${c.f ? c.f(r) : esc(r[c.k] ?? "")}</td>`).join("")}</tr>`).join("")}</table>`;
}

function hbars(rows, key, val, max) {
  const m = Math.max(1, max ?? Math.max(...rows.map((r) => r[val])));
  return rows.map((r) => `<div class="hb"><span class="hb-l">${r.html || esc(r[key] || "알 수 없음")}</span><span class="hb-b"><i style="width:${(r[val] / m) * 100}%"></i></span><span class="hb-n">${r[val]}</span></div>`).join("") || `<p class="muted">아직 기록이 없습니다</p>`;
}

async function blogData(ctx, url) {
  try { return await (await ctx.env.ASSETS.fetch(new URL("/blog/posts.json", url))).json(); } catch { return { posts: [], regions: [] }; }
}

async function postsTab(ctx, url, d) {
  const { posts, regions } = await blogData(ctx, url);
  const byRegion = {};
  posts.forEach((p) => { (byRegion[p.region] = byRegion[p.region] || []).push(p); });
  const today = kstDay();
  const last7 = posts.filter((p) => p.date >= kstDay(6)).length;
  const last30 = posts.filter((p) => p.date >= kstDay(29)).length;
  const covered = regions.filter((r) => byRegion[r.slug]).length;

  // 글별 조회수 (최근 30일)
  let views = {};
  if (d) {
    const rows = (await d.prepare("SELECT path, SUM(n) n FROM hits WHERE day >= ? AND path LIKE '/blog/%' GROUP BY path").bind(kstDay(29)).all()).results;
    rows.forEach((r) => { views[r.path.replace(/^\/blog\//, "")] = r.n; });
  }

  const provBlock = (prov) => {
    const rs = regions.filter((r) => r.prov === prov);
    const n = rs.reduce((a, r) => a + (byRegion[r.slug] || []).length, 0);
    const rows = rs.map((r) => ({ html: `<a href="/${r.slug}" target="_blank">${esc(r.name)}</a>`, c: (byRegion[r.slug] || []).length }))
      .sort((a, b) => b.c - a.c);
    return `<div class="card"><h2>${prov} · ${n}편 <span class="muted">(${rs.filter((r) => byRegion[r.slug]).length}/${rs.length}개 지역)</span></h2>${hbars(rows, "", "c", Math.max(1, ...rows.map((x) => x.c)))}</div>`;
  };
  const empty = regions.filter((r) => !byRegion[r.slug]).map((r) => `<span class="chip">${esc(r.name)}</span>`).join("");
  const list = [...posts].sort((a, b) => (b.date + b.slug).localeCompare(a.date + a.slug));
  const months = {};
  posts.forEach((p) => { months[p.date.slice(0, 7)] = (months[p.date.slice(0, 7)] || 0) + 1; });
  const monthRows = Object.entries(months).sort((a, b) => b[0].localeCompare(a[0])).map(([m, n]) => ({ m, n }));

  return `
    <div class="stats">
      <div class="card stat"><small>전체 블로그 글</small><b>${posts.length}</b><small>편</small></div>
      <div class="card stat"><small>최근 7일 작성</small><b class="accent">${last7}</b><small>최근 30일 ${last30}편</small></div>
      <div class="card stat"><small>글이 있는 지역</small><b>${covered}</b><small>전체 ${regions.length}개 지역 중</small></div>
      <div class="card stat"><small>글이 없는 지역</small><b>${regions.length - covered}</b><small>아래 목록 참고</small></div>
    </div>
    <div class="grid2">${provBlock("서울")}${provBlock("경기")}</div>
    <div class="card"><h2>아직 글이 없는 지역 (${regions.length - covered})</h2><div class="chips">${empty || '<span class="muted">모든 지역에 글이 있습니다</span>'}</div></div>
    <div class="grid2">
      <div class="card"><h2>월별 작성 수</h2>${table(monthRows, [{ t: "월", k: "m" }, { t: "글 수", k: "n", n: 1 }])}</div>
      <div class="card"><h2>최근 30일 조회 많은 글</h2>${table(list.filter((p) => views[p.slug]).sort((a, b) => views[b.slug] - views[a.slug]).slice(0, 10),
        [{ t: "글", f: (p) => `<a href="/blog/${esc(p.slug)}" target="_blank">${esc(p.title)}</a>` }, { t: "조회", f: (p) => views[p.slug] || 0, n: 1 }], "아직 조회 기록이 없습니다")}</div>
    </div>
    <div class="card"><h2>전체 글 목록 (${posts.length})</h2>${table(list, [
      { t: "날짜", k: "date" },
      { t: "지역", f: (p) => esc((regions.find((r) => r.slug === p.region) || {}).name || p.region) },
      { t: "동네", k: "place" },
      { t: "제목", f: (p) => `<a href="/blog/${esc(p.slug)}" target="_blank">${esc(p.title)}</a>` },
      { t: "조회(30일)", f: (p) => views[p.slug] || 0, n: 1 },
    ], "아직 글이 없습니다")}</div>`;
}

// ---------------- 페이지 조회 ----------------
// 기간(오늘·어제·7일·30일·직접 날짜)과 종류(전체·블로그·지역·기타)를 골라 사람이 본 페이지를 조회수 순으로 보여 줍니다.
async function pagesTab(ctx, url, d) {
  const today = kstDay();
  const P = url.searchParams;
  const range = ["today", "yesterday", "7", "30", "day"].includes(P.get("range")) ? P.get("range") : "7";
  let from, to;
  if (range === "today") from = to = today;
  else if (range === "yesterday") from = to = kstDay(1);
  else if (range === "day") { from = to = /^\d{4}-\d{2}-\d{2}$/.test(P.get("day") || "") ? P.get("day") : today; }
  else { from = kstDay(Number(range) - 1); to = today; }
  const kind = ["all", "blog", "region", "etc"].includes(P.get("kind")) ? P.get("kind") : "all";
  const qtext = (P.get("q") || "").trim().slice(0, 60);

  const [{ posts, regions }, rows, landRows, callRows] = await Promise.all([
    blogData(ctx, url),
    d.prepare("SELECT path, SUM(n) n, COUNT(DISTINCT day) days FROM hits WHERE day BETWEEN ? AND ? GROUP BY path").bind(from, to).all().then((r) => r.results),
    d.prepare("SELECT landing path, COUNT(*) v FROM visits WHERE kind = 'person' AND day BETWEEN ? AND ? GROUP BY landing").bind(from, to).all().then((r) => r.results),
    d.prepare("SELECT page path, SUM(n) c FROM events WHERE kind = 'call' AND day BETWEEN ? AND ? GROUP BY page").bind(from, to).all().then((r) => r.results),
  ]);
  const title = {};
  posts.forEach((p) => { title["/blog/" + p.slug] = p.title; });
  regions.forEach((r) => { title["/" + r.slug] = r.name + " 지역 페이지"; });
  Object.assign(title, { "/": "홈", "/blog/": "블로그 목록", "/blog": "블로그 목록" });
  const norm = (p) => (p || "").replace(/\.html$/, "").replace(/\/index$/, "/");
  const land = {}, call = {};
  landRows.forEach((r) => { land[norm(r.path)] = (land[norm(r.path)] || 0) + r.v; });
  callRows.forEach((r) => { call[norm(r.path)] = (call[norm(r.path)] || 0) + r.c; });
  const regionSet = new Set(regions.map((r) => "/" + r.slug));
  const typeOf = (p) => (p.startsWith("/blog/") && p.length > 6 && !p.startsWith("/blog/page/") ? "blog" : regionSet.has(p) ? "region" : "etc");

  let list = rows.map((r) => ({ ...r, path: norm(r.path) }))
    .map((r) => ({ ...r, type: typeOf(r.path), t: title[r.path] || "", land: land[r.path] || 0, call: call[r.path] || 0 }));
  const total = list.reduce((a, r) => a + r.n, 0);
  const cnt = { blog: 0, region: 0, etc: 0 };
  list.forEach((r) => { cnt[r.type] += r.n; });
  const viewedBlog = new Set(list.filter((r) => r.type === "blog").map((r) => r.path));
  if (kind !== "all") list = list.filter((r) => r.type === kind);
  if (qtext) list = list.filter((r) => r.path.includes(qtext) || r.t.includes(qtext));
  list.sort((a, b) => b.n - a.n || a.path.localeCompare(b.path));

  const link = (o) => { const q = new URLSearchParams({ tab: "pages", range, kind, ...(range === "day" ? { day: from } : {}), ...(qtext ? { q: qtext } : {}), ...o }); return "/admin?" + q; };
  const rBtn = (k, label) => `<a class="pill ${range === k ? "on" : ""}" href="${link({ range: k })}">${label}</a>`;
  const kBtn = (k, label, n) => `<a class="pill ${kind === k ? "on" : ""}" href="${link({ kind: k })}">${label} <b>${n}</b></a>`;
  const shown = list.slice(0, 500);
  const label = { blog: "블로그", region: "지역", etc: "기타" };

  return `
    <div class="card">
      <div class="pills">${rBtn("today", "오늘")}${rBtn("yesterday", "어제")}${rBtn("7", "최근 7일")}${rBtn("30", "최근 30일")}
        <form method="get" action="/admin" class="inl"><input type="hidden" name="tab" value="pages"><input type="hidden" name="range" value="day"><input type="hidden" name="kind" value="${kind}">
          <input type="date" name="day" value="${range === "day" ? from : ""}" max="${today}" onchange="this.form.submit()"></form></div>
      <div class="pills" style="margin-top:10px">${kBtn("all", "전체", total)}${kBtn("blog", "블로그 글", cnt.blog)}${kBtn("region", "지역 페이지", cnt.region)}${kBtn("etc", "기타", cnt.etc)}
        <form method="get" action="/admin" class="inl"><input type="hidden" name="tab" value="pages"><input type="hidden" name="range" value="${range}"><input type="hidden" name="kind" value="${kind}">${range === "day" ? `<input type="hidden" name="day" value="${from}">` : ""}
          <input name="q" value="${esc(qtext)}" placeholder="주소·제목 검색"><button>검색</button></form></div>
      <p class="muted" style="margin-top:10px">${from === to ? from : from + " ~ " + to} · 조회 ${total}회 · 페이지 ${rows.length}개 · 사람이 본 것만 셉니다 (봇·해외·관리자 제외)</p>
    </div>
    <div class="card"><h2>조회한 페이지 (${list.length}${list.length > 500 ? ", 상위 500개만 표시" : ""})</h2>${table(shown, [
      { t: "종류", f: (r) => label[r.type] },
      { t: "페이지", f: (r) => `<a href="${esc(r.path)}" target="_blank">${esc(r.t || r.path)}</a>${r.t ? `<div class="muted">${esc(r.path)}</div>` : ""}` },
      { t: "조회", k: "n", n: 1 },
      { t: "첫 방문", f: (r) => r.land || "", n: 1 },
      { t: "전화", f: (r) => r.call ? `<b class="accent">${r.call}</b>` : "", n: 1 },
      { t: "조회한 날", k: "days", n: 1 },
    ], "이 기간에 조회 기록이 없습니다")}
    <p class="muted" style="margin-top:8px">첫 방문: 이 페이지로 처음 들어온 방문자 수 · 전화: 이 페이지에서 누른 전화 버튼 수</p></div>
    ${kind === "blog" || kind === "all" ? `<div class="card"><h2>이 기간에 조회가 없는 블로그 글 <span class="muted">(${posts.filter((p) => !viewedBlog.has("/blog/" + p.slug)).length}편)</span></h2>
      <p class="muted">검색이나 다른 페이지에서 아직 들어오지 않은 글입니다. 최근 글부터 30편만 표시합니다.</p>
      ${table(posts.filter((p) => !viewedBlog.has("/blog/" + p.slug)).sort((a, b) => b.date.localeCompare(a.date)).slice(0, 30),
        [{ t: "날짜", k: "date" }, { t: "제목", f: (p) => `<a href="/blog/${esc(p.slug)}" target="_blank">${esc(p.title)}</a>` }], "모든 글이 조회됐습니다")}</div>` : ""}`;
}

async function dashboard(ctx, url, d) {
  const today = kstDay();
  let day = url.searchParams.get("day") || today;
  if (!/^\d{4}-\d{2}-\d{2}$/.test(day)) day = today;
  const tab = ["posts", "pages"].includes(url.searchParams.get("tab")) ? url.searchParams.get("tab") : "stats";

  let body;
  if (tab === "posts") {
    body = await postsTab(ctx, url, d);
  } else if (tab === "pages" && d) {
    body = await pagesTab(ctx, url, d);
  } else if (!d) {
    body = `<div class="card warn">트래픽 기록용 D1 데이터베이스가 연결되지 않았습니다. Pages 설정 → 바인딩에서 D1(변수 이름 <b>DB</b>)을 연결하세요.</div>`;
  } else {
    const from14 = kstDay(13);
    const q = (sql, ...b) => d.prepare(sql).bind(...b).all().then((r) => r.results);
    const [vDays, hDays, cDays, mDays, geoR, geoC, devs, hours, refs, kws, pages, calls, callPages, bDays, botOrgs, lands, personOrgs] = await Promise.all([
      q("SELECT day, COUNT(*) v FROM visits WHERE kind = 'person' AND day >= ? GROUP BY day", from14),
      q("SELECT day, SUM(n) h FROM hits WHERE day >= ? GROUP BY day", from14),
      q("SELECT day, SUM(n) c FROM events WHERE kind = 'call' AND day >= ? GROUP BY day", from14),
      q("SELECT day, SUM(device = '휴대폰') m FROM visits WHERE kind = 'person' AND day >= ? GROUP BY day", from14),
      q("SELECT region, COUNT(*) v FROM visits WHERE kind = 'person' AND day = ? GROUP BY region ORDER BY v DESC LIMIT 12", day),
      q("SELECT region, city, COUNT(*) v FROM visits WHERE kind = 'person' AND day = ? GROUP BY region, city ORDER BY v DESC LIMIT 20", day),
      q("SELECT device, COUNT(*) v FROM visits WHERE kind = 'person' AND day = ? GROUP BY device ORDER BY v DESC", day),
      q("SELECT hour, COUNT(*) v FROM visits WHERE kind = 'person' AND day = ? GROUP BY hour", day),
      q("SELECT ref, COUNT(*) v FROM visits WHERE kind = 'person' AND day = ? GROUP BY ref ORDER BY v DESC LIMIT 12", day),
      q("SELECT kw, SUM(n) n FROM keywords WHERE day >= ? GROUP BY kw ORDER BY n DESC LIMIT 15", kstDay(6)),
      q("SELECT path, n FROM hits WHERE day = ? ORDER BY n DESC LIMIT 20", day),
      q("SELECT label, SUM(n) n FROM events WHERE kind = 'call' AND day = ? GROUP BY label ORDER BY n DESC", day),
      q("SELECT page, SUM(n) n FROM events WHERE kind = 'call' AND day = ? GROUP BY page ORDER BY n DESC LIMIT 15", day),
      q("SELECT day, COUNT(*) b FROM visits WHERE kind != 'person' AND day >= ? GROUP BY day", from14),
      q("SELECT CASE WHEN kind = 'foreign' THEN '해외 접속 · ' || COALESCE(NULLIF(country, ''), '?') ELSE COALESCE(NULLIF(org, ''), '알 수 없음') END org, COUNT(*) v FROM visits WHERE kind != 'person' AND day = ? GROUP BY 1 ORDER BY v DESC LIMIT 12", day),
      q("SELECT landing, COUNT(*) v FROM visits WHERE kind = 'person' AND day = ? GROUP BY landing ORDER BY v DESC LIMIT 15", day),
      q("SELECT COALESCE(NULLIF(org, ''), '알 수 없음') org, COUNT(*) v FROM visits WHERE kind = 'person' AND day = ? GROUP BY 1 ORDER BY v DESC LIMIT 12", day),
    ]);
    const mk = (rows, k) => Object.fromEntries(rows.map((r) => [r.day, r[k]]));
    const V = mk(vDays, "v"), H = mk(hDays, "h"), C = mk(cDays, "c"), M = mk(mDays, "m"), B = mk(bDays, "b");
    const days = [...Array(14)].map((_, i) => kstDay(13 - i));
    const sum = (arr, m) => arr.reduce((a, x) => a + (m[x] || 0), 0);
    const last7 = days.slice(7);
    const rate = (c, v) => (v ? Math.round((c / v) * 1000) / 10 : 0) + "%";
    const max = Math.max(1, ...days.map((x) => V[x] || 0));
    const bars = days.map((x) => `<a class="bar ${x === day ? "sel" : ""}" href="/admin?day=${x}" title="${x} 방문자 ${V[x] || 0} · 전화 ${C[x] || 0}">
        <span style="height:${((V[x] || 0) / max) * 100}%"></span><em>${x.slice(5).replace("-", "/")}</em></a>`).join("");
    const daily = [...days].reverse().map((x) => ({ x, v: V[x] || 0, h: H[x] || 0, c: C[x] || 0, b: B[x] || 0, m: V[x] ? Math.round(((M[x] || 0) / V[x]) * 100) + "%" : "-" }));
    const hourMap = Object.fromEntries(hours.map((r) => [r.hour, r.v]));
    const hMax = Math.max(1, ...hours.map((r) => r.v));
    const hourBars = [...Array(24)].map((_, i) => `<div class="hbar" title="${i}시 ${hourMap[i] || 0}명"><span style="height:${((hourMap[i] || 0) / hMax) * 100}%"></span><em>${i % 3 === 0 ? i : ""}</em></div>`).join("");
    const dv = V[day] || 0, dc = C[day] || 0;
    const link = (p) => `<a href="${esc(p)}" target="_blank">${esc(p)}</a>`;

    body = `
    <div class="stats">
      <div class="card stat"><small>오늘 방문자</small><b>${V[today] || 0}</b><small>조회 ${H[today] || 0}</small></div>
      <div class="card stat"><small>오늘 전화 클릭</small><b class="accent">${C[today] || 0}</b><small>전환율 ${rate(C[today] || 0, V[today] || 0)}</small></div>
      <div class="card stat"><small>최근 7일 방문자</small><b>${sum(last7, V)}</b><small>조회 ${sum(last7, H)}</small></div>
      <div class="card stat"><small>최근 7일 전화 클릭</small><b class="accent">${sum(last7, C)}</b><small>전환율 ${rate(sum(last7, C), sum(last7, V))}</small></div>
    </div>
    <div class="card"><h2>일별 방문자 (최근 14일) <span class="muted">· 막대를 누르면 그날 상세</span></h2><div class="chart">${bars}</div></div>
    <div class="card dayhead">
      <form method="get" action="/admin"><h2>${day}${day === today ? " (오늘)" : ""} 상세</h2>
        <input type="date" name="day" value="${day}" max="${today}" onchange="this.form.submit()"></form>
      <div class="mini"><span>방문자 <b>${dv}</b></span><span>조회 <b>${H[day] || 0}</b></span><span>전화 클릭 <b class="accent">${dc}</b></span><span>전환율 <b>${rate(dc, dv)}</b></span><span class="muted">제외한 접속 ${B[day] || 0} (봇·해외)</span></div>
    </div>
    <div class="grid2">
      <div class="card"><h2>지역별 방문자 (시·도)</h2>${hbars(geoR, "region", "v")}</div>
      <div class="card"><h2>지역별 방문자 (시·군·구)</h2>${table(geoC, [{ t: "시·도", k: "region" }, { t: "시·군·구", f: (r) => esc(r.city || "알 수 없음") }, { t: "방문자", k: "v", n: 1 }])}</div>
      <div class="card"><h2>전화 버튼 클릭 (버튼별)</h2>${hbars(calls, "label", "n")}</div>
      <div class="card"><h2>전화 버튼 클릭 (페이지별)</h2>${table(callPages, [{ t: "페이지", f: (r) => link(r.page) }, { t: "클릭", k: "n", n: 1 }], "아직 전화 클릭이 없습니다")}</div>
      <div class="card"><h2>유입 경로</h2>${hbars(refs, "ref", "v")}</div>
      <div class="card"><h2>처음 들어온 페이지</h2>${table(lands, [{ t: "페이지", f: (r) => link(r.landing) }, { t: "방문자", k: "v", n: 1 }])}</div>
      <div class="card"><h2>방문자 통신사·접속 회사</h2><p class="muted">SK브로드밴드·KT·LG유플러스 같은 통신사면 사람일 가능성이 큽니다. 처음 보는 회사 이름이 많으면 자동 프로그램일 수 있습니다.</p>${hbars(personOrgs, "org", "v")}</div>
      <div class="card"><h2>기기</h2>${hbars(devs, "device", "v")}</div>
      <div class="card"><h2>시간대별 방문자</h2><div class="hchart">${hourBars}</div></div>
      <div class="card"><h2>많이 본 페이지</h2>${table(pages, [{ t: "페이지", f: (r) => link(r.path) }, { t: "조회", k: "n", n: 1 }])}</div>
      <div class="card"><h2>검색어 (최근 7일)</h2><p class="muted">네이버·다음 등에서 검색어가 전달된 경우만 표시됩니다.</p>${table(kws, [{ t: "검색어", k: "kw" }, { t: "유입", k: "n", n: 1 }])}</div>
    </div>
    <div class="grid2">
      <div class="card"><h2>제외한 접속 (봇·데이터센터·해외) <span class="muted">· 방문자 수에서 제외</span></h2>${hbars(botOrgs, "org", "v")}</div>
      <div class="card"><h2>날짜별 요약 (14일)</h2>${table(daily, [{ t: "날짜", f: (r) => `<a href="/admin?day=${r.x}">${r.x.slice(5)}</a>` }, { t: "방문자", k: "v", n: 1 }, { t: "조회", k: "h", n: 1 }, { t: "전화", k: "c", n: 1 }, { t: "휴대폰", k: "m", n: 1 }, { t: "제외", k: "b", n: 1 }])}</div>
    </div>
    <p class="muted">지역은 접속한 인터넷 주소(IP) 기준이라 실제 위치와 다를 수 있습니다. 휴대폰 데이터로 접속하면 통신사 위치(주로 서울)로 잡히는 경우가 많습니다.<br>방문자 수는 사람만 셉니다. 검색엔진·수집기처럼 봇 이름을 밝히거나 데이터센터에서 온 접속, 해외 접속은 '제외한 접속'으로 따로 보여 줍니다. 관리자로 로그인한 상태의 방문은 기록하지 않습니다.</p>`;
  }

  return page("관리자", `
    <div class="top"><h1>24시출장열쇠 관리자</h1><div><a href="/" target="_blank">사이트 보기</a> · <a href="/admin/logout">로그아웃</a></div></div>
    <nav class="tabs"><a href="/admin" class="${tab === "stats" ? "on" : ""}">방문 통계</a><a href="/admin?tab=pages" class="${tab === "pages" ? "on" : ""}">📄 페이지 조회</a><a href="/admin?tab=posts" class="${tab === "posts" ? "on" : ""}">블로그 글 현황</a></nav>
    ${body}`);
}

function loginPage(msg) {
  return page("관리자 로그인", `<form class="card login" method="post" action="/admin/login">
    <h1>24시출장열쇠 관리자</h1>
    ${msg ? `<p class="err">${msg}</p>` : ""}
    <label>아이디<input name="id" autocomplete="username" required></label>
    <label>비밀번호<input name="pw" type="password" autocomplete="current-password" required></label>
    <button>로그인</button></form>`);
}

function page(title, body) {
  return `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><title>${title} | 24시출장열쇠</title>
<style>
:root{--bg:#f4f3ef;--card:#fff;--fg:#141414;--muted:#6b6b66;--line:#e2dfd6;--red:#e3120b;--ink:#141414}
*{box-sizing:border-box;margin:0}body{background:var(--bg);color:var(--fg);font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;padding:24px 16px 60px;max-width:1080px;margin:0 auto;line-height:1.6}
a{color:var(--ink)}h1{font-size:1.4rem}h2{font-size:1.05rem;margin-bottom:12px}
.tabs{display:flex;gap:6px;margin-bottom:16px;border-bottom:2px solid var(--line);overflow-x:auto}.tabs a{padding:10px 16px;text-decoration:none;color:var(--muted);font-weight:700;border-bottom:3px solid transparent;margin-bottom:-2px;white-space:nowrap}.tabs a.on{color:var(--ink);border-color:var(--red)}
.top{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin-bottom:18px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:18px;margin-bottom:16px}.warn{background:#fff6e0}
.stats{display:grid;gap:12px;grid-template-columns:repeat(4,1fr)}.stat b{display:block;font-size:2rem}.stat small{color:var(--muted)}
@media(max-width:860px){.stats{grid-template-columns:1fr 1fr}}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:700px){.grid2{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse}td{padding:8px 6px;border-bottom:1px solid var(--line);vertical-align:middle;word-break:break-all}.n{text-align:right;white-space:nowrap}
th{font-size:.8rem;color:var(--muted);text-align:left;padding:6px;border-bottom:1px solid var(--line)}
.muted{color:var(--muted);font-size:.88rem}.accent{color:var(--red)}
button{background:var(--red);color:#fff;border:0;border-radius:8px;padding:10px 14px;font-weight:800;cursor:pointer;font-size:.95rem}
.chart{display:flex;align-items:flex-end;gap:6px;height:180px;padding-top:10px}.bar{flex:1;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;text-decoration:none}
.bar span{width:100%;background:var(--ink);border-radius:3px 3px 0 0;min-height:2px}.bar em{font-style:normal;font-size:.7rem;color:var(--muted);margin-top:4px}
a.bar.sel span{background:var(--red)}a.bar:hover span{opacity:.75}
.login{max-width:360px;margin:12vh auto;display:grid;gap:14px}.login input{display:block;width:100%;margin-top:4px;padding:11px;border:1px solid var(--line);border-radius:8px;font-size:1rem}
.err{color:var(--red);font-weight:700}
.dayhead form{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.dayhead h2{margin:0}
.dayhead input{padding:8px 10px;border:1px solid var(--line);border-radius:8px;font-size:.95rem}
.mini{display:flex;gap:18px;flex-wrap:wrap;margin-top:12px;color:var(--muted)}.mini b{color:var(--fg);font-size:1.15rem;margin-left:4px}
.hb{display:grid;grid-template-columns:130px 1fr 42px;gap:8px;align-items:center;padding:4px 0;font-size:.92rem}
.hb-l{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.hb-b{background:#efede6;border-radius:3px;height:14px;overflow:hidden}.hb-b i{display:block;height:100%;background:var(--ink)}
.hb-n{text-align:right;font-weight:700}
.hchart{display:flex;align-items:flex-end;gap:3px;height:140px}.hbar{flex:1;height:100%;display:flex;flex-direction:column;justify-content:flex-end;align-items:center}
.hbar span{width:100%;background:var(--ink);border-radius:2px 2px 0 0;min-height:2px}.hbar em{font-style:normal;font-size:.68rem;color:var(--muted);height:14px;margin-top:3px}
.pills{display:flex;flex-wrap:wrap;gap:6px;align-items:center}.pill{border:1px solid var(--line);border-radius:999px;padding:5px 12px;text-decoration:none;font-weight:700;font-size:.9rem;background:#faf9f6}.pill.on{background:var(--ink);color:#fff;border-color:var(--ink)}.pill b{font-weight:800;margin-left:2px}
.inl{display:flex;gap:6px;align-items:center}.inl input{padding:6px 10px;border:1px solid var(--line);border-radius:8px;font-size:.9rem}.inl button{padding:6px 12px}
.chips{display:flex;flex-wrap:wrap;gap:6px}.chip{border:1px solid var(--line);background:#faf9f6;border-radius:999px;padding:3px 10px;font-size:.88rem}
</style></head><body>${body}</body></html>`;
}
