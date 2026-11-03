// 전화 버튼 클릭 기록 (관리자 통계용)
(function () {
  document.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href^="tel:"]');
    if (!a) return;
    var label = a.classList.contains("h-call") ? "상단 번호" : a.classList.contains("tel-box") ? "큰 전화 버튼"
      : a.closest(".callbar") ? "하단 고정 버튼" : a.closest(".side") ? "옆 칸 번호" : "본문 번호";
    var body = JSON.stringify({ kind: "call", page: location.pathname, label: label });
    try { navigator.sendBeacon("/api/event", new Blob([body], { type: "application/json" })); } catch (err) {}
  });
})();
