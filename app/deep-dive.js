function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>'"]/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  })[character]);
}

const SECTION_LABELS = {
  advancedClinicalDetail: 'Advanced clinical detail',
  practicalExample: 'Worked clinical example',
  limitationsCautions: 'Limits & cautions',
  whyPsychologistsCare: 'Why psychologists care',
  whenItGoesWrong: 'When it goes wrong',
  clinicalPearl: 'Clinical pearl'
};

const ORDER = [
  'advancedClinicalDetail',
  'practicalExample',
  'whyPsychologistsCare',
  'whenItGoesWrong',
  'clinicalPearl',
  'limitationsCautions'
];

function authoredSections(details) {
  const sections = details?.sections;
  if (!sections || Array.isArray(sections)) return [];
  return ORDER.filter(key => sections[key]).map(key => ({
    label: SECTION_LABELS[key],
    body: sections[key],
  }));
}

function derivedSections(details) {
  const sections = [];
  const mechanism = Array.isArray(details?.mechanismMap) ? details.mechanismMap : [];
  if (mechanism.length) {
    sections.push({
      label: 'Mechanism map',
      list: mechanism.map(item => `${item.label}: ${item.detail}`),
    });
  }
  const prompts = Array.isArray(details?.reviewPrompts) ? details.reviewPrompts.slice(0, 4) : [];
  if (prompts.length) {
    sections.push({
      label: 'Retrieval prompts',
      list: prompts.map(item => `${item.prompt} — ${item.answer}`),
    });
  }
  const references = Array.isArray(details?.references) ? details.references : [];
  if (references.length) {
    sections.push({
      label: 'Evidence trail',
      list: references.map(item => `${item.type || 'Reference'}: ${item.citation}`),
    });
  }
  return sections;
}

function deepDiveSections(details) {
  const authored = authoredSections(details);
  const derived = derivedSections(details);
  if (authored.length) {
    const hasEvidence = authored.some(item => item.label === 'Limits & cautions');
    return hasEvidence ? authored : [...authored, ...derived.filter(item => item.label === 'Evidence trail')];
  }
  return derived;
}

export function hasDeepDive(details) {
  return deepDiveSections(details).length > 0;
}

export function renderDeepDiveButton(details) {
  if (!hasDeepDive(details)) return '';
  const authored = authoredSections(details).length > 0;
  const hint = authored
    ? 'Open the fuller clinical explanation without crowding the main concept.'
    : 'Open mechanism, retrieval prompts and the evidence trail.';
  return `<div class="deep-dive-launch"><button class="secondary" data-open-deep-dive>Deep dive</button><span>${escapeHTML(hint)}</span></div>`;
}

function renderSection(section) {
  if (section.list) {
    return `<section class="deep-dive-section"><h3>${escapeHTML(section.label)}</h3><ul>${section.list.map(item => `<li>${escapeHTML(item)}</li>`).join('')}</ul></section>`;
  }
  return `<section class="deep-dive-section"><h3>${escapeHTML(section.label)}</h3><p>${escapeHTML(section.body)}</p></section>`;
}

function ensureDialog() {
  let dialog = document.querySelector('#deepDiveDialog');
  if (dialog) return dialog;
  dialog = document.createElement('dialog');
  dialog.id = 'deepDiveDialog';
  dialog.className = 'deep-dive-dialog';
  dialog.setAttribute('aria-labelledby', 'deepDiveTitle');
  dialog.innerHTML = '<div class="deep-dive-shell"><div class="dialog-head"><div><div class="eyebrow">Secondary clinical layer</div><h2 id="deepDiveTitle">Deep dive</h2></div><button type="button" data-close-deep-dive aria-label="Close deep dive">×</button></div><div id="deepDiveBody" class="deep-dive-body"></div></div>';
  document.body.appendChild(dialog);
  dialog.querySelector('[data-close-deep-dive]').onclick = () => dialog.close();
  dialog.addEventListener('click', event => {
    if (event.target === dialog) dialog.close();
  });
  return dialog;
}

export function bindDeepDive(root, details, conceptTitle) {
  const button = root?.querySelector('[data-open-deep-dive]');
  if (!button || !hasDeepDive(details)) return;
  button.onclick = () => {
    const dialog = ensureDialog();
    const sections = deepDiveSections(details);
    dialog.querySelector('#deepDiveTitle').textContent = conceptTitle;
    dialog.querySelector('#deepDiveBody').innerHTML = sections.map(renderSection).join('');
    const restoreFocus = () => {
      dialog.removeEventListener('close', restoreFocus);
      button.focus();
    };
    dialog.addEventListener('close', restoreFocus);
    dialog.showModal();
    dialog.querySelector('[data-close-deep-dive]').focus();
  };
}
