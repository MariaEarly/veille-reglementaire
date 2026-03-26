def render_dashboard() -> str:
    return """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Veille Réglementaire</title>
  <style>
    :root {
      --bg: #f5f1e8;
      --surface: #fffaf0;
      --card: #ffffff;
      --border: #d6c7ad;
      --text: #1f1a14;
      --muted: #6f6558;
      --accent: #9f3d24;
      --accent-dark: #7d2f1b;
      --accent2: #1e5b52;
      --accent2-light: #2d8176;
      --warn: #a36a00;
      --success: #2d8176;
      --shadow-sm: 0 2px 8px rgba(31, 26, 20, 0.08);
      --shadow-md: 0 4px 16px rgba(31, 26, 20, 0.12);
      --shadow-lg: 0 12px 32px rgba(31, 26, 20, 0.15);
      --radius: 12px;
      --radius-lg: 16px;
      --score-low: #90a4ae;
      --score-mid: #f9a825;
      --score-high: #e65100;
      --score-critical: #b71c1c;
    }

    * {
      box-sizing: border-box;
    }

    html, body {
      margin: 0;
      padding: 0;
      height: 100%;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Georgia, serif;
      color: var(--text);
      background: radial-gradient(circle at top left, rgba(159, 61, 36, 0.08), transparent 24rem),
                  radial-gradient(circle at bottom right, rgba(30, 91, 82, 0.08), transparent 24rem),
                  var(--bg);
      line-height: 1.5;
    }

    a {
      color: var(--accent2);
      text-decoration: none;
      transition: color 150ms ease;
    }

    a:hover {
      color: var(--accent2-light);
    }

    .app {
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    /* Header */
    .header {
      background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 250, 240, 0.95));
      border-bottom: 1px solid var(--border);
      box-shadow: var(--shadow-sm);
      padding: 20px 24px;
      position: sticky;
      top: 0;
      z-index: 100;
    }

    .header-content {
      max-width: 1400px;
      margin: 0 auto;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }

    .header-title {
      display: flex;
      align-items: baseline;
      gap: 12px;
    }

    .header-title h1 {
      margin: 0;
      font-size: 1.6rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .header-stats {
      display: flex;
      align-items: center;
      gap: 20px;
      flex: 1;
      margin-left: 40px;
    }

    .stat {
      display: flex;
      flex-direction: column;
      gap: 4px;
    }

    .stat-label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--muted);
      font-weight: 600;
    }

    .stat-value {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--accent);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    /* Button Styles */
    button {
      cursor: pointer;
      border: none;
      border-radius: var(--radius);
      font-family: inherit;
      font-size: 0.95rem;
      font-weight: 600;
      transition: all 150ms ease;
    }

    .btn {
      padding: 10px 20px;
      background: var(--accent);
      color: white;
      border: none;
      border-radius: var(--radius);
      cursor: pointer;
      font-weight: 600;
      font-size: 0.95rem;
      transition: all 150ms ease;
    }

    .btn:hover {
      background: var(--accent-dark);
      box-shadow: var(--shadow-md);
    }

    .btn-secondary {
      background: var(--accent2);
      color: white;
    }

    .btn-secondary:hover {
      background: var(--accent2-light);
    }

    .btn-small {
      padding: 6px 12px;
      font-size: 0.85rem;
    }

    .btn-text {
      background: transparent;
      color: var(--accent);
      padding: 6px 12px;
    }

    .btn-text:hover {
      background: rgba(159, 61, 36, 0.1);
    }

    .btn-refresh {
      padding: 12px 24px;
      font-size: 1rem;
      background: var(--accent);
      color: white;
      display: flex;
      align-items: center;
      gap: 8px;
      white-space: nowrap;
    }

    .btn-refresh:hover {
      background: var(--accent-dark);
      box-shadow: var(--shadow-md);
    }

    .btn-refresh.loading {
      opacity: 0.8;
    }

    .spinner {
      display: inline-block;
      width: 1em;
      height: 1em;
      border: 2px solid rgba(255, 255, 255, 0.3);
      border-top-color: white;
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
      to { transform: rotate(360deg); }
    }

    /* Tabs */
    .tabs {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--border);
    }

    .tab-btn {
      background: transparent;
      color: var(--muted);
      border: none;
      padding: 12px 20px;
      font-weight: 600;
      cursor: pointer;
      border-bottom: 3px solid transparent;
      transition: all 150ms ease;
      position: relative;
    }

    .tab-btn:hover {
      color: var(--text);
    }

    .tab-btn.active {
      color: var(--accent);
      border-bottom-color: var(--accent);
    }

    .tab-badge {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 20px;
      height: 20px;
      background: var(--accent);
      color: white;
      border-radius: 50%;
      font-size: 0.75rem;
      font-weight: 700;
      margin-left: 6px;
    }

    /* Main container */
    .main {
      flex: 1;
      max-width: 1400px;
      margin: 0 auto;
      width: 100%;
      padding: 0 24px 40px;
    }

    .tab-content {
      display: none;
    }

    .tab-content.active {
      display: block;
    }

    /* Search & Filter */
    .search-bar {
      margin-bottom: 20px;
    }

    .search-input {
      width: 100%;
      padding: 12px 16px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      font-size: 1rem;
      background: var(--card);
      color: var(--text);
      transition: border-color 150ms ease;
    }

    .search-input:focus {
      outline: none;
      border-color: var(--accent);
    }

    .filters {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
      flex-wrap: wrap;
      align-items: center;
    }

    .filter-group {
      display: flex;
      gap: 8px;
      align-items: center;
    }

    .filter-group label {
      font-size: 0.85rem;
      font-weight: 600;
      color: var(--muted);
    }

    .filter-select {
      padding: 8px 12px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      background: var(--card);
      color: var(--text);
      font-size: 0.9rem;
      cursor: pointer;
    }

    .filter-select:focus {
      outline: none;
      border-color: var(--accent);
    }

    /* Items Grid */
    .items-container {
      display: grid;
      gap: 16px;
    }

    .item-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      transition: all 150ms ease;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 20px;
      align-items: start;
    }

    .item-card:hover {
      border-color: var(--accent);
      box-shadow: var(--shadow-md);
      transform: translateY(-2px);
    }

    .item-content {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .item-header {
      display: flex;
      align-items: start;
      gap: 12px;
    }

    .item-title {
      flex: 1;
      margin: 0;
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--text);
    }

    .item-title a {
      color: var(--accent2);
    }

    .item-title a:hover {
      color: var(--accent2-light);
    }

    .score-badge {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      color: white;
      flex-shrink: 0;
      font-size: 0.9rem;
    }

    .score-low { background: var(--score-low); }
    .score-mid { background: var(--score-mid); color: var(--text); }
    .score-high { background: var(--score-high); }
    .score-critical { background: var(--score-critical); }

    .item-meta {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
      align-items: center;
    }

    .pill {
      display: inline-flex;
      align-items: center;
      padding: 4px 10px;
      border-radius: 12px;
      font-size: 0.8rem;
      font-weight: 600;
    }

    .pill-source {
      background: rgba(30, 91, 82, 0.15);
      color: var(--accent2);
    }

    .pill-rss {
      background: rgba(33, 150, 243, 0.15);
      color: #2196f3;
    }

    .pill-press {
      background: rgba(255, 152, 0, 0.15);
      color: #ff9800;
    }

    .pill-gmail {
      background: rgba(76, 175, 80, 0.15);
      color: #4caf50;
    }

    .pill-category {
      background: rgba(159, 61, 36, 0.15);
      color: var(--accent);
    }

    .pill-status {
      cursor: pointer;
      transition: all 150ms ease;
    }

    .pill-status:hover {
      opacity: 0.8;
      transform: scale(1.05);
    }

    .status-new { background: rgba(33, 150, 243, 0.15); color: #2196f3; }
    .status-important { background: rgba(244, 67, 54, 0.15); color: #f44336; }
    .status-reviewed { background: rgba(76, 175, 80, 0.15); color: #4caf50; }
    .status-archived { background: rgba(158, 158, 158, 0.15); color: #9e9e9e; }

    .item-summary {
      font-size: 0.95rem;
      color: var(--muted);
      line-height: 1.6;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 3;
      -webkit-box-orient: vertical;
    }

    .item-footer {
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.85rem;
      color: var(--muted);
    }

    .item-date {
      white-space: nowrap;
    }

    .item-actions {
      display: flex;
      flex-direction: column;
      gap: 8px;
      align-items: flex-end;
    }

    .btn-flag {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--muted);
      padding: 8px 12px;
      border-radius: var(--radius);
      cursor: pointer;
      transition: all 150ms ease;
    }

    .btn-flag:hover {
      border-color: var(--accent);
      color: var(--accent);
    }

    .btn-flag.flagged {
      background: rgba(159, 61, 36, 0.15);
      border-color: var(--accent);
      color: var(--accent);
    }

    /* Sources */
    .sources-actions {
      display: flex;
      gap: 12px;
      margin-bottom: 24px;
    }

    .sources-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;
    }

    .source-card {
      background: var(--card);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 20px;
      box-shadow: var(--shadow-sm);
      transition: all 150ms ease;
    }

    .source-card:hover {
      border-color: var(--accent);
      box-shadow: var(--shadow-md);
    }

    .source-name {
      font-size: 1.1rem;
      font-weight: 700;
      margin: 0 0 12px 0;
      color: var(--text);
    }

    .source-info {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 16px;
    }

    .source-meta {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .source-url {
      font-size: 0.85rem;
      color: var(--muted);
      word-break: break-all;
    }

    .source-count {
      font-size: 0.85rem;
      color: var(--muted);
    }

    .source-actions {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .form-add-source {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 20px;
      margin-bottom: 24px;
    }

    .form-group {
      margin-bottom: 16px;
    }

    .form-group label {
      display: block;
      margin-bottom: 6px;
      font-weight: 600;
      font-size: 0.95rem;
    }

    .form-group input,
    .form-group select {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid var(--border);
      border-radius: var(--radius);
      font-size: 0.95rem;
      font-family: inherit;
    }

    .form-group input:focus,
    .form-group select:focus {
      outline: none;
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(159, 61, 36, 0.1);
    }

    .form-actions {
      display: flex;
      gap: 12px;
    }

    /* Digest */
    .digest-period {
      display: flex;
      gap: 8px;
      margin-bottom: 24px;
    }

    .digest-stats {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius-lg);
      padding: 20px;
      margin-bottom: 24px;
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
      gap: 20px;
    }

    .digest-stat {
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .digest-stat-label {
      font-size: 0.85rem;
      color: var(--muted);
      font-weight: 600;
    }

    .digest-stat-value {
      font-size: 1.8rem;
      font-weight: 700;
      color: var(--accent);
    }

    /* Toast */
    .toast {
      position: fixed;
      bottom: 24px;
      right: 24px;
      background: var(--success);
      color: white;
      padding: 16px 24px;
      border-radius: var(--radius);
      box-shadow: var(--shadow-lg);
      z-index: 1000;
      animation: slideIn 300ms ease;
      max-width: 400px;
    }

    .toast.error {
      background: #b71c1c;
    }

    @keyframes slideIn {
      from {
        transform: translateX(400px);
        opacity: 0;
      }
      to {
        transform: translateX(0);
        opacity: 1;
      }
    }

    .toast-close {
      background: transparent;
      color: white;
      border: none;
      cursor: pointer;
      font-size: 1.2rem;
      padding: 0;
      margin-left: 16px;
    }

    /* Empty State */
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: var(--muted);
    }

    .empty-state-icon {
      font-size: 3rem;
      margin-bottom: 16px;
    }

    .empty-state-title {
      font-size: 1.2rem;
      font-weight: 700;
      margin: 0 0 8px 0;
      color: var(--text);
    }

    .empty-state-desc {
      font-size: 0.95rem;
      margin: 0;
    }

    /* Responsive */
    @media (max-width: 768px) {
      .header-content {
        flex-direction: column;
        align-items: flex-start;
        gap: 16px;
      }

      .header-stats {
        margin-left: 0;
        width: 100%;
        justify-content: space-between;
      }

      .item-card {
        grid-template-columns: 1fr;
      }

      .sources-grid {
        grid-template-columns: 1fr;
      }

      .main {
        padding: 0 16px 24px;
      }
    }
  </style>
</head>
<body>
  <div class="app">
    <!-- Header -->
    <header class="header">
      <div class="header-content">
        <div class="header-title">
          <h1>📋 Veille Réglementaire</h1>
        </div>

        <div class="header-stats">
          <div class="stat">
            <span class="stat-label">Articles</span>
            <span class="stat-value" id="stat-items">0</span>
          </div>
          <div class="stat">
            <span class="stat-label">Important</span>
            <span class="stat-value" id="stat-important">0</span>
          </div>
          <div class="stat">
            <span class="stat-label">Early Brief</span>
            <span class="stat-value" id="stat-early-brief">0</span>
          </div>
          <div class="stat">
            <span class="stat-label">Sources</span>
            <span class="stat-value" id="stat-sources">0</span>
          </div>
        </div>

        <div class="header-actions">
          <button class="btn-refresh" id="refresh-all-btn">
            <span id="refresh-spinner" style="display:none" class="spinner"></span>
            <span id="refresh-text">🔄 Rafraîchir toutes les sources</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main">
      <!-- Tabs -->
      <div class="tabs">
        <button class="tab-btn active" data-tab="feed">
          Fil d'actualité
        </button>
        <button class="tab-btn" data-tab="early-brief">
          Early Brief
          <span class="tab-badge" id="early-brief-badge" style="display:none">0</span>
        </button>
        <button class="tab-btn" data-tab="sources">
          Sources
        </button>
        <button class="tab-btn" data-tab="digest">
          Digest
        </button>
      </div>

      <!-- Tab: Fil d'actualité -->
      <div class="tab-content active" id="tab-feed">
        <div class="search-bar">
          <input type="text" class="search-input" id="search-input" placeholder="Chercher parmi les articles...">
        </div>

        <div class="filters">
          <div class="filter-group">
            <label for="filter-category">Catégorie:</label>
            <select class="filter-select" id="filter-category">
              <option value="">Toutes</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="filter-status">Statut:</label>
            <select class="filter-select" id="filter-status">
              <option value="">Tous</option>
              <option value="new">Nouveau</option>
              <option value="important">Important</option>
              <option value="reviewed">Examiné</option>
              <option value="archived">Archivé</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="filter-score-min">Score min:</label>
            <select class="filter-select" id="filter-score-min">
              <option value="0">Tous</option>
              <option value="20">20+</option>
              <option value="40">40+</option>
              <option value="60">60+</option>
            </select>
          </div>
          <div class="filter-group">
            <label for="filter-sort">Trier par:</label>
            <select class="filter-select" id="filter-sort">
              <option value="score">Score (décroissant)</option>
              <option value="date">Date (récent)</option>
            </select>
          </div>
        </div>

        <div class="items-container" id="items-list">
          <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <h3 class="empty-state-title">Aucun article</h3>
            <p class="empty-state-desc">Cliquez sur "Rafraîchir toutes les sources" pour charger les articles</p>
          </div>
        </div>
      </div>

      <!-- Tab: Early Brief -->
      <div class="tab-content" id="tab-early-brief">
        <div class="items-container" id="early-brief-list">
          <div class="empty-state">
            <div class="empty-state-icon">⭐</div>
            <h3 class="empty-state-title">Pas d'articles marqués</h3>
            <p class="empty-state-desc">Marquez des articles pour l'Early Brief en cliquant l'icône ⭐</p>
          </div>
        </div>
      </div>

      <!-- Tab: Sources -->
      <div class="tab-content" id="tab-sources">
        <div class="sources-actions">
          <button class="btn btn-secondary" id="seed-sources-btn">🌱 Seed all sources</button>
          <button class="btn" id="refresh-sources-btn" style="display:none">🔄 Refresh all sources</button>
        </div>

        <div style="margin-bottom: 24px;">
          <button class="btn" id="toggle-add-source-btn" style="width: auto;">➕ Add source</button>
        </div>

        <div class="form-add-source" id="add-source-form" style="display:none;">
          <form id="source-form">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px;">
              <div class="form-group">
                <label for="source-name">Source name:</label>
                <input type="text" id="source-name" placeholder="e.g., Reuters Tech News" required>
              </div>
              <div class="form-group">
                <label for="source-type">Type:</label>
                <select id="source-type" required>
                  <option value="rss">RSS</option>
                  <option value="press">Press</option>
                  <option value="gmail">Gmail</option>
                </select>
              </div>
              <div class="form-group" style="grid-column: 1 / -1;">
                <label for="source-url">URL/Feed:</label>
                <input type="text" id="source-url" placeholder="https://..." required>
              </div>
              <div class="form-group">
                <label for="source-category">Category:</label>
                <select id="source-category" required>
                  <option value="Tech">Tech</option>
                  <option value="Finance">Finance</option>
                  <option value="Legal">Legal</option>
                  <option value="Health">Health</option>
                  <option value="Other">Other</option>
                </select>
              </div>
            </div>
            <div class="form-actions">
              <button type="submit" class="btn">Create source</button>
              <button type="button" class="btn-text" id="cancel-add-source-btn">Cancel</button>
            </div>
          </form>
        </div>

        <div class="sources-grid" id="sources-list">
          <div class="empty-state" style="grid-column: 1 / -1;">
            <div class="empty-state-icon">🌐</div>
            <h3 class="empty-state-title">No sources</h3>
            <p class="empty-state-desc">Click "🌱 Seed all sources" to add pre-configured sources or create one manually</p>
          </div>
        </div>

        <div id="gmail-status" style="margin-top: 24px; padding: 16px; background: var(--surface); border-radius: var(--radius-lg); border: 1px solid var(--border); display: none;">
          <h3 style="margin: 0 0 12px 0;">Gmail Configuration</h3>
          <p id="gmail-status-text" style="margin: 0; color: var(--muted);"></p>
        </div>
      </div>

      <!-- Tab: Digest -->
      <div class="tab-content" id="tab-digest">
        <div class="digest-period">
          <button class="btn" data-period="3" id="period-3">3 jours</button>
          <button class="btn active" data-period="7" id="period-7">7 jours</button>
          <button class="btn" data-period="14" id="period-14">14 jours</button>
          <button class="btn" data-period="30" id="period-30">30 jours</button>
        </div>

        <div class="digest-stats" id="digest-stats">
          <div class="digest-stat">
            <span class="digest-stat-label">Period</span>
            <span class="digest-stat-value" id="digest-period-val">7</span>
          </div>
          <div class="digest-stat">
            <span class="digest-stat-label">Articles</span>
            <span class="digest-stat-value" id="digest-count-val">0</span>
          </div>
        </div>

        <div class="items-container" id="digest-list">
          <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <h3 class="empty-state-title">Aucune donnée</h3>
            <p class="empty-state-desc">Charger les sources pour générer le digest</p>
          </div>
        </div>
      </div>
    </main>
  </div>

  <script>
    // State
    const state = {
      items: [],
      sources: [],
      categories: new Set(),
      currentTab: 'feed',
      searchQuery: '',
      filters: {
        category: '',
        status: '',
        scoreMin: 0,
        sort: 'score'
      },
      digestPeriod: 7
    };

    // Debounce helper
    function debounce(fn, delay) {
      let timeoutId;
      return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => fn(...args), delay);
      };
    }

    // Toast notifications
    function showToast(message, isError = false) {
      const toast = document.createElement('div');
      toast.className = `toast ${isError ? 'error' : ''}`;
      toast.innerHTML = `
        ${message}
        <button class="toast-close">&times;</button>
      `;
      document.body.appendChild(toast);
      toast.querySelector('.toast-close').addEventListener('click', () => toast.remove());
      setTimeout(() => toast.remove(), 5000);
    }

    // API calls
    async function fetchItems(search = '') {
      try {
        const url = search ? `/items/search?q=${encodeURIComponent(search)}` : '/items';
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to fetch items');
        state.items = await res.json();
        updateCategoryFilter();
        renderItems();
      } catch (err) {
        console.error(err);
        showToast('Failed to load items', true);
      }
    }

    async function fetchSources() {
      try {
        const res = await fetch('/sources');
        if (!res.ok) throw new Error('Failed to fetch sources');
        state.sources = await res.json();
        renderSources();
        updateStats();
      } catch (err) {
        console.error(err);
        showToast('Failed to load sources', true);
      }
    }

    async function refreshAllSources() {
      const btn = document.getElementById('refresh-all-btn');
      const spinner = document.getElementById('refresh-spinner');
      const text = document.getElementById('refresh-text');

      btn.disabled = true;
      btn.classList.add('loading');
      spinner.style.display = 'inline-block';
      text.textContent = 'Rafraîchissement en cours...';

      try {
        const res = await fetch('/ingest/all', { method: 'POST' });
        if (!res.ok) throw new Error('Refresh failed');
        const result = await res.json();

        let msg = `✅ ${result.total_created} nouveaux articles sur ${result.sources_processed} sources`;
        if (result.details?.some(d => d.error)) {
          msg += ' (avec erreurs)';
        }
        showToast(msg);

        // Reload data
        await fetchItems();
        await fetchSources();
      } catch (err) {
        console.error(err);
        showToast('Erreur lors du rafraîchissement', true);
      } finally {
        btn.disabled = false;
        btn.classList.remove('loading');
        spinner.style.display = 'none';
        text.textContent = '🔄 Rafraîchir toutes les sources';
      }
    }

    async function seedSources() {
      const btn = document.getElementById('seed-sources-btn');
      btn.disabled = true;

      try {
        const res = await fetch('/sources/seed', { method: 'POST' });
        if (!res.ok) throw new Error('Seed failed');
        showToast('✅ Sources seeded successfully');
        await fetchSources();
      } catch (err) {
        console.error(err);
        showToast('Failed to seed sources', true);
      } finally {
        btn.disabled = false;
      }
    }

    async function deleteSource(id) {
      if (!confirm('Delete this source?')) return;

      try {
        const res = await fetch(`/sources/${id}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Delete failed');
        showToast('✅ Source deleted');
        await fetchSources();
      } catch (err) {
        console.error(err);
        showToast('Failed to delete source', true);
      }
    }

    async function createSource(e) {
      e.preventDefault();
      const form = new FormData(e.target);
      const data = {
        name: form.get('name'),
        source_type: form.get('type'),
        url: form.get('url'),
        category: form.get('category')
      };

      try {
        const res = await fetch('/sources', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Create failed');
        showToast('✅ Source created');
        e.target.reset();
        document.getElementById('add-source-form').style.display = 'none';
        await fetchSources();
      } catch (err) {
        console.error(err);
        showToast('Failed to create source', true);
      }
    }

    async function updateItemStatus(id, status) {
      try {
        const res = await fetch(`/items/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status })
        });
        if (!res.ok) throw new Error('Update failed');
        await fetchItems(state.searchQuery);
      } catch (err) {
        console.error(err);
        showToast('Failed to update item', true);
      }
    }

    async function toggleEarlyBrief(id, flagged) {
      try {
        const res = await fetch(`/items/${id}`, {
          method: 'PATCH',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ early_brief: !flagged })
        });
        if (!res.ok) throw new Error('Update failed');
        await fetchItems(state.searchQuery);
        await fetchEarlyBrief();
      } catch (err) {
        console.error(err);
        showToast('Failed to update Early Brief', true);
      }
    }

    async function fetchEarlyBrief() {
      try {
        const res = await fetch('/early-brief');
        if (!res.ok) throw new Error('Failed to fetch');
        const items = await res.json();
        renderEarlyBrief(items);

        const badge = document.getElementById('early-brief-badge');
        if (items.length > 0) {
          badge.textContent = items.length;
          badge.style.display = 'inline-flex';
        } else {
          badge.style.display = 'none';
        }
      } catch (err) {
        console.error(err);
      }
    }

    async function fetchDigest(days) {
      try {
        const res = await fetch(`/digest?days=${days}`);
        if (!res.ok) throw new Error('Failed to fetch');
        const data = await res.json();
        renderDigest(data);
      } catch (err) {
        console.error(err);
        showToast('Failed to load digest', true);
      }
    }

    async function checkGmailStatus() {
      try {
        const res = await fetch('/health');
        if (!res.ok) throw new Error('Failed to check');
        const data = await res.json();
        const gmailDiv = document.getElementById('gmail-status');
        const gmailText = document.getElementById('gmail-status-text');

        if (data.gmail_configured) {
          gmailDiv.style.display = 'block';
          gmailText.textContent = '✅ Gmail configured and ready';
        } else {
          gmailDiv.style.display = 'block';
          gmailText.innerHTML = 'Gmail not configured. <a href="https://developers.google.com" target="_blank">Setup instructions</a>';
        }
      } catch (err) {
        console.error(err);
      }
    }

    // Rendering
    function renderItems() {
      const container = document.getElementById('items-list');
      let filtered = state.items;

      // Apply filters
      if (state.filters.category) {
        filtered = filtered.filter(i => i.category === state.filters.category);
      }
      if (state.filters.status) {
        filtered = filtered.filter(i => i.status === state.filters.status);
      }
      if (state.filters.scoreMin > 0) {
        filtered = filtered.filter(i => i.score >= state.filters.scoreMin);
      }

      // Sort
      if (state.filters.sort === 'date') {
        filtered.sort((a, b) => new Date(b.published_at) - new Date(a.published_at));
      } else {
        filtered.sort((a, b) => b.score - a.score);
      }

      if (filtered.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">📭</div>
            <h3 class="empty-state-title">Aucun article</h3>
            <p class="empty-state-desc">Essayez d'ajuster les filtres ou rafraîchissez les sources</p>
          </div>
        `;
        return;
      }

      container.innerHTML = filtered.map(item => {
        const scoreClass = item.score < 20 ? 'score-low' : item.score < 40 ? 'score-mid' : item.score < 60 ? 'score-high' : 'score-critical';
        const statusClass = `status-${item.status}`;
        const isFlagged = item.early_brief;
        const sourceType = item.source_type?.toLowerCase() || 'rss';

        return `
          <div class="item-card">
            <div class="item-content">
              <div class="item-header">
                <h3 class="item-title">
                  <a href="${item.url}" target="_blank" rel="noopener">${item.title}</a>
                </h3>
              </div>

              <div class="item-meta">
                <span class="pill pill-${sourceType}">${sourceType.toUpperCase()}</span>
                <span class="pill pill-source">${item.source_name}</span>
                <span class="pill pill-category">${item.category}</span>
                <span class="pill pill-status status-${item.status}" onclick="cycleStatus('${item.id}', '${item.status}')" title="Click to cycle">
                  ${item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                </span>
              </div>

              ${item.summary ? `<p class="item-summary">${escapeHtml(item.summary)}</p>` : ''}

              <div class="item-footer">
                <span class="item-date">${formatDate(item.published_at)}</span>
              </div>
            </div>

            <div class="item-actions">
              <div class="score-badge ${scoreClass}">${item.score}</div>
              <button class="btn-flag ${isFlagged ? 'flagged' : ''}" onclick="toggleEarlyBrief('${item.id}', ${isFlagged})">
                ${isFlagged ? '⭐ Flagged' : '☆ Flag'}
              </button>
            </div>
          </div>
        `;
      }).join('');

      updateStats();
    }

    function renderEarlyBrief(items) {
      const container = document.getElementById('early-brief-list');

      if (items.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">⭐</div>
            <h3 class="empty-state-title">Pas d'articles marqués</h3>
            <p class="empty-state-desc">Marquez des articles pour l'Early Brief en cliquant l'icône ⭐</p>
          </div>
        `;
        return;
      }

      // Sort by score descending
      items.sort((a, b) => b.score - a.score);

      container.innerHTML = items.map(item => {
        const scoreClass = item.score < 20 ? 'score-low' : item.score < 40 ? 'score-mid' : item.score < 60 ? 'score-high' : 'score-critical';
        const sourceType = item.source_type?.toLowerCase() || 'rss';

        return `
          <div class="item-card">
            <div class="item-content">
              <div class="item-header">
                <h3 class="item-title">
                  <a href="${item.url}" target="_blank" rel="noopener">${item.title}</a>
                </h3>
              </div>

              <div class="item-meta">
                <span class="pill pill-${sourceType}">${sourceType.toUpperCase()}</span>
                <span class="pill pill-source">${item.source_name}</span>
                <span class="pill pill-category">${item.category}</span>
              </div>

              ${item.summary ? `<p class="item-summary">${escapeHtml(item.summary)}</p>` : ''}

              <div class="item-footer">
                <span class="item-date">${formatDate(item.published_at)}</span>
              </div>
            </div>

            <div class="item-actions">
              <div class="score-badge ${scoreClass}">${item.score}</div>
              <button class="btn-flag flagged" onclick="toggleEarlyBrief('${item.id}', true)">
                ⭐ Unflag
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    function renderDigest(data) {
      document.getElementById('digest-period-val').textContent = data.period_days;
      document.getElementById('digest-count-val').textContent = data.count;

      const container = document.getElementById('digest-list');
      const items = data.top_items || [];

      if (items.length === 0) {
        container.innerHTML = `
          <div class="empty-state">
            <div class="empty-state-icon">📊</div>
            <h3 class="empty-state-title">Aucune donnée</h3>
            <p class="empty-state-desc">Charger les sources pour générer le digest</p>
          </div>
        `;
        return;
      }

      container.innerHTML = items.map(item => {
        const scoreClass = item.score < 20 ? 'score-low' : item.score < 40 ? 'score-mid' : item.score < 60 ? 'score-high' : 'score-critical';
        const sourceType = item.source_type?.toLowerCase() || 'rss';

        return `
          <div class="item-card">
            <div class="item-content">
              <div class="item-header">
                <h3 class="item-title">
                  <a href="${item.url}" target="_blank" rel="noopener">${item.title}</a>
                </h3>
              </div>

              <div class="item-meta">
                <span class="pill pill-${sourceType}">${sourceType.toUpperCase()}</span>
                <span class="pill pill-source">${item.source_name}</span>
                <span class="pill pill-category">${item.category}</span>
              </div>

              ${item.summary ? `<p class="item-summary">${escapeHtml(item.summary)}</p>` : ''}

              <div class="item-footer">
                <span class="item-date">${formatDate(item.published_at)}</span>
                ${item.author ? `<span>By ${escapeHtml(item.author)}</span>` : ''}
              </div>
            </div>

            <div class="item-actions">
              <div class="score-badge ${scoreClass}">${item.score}</div>
            </div>
          </div>
        `;
      }).join('');
    }

    function renderSources() {
      const container = document.getElementById('sources-list');

      if (state.sources.length === 0) {
        container.innerHTML = `
          <div class="empty-state" style="grid-column: 1 / -1;">
            <div class="empty-state-icon">🌐</div>
            <h3 class="empty-state-title">No sources</h3>
            <p class="empty-state-desc">Click "🌱 Seed all sources" to add pre-configured sources or create one manually</p>
          </div>
        `;
        return;
      }

      container.innerHTML = state.sources.map(source => {
        const typeBadge = source.source_type === 'rss' ? 'pill-rss' : source.source_type === 'press' ? 'pill-press' : 'pill-gmail';
        const typeLabel = source.source_type === 'rss' ? 'RSS' : source.source_type === 'press' ? 'Presse' : 'Gmail';

        return `
          <div class="source-card">
            <h3 class="source-name">${source.name}</h3>
            <div class="source-info">
              <div class="source-meta">
                <span class="pill ${typeBadge}">${typeLabel}</span>
                <span class="pill pill-category">${source.category}</span>
              </div>
              <div class="source-url">${escapeHtml(source.url)}</div>
              <div class="source-count">Articles: ${source.article_count || 0}</div>
            </div>
            <div class="source-actions">
              ${source.source_type !== 'gmail' ? `<button class="btn-small btn-text" onclick="ingestSource('${source.id}')">Ingest</button>` : ''}
              <button class="btn-small btn-text" onclick="deleteSource('${source.id}')">Delete</button>
            </div>
          </div>
        `;
      }).join('');
    }

    function updateCategoryFilter() {
      state.categories.clear();
      state.items.forEach(item => {
        if (item.category) state.categories.add(item.category);
      });

      const select = document.getElementById('filter-category');
      const current = select.value;
      select.innerHTML = '<option value="">Toutes</option>' +
        Array.from(state.categories).sort().map(cat =>
          `<option value="${cat}">${cat}</option>`
        ).join('');
      select.value = current;
    }

    function updateStats() {
      const items = state.items;
      document.getElementById('stat-items').textContent = items.length;
      document.getElementById('stat-important').textContent = items.filter(i => i.status === 'important').length;
      document.getElementById('stat-sources').textContent = state.sources.length;
    }

    function cycleStatus(id, currentStatus) {
      const cycle = ['new', 'important', 'reviewed', 'archived'];
      const idx = cycle.indexOf(currentStatus);
      const next = cycle[(idx + 1) % cycle.length];
      updateItemStatus(id, next);
    }

    function formatDate(dateStr) {
      if (!dateStr) return '';
      const d = new Date(dateStr);
      const now = new Date();
      const diff = now - d;
      const days = Math.floor(diff / 86400000);

      if (days === 0) return "Aujourd" + "'" + "hui";
      if (days === 1) return 'Hier';
      if (days < 7) return `${days}j`;

      return d.toLocaleDateString('fr-FR', { month: 'short', day: 'numeric' });
    }

    function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
    }

    async function ingestSource(id) {
      try {
        const res = await fetch(`/ingest/rss/${id}`, { method: 'POST' });
        if (!res.ok) throw new Error('Ingest failed');
        const result = await res.json();
        showToast(`✅ Ingested ${result.created} articles`);
        await fetchItems();
        await fetchSources();
      } catch (err) {
        console.error(err);
        showToast('Failed to ingest source', true);
      }
    }

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const tab = btn.dataset.tab;
        state.currentTab = tab;

        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        btn.classList.add('active');
        document.getElementById(`tab-${tab}`).classList.add('active');

        if (tab === 'early-brief') {
          await fetchEarlyBrief();
        } else if (tab === 'digest') {
          await fetchDigest(state.digestPeriod);
        }
      });
    });

    // Event listeners
    document.getElementById('search-input').addEventListener('input', debounce(e => {
      state.searchQuery = e.target.value;
      fetchItems(state.searchQuery);
    }, 300));

    document.getElementById('filter-category').addEventListener('change', e => {
      state.filters.category = e.target.value;
      renderItems();
    });

    document.getElementById('filter-status').addEventListener('change', e => {
      state.filters.status = e.target.value;
      renderItems();
    });

    document.getElementById('filter-score-min').addEventListener('change', e => {
      state.filters.scoreMin = parseInt(e.target.value);
      renderItems();
    });

    document.getElementById('filter-sort').addEventListener('change', e => {
      state.filters.sort = e.target.value;
      renderItems();
    });

    document.getElementById('refresh-all-btn').addEventListener('click', refreshAllSources);

    document.getElementById('seed-sources-btn').addEventListener('click', seedSources);

    document.getElementById('toggle-add-source-btn').addEventListener('click', () => {
      const form = document.getElementById('add-source-form');
      form.style.display = form.style.display === 'none' ? 'block' : 'none';
    });

    document.getElementById('cancel-add-source-btn').addEventListener('click', () => {
      document.getElementById('add-source-form').style.display = 'none';
      document.getElementById('source-form').reset();
    });

    document.getElementById('source-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(e.target);
      const data = {
        name: document.getElementById('source-name').value,
        source_type: document.getElementById('source-type').value,
        url: document.getElementById('source-url').value,
        category: document.getElementById('source-category').value
      };

      try {
        const res = await fetch('/sources', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error('Create failed');
        showToast('✅ Source created');
        e.target.reset();
        document.getElementById('add-source-form').style.display = 'none';
        await fetchSources();
      } catch (err) {
        console.error(err);
        showToast('Failed to create source', true);
      }
    });

    // Digest period buttons
    document.querySelectorAll('[data-period]').forEach(btn => {
      btn.addEventListener('click', async () => {
        document.querySelectorAll('[data-period]').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        state.digestPeriod = parseInt(btn.dataset.period);
        await fetchDigest(state.digestPeriod);
      });
    });

    // Initialize
    (async () => {
      await fetchItems();
      await fetchSources();
      await checkGmailStatus();
    })();
  </script>
</body>
</html>
"""
