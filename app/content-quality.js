function escapeHTML(value) {
  return String(value ?? '').replace(/[&<>'"]/g, character => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
  })[character]);
}

function explicitBoundary(details) {
  const sections = details?.sections;
  if (sections && !Array.isArray(sections)) {
    if (sections.limitationsCautions) return sections.limitationsCautions;
    if (sections.whenItGoesWrong) return sections.whenItGoesWrong;
  }
  const mechanism = Array.isArray(details?.mechanismMap) ? details.mechanismMap : [];
  const boundary = mechanism.find(item => /boundary|limit|caution|scope/i.test(item?.label || ''));
  return boundary?.detail || '';
}

export function contentQuality(details) {
  const references = Array.isArray(details?.references) ? details.references : [];
  const objectives = Array.isArray(details?.learningObjectives) ? details.learningObjectives : [];
  const boundary = explicitBoundary(details);
  return {
    sourceCount: references.length,
    objectiveCount: objectives.length,
    hasBoundary: Boolean(boundary),
    boundary,
    deepDiveAuthored: Boolean(details?.sections && !Array.isArray(details.sections)),
  };
}

export function renderContentQualitySummary(details) {
  const quality = contentQuality(details);
  const sourceLabel = `${quality.sourceCount} source${quality.sourceCount === 1 ? '' : 's'}`;
  const limitLabel = quality.hasBoundary ? 'Explicit limits stated' : 'Contextual interpretation required';
  return `<aside class="content-quality" aria-label="Evidence and scope"><span class="content-quality-label">Evidence &amp; scope</span><span>${escapeHTML(sourceLabel)}</span><span aria-hidden="true">·</span><span>${escapeHTML(limitLabel)}</span></aside>`;
}

export function searchableDetailText(details) {
  if (!details) return [];
  const mechanism = (details.mechanismMap || []).flatMap(item => [item?.label, item?.detail]);
  const prompts = (details.reviewPrompts || []).flatMap(item => [item?.prompt, item?.answer]);
  const sections = details.sections && !Array.isArray(details.sections)
    ? Object.values(details.sections)
    : [];
  return [
    ...(details.learningObjectives || []),
    ...(details.tags || []),
    ...(details.searchTerms || []),
    ...mechanism,
    ...prompts,
    ...sections,
  ].filter(Boolean);
}
