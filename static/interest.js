(function () {
  const KEY = 'gensaku_interest_v1';
  const MAX_STORE = 12;
  const MAX_SHOW = 6;

  function load() {
    try {
      const items = JSON.parse(localStorage.getItem(KEY) || '[]');
      return Array.isArray(items) ? items : [];
    } catch (e) {
      return [];
    }
  }

  function saveItem(item) {
    if (!item || !item.id || !item.buy_url) return;
    const next = load().filter((x) => x.id !== item.id);
    next.unshift({
      id: String(item.id),
      title: String(item.title || '').slice(0, 80),
      buy_url: String(item.buy_url),
      cover_url: String(item.cover_url || ''),
      buy_label: String(item.buy_label || 'Amazonで見る'),
    });
    localStorage.setItem(KEY, JSON.stringify(next.slice(0, MAX_STORE)));
  }

  function fromWorkPage() {
    const el = document.getElementById('workInterest');
    if (!el) return;
    try {
      saveItem(JSON.parse(el.textContent));
    } catch (e) {
      /* ignore */
    }
  }

  function fromHomeCards() {
    document.querySelectorAll('.work-card[data-work-id]').forEach((card) => {
      card.addEventListener('click', () => {
        saveItem({
          id: card.dataset.workId,
          title: card.dataset.sourceTitle || card.dataset.title,
          buy_url: card.dataset.buyUrl,
          cover_url: card.dataset.coverUrl,
          buy_label: card.dataset.buyLabel,
        });
      });
    });
  }

  function cardNode(item) {
    const a = document.createElement('a');
    a.className = 'aff-card';
    a.href = item.buy_url;
    a.target = '_blank';
    a.rel = 'noopener sponsored';
    a.dataset.workId = item.id;
    const img = document.createElement('img');
    img.src = item.cover_url;
    img.alt = item.title;
    img.width = 80;
    img.height = 113;
    img.loading = 'lazy';
    const title = document.createElement('span');
    title.className = 'aff-card-title';
    title.textContent = item.title;
    const cta = document.createElement('span');
    cta.className = 'aff-card-cta';
    cta.textContent = item.buy_label;
    a.append(img, title, cta);
    return a;
  }

  function renderAff() {
    const listEl = document.getElementById('affList');
    const titleEl = document.getElementById('affTitle');
    if (!listEl) return;
    const viewed = load();
    if (!viewed.length) return;

    const defaults = [...listEl.querySelectorAll('a.aff-card')].map((a) => ({
      id: a.dataset.workId || a.href,
      title: (a.querySelector('.aff-card-title') || {}).textContent || '',
      buy_url: a.href,
      cover_url: (a.querySelector('img') || {}).src || '',
      buy_label: (a.querySelector('.aff-card-cta') || {}).textContent || 'Amazonで見る',
    }));

    const seen = new Set();
    const merged = [];
    for (const item of viewed.concat(defaults)) {
      if (!item.buy_url || seen.has(item.id)) continue;
      seen.add(item.id);
      merged.push(item);
      if (merged.length >= MAX_SHOW) break;
    }
    if (!merged.length) return;
    if (titleEl) titleEl.textContent = '最近見た原作';
    listEl.replaceChildren(...merged.map(cardNode));
  }

  fromWorkPage();
  fromHomeCards();
  renderAff();
})();
