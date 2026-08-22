
const root = document.querySelector('#experienceRoot');
const app = document.querySelector('#app');

function focusFirstHeading() {
  const heading = root.querySelector('h1');
  if (heading) {
    heading.setAttribute('tabindex', '-1');
    heading.focus();
  }
}

function showSplash() {
  if (!root || !app) return;

  app.hidden = true;
  root.hidden = false;
  root.dataset.experienceStage = 'splash';

  root.innerHTML = `
    <section
      class="experience-screen experience-splash"
      data-experience-stage="splash"
      aria-labelledby="splashTitle"
    >
      <div class="splash-visual" data-artwork-status="structural-placeholder">
        <img
          src="./assets/illustrations/brain-overview.svg"
          alt=""
          aria-hidden="true"
        >
      </div>

      <div class="splash-copy">
        <p class="eyebrow">Clinical neuroscience, made navigable</p>
        <h1 id="splashTitle">Neuro Atlas</h1>
        <p>
          Learn the theory. Explore the brain. Move between both whenever
          understanding needs a spatial anchor.
        </p>

        <button
          type="button"
          class="primary experience-enter"
          data-enter-atlas
        >
          Enter Atlas
        </button>
      </div>
    </section>
  `;

  root.querySelector('[data-enter-atlas]').addEventListener(
    'click',
    showGateway,
  );

  focusFirstHeading();
}

function showGateway() {
  if (!root || !app) return;

  app.hidden = true;
  root.hidden = false;
  root.dataset.experienceStage = 'gateway';

  root.innerHTML = `
    <section
      class="experience-screen experience-gateway"
      data-experience-stage="gateway"
      aria-labelledby="gatewayTitle"
    >
      <header class="gateway-header">
        <p class="eyebrow">Choose how you want to learn</p>
        <h1 id="gatewayTitle">Where do you want to begin?</h1>
        <p>
          Both experiences are connected. You can move between conceptual
          learning and spatial exploration at any time.
        </p>
      </header>

      <div class="gateway-options">
        <button
          type="button"
          class="gateway-card"
          data-experience-mode="theory"
        >
          <span class="gateway-symbol" aria-hidden="true">≣</span>
          <span>
            <strong>Learn the Theory</strong>
            <small>
              Structured neuroscience, clinical concepts, evidence,
              deep dives, quizzes and mastery.
            </small>
          </span>
          <span class="gateway-arrow" aria-hidden="true">→</span>
        </button>

        <button
          type="button"
          class="gateway-card"
          data-experience-mode="brain"
        >
          <span class="gateway-symbol" aria-hidden="true">◎</span>
          <span>
            <strong>Explore the Brain</strong>
            <small>
              Interactive anatomy, structures, circuits, pathways,
              networks and whole-brain reasoning.
            </small>
          </span>
          <span class="gateway-arrow" aria-hidden="true">→</span>
        </button>
      </div>

      <button
        type="button"
        class="secondary gateway-back"
        data-back-splash
      >
        Back
      </button>
    </section>
  `;

  root.querySelector('[data-back-splash]').addEventListener(
    'click',
    showSplash,
  );

  root.querySelectorAll('[data-experience-mode]').forEach((button) => {
    button.addEventListener('click', () => {
      enterMode(button.dataset.experienceMode);
    });
  });

  focusFirstHeading();
}

function enterMode(mode) {
  if (!root || !app) return;

  const selected = mode === 'brain' ? 'brain' : 'theory';

  root.hidden = true;
  delete root.dataset.experienceStage;
  root.innerHTML = '';

  app.hidden = false;

  if (typeof window.NeuroAtlasOpenMode === 'function') {
    window.NeuroAtlasOpenMode(selected);
  } else {
    window.dispatchEvent(
      new CustomEvent('neuroatlas:experience-mode', {
        detail: {mode: selected},
      }),
    );
  }

  requestAnimationFrame(() => {
    document.querySelector('#main h1')?.focus();
  });
}

function installExperienceShell() {
  if (!root || !app) return;

  app.hidden = true;

  if (window.NeuroAtlasAcknowledgement?.accepted) {
    showSplash();
    return;
  }

  window.addEventListener(
    'neuroatlas:acknowledgement',
    (event) => {
      if (event.detail?.accepted) {
        showSplash();
      }
    },
    {once: true},
  );
}

window.NeuroAtlasExperience = Object.freeze({
  showSplash,
  showGateway,
  enterMode,
});

if (document.readyState === 'loading') {
  document.addEventListener(
    'DOMContentLoaded',
    installExperienceShell,
    {once: true},
  );
} else {
  installExperienceShell();
}
