const P8 = Object.freeze({ release: '1.0.0-rc1', phase: 'P8', featureFreeze: true });

function downloadJson(filename, payload) {
  const blob = new Blob([`${JSON.stringify(payload, null, 2)}\n`], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

function installRcMetadata() {
  window.NeuroAtlasReleaseCandidate = P8;
  const footer = document.querySelector('.release-footer');
  if (!footer || footer.querySelector('.rc-meta')) return;
  const meta = document.createElement('span');
  meta.className = 'rc-meta';
  meta.textContent = 'v1.0.0-rc1 · feature frozen';
  footer.prepend(meta);
}

function installFeedback() {
  const nav = document.querySelector('.release-footer nav');
  if (!nav || document.querySelector('#betaFeedbackDialog')) return;
  const button = document.createElement('button');
  button.type = 'button';
  button.id = 'betaFeedbackButton';
  button.textContent = 'Beta feedback';
  nav.append(button);

  const dialog = document.createElement('dialog');
  dialog.id = 'betaFeedbackDialog';
  dialog.className = 'release-dialog beta-feedback-dialog';
  dialog.innerHTML = `
    <form method="dialog" class="dialog-head"><h2>Beta feedback</h2><button aria-label="Close beta feedback">×</button></form>
    <form id="betaFeedbackForm" class="feedback-grid">
      <p>Export a local feedback file. Nothing is transmitted automatically.</p>
      <label>Area<select name="area"><option>General</option><option>Clinical content</option><option>Assessment</option><option>Accessibility</option><option>Performance / offline</option><option>Bug</option></select></label>
      <label>Severity<select name="severity"><option>Suggestion</option><option>Minor</option><option>Major</option><option>Release blocker</option></select></label>
      <label>Feedback<textarea name="feedback" required></textarea></label>
      <button class="primary" type="submit">Export feedback JSON</button>
    </form>`;
  document.body.append(dialog);
  button.addEventListener('click', () => dialog.showModal());
  dialog.querySelector('#betaFeedbackForm').addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(event.currentTarget);
    downloadJson('neuro-atlas-beta-feedback.json', {
      release: P8.release,
      createdAt: new Date().toISOString(),
      area: data.get('area'), severity: data.get('severity'), feedback: data.get('feedback'),
      route: location.hash || 'home',
    });
    dialog.close();
  });
}

async function install() {
  installRcMetadata();
  installFeedback();

  // The release footer is installed by another productisation module and may
  // not exist yet when this module first executes. Retry when the DOM changes
  // instead of silently abandoning RC metadata/feedback installation.
  if (!document.querySelector('#betaFeedbackButton')) {
    const observer = new MutationObserver(() => {
      installRcMetadata();
      installFeedback();
      if (document.querySelector('#betaFeedbackButton')) observer.disconnect();
    });
    observer.observe(document.body || document.documentElement, {
      childList: true,
      subtree: true,
    });
    window.setTimeout(() => observer.disconnect(), 10000);
  }

  window.dispatchEvent(new CustomEvent('neuroatlas:release-candidate-ready', { detail: P8 }));
}

if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install, { once: true });
else install();
