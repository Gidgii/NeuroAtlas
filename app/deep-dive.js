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

export function hasDeepDive(details) {
  const sections = details?.sections;
  return Boolean(sections && !Array.isArray(sections) && ORDER.some(key => sections[key]));
}

export function renderDeepDiveButton(details) {
  if (!hasDeepDive(details)) return '';
  return `<div class="deep-dive-launch"><button class="secondary" data-open-deep-dive>Deep dive</button><span>Open the fuller clinical explanation without crowding the main concept.</span></div>`;
}

function ensureDialog() {
  let dialog = document.querySelector('#deepDiveDialog');
  if (dialog) return dialog;
  dialog = document.createElement('dialog');
  dialog.id = 'deepDiveDialog';
  dialog.className = 'deep-dive-dialog';
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
    const sections = details.sections;
    dialog.querySelector('#deepDiveTitle').textContent = conceptTitle;
    dialog.querySelector('#deepDiveBody').innerHTML = ORDER
      .filter(key => sections[key])
      .map(key => `<section class="deep-dive-section"><h3>${escapeHTML(SECTION_LABELS[key])}</h3><p>${escapeHTML(sections[key])}</p></section>`)
      .join('');
    dialog.showModal();
    dialog.querySelector('[data-close-deep-dive]').focus();
  };
}
