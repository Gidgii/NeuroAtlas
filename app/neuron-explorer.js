const esc = value => String(value).replace(/[&<>'"]/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[char]));

export function renderNeuronExplorer(details) {
  if (!details?.anatomy?.length) return '';
  const buttons = details.anatomy.map((part, index) => `
    <button class="neuron-part ${index === 0 ? 'active' : ''}" data-neuron-part="${esc(part.id)}" aria-pressed="${index === 0}">
      <strong>${esc(part.label)}</strong><span>${esc(part.short)}</span>
    </button>`).join('');
  const first = details.anatomy[0];
  return `<section class="neuron-explorer" aria-labelledby="neuron-explorer-title">
    <div class="explorer-heading">
      <div><div class="eyebrow">Interactive anatomy</div><h2 id="neuron-explorer-title">Follow a signal through the neuron</h2></div>
      <button class="signal-button" data-run-neuron-signal><span aria-hidden="true">▶</span> Run signal</button>
    </div>
    <p class="explorer-instruction">${esc(details.interaction.instruction)}</p>
    <div class="neuron-canvas-wrap">
      <svg class="neuron-canvas" viewBox="0 0 1000 500" role="img" aria-labelledby="neuron-svg-title neuron-svg-desc">
        <title id="neuron-svg-title">Interactive multipolar neuron</title>
        <desc id="neuron-svg-desc">A labelled neuron showing dendrites, soma, axon hillock, myelinated axon, nodes of Ranvier and presynaptic terminals.</desc>
        <defs>
          <filter id="neuronGlow"><feGaussianBlur stdDeviation="4" result="blur"/><feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
          <linearGradient id="axonGradient" x1="0" x2="1"><stop stop-color="#50f1d2"/><stop offset="1" stop-color="#ffd166"/></linearGradient>
        </defs>
        <g class="neuron-structure part-dendrites" data-svg-part="dendrites" tabindex="0" role="button" aria-label="Dendrites: input branches">
          <path d="M270 240C205 205 185 140 120 105M210 205C155 200 115 170 70 170M220 265C155 285 120 340 65 365M285 185C260 120 280 80 250 38M270 300C250 365 280 405 250 465"/>
          <path d="M120 105 80 70M120 105l12-50M70 170 32-35M65 365l45-5M65 365l25 38M250 38l-35 28M250 465l-30-35"/>
        </g>
        <g class="neuron-structure part-soma" data-svg-part="soma" tabindex="0" role="button" aria-label="Soma: metabolic and integrative centre">
          <path class="soma-shape" d="M214 245c0-72 53-123 121-123 78 0 132 50 132 121 0 79-60 132-137 132-68 0-116-55-116-130Z"/>
          <circle class="nucleus-detail" cx="337" cy="246" r="46"/>
          <path class="organelle-detail" d="M265 210q30-25 48 5t-45 31m108 39q32-22 52 8t-43 29"/>
        </g>
        <path class="neuron-structure part-hillock" data-svg-part="hillock" tabindex="0" role="button" aria-label="Axon hillock: action-potential decision zone" d="M445 222c45 0 72 9 108 28-34 22-67 33-111 31Z"/>
        <path class="neuron-structure part-axon axon-core-detail" data-svg-part="axon" tabindex="0" role="button" aria-label="Axon: long-distance output cable" d="M520 255C650 255 745 250 887 250"/>
        <g class="neuron-structure part-myelin" data-svg-part="myelin" tabindex="0" role="button" aria-label="Myelin: insulating sheath">
          <rect x="555" y="218" width="92" height="70" rx="34"/><rect x="670" y="218" width="92" height="70" rx="34"/><rect x="785" y="218" width="92" height="70" rx="34"/>
        </g>
        <g class="neuron-structure part-nodes" data-svg-part="nodes" tabindex="0" role="button" aria-label="Nodes of Ranvier: signal regeneration points">
          <circle cx="658" cy="253" r="11"/><circle cx="773" cy="253" r="11"/>
        </g>
        <g class="neuron-structure part-terminals" data-svg-part="terminals" tabindex="0" role="button" aria-label="Presynaptic terminals: chemical output sites">
          <path d="M877 250c42 0 42-65 75-65m-75 65c42 0 42 65 75 65m-65-65h75"/>
          <circle cx="958" cy="185" r="17"/><circle cx="968" cy="250" r="17"/><circle cx="958" cy="315" r="17"/>
        </g>
        <circle class="travelling-signal" cx="500" cy="253" r="12" aria-hidden="true"/>
      </svg>
      <div class="signal-status" data-signal-status aria-live="polite">Ready: select a structure or run the signal.</div>
    </div>
    <div class="neuron-part-list" role="list">${buttons}</div>
    <article class="neuron-detail" data-neuron-detail aria-live="polite">
      <div class="eyebrow">${esc(first.short)}</div><h3>${esc(first.label)}</h3><p>${esc(first.detail)}</p><aside><strong>Clinical link</strong>${esc(first.clinical)}</aside>
    </article>
  </section>`;
}

export function bindNeuronExplorer(root, details) {
  if (!root || !details?.anatomy) return;
  const detail = root.querySelector('[data-neuron-detail]');
  const status = root.querySelector('[data-signal-status]');
  const signal = root.querySelector('.travelling-signal');
  const controls = [...root.querySelectorAll('[data-neuron-part]')];
  const svgParts = [...root.querySelectorAll('[data-svg-part]')];
  const select = id => {
    const part = details.anatomy.find(item => item.id === id);
    if (!part) return;
    controls.forEach(button => { const active = button.dataset.neuronPart === id; button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active)); });
    svgParts.forEach(node => node.classList.toggle('selected', node.dataset.svgPart === id));
    detail.innerHTML = `<div class="eyebrow">${esc(part.short)}</div><h3>${esc(part.label)}</h3><p>${esc(part.detail)}</p><aside><strong>Clinical link</strong>${esc(part.clinical)}</aside>`;
    status.textContent = `${part.label} selected. ${part.short}.`;
  };
  controls.forEach(button => button.addEventListener('click', () => select(button.dataset.neuronPart)));
  svgParts.forEach(node => {
    node.addEventListener('click', () => select(node.dataset.svgPart));
    node.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); select(node.dataset.svgPart); } });
  });
  root.querySelector('[data-run-neuron-signal]')?.addEventListener('click', button => {
    signal.classList.remove('running'); void signal.getBoundingClientRect(); signal.classList.add('running');
    button.currentTarget.disabled = true;
    details.interaction.signalSteps.forEach((step, index) => setTimeout(() => { status.textContent = `Step ${index + 1}: ${step}`; }, index * 900));
    setTimeout(() => { button.currentTarget.disabled = false; status.textContent = 'Signal complete: electrical integration became chemical communication.'; }, details.interaction.signalSteps.length * 900);
  });
}
