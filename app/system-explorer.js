const escapeHTML=value=>String(value??'').replace(/[&<>'"]/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[ch]));
const asArray=value=>Array.isArray(value)?value:value==null?[]:[value];
const joinText=value=>asArray(value).filter(Boolean).map(item=>typeof item==='string'?item:item.label||item.text||'').filter(Boolean).join('; ');
const slug=value=>String(value||'part').toLowerCase().replace(/[^a-z0-9]+/g,'-').replace(/^-|-$/g,'');

function anatomyValue(details,key){
  const anatomy=details.anatomy;
  if(Array.isArray(anatomy)){
    const aliases={functions:['function'],lesions:['lesionEffects','lesionPatterns','associatedDisorders'],symptoms:['associatedPresentations','associatedDisorders']};
    return joinText(anatomy.map(item=>item[key]||aliases[key]?.map(alias=>item[alias]).find(Boolean)));
  }
  if(!anatomy||typeof anatomy!=='object')return '';
  const aliases={lesions:['lesionEffects','lesionPatterns'],symptoms:['associatedPresentations','neurologicalPresentations','psychologicalPresentations']};
  for(const candidate of [key,...(aliases[key]||[])])if(anatomy[candidate])return joinText(anatomy[candidate]);
  return '';
}

function canonicalParts(details){
  if(Array.isArray(details.explorerParts)&&details.explorerParts.length)return details.explorerParts;
  if(Array.isArray(details.anatomy))return details.anatomy.map(item=>({
    id:item.id||slug(item.label),label:item.label||item.id,short:item.function||item.short||'',
    detail:item.function||item.detail||item.connections||'',clinical:item.clinicalSignificance||item.associatedDisorders||item.clinical||''
  }));
  const anatomy=details.anatomy||{};
  const names=asArray(anatomy.regions||anatomy.substructures).filter(Boolean);
  const functionText=joinText(anatomy.functions);
  const clinicalText=anatomy.clinicalSignificance||anatomy.lesionEffects||joinText(anatomy.lesionPatterns)||details.sections?.whenItGoesWrong||'';
  return names.map(name=>({id:slug(name),label:name,short:functionText,detail:functionText||anatomy.position||'',clinical:clinicalText}));
}

function canonicalStages(details){
  const configured=asArray(details.explorer?.stages);
  const labels={inputs:'Inputs',connections:'Connections',outputs:'Outputs'};
  const stages=configured.map(key=>({id:key,label:labels[key]||key,text:anatomyValue(details,key)})).filter(stage=>stage.text);
  if(stages.length)return stages;
  return asArray(details.interaction?.stages).filter(stage=>stage?.text).map((stage,index)=>({id:stage.id||`stage-${index+1}`,label:stage.label||`Stage ${index+1}`,text:stage.text}));
}

function canonicalOverlays(details){
  const labels={bloodSupply:'Blood supply',functions:'Functions',lesions:'Lesion effects',symptoms:'Presentations'};
  return asArray(details.explorer?.overlays).map(key=>({id:key,label:labels[key]||key,text:anatomyValue(details,key)})).filter(overlay=>overlay.text);
}

function model(details){return {parts:canonicalParts(details),stages:canonicalStages(details),overlays:canonicalOverlays(details)}}
function destinationMarkup(item){const ids=[...asArray(item.conceptIds),...asArray(item.conceptId)].filter(Boolean);return ids.length?`<nav class="system-destinations" aria-label="Detailed atlas destinations">${ids.map(id=>`<button class="secondary" data-open="${escapeHTML(id)}">Open ${escapeHTML(id.replace(/-/g,' '))}</button>`).join('')}</nav>`:''}
function detailMarkup(item){return `<div class="eyebrow">Selected component</div><h3>${escapeHTML(item.label)}</h3><p>${escapeHTML(item.detail||item.short||'No additional description is available.')}</p>${item.clinical?`<aside><strong>Clinical relevance</strong>${escapeHTML(item.clinical)}</aside>`:''}${destinationMarkup(item)}`}

export function renderSystemExplorer(details){
  const {parts,stages,overlays}=model(details),first=parts[0];
  if(!first)return '';
  const title=details.interaction?.title||`Explore ${details.title}`;
  const instruction=details.interaction?.instruction||'Select a component, inspect available overlays, or run the pathway sequence.';
  const modes=asArray(details.explorer?.comparisonModes);
  return `<section class="system-explorer" data-system-explorer="${escapeHTML(details.id)}" aria-labelledby="system-title-${escapeHTML(details.id)}"><div class="system-explorer-head"><div><div class="eyebrow">Interactive model</div><h2 id="system-title-${escapeHTML(details.id)}">${escapeHTML(title)}</h2><p>${escapeHTML(instruction)}</p></div>${stages.length?'<button class="system-run-button" data-system-run>Run sequence</button>':''}</div>${modes.length?`<div class="system-overlay-list" role="group" aria-label="${escapeHTML(details.explorer?.comparisonLabel||'Healthy and pathology comparison')}">${modes.map((mode,index)=>`<button class="system-overlay-button ${index===0?'active':''}" data-system-comparison="${escapeHTML(mode.id)}" data-system-comparison-part="${escapeHTML(mode.part)}" aria-pressed="${index===0}">${escapeHTML(mode.label)}</button>`).join('')}</div>`:''}${stages.length?`<div class="system-stage" role="group" aria-label="${escapeHTML(details.accessibility?.screenReaderSummary||title)}"><div class="system-track" aria-hidden="true">${stages.map((stage,index)=>`<div class="system-node" data-stage="${index}"><span>${index+1}</span><b>${escapeHTML(stage.label)}</b></div>`).join('')}</div><p class="system-stage-text" data-stage-text aria-live="polite">${escapeHTML(stages[0].text)}</p></div>`:''}<div class="system-part-list" aria-label="Selectable anatomical components">${parts.map((item,index)=>`<button class="system-part-button ${index===0?'active':''}" data-system-part="${escapeHTML(item.id)}" aria-pressed="${index===0}"><strong>${escapeHTML(item.label)}</strong><span>${escapeHTML(item.short)}</span></button>`).join('')}</div>${overlays.length?`<div class="system-overlay-list" aria-label="Anatomical overlays">${overlays.map(item=>`<button class="system-overlay-button" data-system-overlay="${escapeHTML(item.id)}" aria-pressed="false">${escapeHTML(item.label)}</button>`).join('')}</div>`:''}<article class="system-detail" data-system-detail aria-live="polite">${detailMarkup(first)}</article>${details.explorer?.returnToOverview?'<button class="secondary system-overview-button" data-system-overview>Return to overview</button>':''}</section>`;
}

export function bindSystemExplorer(root,details){
  if(!root||!details||root.classList.contains('system-explorer-empty'))return;
  const {parts,stages,overlays}=model(details),partButtons=[...root.querySelectorAll('[data-system-part]')],overlayButtons=[...root.querySelectorAll('[data-system-overlay]')],comparisonButtons=[...root.querySelectorAll('[data-system-comparison]')],detail=root.querySelector('[data-system-detail]'),run=root.querySelector('[data-system-run]'),stageText=root.querySelector('[data-stage-text]'),nodes=[...root.querySelectorAll('[data-stage]')];
  const bindDestinations=()=>detail.querySelectorAll('[data-open]').forEach(button=>button.onclick=()=>window.openAtlasConcept?.(button.dataset.open));
  const selectPart=id=>{const item=parts.find(part=>part.id===id)||parts[0];if(!item)return;partButtons.forEach(button=>{const active=button.dataset.systemPart===item.id;button.classList.toggle('active',active);button.setAttribute('aria-pressed',String(active))});overlayButtons.forEach(button=>{button.classList.remove('active');button.setAttribute('aria-pressed','false')});detail.innerHTML=detailMarkup(item);bindDestinations()};
  partButtons.forEach(button=>button.onclick=()=>selectPart(button.dataset.systemPart));
  comparisonButtons.forEach(button=>button.onclick=()=>{comparisonButtons.forEach(candidate=>{const active=candidate===button;candidate.classList.toggle('active',active);candidate.setAttribute('aria-pressed',String(active))});selectPart(button.dataset.systemComparisonPart)});
  overlayButtons.forEach(button=>button.onclick=()=>{const item=overlays.find(overlay=>overlay.id===button.dataset.systemOverlay);if(!item)return;overlayButtons.forEach(candidate=>{const active=candidate===button;candidate.classList.toggle('active',active);candidate.setAttribute('aria-pressed',String(active))});partButtons.forEach(candidate=>{candidate.classList.remove('active');candidate.setAttribute('aria-pressed','false')});detail.innerHTML=`<div class="eyebrow">Overlay</div><h3>${escapeHTML(item.label)}</h3><p>${escapeHTML(item.text)}</p>`});
  root.querySelector('[data-system-overview]')?.addEventListener('click',()=>selectPart(parts[0]?.id));
  bindDestinations();
  if(!run||!stages.length)return;
  let timer=null;
  run.onclick=()=>{if(timer)return;let index=0;run.disabled=true;root.classList.add('system-running');const advance=()=>{nodes.forEach((node,nodeIndex)=>node.classList.toggle('active',nodeIndex===index));const stage=stages[index];if(!stage){finish();return}stageText.textContent=`${stage.label}: ${stage.text}`;index+=1;if(index>=stages.length)finish()};const finish=()=>{if(timer)clearInterval(timer);timer=null;run.disabled=false;root.classList.remove('system-running')};if(window.matchMedia?.('(prefers-reduced-motion: reduce)').matches){stages.forEach((stage,nodeIndex)=>{nodes.forEach((node,index)=>node.classList.toggle('active',index===nodeIndex));stageText.textContent=`${stage.label}: ${stage.text}`});finish();return}advance();if(index<stages.length)timer=setInterval(advance,1200)};
}
