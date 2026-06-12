let period = 'd';

function esc(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function loadRankings() {
  const status = document.getElementById('rankStatus');
  const body = document.getElementById('rankBody');
  status.textContent = '読み込み中...';
  try {
    const res = await fetch(`/api/rankings?period=${period}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    body.innerHTML = (data.items || []).map((item) => `
      <tr>
        <td class="rank">${item.rank}</td>
        <td><a href="${esc(item.url)}" target="_blank" rel="noopener">${esc(item.title)}</a></td>
        <td>${esc(item.writer)}</td>
        <td>${esc(item.end_label)}${item.isstop_label ? ' / ' + esc(item.isstop_label) : ''}</td>
        <td>${esc(item.pt)}</td>
      </tr>
    `).join('');
    status.textContent = `${data.period_label} ${data.count}件`;
  } catch (err) {
    status.textContent = `エラー: ${err.message}`;
  }
}

document.getElementById('periodTabs')?.addEventListener('click', (e) => {
  const btn = e.target.closest('.tab');
  if (!btn) return;
  period = btn.dataset.period;
  document.querySelectorAll('#periodTabs .tab').forEach((t) => t.classList.toggle('active', t === btn));
  loadRankings();
});

loadRankings();
