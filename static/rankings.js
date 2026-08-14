let period = 'd';

function esc(s) {
  return String(s ?? '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

async function loadRankings() {
  const status = document.getElementById('rankStatus');
  const body = document.getElementById('rankBody');
    status.textContent = document.body.dataset.rankLoading || 'Loading…';
  try {
    const res = await fetch(`/api/rankings?period=${period}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (data.error) {
      body.innerHTML = '';
      status.textContent = data.error;
      return;
    }
    body.innerHTML = (data.items || []).map((item) => `
      <tr>
        <td class="rank">${item.rank}</td>
        <td><a href="${esc(item.url)}" target="_blank" rel="noopener">${esc(item.title)}</a></td>
        <td>${esc(item.writer)}</td>
        <td>${esc(item.end_label)}${item.isstop_label ? ' / ' + esc(item.isstop_label) : ''}</td>
        <td>${esc(item.pt)}</td>
      </tr>
    `).join('');
    status.textContent = data.warning
      ? `${data.period_label} ${data.count}件（${data.warning}）`
      : `${data.period_label} ${data.count}件`;
  } catch (err) {
    status.textContent = `${document.body.dataset.rankError || 'Error'}: ${err.message}`;
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
