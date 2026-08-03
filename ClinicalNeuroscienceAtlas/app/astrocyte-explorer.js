const esc=s=>String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));

export function renderAstrocyteExplorer(detail){
  const parts=detail.anatomy||[];
  return `<section class="astro-explorer" aria-labelledby="astro-explorer-title">
    <div class="explorer-heading">
      <div><div class="eyebrow">Interactive cell atlas</div><h2 id="astro-explorer-title">Astrocyte support systems</h2></div>
      <button class="support-button" type="button" data-run-support aria-describedby="astro-support-status">Run support cycle</button>
    </div>
    <p class="explorer-instruction">${esc(detail.interaction?.instruction||'Select a structure to inspect its function.')}</p>
    <div class="astro-canvas-wrap">
      <svg class="astro-canvas" viewBox="0 0 900 470" role="img" aria-labelledby="astro-svg-title astro-svg-desc">
        <title id="astro-svg-title">Interactive astrocyte anatomy</title>
        <desc id="astro-svg-desc">A star-shaped astrocyte contacts a synapse and capillary. Selectable structures show glutamate uptake, potassium buffering, metabolic support and neurovascular coupling.</desc>
        <defs>
          <radialGradient id="astroBody" cx="40%" cy="35%"><stop stop-color="#66f7dc"/><stop offset="1" stop-color="#176b7e"/></radialGradient>
          <linearGradient id="blood" x1="0" x2="1"><stop stop-color="#ff4db8"/><stop offset="1" stop-color="#ff7a59"/></linearGradient>
          <filter id="astroGlow"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <g class="astro-part part-network" data-astro-part="network" tabindex="0" role="button" aria-label="Gap-junction network">
          <path d="M118 88 C195 140 245 122 305 190 M106 350 C178 300 238 318 302 252 M770 86 C684 132 635 132 575 194"/>
          <circle cx="105" cy="82" r="24"/><circle cx="94" cy="360" r="24"/><circle cx="787" cy="76" r="24"/>
        </g>
        <g class="astro-part part-capillary" data-astro-part="endfeet" tabindex="0" role="button" aria-label="Vascular endfeet and capillary">
          <path d="M70 420 C260 350 560 450 845 362"/>
          <path class="endfoot" d="M338 322 C330 365 310 391 276 407 M490 327 C514 364 535 385 575 397"/>
        </g>
        <g class="astro-part part-processes" data-astro-part="perisynaptic" tabindex="0" role="button" aria-label="Perisynaptic processes">
          <path d="M392 220 C290 165 264 95 246 48 M395 231 C280 230 210 212 154 177 M405 246 C294 282 252 335 229 384 M475 228 C555 170 583 112 596 52 M478 245 C598 251 681 230 749 196 M462 270 C539 313 583 344 626 391"/>
        </g>
        <g class="astro-part part-soma" data-astro-part="soma" tabindex="0" role="button" aria-label="Astrocyte soma">
          <path d="M393 178 C430 144 486 157 510 197 C534 237 511 289 467 306 C421 324 368 301 353 258 C338 216 357 190 393 178Z"/>
          <circle cx="430" cy="235" r="32"/>
        </g>
        <g class="astro-part part-synapse" data-astro-part="transporters" tabindex="0" role="button" aria-label="Glutamate transporters at the synapse">
          <path d="M655 115 q35 -28 70 0 v36 q-35 24 -70 0Z"/>
          <path d="M652 182 q38 22 76 0"/>
          <circle class="glutamate g1" cx="670" cy="157" r="7"/><circle class="glutamate g2" cx="692" cy="165" r="7"/><circle class="glutamate g3" cx="715" cy="154" r="7"/>
          <path class="uptake-path" d="M690 164 C625 174 555 190 488 220"/>
        </g>
        <g class="astro-part part-potassium" data-astro-part="potassium" tabindex="0" role="button" aria-label="Potassium buffering">
          <circle class="kion k1" cx="294" cy="190" r="10"/><circle class="kion k2" cx="270" cy="224" r="10"/><circle class="kion k3" cx="304" cy="258" r="10"/>
          <path class="kpath" d="M288 220 C340 220 365 220 395 230"/>
        </g>
        <g class="astro-part part-metabolism" data-astro-part="metabolism" tabindex="0" role="button" aria-label="Metabolic support">
          <path d="M376 334 q54 -34 108 0 l-13 40 q-41 26 -82 0Z"/>
          <circle class="fuel f1" cx="410" cy="349" r="8"/><circle class="fuel f2" cx="438" cy="342" r="8"/><circle class="fuel f3" cx="456" cy="358" r="8"/>
        </g>
        <circle class="support-pulse" cx="430" cy="235" r="12" aria-hidden="true"/>
      </svg>
      <div id="astro-support-status" class="signal-status" aria-live="polite">Select a system or run the support cycle.</div>
    </div>
    <div class="astro-part-list" role="list">
      ${parts.map((p,i)=>`<button class="astro-part-button${i===0?' active':''}" type="button" data-astro-select="${esc(p.id)}"><strong>${esc(p.label)}</strong><span>${esc(p.short)}</span></button>`).join('')}
    </div>
    <div class="astro-detail" data-astro-detail aria-live="polite"></div>
  </section>`;
}

export function bindAstrocyteExplorer(root,detail){
  if(!root||!detail)return;
  const parts=new Map((detail.anatomy||[]).map(p=>[p.id,p]));
  const detailBox=root.querySelector('[data-astro-detail]');
  const status=root.querySelector('#astro-support-status');
  let timers=[];
  const clear=()=>{timers.forEach(clearTimeout);timers=[];root.classList.remove('support-running')};
  const select=id=>{
    const part=parts.get(id); if(!part)return;
    root.querySelectorAll('[data-astro-select],[data-astro-part]').forEach(el=>el.classList.toggle('active',(el.dataset.astroSelect||el.dataset.astroPart)===id));
    detailBox.innerHTML=`<h3>${esc(part.label)}</h3><p>${esc(part.detail)}</p><aside><strong>Clinical connection</strong>${esc(part.clinical)}</aside>`;
  };
  root.querySelectorAll('[data-astro-select],[data-astro-part]').forEach(el=>{
    const activate=()=>select(el.dataset.astroSelect||el.dataset.astroPart);
    el.addEventListener('click',activate);
    el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate()}});
  });
  const run=root.querySelector('[data-run-support]');
  run?.addEventListener('click',()=>{
    clear(); root.classList.add('support-running'); run.disabled=true;
    const steps=detail.interaction?.supportSteps||[];
    steps.forEach((step,i)=>timers.push(setTimeout(()=>{status.textContent=`${i+1} of ${steps.length}: ${step}`;if(i===steps.length-1){run.disabled=false;timers.push(setTimeout(()=>root.classList.remove('support-running'),900))}},i*1250)));
  });
  select(detail.anatomy?.[0]?.id);
}
