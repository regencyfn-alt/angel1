// MICHRON PHYSICS - Shared Navigation Component
// Include this script in all pages to ensure consistent navigation
// Usage: <script src="nav.js"></script> (before closing </body>)

(function() {
  // Full navigation structure
  const NAV_ITEMS = [
    { href: 'index.html', label: 'Classic', title: 'ANGEL-1 Chronon Network' },
    { href: 'torsion-field.html', label: 'Torsion', title: 'Torsion Field Dynamics' },
    { href: 'breath-field.html', label: 'Breath', title: 'Breath Field Cycle' },
    { href: 'breath-field-sound.html', label: 'Breath+Sound', title: 'Breath Field with Audio' },
    { href: 'chronos.html', label: 'Chronos', title: 'Chronos Avatar' },
    { href: 'square_plaquettes.html', label: 'Square', title: 'Square Plaquette Flip' },
    { href: 'angel2_triangular.html', label: 'Triangle', title: 'Triangular Network' },
    { href: 'theater.html', label: 'Theater', title: 'Movie Perception System' },
    { href: 'orchestra.html', label: 'Orchestra', title: 'Multi-Agent Collaboration', hidden: true }
  ];

  // Get current page
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';

  // Inject CSS if not already present
  if (!document.getElementById('michron-nav-styles')) {
    const style = document.createElement('style');
    style.id = 'michron-nav-styles';
    style.textContent = `
      .michron-nav {
        background: linear-gradient(135deg, #1a1f2e 0%, #0f1620 100%);
        border-bottom: 2px solid #22303d;
        padding: 16px 24px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 12px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      }
      .michron-nav-brand {
        font-size: 20px;
        font-weight: 700;
        background: linear-gradient(135deg, #60a5fa 0%, #10b981 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
      }
      .michron-nav-links {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      .michron-nav-links a {
        padding: 8px 16px;
        border-radius: 6px;
        text-decoration: none;
        color: #9ca3af;
        font-size: 14px;
        font-weight: 500;
        transition: all 0.2s;
        border: 1px solid transparent;
      }
      .michron-nav-links a:hover {
        color: #e8ecef;
        background: rgba(96, 165, 250, 0.1);
        border-color: #22303d;
      }
      .michron-nav-links a.active {
        color: #60a5fa;
        background: rgba(96, 165, 250, 0.15);
        border-color: #60a5fa;
      }
      @media (max-width: 600px) {
        .michron-nav { padding: 12px 16px; }
        .michron-nav-brand { font-size: 16px; }
        .michron-nav-links a { padding: 6px 12px; font-size: 13px; }
      }
    `;
    document.head.appendChild(style);
  }

  // Build nav HTML
  function buildNav() {
    const links = NAV_ITEMS
      .filter(item => !item.hidden)
      .map(item => {
        const isActive = currentPage === item.href || 
                         (currentPage === '' && item.href === 'index.html');
        return `<a href="${item.href}" class="${isActive ? 'active' : ''}" title="${item.title}">${item.label}</a>`;
      }).join('\n        ');

    return `<nav class="michron-nav">
      <div class="michron-nav-brand">MICHRON PHYSICS</div>
      <div class="michron-nav-links">
        ${links}
      </div>
    </nav>`;
  }

  // Inject or replace nav
  function injectNav() {
    // Find existing nav
    const existingNav = document.querySelector('nav.nav, nav.michron-nav, header nav');
    
    if (existingNav) {
      // Replace existing nav
      existingNav.outerHTML = buildNav();
    } else {
      // No nav found, inject at top of body
      document.body.insertAdjacentHTML('afterbegin', buildNav());
    }
  }

  // Run when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectNav);
  } else {
    injectNav();
  }
})();
