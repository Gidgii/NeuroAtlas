const esc=s=>String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));

export function renderOligodendrocyteExplorer(detail){
  const parts=detail.anatomy||[];
  return `<section class="oligo-explorer" aria-labelledby="oligo-explorer-title">
    <div class="explorer-heading">
      <div><div class="eyebrow">Interactive cell atlas</div><h2 id="oligo-explorer-title">Oligodendrocyte and myelinated axon</h2></div>
      <button class="oligo-run-button" type="button" data-run-conduction aria-describedby="oligo-status">Run conduction sequence</button>
    </div>
    <p class="explorer-instruction">${esc(detail.interaction?.instruction||'Select a structure to inspect its function.')}</p>
    <div class="oligo-canvas-wrap">
      <svg class="oligo-canvas" viewBox="0 0 960 500" role="img" aria-labelledby="oligo-svg-title oligo-svg-desc">
        <title id="oligo-svg-title">Interactive oligodendrocyte and myelinated axon anatomy</title>
        <desc id="oligo-svg-desc">An oligodendrocyte extends processes to multiple axons. One enlarged axon shows compact myelin internodes, nodes of Ranvier and paranodal junctions.</desc>
        <defs>
          <radialGradient id="oligoSoma" cx="38%" cy="32%"><stop stop-color="#bdf8ff"/><stop offset="1" stop-color="#36718f"/></radialGradient>
          <linearGradient id="myelinWrap" x1="0" x2="1"><stop stop-color="#54f2d1"/><stop offset=".5" stop-color="#b9fff1"/><stop offset="1" stop-color="#30a8a0"/></linearGradient>
          <filter id="oligoGlow"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <g class="oligo-part part-soma-oligo" data-oligo-part="soma" tabindex="0" role="button" aria-label="Oligodendrocyte soma">
          <path d="M183 175 C228 130 298 136 333 185 C367 232 342 301 284 322 C226 344 162 312 147 257 C136 218 151 194 183 175Z"/>
          <ellipse cx="239" cy="232" rx="36" ry="43"/>
        </g>
        <g class="oligo-part part-processes-oligo" data-oligo-part="processes" tabindex="0" role="button" aria-label="Myelinating processes">
          <path d="M300 184 C405 110 486 102 576 117 M327 224 C425 205 514 205 604 220 M310 276 C405 349 505 369 600 376"/>
          <path d="M300 184 C384 64 462 46 542 58 M310 276 C380 416 469 449 548 438"/>
        </g>
        <g class="oligo-part part-axon-oligo" aria-hidden="true"><path d="M80 220 H902"/></g>
        <g class="oligo-part part-myelin-oligo" data-oligo-part="myelin" tabindex="0" role="button" aria-label="Compact myelin">
          <rect x="350" y="185" width="150" height="70" rx="35"/><rect x="540" y="185" width="150" height="70" rx="35"/><rect x="730" y="185" width="150" height="70" rx="35"/>
          <path d="M370 200 h110 M370 220 h110 M370 240 h110 M560 200 h110 M560 220 h110 M560 240 h110 M750 200 h110 M750 220 h110 M750 240 h110"/>
        </g>
        <g class="oligo-part part-internode-oligo" data-oligo-part="internode" tabindex="0" role="button" aria-label="Myelin internode">
          <path d="M365 168 H485"/><path d="M365 160 v16 M485 160 v16"/>
        </g>
        <g class="oligo-part part-node-oligo" data-oligo-part="node" tabindex="0" role="button" aria-label="Node of Ranvier">
          <rect x="505" y="195" width="28" height="50" rx="12"/><rect x="695" y="195" width="28" height="50" rx="12"/>
        </g>
        <g class="oligo-part part-paranode-oligo" data-oligo-part="paranode" tabindex="0" role="button" aria-label="Paranodal junction">
          <path d="M488 190 l18 12 v36 l-18 12 M540 190 l-10 12 v36 l10 12 M678 190 l18 12 v36 l-18 12 M730 190 l-10 12 v36 l10 12"/>
        </g>
        <g class="oligo-part part-metabolic-oligo" data-oligo-part="metabolic" tabindex="0" role="button" aria-label="Axonal metabolic support">
          <circle cx="403" cy="280" r="9"/><circle cx="432" cy="298" r="8"/><circle cx="462" cy="282" r="7"/><path d="M338 274 C365 300 386 303 407 286"/>
        </g>
        <g class="signal-packets" aria-hidden="true"><circle class="signal s1" cx="330" cy="220" r="11"/><circle class="signal s2" cx="519" cy="220" r="11"/><circle class="signal s3" cx="709" cy="220" r="11"/><circle class="signal s4" cx="892" cy="220" r="11"/></g>
      </svg>
      <div id="oligo-status" class="signal-status" aria-live="polite">Select a structure or run the conduction sequence.</div>
    </div>
    <div class="oligo-part-list" role="list">
      ${parts.map((p,i)=>`<button class="oligo-part-button${i===0?' active':''}" type="button" data-oligo-select="${esc(p.id)}"><strong>${esc(p.label)}</strong><span>${esc(p.short)}</span></button>`).join('')}
    </div>
    <div class="oligo-detail" data-oligo-detail aria-live="polite"></div>
  </section>`;
}

export function bindOligodendrocyteExplorer(root,detail){
  if(!root||!detail)return;
  const parts=new Map((detail.anatomy||[]).map(p=>[p.id,p]));
  const detailBox=root.querySelector('[data-oligo-detail]');
  const status=root.querySelector('#oligo-status');
  const run=root.querySelector('[data-run-conduction]');
  let timers=[];
  const clear=()=>{timers.forEach(clearTimeout);timers=[];root.classList.remove('conduction-running');if(run)run.disabled=false};
  const select=id=>{
    const part=parts.get(id);if(!part)return;
    root.querySelectorAll('[data-oligo-select],[data-oligo-part]').forEach(el=>el.classList.toggle('active',(el.dataset.oligoSelect||el.dataset.oligoPart)===id));
    detailBox.innerHTML=`<h3>${esc(part.label)}</h3><p>${esc(part.detail)}</p><aside><strong>Clinical connection</strong>${esc(part.clinical)}</aside>`;
  };
  root.querySelectorAll('[data-oligo-select],[data-oligo-part]').forEach(el=>{
    const activate=()=>select(el.dataset.oligoSelect||el.dataset.oligoPart);
    el.addEventListener('click',activate);
    el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate()}});
  });
  run?.addEventListener('click',()=>{
    clear();root.classList.add('conduction-running');run.disabled=true;
    const steps=detail.interaction?.conductionSteps||[];
    steps.forEach((step,i)=>timers.push(setTimeout(()=>{
      status.textContent=`${i+1} of ${steps.length}: ${step}`;
      if(i===steps.length-1)timers.push(setTimeout(()=>{root.classList.remove('conduction-running');run.disabled=false},1000));
    },i*1250)));
  });
  select(detail.anatomy?.[0]?.id);
}
