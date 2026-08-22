import {SpacedRepetition} from './spaced-repetition.js';
import {MasteryTracker} from './mastery-tracker.js';
import {CompetencyTracker, COMPETENCIES} from './competency-tracker.js';
import {CalibrationTracker, CONFIDENCE_LEVELS} from './calibration-tracker.js';
import {renderDeepDiveButton, bindDeepDive} from './deep-dive.js';
import {renderContentQualitySummary, searchableDetailText} from './content-quality.js';
import {focusMainHeading, installAccessibilityRuntime} from './accessibility-runtime.js';
import {hasVisualScene, renderVisualScene} from './visual-scenes.js';
import {renderNeuronExplorer, bindNeuronExplorer} from './neuron-explorer.js';
import {renderAstrocyteExplorer, bindAstrocyteExplorer} from './astrocyte-explorer.js';
import {renderMicrogliaExplorer, bindMicrogliaExplorer} from './microglia-explorer.js';
import {renderOligodendrocyteExplorer, bindOligodendrocyteExplorer} from './oligodendrocyte-explorer.js';
import {renderSystemExplorer, bindSystemExplorer} from './system-explorer.js';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const store={get(k,f){try{return JSON.parse(localStorage.getItem(k))??f}catch{return f}},set(k,v){localStorage.setItem(k,JSON.stringify(v))}};
const state={route:'home',mode:'theory',pendingMode:null,bridgeFrom:null,level:null,concept:null,tab:'simple',visualOpen:false,curriculum:null,details:{},brainBridge:null,progress:store.get('cna-progress',{}),bookmarks:new Set(store.get('cna-bookmarks',[])),last:store.get('cna-last',null),review:new SpacedRepetition(),mastery:new MasteryTracker(),competency:new CompetencyTracker(),calibration:new CalibrationTracker(),reviewFocus:null,reviewSkill:null,reviewConfidence:null,evidenceLibrary:null,evidenceReview:null};
const labels={simple:'Explain Simply',psych:'Explain Like a Psychologist',advanced:'Advanced Clinical Detail',analogy:'Think Of It Like…',care:'Why Psychologists Care',wrong:'When It Goes Wrong',pearl:'Clinical Pearl'};
const main=$('#main');
const escapeHTML=s=>String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));
function toast(message){const el=$('#toast');el.textContent=message;el.classList.add('show');clearTimeout(toast.t);toast.t=setTimeout(()=>el.classList.remove('show'),1800)}
function concepts(level=null){return state.curriculum.concepts.filter(c=>!level||c.level===level).sort((a,b)=>a.level-b.level||a.order-b.order)}
function completed(id){return !!state.progress[id]?.completed}
function levelPct(level){const list=concepts(level);return Math.round(list.filter(c=>completed(c.id)).length/list.length*100)}
function saveProgress(){store.set('cna-progress',state.progress)}
function setRoute(route,data={}){
  if(route==='brain')state.mode='brain';
  if(route==='home'||route==='learn')state.mode='theory';
  state.route=route;
  Object.assign(state,data);
  render();
  focusMainHeading(main);
  window.scrollTo({top:0,behavior:'instant'})
}
window.openAtlasConcept=id=>setRoute('concept',{
  concept:id,
  tab:'simple',
  visualOpen:false,
  mode:'theory',
  bridgeFrom:null
});
window.NeuroAtlasOpenMode=mode=>{
  const selected=mode==='brain'?'brain':'theory';
  if(!state.curriculum){
    state.pendingMode=selected;
    return;
  }
  setRoute(selected==='brain'?'brain':'home',{
    level:null,
    bridgeFrom:null,
    mode:selected
  });
};
window.addEventListener('neuroatlas:experience-mode',event=>{
  window.NeuroAtlasOpenMode(event.detail?.mode);
});
function updateNav(){ $$('.nav-item').forEach(b=>{const active=b.dataset.route===state.route||(state.route==='concept'&&state.mode==='theory'&&b.dataset.route==='learn')||(state.route==='concept'&&state.mode==='brain'&&b.dataset.route==='brain');b.classList.toggle('active',active)}); const n=state.review.countDue(concepts().map(c=>c.id)); const badge=$('#reviewBadge');badge.textContent=n;badge.hidden=!n}
function home(){const resume=state.last&&concepts().find(c=>c.id===state.last);return `<section class="hero-home"><div class="eyebrow">Designed for psychology in practice</div><h1>See the brain differently.</h1><p>Build a clinically useful model of cells, systems and networks—one concise concept at a time.</p></section>${resume?`<button class="resume-card" data-open="${resume.id}"><div><div class="eyebrow">Pick up where you left off</div><h2>${escapeHTML(resume.title)}</h2><p>Level ${resume.level} · ${escapeHTML(resume.subtitle)}</p></div><span class="primary">Resume</span></button>`:''}<div class="section-head"><h2>Learning pathway</h2><span>${concepts().filter(c=>completed(c.id)).length}/${concepts().length} complete</span></div><div class="level-list">${state.curriculum.levels.map(l=>`<button class="level-card" data-level="${l.id}"><span class="level-number">${l.id}</span><span><h3>${escapeHTML(l.title)}</h3><p>${escapeHTML(l.description)}</p><div class="progress-track"><div class="progress-fill" style="width:${levelPct(l.id)}%"></div></div></span><span class="level-progress">${levelPct(l.id)}%</span></button>`).join('')}</div>`}
function brainBridgeConfig(){
  return state.brainBridge||{
    interactiveTargets:[],
    links:{},
    noDirectLocalisation:{}
  }
}
function bridgeLinksFor(id){
  return brainBridgeConfig().links?.[id]||[]
}
function brainTargetIds(){
  return new Set(
    (brainBridgeConfig().interactiveTargets||[]).map(item=>item.id)
  )
}
function reverseBridgeLinks(targetId){
  return Object.entries(brainBridgeConfig().links||{})
    .flatMap(([source,items])=>
      (items||[])
        .filter(item=>item.target===targetId)
        .map(item=>({source,...item}))
    )
}
function relationKindLabel(kind){
  return String(kind||'anatomical context').replace(/-/g,' ')
}
function brainHome(){
  const config=brainBridgeConfig();
  const groups=new Map();
  for(const item of config.interactiveTargets||[]){
    const c=concepts().find(candidate=>candidate.id===item.id);
    if(!c)continue;
    const category=item.category||'Interactive brain';
    if(!groups.has(category))groups.set(category,[]);
    groups.get(category).push(c);
  }
  return `<div class="page-title brain-home-intro">
    <div class="eyebrow">Interactive Brain</div>
    <h1>Explore the brain.</h1>
    <p>
      Move through anatomy, pathways, circuits and functional networks.
      Every relevant interactive view can link back to the theory that
      explains what you are seeing.
    </p>
  </div>
  ${[...groups.entries()].map(([category,items])=>`
    <section class="brain-category">
      <header>
        <h2>${escapeHTML(category)}</h2>
        <p>${items.length} interactive view${items.length===1?'':'s'}</p>
      </header>
      <div class="concept-grid">
        ${items.map(c=>`
          <button class="concept-card" data-open-brain="${c.id}">
            <img
              class="concept-thumb"
              src="assets/illustrations/${c.hero}"
              alt=""
              loading="lazy"
              decoding="async"
            >
            <div class="concept-card-body">
              <h3>${escapeHTML(c.title)}</h3>
              <p>${escapeHTML(c.subtitle)}</p>
              <div class="concept-meta">
                <span class="concept-meta-left">
                  <span>Interactive Brain</span>
                  <span class="interaction-pill">Explore</span>
                </span>
              </div>
            </div>
          </button>
        `).join('')}
      </div>
    </section>
  `).join('')}`
}
function bridgeContext(c){
  if(!state.bridgeFrom)return '';
  const source=concepts().find(item=>item.id===state.bridgeFrom);
  if(!source)return '';
  const label=state.mode==='brain'
    ?'Theory → Interactive Brain'
    :'Interactive Brain → Theory';
  return `<div class="brain-bridge-context">
    <span>${escapeHTML(label)}</span>
    <strong>${escapeHTML(source.title)}</strong>
    <span aria-hidden="true">→</span>
    <strong>${escapeHTML(c.title)}</strong>
  </div>`
}
function brainBridgeSections(c){
  const config=brainBridgeConfig();
  const forward=bridgeLinksFor(c.id);
  const reverse=brainTargetIds().has(c.id)
    ?reverseBridgeLinks(c.id)
    :[];
  const boundary=config.noDirectLocalisation?.[c.id];

  const forwardMarkup=forward.length?`
    <section
      class="brain-bridge-panel"
      data-theory-brain-bridge
      aria-labelledby="brain-links-${c.id}"
    >
      <div class="eyebrow">Theory ↔ Interactive Brain</div>
      <h2 id="brain-links-${c.id}">Explore the relevant brain systems</h2>
      <p>
        These are spatial learning anchors. Distributed mechanisms are not
        reduced to a single location, and a link does not imply diagnostic
        specificity or causation.
      </p>
      <div class="brain-link-grid">
        ${forward.map(item=>{
          const target=concepts().find(candidate=>candidate.id===item.target);
          if(!target)return '';
          return `<button
            class="brain-link-card"
            data-brain-link="${escapeHTML(item.target)}"
            data-brain-source="${escapeHTML(c.id)}"
          >
            <span>${escapeHTML(relationKindLabel(item.kind))}</span>
            <strong>${escapeHTML(item.label||target.title)}</strong>
            <p>${escapeHTML(item.rationale||target.subtitle)}</p>
          </button>`
        }).join('')}
      </div>
    </section>
  `:boundary?`
    <section
      class="brain-bridge-panel brain-boundary"
      data-no-direct-localisation
    >
      <div class="eyebrow">Theory ↔ Interactive Brain</div>
      <h2>No single brain location</h2>
      <p>${escapeHTML(boundary)}</p>
    </section>
  `:'';

  const reverseMarkup=reverse.length?`
    <section
      class="brain-bridge-panel"
      data-brain-theory-bridge
      aria-labelledby="theory-links-${c.id}"
    >
      <div class="eyebrow">Interactive Brain ↔ Theory</div>
      <h2 id="theory-links-${c.id}">Related theory</h2>
      <p>
        Use these links to move from spatial anatomy back into the concepts,
        mechanisms and clinical boundaries that explain it.
      </p>
      <div class="brain-link-grid">
        ${reverse.map(item=>{
          const source=concepts().find(candidate=>candidate.id===item.source);
          if(!source)return '';
          return `<button
            class="brain-link-card"
            data-theory-link="${escapeHTML(item.source)}"
            data-theory-source="${escapeHTML(c.id)}"
          >
            <span>${escapeHTML(relationKindLabel(item.kind))}</span>
            <strong>${escapeHTML(source.title)}</strong>
            <p>${escapeHTML(item.rationale||source.subtitle)}</p>
          </button>`
        }).join('')}
      </div>
    </section>
  `:'';

  return `${forwardMarkup}${reverseMarkup}`
}

function learn(level=state.level){if(!level)return `<div class="page-title"><div class="eyebrow">Foundations to functional networks</div><h1>Choose a level</h1><p>Progress from cellular foundations through signalling, plasticity and large-scale functional networks.</p></div><div class="level-list">${state.curriculum.levels.map(l=>`<button class="level-card" data-level="${l.id}"><span class="level-number">${l.id}</span><span><h3>${escapeHTML(l.title)}</h3><p>${escapeHTML(l.description)}</p></span><span class="level-progress">${levelPct(l.id)}%</span></button>`).join('')}</div>`;const l=state.curriculum.levels.find(x=>x.id===level);return `<div class="page-title"><div class="eyebrow">Level ${l.id}</div><h1>${escapeHTML(l.title)}</h1><p>${escapeHTML(l.description)}</p></div><div class="concept-grid">${concepts(level).map(c=>`<button class="concept-card" data-open="${c.id}"><img class="concept-thumb" src="assets/illustrations/${c.hero}" alt="" loading="lazy" decoding="async"><div class="concept-card-body"><h3>${escapeHTML(c.title)}</h3><p>${escapeHTML(c.subtitle)}</p><div class="concept-meta"><span class="concept-meta-left"><span>Concept ${c.order}</span>${hasInteractiveModel(c)?'<span class="interaction-pill">Interactive</span>':''}</span><span class="status-pill ${completed(c.id)?'complete':''}">${completed(c.id)?'Complete':'Start'}</span></div></div></button>`).join('')}</div>`}

function conceptDetails(c){return state.details[c.id]||null}
function explorerMarkup(c,d=conceptDetails(c)){if(!d)return '';return c.id==='neurons'?renderNeuronExplorer(d):c.id==='astrocytes'?renderAstrocyteExplorer(d):c.id==='microglia'?renderMicrogliaExplorer(d):c.id==='oligodendrocytes'?renderOligodendrocyteExplorer(d):renderSystemExplorer(d)}
function hasInteractiveModel(c){return !!explorerMarkup(c)}
function conceptAlt(c){const d=conceptDetails(c);return d?.altText||d?.accessibility?.altText||`${c.title}: ${c.subtitle}.`}
function selectedQuiz(c){const details=conceptDetails(c),bank=details?.quizBank||details?.quiz;if(!bank?.length)return c.quiz;const attempts=state.progress[c.id]?.attempts||0;return bank[attempts%bank.length]}
function quizAnswer(q){return q.answer??q.correctAnswer}
function productionExtras(c){const d=conceptDetails(c);if(!d)return '';const objectives=(d.learningObjectives||[]).map(x=>`<li>${escapeHTML(x)}</li>`).join('');const refs=(d.references||[]).map(r=>`<li><span>${escapeHTML(r.type||'Reference')}</span>${r.url?`<a href="${escapeHTML(r.url)}" target="_blank" rel="noopener noreferrer">${escapeHTML(r.citation)}</a>`:`<p>${escapeHTML(r.citation)}</p>`}</li>`).join('');const explorer=explorerMarkup(c);const deepDive=renderDeepDiveButton(d);const quality=renderContentQualitySummary(d);return `${quality}${deepDive}${explorer?`<div id="interactive-model-${c.id}" class="interactive-model-anchor">${explorer}</div>`:''}<section class="learning-objectives" aria-labelledby="objectives-${c.id}"><div class="eyebrow">Learning objectives</div><h2 id="objectives-${c.id}">By the end of this concept</h2><ul>${objectives}</ul></section><details class="learn-more"><summary>Learn more &amp; references</summary><ol>${refs}</ol></details>`}

function concept(){const c=concepts().find(x=>x.id===state.concept);if(!c)return home();state.last=c.id;store.set('cna-last',c.id);const tabs=Object.keys(labels),visualAvailable=hasVisualScene(c.id);return `<article class="concept-view"><div class="hero-frame"><img class="concept-hero" src="assets/illustrations/${c.hero}" alt="${escapeHTML(conceptAlt(c))}" decoding="async" fetchpriority="high"><div class="hero-glow" aria-hidden="true"></div>${visualAvailable?`<button class="example-button" data-open-visual aria-expanded="${state.visualOpen}"><span aria-hidden="true">▶</span> ${state.visualOpen?'Close live model':'Bring it to life'}</button>`:''}</div>${visualAvailable&&state.visualOpen?renderVisualScene(c.id):''}<header class="concept-header"><div class="eyebrow">Level ${c.level} · Concept ${c.order}</div><h1>${escapeHTML(c.title)}</h1><p>${escapeHTML(c.subtitle)}</p>${bridgeContext(c)}${hasInteractiveModel(c)?`<div class="concept-tools"><button class="secondary explore-model-button" data-jump-explorer>Explore interactive model</button><span>Inspect components, pathways and clinical effects.</span></div>`:''}<button class="bookmark-toggle ${state.bookmarks.has(c.id)?'saved':''}" data-bookmark="${c.id}" aria-label="${state.bookmarks.has(c.id)?'Remove bookmark':'Save bookmark'}">${state.bookmarks.has(c.id)?'♥':'♡'}</button></header><div class="tabs" role="tablist">${tabs.map(k=>`<button class="tab ${state.tab===k?'active':''}" data-tab="${k}" role="tab" aria-selected="${state.tab===k}">${labels[k]}</button>`).join('')}</div><section class="content-panel ${state.tab==='pearl'?'clinical-pearl':''}" role="tabpanel"><h2>${labels[state.tab]}</h2><p>${escapeHTML(c[state.tab])}</p></section>${productionExtras(c)}${brainBridgeSections(c)}<div class="concept-actions"><button class="secondary" data-prev="${c.id}">Previous</button><button class="primary" data-quiz="${c.id}">Quiz &amp; continue</button></div></article>`}
function quiz(id){const c=concepts().find(x=>x.id===id),q=selectedQuiz(c);return `<section class="quiz-card" data-quiz-card="${c.id}"><div class="eyebrow">Knowledge check</div><h2>${escapeHTML(q.question)}</h2><div class="answers">${q.options.map((o,i)=>`<button class="answer-button" data-answer="${i}">${escapeHTML(o)}</button>`).join('')}</div><div class="feedback" hidden></div></section>`}
function availableCompetencies(c){const d=conceptDetails(c)||{},skills=['recognise','explain'];if(d.spatialMap||d.pathwayTrace)skills.push('localise');if(d.clinicalComparison||d.lesionLab)skills.push('compare');if(d.assessmentLab||d.integratedCaseLab)skills.push('apply');return [...new Set(skills)]}
function competencyPrompt(c,skill){const d=conceptDetails(c)||{},q=selectedQuiz(c),answer=q.options[quizAnswer(q)],prompts=d.reviewPrompts||[];if(skill==='recognise')return {prompt:q.question,answer,explanation:q.explanation||q.rationale};if(skill==='explain'){const item=prompts[0];return {prompt:item?.prompt||`Explain ${c.title} in your own words.`,answer:item?.answer||c.simple,explanation:'Check whether your explanation preserved the core mechanism rather than only naming the concept.'}}if(skill==='localise')return {prompt:`From memory, localise ${c.title} and relate it to one neighbouring structure, pathway, or network.`,answer:c.psych,explanation:'Use the interactive anatomy or pathway view to verify your spatial model after retrieval.'};if(skill==='compare')return {prompt:`Contrast intact versus disrupted ${c.title}. What changes, and what might you observe clinically?`,answer:`${c.wrong} ${c.care}`,explanation:'A strong comparison links mechanism to observable function without treating one sign as uniquely localising.'};return {prompt:`Apply ${c.title} to a clinical presentation. What evidence would support your hypothesis, and what would make you reconsider it?`,answer:c.pearl||c.care,explanation:'Application requires converging evidence, alternatives, and an explicit limit on inference.'}}
function reviewItem(c){const skill=state.competency.nextSkill(c.id,availableCompetencies(c)),content=competencyPrompt(c,skill),meta=COMPETENCIES.find(item=>item.id===skill);return {skill,mode:meta?.label||'Retrieval',...content}}
function rankedDue(){return state.mastery.rankCards(state.review.due(concepts().map(c=>c.id)),completed)}
function review(){const due=rankedDue();let card=state.reviewFocus?state.review.get(state.reviewFocus):due[0];if(state.reviewFocus&&!card){state.review.add(state.reviewFocus);card=state.review.get(state.reviewFocus)}if(!card)return `<section class="review-empty"><span>✓</span><h1>You’re caught up</h1><p>No concepts are due for review. Completing quizzes will build your review queue.</p><button class="primary" data-route-go="learn">Keep learning</button></section>`;const c=concepts().find(x=>x.id===card.id);if(!c)return `<section class="review-empty"><h1>Review unavailable</h1><button class="primary" data-route-go="learn">Keep learning</button></section>`;const item=reviewItem(c),score=state.mastery.score(c.id,completed(c.id)),skillScore=state.competency.score(c.id,item.skill);state.reviewSkill=item.skill;state.reviewConfidence=null;return `<section class="review-card"><div class="eyebrow">${escapeHTML(item.mode)} competency · ${state.competency.label(skillScore)}</div><h1>${escapeHTML(c.title)}</h1><div class="competency-target"><strong>Current target: ${escapeHTML(item.mode)}</strong><span>Overall mastery ${score}%</span></div><p class="review-prompt">${escapeHTML(item.prompt)}</p><p class="retrieval-instruction">Answer from memory, then rate how confident you are before revealing. Calibration matters as much as accuracy in clinical reasoning.</p><fieldset class="confidence-check"><legend>How confident are you?</legend><div class="confidence-options">${CONFIDENCE_LEVELS.map(level=>`<button type="button" class="confidence-button" data-confidence="${level.id}" aria-pressed="false"><strong>${escapeHTML(level.label)}</strong><span>${escapeHTML(level.description)}</span></button>`).join('')}</div></fieldset><button class="primary" id="revealReview" disabled>Reveal answer</button><div id="reviewAnswer" class="review-answer" hidden><strong>${escapeHTML(item.answer)}</strong><p>${escapeHTML(item.explanation)}</p><div class="rating-row"><button class="rating-button" data-grade="1">Again</button><button class="rating-button" data-grade="3">Hard</button><button class="rating-button" data-grade="4">Good</button><button class="rating-button" data-grade="5">Easy</button></div></div></section>`}
function progress(){const all=concepts(),ids=all.map(c=>c.id),total=all.length,done=all.filter(c=>completed(c.id)).length,book=state.bookmarks.size,due=state.review.countDue(ids),weak=state.mastery.weakest(ids,completed,5),profile=COMPETENCIES.map(skill=>({...skill,score:state.competency.aggregate(skill.id,ids)})),calibration=state.calibration.profile();return `<div class="page-title"><div class="eyebrow">Your learning</div><h1>Progress</h1><p>Coverage, mastery, competency and confidence calibration are different. The goal is to progress toward clinically responsible application with confidence that matches the evidence.</p></div><div class="stats-grid"><div class="stat-card"><strong>${done}</strong><span>Concepts complete</span></div><div class="stat-card"><strong>${Math.round(done/total*100)}%</strong><span>Coverage</span></div><div class="stat-card"><strong>${book}</strong><span>Bookmarks</span></div><div class="stat-card"><strong>${due}</strong><span>Reviews due</span></div></div><div class="section-head"><h2>Competency profile</h2><span>Evidence by reasoning level</span></div><div class="competency-grid">${profile.map(skill=>`<div class="competency-card"><div><strong>${escapeHTML(skill.label)}</strong><span>${escapeHTML(skill.description)}</span></div><b>${skill.score===null?'—':`${skill.score}%`}</b><small>${state.competency.label(skill.score)}</small><div class="progress-track"><div class="progress-fill" style="width:${skill.score??0}%"></div></div></div>`).join('')}</div><div class="section-head"><h2>Confidence calibration</h2><span>Does confidence match performance?</span></div><section class="calibration-card"><div class="calibration-score"><strong>${calibration.score===null?'—':`${calibration.score}%`}</strong><span>${escapeHTML(calibration.label)}</span></div><div class="calibration-detail"><p>${escapeHTML(state.calibration.guidance(calibration))}</p><div><span>${calibration.attempts} rated reviews</span><span>${calibration.highConfidenceErrors} high-confidence misses</span><span>${calibration.lowConfidenceSuccess} low-confidence successes</span></div></div></section>${weak.length?`<div class="section-head"><h2>Retrieval priorities</h2><span>Lowest mastery evidence first</span></div><div class="adaptive-priority-list">${weak.map(item=>{const c=all.find(x=>x.id===item.id),skill=state.competency.nextSkill(c.id,availableCompetencies(c)),meta=COMPETENCIES.find(x=>x.id===skill);return `<div class="adaptive-priority"><div><strong>${escapeHTML(c.title)}</strong><span>${state.mastery.label(item.score)} · ${item.score}% · next: ${escapeHTML(meta?.label||skill)}</span></div><button class="secondary" data-focus-review="${c.id}">Practice</button></div>`}).join('')}</div>`:''}<div class="section-head"><h2>Level completion</h2></div><div class="mastery-list">${state.curriculum.levels.map(l=>`<div class="mastery-row"><p>Level ${l.id} · ${escapeHTML(l.title)}</p><strong>${levelPct(l.id)}%</strong><div class="progress-track" style="grid-column:1/-1"><div class="progress-fill" style="width:${levelPct(l.id)}%"></div></div></div>`).join('')}</div>`}
function bookmarks(){const list=concepts().filter(c=>state.bookmarks.has(c.id));return `<div class="page-title"><div class="eyebrow">Saved concepts</div><h1>Bookmarks</h1><p>Your clinical quick-reference list.</p></div>${list.length?`<div class="concept-grid">${list.map(c=>`<button class="concept-card" data-open="${c.id}"><img class="concept-thumb" src="assets/illustrations/${c.hero}" alt="" loading="lazy" decoding="async"><div class="concept-card-body"><h3>${escapeHTML(c.title)}</h3><p>${escapeHTML(c.pearl)}</p></div></button>`).join('')}</div>`:'<p class="empty-note">Bookmark a concept using the heart on its learning card.</p>'}`}

function evidencePage(){const sources=state.evidenceLibrary?.sources||[],reviewed=Object.keys(state.evidenceReview?.concepts||{}).length;return `<div class="page-title"><div class="eyebrow">Evidence library</div><h1>Trace the evidence</h1><p>Every production concept is linked to its supporting sources. Clinical recommendations, biomarkers and contested mechanisms are held to a higher standard than stable anatomical foundations.</p></div><section class="evidence-summary"><div><strong>${reviewed}</strong><span>concepts evidence-mapped</span></div><div><strong>${sources.length}</strong><span>indexed sources</span></div><div><strong>Required</strong><span>for future factual changes</span></div></section><label class="evidence-search"><span>Search evidence</span><input id="evidenceFilter" type="search" placeholder="PTSD, neurofeedback, anatomy, guideline…"></label><div class="evidence-policy"><strong>How to read this library</strong><p>Source linkage means a source is relevant to the concept; it does not mean every sentence is proven by that source. The Atlas labels uncertainty and uses current guidelines or systematic reviews for clinical, diagnostic and treatment claims whenever available.</p></div><div class="evidence-list">${sources.map(s=>`<article class="evidence-card" data-evidence-source="${escapeHTML([s.citation,s.sourceType,s.status,(s.conceptIds||[]).join(' ')].join(' ').toLowerCase())}"><div class="evidence-meta"><span>${escapeHTML(s.sourceType||'Reference')}</span><span>${escapeHTML(s.status||'source-linked')}</span>${s.year?`<span>${s.year}</span>`:''}</div><h2>${escapeHTML(s.citation||'Untitled source')}</h2><p>${escapeHTML(s.evidenceStrength||'Evidence source')}</p>${s.limitations?`<p class="evidence-limit"><strong>Boundary:</strong> ${escapeHTML(s.limitations)}</p>`:''}<div class="evidence-footer"><span>${(s.conceptIds||[]).length} linked concept${(s.conceptIds||[]).length===1?'':'s'}</span>${s.url?`<a href="${escapeHTML(s.url)}" target="_blank" rel="noopener noreferrer">Open source ↗</a>`:''}</div></article>`).join('')}</div>`}

function render(){updateNav();main.innerHTML=state.route==='home'?home():state.route==='brain'?brainHome():state.route==='learn'?learn():state.route==='concept'?concept():state.route==='quiz'?quiz(state.concept):state.route==='review'?review():state.route==='progress'?progress():state.route==='bookmarks'?bookmarks():state.route==='evidence'?evidencePage():home();bind()}
function bind(){const c=concepts().find(x=>x.id===state.concept);if(c)bindDeepDive(main,conceptDetails(c),c.title);if(c?.id==='neurons')bindNeuronExplorer(main.querySelector('.neuron-explorer'),conceptDetails(c));if(c?.id==='astrocytes')bindAstrocyteExplorer(main.querySelector('.astro-explorer'),conceptDetails(c));if(c?.id==='microglia')bindMicrogliaExplorer(main.querySelector('.micro-explorer'),conceptDetails(c));if(c?.id==='oligodendrocytes')bindOligodendrocyteExplorer(main.querySelector('.oligo-explorer'),conceptDetails(c));if(c&&conceptDetails(c)&&!['neurons','astrocytes','microglia','oligodendrocytes'].includes(c.id))bindSystemExplorer(main.querySelector('.system-explorer'),conceptDetails(c));main.querySelectorAll('[data-level]').forEach(b=>b.onclick=()=>setRoute('learn',{level:+b.dataset.level}));main.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>setRoute('concept',{concept:b.dataset.open,tab:'simple',visualOpen:false}));main.querySelectorAll('[data-open-brain]').forEach(b=>
  b.onclick=()=>setRoute('concept',{
    concept:b.dataset.openBrain,
    tab:'simple',
    visualOpen:false,
    mode:'brain',
    bridgeFrom:null
  })
);
main.querySelectorAll('[data-brain-link]').forEach(b=>
  b.onclick=()=>setRoute('concept',{
    concept:b.dataset.brainLink,
    tab:'simple',
    visualOpen:false,
    mode:'brain',
    bridgeFrom:b.dataset.brainSource
  })
);
main.querySelectorAll('[data-theory-link]').forEach(b=>
  b.onclick=()=>setRoute('concept',{
    concept:b.dataset.theoryLink,
    tab:'simple',
    visualOpen:false,
    mode:'theory',
    bridgeFrom:b.dataset.theorySource
  })
);const openVisual=main.querySelector('[data-open-visual]');if(openVisual)openVisual.onclick=()=>{state.visualOpen=!state.visualOpen;render();if(state.visualOpen)setTimeout(()=>main.querySelector('[data-visual-demo]')?.scrollIntoView({behavior:'smooth',block:'start'}),30)};const closeVisual=main.querySelector('[data-close-visual]');if(closeVisual)closeVisual.onclick=()=>{state.visualOpen=false;render()};const jumpExplorer=main.querySelector('[data-jump-explorer]');if(jumpExplorer)jumpExplorer.onclick=()=>main.querySelector('.interactive-model-anchor')?.scrollIntoView({behavior:'smooth',block:'start'});main.querySelectorAll('[data-jump-clinical]').forEach(button=>button.onclick=()=>{const target={spatial:'[data-spatial-canvas]',pathway:'[data-pathway-lab]',lesion:'[data-lesion-lab]',comparison:'[data-clinical-comparison]',assessment:'[data-assessment-lab]',integrated:'[data-integrated-case-lab]'}[button.dataset.jumpClinical];main.querySelector(target)?.scrollIntoView({behavior:'smooth',block:'start'})});main.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>{state.tab=b.dataset.tab;render()});main.querySelectorAll('[data-bookmark]').forEach(b=>b.onclick=()=>{const id=b.dataset.bookmark;state.bookmarks.has(id)?state.bookmarks.delete(id):state.bookmarks.add(id);store.set('cna-bookmarks',[...state.bookmarks]);toast(state.bookmarks.has(id)?'Bookmarked':'Bookmark removed');render()});main.querySelectorAll('[data-quiz]').forEach(b=>b.onclick=()=>setRoute('quiz',{concept:b.dataset.quiz}));main.querySelectorAll('[data-prev]').forEach(b=>b.onclick=()=>{const c=concepts().find(x=>x.id===b.dataset.prev),list=concepts(c.level),i=list.findIndex(x=>x.id===c.id);if(i>0)setRoute('concept',{concept:list[i-1].id,tab:'simple',visualOpen:false});else setRoute('learn',{level:c.level})});main.querySelectorAll('[data-answer]').forEach(b=>b.onclick=()=>answerQuiz(b));main.querySelectorAll('[data-route-go]').forEach(b=>b.onclick=()=>setRoute(b.dataset.routeGo));main.querySelectorAll('[data-focus-review]').forEach(b=>b.onclick=()=>{state.reviewFocus=b.dataset.focusReview;state.review.add(state.reviewFocus);setRoute('review')});const reveal=$('#revealReview');main.querySelectorAll('[data-confidence]').forEach(b=>b.onclick=()=>{state.reviewConfidence=+b.dataset.confidence;main.querySelectorAll('[data-confidence]').forEach(x=>{const selected=x===b;x.classList.toggle('selected',selected);x.setAttribute('aria-pressed',selected?'true':'false')});if(reveal)reveal.disabled=false});if(reveal)reveal.onclick=()=>{if(!state.reviewConfidence)return;$('#reviewAnswer').hidden=false;reveal.hidden=true};main.querySelectorAll('[data-grade]').forEach(b=>b.onclick=()=>{const card=state.reviewFocus?state.review.get(state.reviewFocus):rankedDue()[0];if(!card)return;const grade=+b.dataset.grade,correct=grade>=3;state.review.grade(card.id,grade);state.mastery.recordReview(card.id,grade);state.competency.record(card.id,state.reviewSkill||'recognise',{correct,grade});state.calibration.record(card.id,state.reviewSkill||'recognise',{confidence:state.reviewConfidence,correct});state.reviewSkill=null;state.reviewConfidence=null;state.reviewFocus=null;toast('Review scheduled');render()});const evidenceFilter=$('#evidenceFilter');if(evidenceFilter)evidenceFilter.oninput=()=>{const q=evidenceFilter.value.trim().toLowerCase();main.querySelectorAll('[data-evidence-source]').forEach(card=>card.hidden=Boolean(q)&&!card.dataset.evidenceSource.includes(q))}}
function answerQuiz(button){const c=concepts().find(x=>x.id===state.concept),q=selectedQuiz(c),answer=quizAnswer(q),card=button.closest('[data-quiz-card]'),buttons=[...card.querySelectorAll('[data-answer]')],selected=+button.dataset.answer;buttons.forEach((b,i)=>{b.disabled=true;if(i===answer)b.classList.add('correct');else if(i===selected)b.classList.add('incorrect')});const ok=selected===answer;const feedback=card.querySelector('.feedback');feedback.hidden=false;feedback.innerHTML=`<strong>${ok?'Correct.':'Not quite.'}</strong> ${escapeHTML(q.explanation||q.rationale)}<div style="margin-top:.8rem"><button class="primary" id="quizNext">${ok?'Next concept':'Continue'}</button></div>`;state.progress[c.id]={...(state.progress[c.id]||{}),completed:ok||completed(c.id),lastAttempt:Date.now(),correct:ok,attempts:(state.progress[c.id]?.attempts||0)+1};saveProgress();state.mastery.recordQuiz(c.id,ok);state.competency.record(c.id,'recognise',{correct:ok});state.review.add(c.id);$('#quizNext').onclick=()=>{const list=concepts(c.level),i=list.findIndex(x=>x.id===c.id),next=list[i+1];if(next)setRoute('concept',{concept:next.id,tab:'simple',visualOpen:false});else{const levels=state.curriculum.levels.map(l=>l.id).sort((a,b)=>a-b),li=levels.indexOf(c.level);if(li>=0&&li<levels.length-1)setRoute('learn',{level:levels[li+1]});else setRoute('progress')}};updateNav()}
function setupSearch(){const dialog=$('#searchDialog'),input=$('#searchInput'),results=$('#searchResults');$('#searchButton').onclick=()=>{dialog.showModal();input.value='';results.innerHTML='<p class="empty-note">Type to search titles and clinical content.</p>';setTimeout(()=>input.focus(),50)};input.oninput=()=>{const q=input.value.trim().toLowerCase();const list=q?concepts().filter(c=>{const details=conceptDetails(c);return [c.title,c.subtitle,c.simple,c.psych,c.advanced,c.care,c.wrong,c.pearl,...searchableDetailText(details)].some(v=>String(v).toLowerCase().includes(q))}).slice(0,12):[];results.innerHTML=list.length?list.map(c=>`<button class="search-result" data-search-open="${c.id}"><strong>${escapeHTML(c.title)}</strong><small>Level ${c.level} · ${escapeHTML(c.subtitle)}</small></button>`).join(''):'<p class="empty-note">No matching concepts.</p>';results.querySelectorAll('[data-search-open]').forEach(b=>b.onclick=()=>{dialog.close();setRoute('concept',{concept:b.dataset.searchOpen,tab:'simple',visualOpen:false})})}}
async function init(){try{const r=await fetch('./data/curriculum.json');if(!r.ok)throw new Error('Curriculum unavailable');state.curriculum=await r.json();const [evidenceResponse,evidenceMapResponse,brainBridgeResponse]=await Promise.all([fetch('./data/evidence-library.json'),fetch('./data/evidence-review-map.json'),fetch('./data/brain-bridge.json')]);if(evidenceResponse.ok)state.evidenceLibrary=await evidenceResponse.json();if(evidenceMapResponse.ok)state.evidenceReview=await evidenceMapResponse.json();if(brainBridgeResponse.ok)state.brainBridge=await brainBridgeResponse.json();const detailFiles=['cell','membrane','electricity','chemistry','brain-overview','lobes','subcortex','brainstem-cerebellum','action-potentials','amygdala','astrocytes','attention-networks','auditory-system','autonomic-nervous-system','blood-brain-barrier','brain-energy-metabolism','brain-health-ageing','brain-lateralisation','consciousness-arousal','corpus-callosum','cranial-nerves','default-mode-network','embryonic-neural-development','emotion-regulation-networks','epilepsy-neuroscience','executive-function','frontoparietal-control-network','functional-networks','hippocampus','integrated-systems-capstone','language-networks','memory-systems','meninges','microglia','motor-system','myelination','neural-tube-formation','neurodegenerative-disorders','neuroimmunology','neuronal-migration','neurons','neuroplasticity','neurotransmitters','oligodendrocytes','pain-processing','personality-disorders-neuroscience','resting-potential','reward-system','salience-network','sleep-circadian-rhythms','sleep-disorders-neuroscience','somatosensory-system','substance-use-neuroscience','synapses','synaptogenesis','ventricular-system','visual-system','traumatic-brain-injury','migraine-neuroscience','eating-disorders-neuroscience','tic-tourette-neuroscience','intellectual-developmental-disability','learning-disorders-neuroscience','communication-disorders-neuroscience','psychopharmacology-foundations','anxiety-spectrum-comparison','clinical-neuroanatomy-review','attention-neuropsychology','social-cognition-neuropsychology','executive-assessment','language-assessment','neuropsychological-case-formulation','clinical-test-interpretation','semantic-memory-neuropsychology','procedural-learning-neuropsychology','praxis-apraxia','agnosia-recognition','hemispatial-neglect','performance-validity','premorbid-ability-estimation','ecological-validity-functional-cognition','psychiatric-state-confounds','paediatric-neuropsychology','older-adult-neuropsychology','neuropsychological-report-feedback','processing-speed-neuropsychology','working-memory-neuropsychology','episodic-memory-neuropsychology','visuospatial-neuropsychology','eeg-what-it-measures','cortical-generators','volume-conduction','electrode-10-20-system','electrode-impedance','references-and-montages','sampling-and-aliasing','filters-time-constant','amplitude-frequency-phase','eeg-state-dependence','preparation-consent-safety','eyes-open-eyes-closed','hyperventilation','photic-stimulation','sleep-deprived-eeg','ecg-eog-emg-channels','ocular-artifact','muscle-artifact','cardiac-pulse-artifact','movement-sweat-electrode-artifact','artifact-rejection-principles','normal-awake-background','posterior-dominant-rhythm','developmental-eeg','drowsiness-and-sleep-stages','focal-slowing','generalised-slowing','epileptiform-discharges','seizure-patterns','normal-variants','encephalopathy-patterns','qeeg-workflow','fourier-transform','spectral-power','frequency-bands','individual-alpha-frequency','topographic-maps','normative-databases','z-scores-effect-sizes','coherence-connectivity','phase-lag','source-localisation','qeeg-reliability','multiple-comparisons','qeeg-adhd-evidence','qeeg-autism-evidence','qeeg-anxiety-depression-evidence','qeeg-tbi-evidence','medication-substance-effects','clinical-reporting-qeeg','qeeg-ethics-scope','qeeg-neurofeedback-link','eeg-qeeg-capstone','history-of-neurofeedback','learning-theory-neurofeedback','operant-conditioning-neurofeedback','reinforcement-schedules','eeg-versus-neurofeedback','closed-loop-systems','feedback-modalities','sensor-placement','electrode-preparation','signal-quality-impedance','artifact-recognition-neurofeedback','threshold-setting','reward-bands','inhibit-bands','session-structure','baseline-recording','protocol-selection','treatment-planning-neurofeedback','alpha-training','theta-training','beta-training','smr-training','alpha-theta-training','scp-neurofeedback','connectivity-training','coherence-training','phase-training','zscore-neurofeedback','loreta-neurofeedback','heg-neurofeedback','ilf-neurofeedback','adhd-neurofeedback','anxiety-neurofeedback','ptsd-neurofeedback','depression-neurofeedback','autism-neurofeedback','sleep-neurofeedback','peak-performance','medication-considerations-neurofeedback','contraindications-adverse-effects','troubleshooting-nonresponse','ethics-evidence-clinical-limits','foundations-trauma-neuroscience','acute-stress-response','chronic-stress-trauma','hpa-axis-trauma','sympathetic-activation-trauma','parasympathetic-regulation-trauma','polyvagal-theory','amygdala-trauma','hippocampus-trauma','prefrontal-cortex-trauma','salience-network-trauma','default-mode-network-trauma','central-executive-network-trauma','memory-encoding-trauma','memory-consolidation-trauma','memory-reconsolidation-trauma','fear-conditioning-trauma','fear-extinction-trauma','prediction-error-trauma','dissociation-mechanisms','structural-dissociation','emotional-processing-trauma','window-of-tolerance','affect-regulation-trauma','attachment-neuroscience-trauma','developmental-trauma','complex-ptsd-neuroscience','moral-injury','intergenerational-trauma','neurobiology-emdr','bilateral-stimulation-emdr','working-memory-theory-emdr','orienting-response-emdr','adaptive-information-processing','eight-phases-emdr','mechanisms-change-emdr','clinical-indications-emdr','contraindications-precautions-emdr','current-evidence-emdr','clinical-integration-limitations-emdr','cerebral-lobes-atlas','cerebellum-atlas','brainstem-atlas','meninges-atlas','cerebral-vasculature-atlas','limbic-system-atlas','ventricular-system-atlas','cranial-nerves-atlas','deep-nuclei-atlas','thalamus-atlas','hypothalamus-atlas','insula-atlas','cingulate-cortex-atlas','insula-operculum-atlas','reticular-activating-system-atlas','pituitary-and-sella-atlas','basal-ganglia-circuit-explorer','major-white-matter-pathways-atlas','neurotransmitter-pathways-atlas','functional-network-overlay-atlas',
'arterial-territories-stroke-comparison',
'brain-lateralisation-comparison',
'healthy-versus-pathology-comparison',
'lesion-and-symptom-mapping',
'integrated-whole-brain-explorer-and-capstone'
];const detailResponse=await fetch('./data/details-bundle.json');if(!detailResponse.ok)throw new Error('Concept details unavailable');const detailBundle=await detailResponse.json();for(const detail of Object.values(detailBundle)){if(detail?.id&&state.curriculum.concepts.some(concept=>concept.id===detail.id))state.details[detail.id]=detail}$$('.nav-item').forEach(b=>b.onclick=()=>setRoute(b.dataset.route,{level:null,bridgeFrom:null}));$('#homeButton').onclick=()=>setRoute('home',{level:null,mode:'theory',bridgeFrom:null});$('#bookmarkButton').onclick=()=>setRoute('bookmarks');$('#evidenceButton').onclick=()=>setRoute('evidence',{level:null});const modeButton=$('#modeButton');if(modeButton)modeButton.onclick=()=>window.NeuroAtlasExperience?.showGateway();setupSearch();installAccessibilityRuntime({searchButton:$('#searchButton')});render();if(state.pendingMode){const pending=state.pendingMode;state.pendingMode=null;window.NeuroAtlasOpenMode(pending)}if('serviceWorker'in navigator)navigator.serviceWorker.register('./sw.js').catch(()=>{})}catch(e){main.innerHTML=`<section class="review-empty"><h1>Atlas could not load</h1><p>${escapeHTML(e.message)}</p></section>`}}
init();
