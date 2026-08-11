const STORAGE_KEY = 'cna-assessment-v1';
const ASSIGNMENT_KEY = 'cna-assigned-pathway-v1';

const safeParse = (value, fallback) => {
  try {
    return JSON.parse(value) ?? fallback;
  } catch {
    return fallback;
  }
};

const readState = () => safeParse(localStorage.getItem(STORAGE_KEY), { attempts: [] });
const writeState = (value) => localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
const escapeHTML = (value) => String(value).replace(/[&<>'"]/g, (char) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;',
})[char]);

const PATHWAYS = Object.freeze([
  { id: 'localisation', label: 'Clinical localisation', domains: ['localisation'], description: 'Localise before assigning aetiology.' },
  { id: 'neuropsychology', label: 'Neuropsychological reasoning', domains: ['neuropsychology'], description: 'Interpret patterns, validity and state confounds.' },
  { id: 'eeg-qeeg', label: 'EEG / qEEG interpretation', domains: ['eeg-qeeg'], description: 'Signal interpretation with diagnostic guardrails.' },
  { id: 'neurofeedback', label: 'Neurofeedback evidence', domains: ['neurofeedback'], description: 'Separate protocol rationale from demonstrated efficacy.' },
  { id: 'trauma-emdr', label: 'Trauma / EMDR evidence', domains: ['trauma-emdr'], description: 'Separate clinical usefulness, efficacy and mechanism.' },
  { id: 'neurodevelopment', label: 'ASD / ADHD neuroscience', domains: ['neurodevelopment'], description: 'Avoid biomarker and reverse-inference errors.' },
  { id: 'integrated', label: 'Integrated clinical neuroscience', domains: ['integrated', 'localisation', 'neuropsychology', 'eeg-qeeg', 'neurofeedback', 'trauma-emdr', 'neurodevelopment'], description: 'Cross-domain reasoning at Apply level.' },
]);

let bank = [];
let evidenceById = new Map();
let currentCase = null;
let selectedChoice = null;
let selectedConfidence = null;
let activeDomain = 'all';

function assessmentStats() {
  const attempts = readState().attempts || [];
  const correct = attempts.filter((item) => item.correct).length;
  const accuracy = attempts.length ? Math.round((correct / attempts.length) * 100) : null;
  const highConfidenceErrors = attempts.filter((item) => !item.correct && item.confidence >= 3).length;
  return { attempts, correct, accuracy, highConfidenceErrors };
}

function caseScore(caseId) {
  const rows = assessmentStats().attempts.filter((item) => item.caseId === caseId);
  if (!rows.length) return { attempts: 0, accuracy: 0 };
  return {
    attempts: rows.length,
    accuracy: rows.filter((item) => item.correct).length / rows.length,
  };
}

function adaptiveCase() {
  const pool = bank.filter((item) => activeDomain === 'all' || item.domain === activeDomain);
  if (!pool.length) return null;
  return [...pool].sort((a, b) => {
    const aa = caseScore(a.id);
    const bb = caseScore(b.id);
    if (aa.attempts !== bb.attempts) return aa.attempts - bb.attempts;
    if (aa.accuracy !== bb.accuracy) return aa.accuracy - bb.accuracy;
    return b.difficulty - a.difficulty;
  })[0];
}

function evidenceMarkup(item) {
  return (item.evidenceIds || []).map((id) => {
    const source = evidenceById.get(id);
    if (!source) return '';
    const label = escapeHTML(source.citation || id);
    if (source.url) {
      return `<a href="${escapeHTML(source.url)}" target="_blank" rel="noopener noreferrer">${label} ↗</a>`;
    }
    return `<span>${label}</span>`;
  }).join('');
}

function remediationMarkup(item) {
  return (item.conceptIds || []).map((id) => (
    `<button type="button" class="secondary" data-remediate="${escapeHTML(id)}">Review ${escapeHTML(id.replaceAll('-', ' '))}</button>`
  )).join('');
}

function renderAssessment() {
  const dialog = document.querySelector('#assessmentStudio');
  if (!dialog) return;
  const stats = assessmentStats();
  if (!currentCase) currentCase = adaptiveCase();
  const item = currentCase;
  const body = dialog.querySelector('[data-assessment-body]');
  if (!item) {
    body.innerHTML = '<p>No assessment cases match this filter.</p>';
    return;
  }

  body.innerHTML = `
    <section class="assessment-summary" aria-label="Assessment progress">
      <div><strong>${stats.attempts.length}</strong><span>attempts</span></div>
      <div><strong>${stats.accuracy === null ? '—' : `${stats.accuracy}%`}</strong><span>accuracy</span></div>
      <div><strong>${stats.highConfidenceErrors}</strong><span>high-confidence errors</span></div>
    </section>
    <div class="assessment-toolbar">
      <label>Domain
        <select id="assessmentDomain">
          <option value="all">Adaptive mix</option>
          ${[...new Set(bank.map((x) => x.domain))].map((domain) => `<option value="${domain}" ${domain === activeDomain ? 'selected' : ''}>${domain.replaceAll('-', ' ')}</option>`).join('')}
        </select>
      </label>
      <button type="button" class="secondary" data-next-case>Next adaptive case</button>
    </div>
    <article class="assessment-case" data-case-id="${escapeHTML(item.id)}">
      <div class="evidence-meta"><span>${escapeHTML(item.domain)}</span><span>${escapeHTML(item.competency)}</span><span>Difficulty ${item.difficulty}</span></div>
      <h2>${escapeHTML(item.title)}</h2>
      <p>${escapeHTML(item.prompt)}</p>
      <fieldset class="assessment-choices">
        <legend>Choose the best answer</legend>
        ${item.choices.map((choice, index) => `<label><input type="radio" name="assessment-choice" value="${index}"> <span>${escapeHTML(choice)}</span></label>`).join('')}
      </fieldset>
      <fieldset class="confidence-choices">
        <legend>Confidence before feedback</legend>
        ${['Guessing', 'Unsure', 'Fairly sure', 'Certain'].map((label, index) => `<label><input type="radio" name="assessment-confidence" value="${index + 1}"> <span>${label}</span></label>`).join('')}
      </fieldset>
      <button type="button" class="primary" data-submit-assessment disabled>Check reasoning</button>
      <div class="assessment-feedback" data-assessment-feedback hidden></div>
    </article>`;

  selectedChoice = null;
  selectedConfidence = null;
  const submit = body.querySelector('[data-submit-assessment]');
  body.querySelectorAll('input[name="assessment-choice"]').forEach((input) => {
    input.addEventListener('change', () => {
      selectedChoice = Number(input.value);
      submit.disabled = selectedConfidence === null;
    });
  });
  body.querySelectorAll('input[name="assessment-confidence"]').forEach((input) => {
    input.addEventListener('change', () => {
      selectedConfidence = Number(input.value);
      submit.disabled = selectedChoice === null;
    });
  });
  body.querySelector('#assessmentDomain').addEventListener('change', (event) => {
    activeDomain = event.target.value;
    currentCase = null;
    renderAssessment();
  });
  body.querySelector('[data-next-case]').addEventListener('click', () => {
    const choices = bank.filter((candidate) => (activeDomain === 'all' || candidate.domain === activeDomain) && candidate.id !== currentCase?.id);
    currentCase = choices.length ? choices.sort(() => Math.random() - 0.5)[0] : adaptiveCase();
    renderAssessment();
  });
  submit.addEventListener('click', () => submitAssessment(item));
}

function submitAssessment(item) {
  if (selectedChoice === null || selectedConfidence === null) return;
  const correct = selectedChoice === item.correctIndex;
  const state = readState();
  state.attempts = state.attempts || [];
  state.attempts.push({
    caseId: item.id,
    domain: item.domain,
    competency: item.competency,
    correct,
    confidence: selectedConfidence,
    at: new Date().toISOString(),
  });
  writeState(state);

  const feedback = document.querySelector('#assessmentStudio [data-assessment-feedback]');
  feedback.hidden = false;
  feedback.innerHTML = `
    <h3>${correct ? 'Correct reasoning' : 'Recalibrate this reasoning step'}</h3>
    <p>${escapeHTML(item.rationale)}</p>
    <div class="assessment-remediation"><strong>Review the underlying concepts</strong>${remediationMarkup(item)}</div>
    <details open><summary>Evidence used for this explanation</summary><div class="assessment-evidence">${evidenceMarkup(item)}</div></details>`;
  feedback.querySelectorAll('[data-remediate]').forEach((button) => {
    button.addEventListener('click', () => {
      document.querySelector('#assessmentStudio')?.close();
      window.openAtlasConcept?.(button.dataset.remediate);
    });
  });
  document.querySelector('#assessmentStudio [data-submit-assessment]').disabled = true;
}

function learnerReport() {
  const progress = safeParse(localStorage.getItem('cna-progress'), {});
  const assessment = assessmentStats();
  const completed = Object.entries(progress).filter(([, value]) => value?.completed).map(([id]) => id);
  const byDomain = {};
  const byCompetency = {};
  for (const attempt of assessment.attempts) {
    const row = byDomain[attempt.domain] || { attempts: 0, correct: 0 };
    row.attempts += 1;
    row.correct += attempt.correct ? 1 : 0;
    byDomain[attempt.domain] = row;
    const skill = byCompetency[attempt.competency] || { attempts: 0, correct: 0 };
    skill.attempts += 1;
    skill.correct += attempt.correct ? 1 : 0;
    byCompetency[attempt.competency] = skill;
  }
  return {
    generatedAt: new Date().toISOString(),
    completedConcepts: completed,
    assessment: { ...assessment, byDomain, byCompetency },
  };
}

function download(name, content, type = 'application/json') {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = name;
  link.click();
  URL.revokeObjectURL(url);
}

function reportCsv(report) {
  const rows = [['domain', 'attempts', 'correct', 'accuracy']];
  for (const [domain, item] of Object.entries(report.assessment.byDomain || {})) {
    rows.push([domain, item.attempts, item.correct, item.attempts ? Math.round((item.correct / item.attempts) * 100) : 0]);
  }
  return rows.map((row) => row.join(',')).join('\n');
}

function renderEducator() {
  const dialog = document.querySelector('#educatorStudio');
  if (!dialog) return;
  const report = learnerReport();
  const assigned = safeParse(localStorage.getItem(ASSIGNMENT_KEY), null);
  dialog.querySelector('[data-educator-body]').innerHTML = `
    <section class="educator-grid">
      <article>
        <div class="eyebrow">Structured pathways</div>
        <h2>Assign a learning pathway</h2>
        <p>Pathways sequence existing evidence-mapped Atlas concepts and assessment domains. They do not create new clinical recommendations.</p>
        <div class="pathway-list">${PATHWAYS.map((pathway) => `<button type="button" class="pathway-card ${assigned?.id === pathway.id ? 'selected' : ''}" data-pathway="${pathway.id}"><strong>${pathway.label}</strong><span>${pathway.description}</span></button>`).join('')}</div>
      </article>
      <article>
        <div class="eyebrow">Local learner record</div>
        <h2>Progress export</h2>
        <p><strong>${report.completedConcepts.length}</strong> concepts completed · <strong>${report.assessment.attempts.length}</strong> advanced assessment attempts.</p>
        <div class="educator-actions">
          <button type="button" class="secondary" data-export-json>Export JSON</button>
          <button type="button" class="secondary" data-export-csv>Export CSV</button>
          <button type="button" class="secondary" data-print-report>Print report</button>
        </div>
        <p class="empty-note">Exports are portable learner records for educator/LMS workflows; they do not transmit data automatically.</p>
      </article>
    </section>
    <section class="assignment-status">
      <h2>Current assignment</h2>
      <p>${assigned ? `${escapeHTML(assigned.label)} assigned locally on this device.` : 'No pathway is currently assigned.'}</p>
      ${assigned ? '<button type="button" class="secondary" data-clear-assignment>Clear assignment</button>' : ''}
    </section>`;

  dialog.querySelectorAll('[data-pathway]').forEach((button) => {
    button.addEventListener('click', () => {
      const pathway = PATHWAYS.find((item) => item.id === button.dataset.pathway);
      localStorage.setItem(ASSIGNMENT_KEY, JSON.stringify({ ...pathway, assignedAt: new Date().toISOString() }));
      renderEducator();
    });
  });
  dialog.querySelector('[data-export-json]')?.addEventListener('click', () => download('neuroatlas-learner-report.json', JSON.stringify(report, null, 2)));
  dialog.querySelector('[data-export-csv]')?.addEventListener('click', () => download('neuroatlas-assessment-report.csv', reportCsv(report), 'text/csv'));
  dialog.querySelector('[data-print-report]')?.addEventListener('click', () => window.print());
  dialog.querySelector('[data-clear-assignment]')?.addEventListener('click', () => {
    localStorage.removeItem(ASSIGNMENT_KEY);
    renderEducator();
  });
}

function dialogShell(id, title, bodyAttr) {
  const dialog = document.createElement('dialog');
  dialog.id = id;
  dialog.className = 'p67-dialog';
  dialog.innerHTML = `<form method="dialog" class="dialog-head"><h1>${title}</h1><button aria-label="Close ${title}">×</button></form><div class="p67-dialog-body" ${bodyAttr}></div>`;
  document.body.append(dialog);
  return dialog;
}

function installEntryPoints() {
  const top = document.querySelector('.top-actions');
  if (top && !document.querySelector('#assessmentButton')) {
    const practice = document.createElement('button');
    practice.id = 'assessmentButton';
    practice.className = 'icon-button';
    practice.setAttribute('aria-label', 'Open advanced assessment');
    practice.textContent = '✓';
    practice.addEventListener('click', () => {
      currentCase = adaptiveCase();
      renderAssessment();
      document.querySelector('#assessmentStudio').showModal();
    });
    top.append(practice);
  }

  const footer = document.querySelector('.release-footer nav');
  if (footer && !document.querySelector('#educatorButton')) {
    const educator = document.createElement('button');
    educator.id = 'educatorButton';
    educator.type = 'button';
    educator.textContent = 'Educator tools';
    educator.addEventListener('click', () => {
      renderEducator();
      document.querySelector('#educatorStudio').showModal();
    });
    footer.prepend(educator);
  }
}

async function install() {
  try {
    const [bankResponse, evidenceResponse] = await Promise.all([
      fetch('./data/assessment-bank.json'),
      fetch('./data/evidence-library.json'),
    ]);
    if (!bankResponse.ok) return;
    bank = (await bankResponse.json()).cases || [];
    if (evidenceResponse.ok) {
      const evidence = await evidenceResponse.json();
      evidenceById = new Map((evidence.sources || []).map((source) => [source.id, source]));
    }
    dialogShell('assessmentStudio', 'Advanced clinical assessment', 'data-assessment-body');
    dialogShell('educatorStudio', 'Educator Studio', 'data-educator-body');
    installEntryPoints();
    new MutationObserver(installEntryPoints).observe(document.body, { childList: true, subtree: true });
    window.NeuroAtlasP67 = Object.freeze({ phase: 'P6-P7', cases: bank.length, pathways: PATHWAYS.length });
  } catch (error) {
    console.warn('P6-P7 learning tools unavailable', error);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', install, { once: true });
} else {
  install();
}
