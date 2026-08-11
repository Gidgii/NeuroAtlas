const RELEASE = Object.freeze({
  phase: 'P5',
  label: 'Polish & release-readiness',
  evidencePolicy: 'Evidence-linked factual content with higher-tier sourcing for clinical claims',
});

const emit = (name, detail = {}) => {
  window.dispatchEvent(new CustomEvent(`neuroatlas:${name}`, { detail }));
};

async function loadConceptMeta() {
  try {
    const response = await fetch('./data/details-bundle.json');
    if (!response.ok) return new Map();
    const bundle = await response.json();
    return new Map(
      Object.entries(bundle).map(([id, record]) => [
        id,
        {
          module: record.module || '',
          tags: Array.isArray(record.tags) ? record.tags : [],
        },
      ]),
    );
  } catch {
    return new Map();
  }
}

function categoryFor(meta) {
  const haystack = `${meta?.module || ''} ${(meta?.tags || []).join(' ')}`.toLowerCase();
  if (haystack.includes('trauma') || haystack.includes('emdr')) return 'trauma';
  if (haystack.includes('neurofeedback')) return 'neurofeedback';
  if (haystack.includes('eeg') || haystack.includes('qeeg')) return 'eeg';
  if (haystack.includes('anatomy') || haystack.includes('atlas')) return 'anatomy';
  if (haystack.includes('neuropsych') || haystack.includes('clinical')) return 'clinical';
  return 'core';
}

function installSearchScope(metaById) {
  const field = document.querySelector('.search-field');
  const results = document.querySelector('#searchResults');
  if (!field || !results || document.querySelector('#searchScope')) return;

  const control = document.createElement('label');
  control.className = 'search-scope';
  control.innerHTML = `
    <span>Scope</span>
    <select id="searchScope" aria-label="Filter search by topic">
      <option value="all">All topics</option>
      <option value="core">Core neuroscience</option>
      <option value="anatomy">Anatomy atlas</option>
      <option value="clinical">Clinical & neuropsychology</option>
      <option value="eeg">EEG / qEEG</option>
      <option value="neurofeedback">Neurofeedback</option>
      <option value="trauma">Trauma / EMDR</option>
    </select>`;
  field.insertAdjacentElement('afterend', control);

  const apply = () => {
    const scope = control.querySelector('select').value;
    results.querySelectorAll('[data-search-open]').forEach((button) => {
      const id = button.dataset.searchOpen;
      const category = categoryFor(metaById.get(id));
      button.hidden = scope !== 'all' && category !== scope;
    });
  };

  control.querySelector('select').addEventListener('change', () => {
    apply();
    emit('search-scope', { scope: control.querySelector('select').value });
  });

  new MutationObserver(apply).observe(results, { childList: true, subtree: true });
}

function legalDialog(id, title, href, summary) {
  const dialog = document.createElement('dialog');
  dialog.id = id;
  dialog.className = 'release-dialog';
  dialog.innerHTML = `
    <form method="dialog" class="dialog-head">
      <h2>${title}</h2>
      <button aria-label="Close ${title}">×</button>
    </form>
    <div class="release-dialog-body">
      <p>${summary}</p>
      <a class="primary release-link" href="${href}" target="_blank" rel="noopener">Open full ${title.toLowerCase()} ↗</a>
    </div>`;
  document.body.append(dialog);
  return dialog;
}

function installReleaseFooter() {
  if (document.querySelector('.release-footer')) return;
  const shell = document.querySelector('.app-shell');
  if (!shell) return;

  const footer = document.createElement('footer');
  footer.className = 'release-footer';
  footer.setAttribute('aria-label', 'Atlas information');
  footer.innerHTML = `
    <span>Evidence-linked educational atlas</span>
    <nav aria-label="Product information">
      <button type="button" data-release-dialog="privacyDialog">Privacy</button>
      <button type="button" data-release-dialog="accessibilityDialog">Accessibility</button>
      <button type="button" data-release-dialog="releaseDialog">About this release</button>
      <button type="button" id="installAtlas" hidden>Install app</button>
    </nav>`;
  shell.append(footer);

  legalDialog(
    'privacyDialog',
    'Privacy',
    './legal/privacy.html',
    'Learning progress and bookmarks are designed to remain on this device. The Atlas does not require patient information or an account.',
  );
  legalDialog(
    'accessibilityDialog',
    'Accessibility',
    './legal/accessibility.html',
    'The Atlas targets WCAG 2.2 Level AA practices and includes automated accessibility regression checks, without claiming third-party certification.',
  );
  legalDialog(
    'releaseDialog',
    'About this release',
    './legal/release.html',
    'P5 adds product polish, release governance, privacy and accessibility documentation, search scoping and installability hardening.',
  );

  footer.querySelectorAll('[data-release-dialog]').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelector(`#${button.dataset.releaseDialog}`)?.showModal();
    });
  });
}

function installPwaPrompt() {
  const button = document.querySelector('#installAtlas');
  if (!button) return;
  let promptEvent = null;
  window.addEventListener('beforeinstallprompt', (event) => {
    event.preventDefault();
    promptEvent = event;
    button.hidden = false;
  });
  button.addEventListener('click', async () => {
    if (!promptEvent) return;
    await promptEvent.prompt();
    const choice = await promptEvent.userChoice;
    emit('install-choice', { outcome: choice.outcome });
    if (choice.outcome === 'accepted') button.hidden = true;
    promptEvent = null;
  });
}

function installInteractionHooks() {
  document.addEventListener('click', (event) => {
    const button = event.target.closest('button, a');
    if (!button) return;
    const action =
      button.dataset.route ||
      button.dataset.routeGo ||
      button.dataset.open ||
      button.dataset.quiz ||
      button.id ||
      button.getAttribute('href') ||
      'interaction';
    emit('interaction', { action });
  });
}

async function install() {
  document.documentElement.lang = 'en-AU';
  window.NeuroAtlasRelease = RELEASE;
  const metaById = await loadConceptMeta();
  installSearchScope(metaById);
  installReleaseFooter();
  installPwaPrompt();
  installInteractionHooks();
  emit('release-ready', { phase: RELEASE.phase });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', install, { once: true });
} else {
  install();
}
