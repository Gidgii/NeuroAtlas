const CONFIDENCE_PROBABILITY = {1:0.35,2:0.55,3:0.75,4:0.9};
const clamp=(value,min,max)=>Math.max(min,Math.min(max,value));

export const CONFIDENCE_LEVELS = [
  {id:1,label:'Guessing',description:'I am mostly guessing.'},
  {id:2,label:'Unsure',description:'I have a partial model but important uncertainty remains.'},
  {id:3,label:'Fairly sure',description:'I expect my answer to be right, but could explain what would change my mind.'},
  {id:4,label:'Certain',description:'I am highly confident and can justify the reasoning.'},
];

export class CalibrationTracker {
  constructor(storageKey='cna-calibration-v1'){
    this.storageKey=storageKey;
    this.records=this.load();
  }

  load(){
    try{return JSON.parse(localStorage.getItem(this.storageKey))||{}}
    catch{return {}}
  }

  save(){localStorage.setItem(this.storageKey,JSON.stringify(this.records))}

  record(id,skill,{confidence,correct}={}){
    const level=clamp(Number(confidence)||0,1,4);
    if(!CONFIDENCE_PROBABILITY[level]||typeof correct!=='boolean')return null;
    const key=`${id}::${skill||'recognise'}`;
    const entry=this.records[key]??={attempts:0,calibrationTotal:0,highConfidenceErrors:0,lowConfidenceSuccess:0,lastSeen:null};
    const expected=CONFIDENCE_PROBABILITY[level];
    const outcome=correct?1:0;
    const calibration=1-Math.abs(expected-outcome);
    entry.attempts+=1;
    entry.calibrationTotal+=calibration;
    if(level>=3&&!correct)entry.highConfidenceErrors+=1;
    if(level<=2&&correct)entry.lowConfidenceSuccess+=1;
    entry.lastSeen=Date.now();
    this.save();
    return entry;
  }

  profile(){
    const entries=Object.values(this.records);
    const attempts=entries.reduce((sum,item)=>sum+(item.attempts||0),0);
    if(!attempts)return {attempts:0,score:null,label:'Not sampled',highConfidenceErrors:0,lowConfidenceSuccess:0};
    const calibrationTotal=entries.reduce((sum,item)=>sum+(item.calibrationTotal||0),0);
    const score=Math.round(clamp(calibrationTotal/attempts,0,1)*100);
    const highConfidenceErrors=entries.reduce((sum,item)=>sum+(item.highConfidenceErrors||0),0);
    const lowConfidenceSuccess=entries.reduce((sum,item)=>sum+(item.lowConfidenceSuccess||0),0);
    return {attempts,score,label:this.label(score),highConfidenceErrors,lowConfidenceSuccess};
  }

  label(score){
    if(score===null)return 'Not sampled';
    if(score>=85)return 'Well calibrated';
    if(score>=72)return 'Improving';
    if(score>=58)return 'Needs calibration';
    return 'Confidence mismatch';
  }

  guidance(profile=this.profile()){
    if(!profile.attempts)return 'Rate confidence before revealing answers to build a calibration profile.';
    if(profile.highConfidenceErrors>profile.lowConfidenceSuccess&&profile.highConfidenceErrors>=2)return 'Watch for overconfidence: slow down when a localisation or clinical inference feels immediately obvious.';
    if(profile.lowConfidenceSuccess>profile.highConfidenceErrors&&profile.lowConfidenceSuccess>=2)return 'Your knowledge may be stronger than your confidence. Practise committing to a hypothesis before checking.';
    return 'Keep matching confidence to evidence quality, and explicitly name what would change your mind.';
  }
}
