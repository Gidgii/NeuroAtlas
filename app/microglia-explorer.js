const esc=s=>String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]));

export function renderMicrogliaExplorer(detail){
  const parts=detail.anatomy||[];
  return `<section class="micro-explorer" aria-labelledby="micro-explorer-title">
    <div class="explorer-heading">
      <div><div class="eyebrow">Interactive cell atlas</div><h2 id="micro-explorer-title">Microglial surveillance systems</h2></div>
      <button class="micro-run-button" type="button" data-run-surveillance aria-describedby="micro-status">Run surveillance cycle</button>
    </div>
    <p class="explorer-instruction">${esc(detail.interaction?.instruction||'Select a structure to inspect its function.')}</p>
    <div class="micro-canvas-wrap">
      <svg class="micro-canvas" viewBox="0 0 900 470" role="img" aria-labelledby="micro-svg-title micro-svg-desc">
        <title id="micro-svg-title">Interactive microglia anatomy</title>
        <desc id="micro-svg-desc">A ramified microglial cell surveys nearby synapses, detects damage signals, engulfs tagged debris and returns to homeostatic surveillance.</desc>
        <defs>
          <radialGradient id="microBody" cx="38%" cy="34%"><stop stop-color="#d8b6ff"/><stop offset="1" stop-color="#613a82"/></radialGradient>
          <filter id="microGlow"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
        </defs>
        <g class="micro-part part-processes-micro" data-micro-part="processes" tabindex="0" role="button" aria-label="Surveying processes">
          <path d="M430 225 C330 185 285 115 244 54 M418 235 C298 248 212 222 132 176 M422 254 C322 311 270 360 226 423 M474 221 C570 160 636 108 688 54 M488 240 C608 225 697 243 785 204 M478 260 C578 318 643 365 701 424"/>
          <path d="M244 54 l-40 -28 m40 28 l13 -44 M132 176 l-54 -10 m54 10 l-25 37 M226 423 l-44 23 m44 -23 l8 39 M688 54 l45 -31 m-45 31 l-4 -44 M785 204 l54 -21 m-54 21 l31 30 M701 424 l44 28 m-44 -28 l-2 39"/>
        </g>
        <g class="micro-part part-soma-micro" data-micro-part="soma" tabindex="0" role="button" aria-label="Microglial soma">
          <path d="M393 184 C430 151 486 160 515 202 C540 239 518 292 472 308 C425 324 371 300 357 258 C344 219 359 195 393 184Z"/>
          <ellipse cx="434" cy="236" rx="29" ry="37"/>
        </g>
        <g class="micro-part part-signals-micro" data-micro-part="signals" tabindex="0" role="button" aria-label="Damage signal receptors">
          <circle class="danger d1" cx="760" cy="116" r="10"/><circle class="danger d2" cx="796" cy="138" r="8"/><circle class="danger d3" cx="742" cy="151" r="7"/>
          <path d="M752 150 C690 175 625 194 507 225"/>
        </g>
        <g class="micro-part part-synapse-micro" data-micro-part="synapse" tabindex="0" role="button" aria-label="Synaptic contact">
          <path d="M112 90 q45 -35 90 0 v42 q-45 29 -90 0Z"/><path d="M104 166 q55 32 110 0"/>
          <circle cx="132" cy="142" r="7"/><circle cx="158" cy="149" r="7"/><circle cx="184" cy="139" r="7"/>
        </g>
        <g class="micro-part part-complement-micro" data-micro-part="complement" tabindex="0" role="button" aria-label="Complement tagging">
          <polygon points="154,118 162,132 178,134 166,145 170,161 154,153 140,161 143,145 132,134 148,132"/>
          <polygon points="204,112 211,124 225,126 215,136 218,150 204,143 191,150 194,136 184,126 198,124"/>
        </g>
        <g class="micro-part part-phago-micro" data-micro-part="phagocytosis" tabindex="0" role="button" aria-label="Phagocytic compartment">
          <circle cx="444" cy="278" r="30"/><circle class="debris" cx="441" cy="278" r="9"/><path d="M389 290 C340 307 301 329 267 350"/>
        </g>
        <g class="micro-part part-cytokine-micro" data-micro-part="cytokines" tabindex="0" role="button" aria-label="Signalling molecules">
          <circle class="cytokine c1" cx="510" cy="315" r="8"/><circle class="cytokine c2" cx="541" cy="332" r="8"/><circle class="cytokine c3" cx="572" cy="312" r="8"/>
        </g>
        <circle class="micro-pulse" cx="444" cy="238" r="14" aria-hidden="true"/>
      </svg>
      <div id="micro-status" class="signal-status" aria-live="polite">Select a system or run the surveillance cycle.</div>
    </div>
    <div class="micro-part-list" role="list">
      ${parts.map((p,i)=>`<button class="micro-part-button${i===0?' active':''}" type="button" data-micro-select="${esc(p.id)}"><strong>${esc(p.label)}</strong><span>${esc(p.short)}</span></button>`).join('')}
    </div>
    <div class="micro-detail" data-micro-detail aria-live="polite"></div>
  </section>`;
}

export function bindMicrogliaExplorer(root,detail){
  if(!root||!detail)return;
  const parts=new Map((detail.anatomy||[]).map(p=>[p.id,p]));
  const detailBox=root.querySelector('[data-micro-detail]');
  const status=root.querySelector('#micro-status');
  let timers=[];
  const clear=()=>{timers.forEach(clearTimeout);timers=[];root.classList.remove('surveillance-running')};
  const select=id=>{
    const part=parts.get(id); if(!part)return;
    root.querySelectorAll('[data-micro-select],[data-micro-part]').forEach(el=>el.classList.toggle('active',(el.dataset.microSelect||el.dataset.microPart)===id));
    detailBox.innerHTML=`<h3>${esc(part.label)}</h3><p>${esc(part.detail)}</p><aside><strong>Clinical connection</strong>${esc(part.clinical)}</aside>`;
  };
  root.querySelectorAll('[data-micro-select],[data-micro-part]').forEach(el=>{
    const activate=()=>select(el.dataset.microSelect||el.dataset.microPart);
    el.addEventListener('click',activate);
    el.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate()}});
  });
  const run=root.querySelector('[data-run-surveillance]');
  run?.addEventListener('click',()=>{
    clear();root.classList.add('surveillance-running');run.disabled=true;
    const steps=detail.interaction?.surveillanceSteps||[];
    steps.forEach((step,i)=>timers.push(setTimeout(()=>{status.textContent=`${i+1} of ${steps.length}: ${step}`;if(i===steps.length-1){run.disabled=false;timers.push(setTimeout(()=>root.classList.remove('surveillance-running'),900))}},i*1250)));
  });
  select(detail.anatomy?.[0]?.id);
}
