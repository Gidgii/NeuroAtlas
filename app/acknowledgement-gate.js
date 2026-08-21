const STORAGE_KEY = 'neuroatlas-acknowledgement';
const NOTICE_VERSION = '2026-08-21.1';
const APP_RELEASE = '1.0.0-rc1';

const REQUIRED_ACKNOWLEDGEMENTS = Object.freeze([
  'educational-use',
  'independent-verification',
  'accuracy-limitations',
  'no-client-data',
]);

function currentAcceptance() {
  try {
    const record = JSON.parse(localStorage.getItem(STORAGE_KEY));
    if (
      record &&
      record.noticeVersion === NOTICE_VERSION &&
      REQUIRED_ACKNOWLEDGEMENTS.every((item) =>
        Array.isArray(record.acknowledgements) &&
        record.acknowledgements.includes(item)
      )
    ) {
      return record;
    }
  } catch {
    // Invalid or cleared local state requires acknowledgement again.
  }
  return null;
}

function saveAcceptance() {
  const record = {
    schemaVersion: '1.0',
    noticeVersion: NOTICE_VERSION,
    appRelease: APP_RELEASE,
    acceptedAt: new Date().toISOString(),
    acknowledgements: [...REQUIRED_ACKNOWLEDGEMENTS],
    storageModel: 'local-device-only',
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify(record));
  return record;
}

function createGate() {
  const dialog = document.createElement('dialog');
  dialog.id = 'acknowledgementGate';
  dialog.className = 'acknowledgement-gate';
  dialog.setAttribute('aria-labelledby', 'acknowledgementTitle');
  dialog.setAttribute('aria-describedby', 'acknowledgementIntro');

  dialog.innerHTML = `
    <form class="acknowledgement-card">
      <p class="eyebrow">Before entering Neuro Atlas</p>
      <h1 id="acknowledgementTitle">Please acknowledge</h1>
      <p id="acknowledgementIntro">
        Neuro Atlas is an educational clinical neuroscience resource.
        Please confirm each point before continuing.
      </p>

      <fieldset class="acknowledgement-list">
        <legend class="visually-hidden">Required acknowledgements</legend>

        <label>
          <input type="checkbox" data-ack="educational-use">
          <span>
            <strong>Educational use only.</strong>
            Neuro Atlas is not medical, psychological, diagnostic or treatment advice,
            and does not replace individual assessment or professional judgement.
          </span>
        </label>

        <label>
          <input type="checkbox" data-ack="independent-verification">
          <span>
            <strong>I will verify clinical information.</strong>
            I will check appropriate current sources, guidelines, training and supervision
            before relying on Atlas content in clinical decisions.
          </span>
        </label>

        <label>
          <input type="checkbox" data-ack="accuracy-limitations">
          <span>
            <strong>Content may change or contain errors.</strong>
            Neuroscience evidence evolves and, despite review, information may contain
            errors, omissions or become outdated. I will not use Neuro Atlas as my sole source.
          </span>
        </label>

        <label>
          <input type="checkbox" data-ack="no-client-data">
          <span>
            <strong>No patient or client information.</strong>
            I will not enter names, health records, case notes or other identifying
            patient/client information into Neuro Atlas.
          </span>
        </label>
      </fieldset>

      <p class="acknowledgement-feedback">
        Found something inaccurate or not working? Feedback is welcomed and helps improve the Atlas.
      </p>

      <p class="acknowledgement-links">
        <a href="./legal/disclaimer.html" target="_blank" rel="noopener">
          Read the full educational use &amp; disclaimer notice
        </a>
        ·
        <a href="./legal/privacy.html" target="_blank" rel="noopener">
          Privacy
        </a>
      </p>

      <button type="submit" class="primary acknowledgement-enter" disabled>
        Acknowledge &amp; enter
      </button>
    </form>
  `;

  dialog.addEventListener('cancel', (event) => {
    event.preventDefault();
  });

  const checks = [...dialog.querySelectorAll('[data-ack]')];
  const enter = dialog.querySelector('.acknowledgement-enter');

  const update = () => {
    enter.disabled = !checks.every((checkbox) => checkbox.checked);
  };

  checks.forEach((checkbox) => checkbox.addEventListener('change', update));

  dialog.querySelector('form').addEventListener('submit', (event) => {
    event.preventDefault();

    if (!checks.every((checkbox) => checkbox.checked)) return;

    const record = saveAcceptance();
    dialog.close();
    dialog.remove();

    window.dispatchEvent(
      new CustomEvent('neuroatlas:acknowledgement', {
        detail: {
          accepted: true,
          noticeVersion: record.noticeVersion,
          acceptedAt: record.acceptedAt,
        },
      })
    );
  });

  document.body.append(dialog);
  dialog.showModal();
}

function installAcknowledgementGate() {
  const existing = currentAcceptance();

  window.NeuroAtlasAcknowledgement = Object.freeze({
    noticeVersion: NOTICE_VERSION,
    storageKey: STORAGE_KEY,
    accepted: Boolean(existing),
    record: existing,
  });

  if (existing) return;

  createGate();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', installAcknowledgementGate, {
    once: true,
  });
} else {
  installAcknowledgementGate();
}
