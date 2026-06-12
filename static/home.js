const els = {
  seasonSelect: document.getElementById('seasonSelect'),
  filterSource: document.getElementById('filterSource'),
  filterHasSource: document.getElementById('filterHasSource'),
  searchInput: document.getElementById('searchInput'),
  workGrid: document.getElementById('workGrid'),
  emptyMsg: document.getElementById('emptyMsg'),
  statusLine: document.getElementById('statusLine'),
};

function applyFilters() {
  const src = els.filterSource.value;
  const hasOnly = els.filterHasSource.checked;
  const q = els.searchInput.value.trim().toLowerCase();
  let visible = 0;
  els.workGrid.querySelectorAll('.work-card').forEach((card) => {
    let ok = true;
    if (src && card.dataset.source !== src) ok = false;
    if (hasOnly && card.dataset.hasSource !== '1') ok = false;
    if (q && !card.dataset.search.toLowerCase().includes(q)) ok = false;
    card.classList.toggle('hidden', !ok);
    if (ok) visible += 1;
  });
  els.emptyMsg.classList.toggle('hidden', visible > 0);
  els.statusLine.textContent = `${visible}作品表示`;
}

els.seasonSelect?.addEventListener('change', () => {
  const season = els.seasonSelect.value;
  window.location.href = `/?season=${encodeURIComponent(season)}`;
});

[els.filterSource, els.filterHasSource, els.searchInput].forEach((el) => {
  el?.addEventListener('input', applyFilters);
  el?.addEventListener('change', applyFilters);
});

applyFilters();
