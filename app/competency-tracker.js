export const COMPETENCIES = [
  {id:'recognise', label:'Recognise', description:'Identify the core structure, process, or principle.'},
  {id:'explain', label:'Explain', description:'Explain the concept accurately in your own words.'},
  {id:'localise', label:'Localise', description:'Place the structure or pathway in an anatomical or network context.'},
  {id:'compare', label:'Compare', description:'Distinguish intact and disrupted function or competing patterns.'},
  {id:'apply', label:'Apply', description:'Use the concept in clinical reasoning without overclaiming.'},
];

const clamp=(value,min,max)=>Math.max(min,Math.min(max,value));

export class CompetencyTracker {
  constructor(storageKey='cna-competency-v1'){
    this.storageKey=storageKey;
    this.records=this.load();
  }

  load(){
    try{return JSON.parse(localStorage.getItem(this.storageKey))||{}}
    catch{return {}}
  }

  save(){localStorage.setItem(this.storageKey,JSON.stringify(this.records))}

  ensure(id,skill){
    const concept=this.records[id]??={};
    return concept[skill]??={attempts:0,success:0,gradeTotal:0,lastSeen:null};
  }

  record(id,skill,{correct=null,grade=null}={}){
    const entry=this.ensure(id,skill);
    entry.attempts+=1;
    if(correct===true)entry.success+=1;
    if(grade!==null)entry.gradeTotal+=clamp(Number(grade)||0,0,5);
    entry.lastSeen=Date.now();
    this.save();
    return entry;
  }

  hasEvidence(id,skill){return !!this.records[id]?.[skill]?.attempts}

  score(id,skill){
    const entry=this.records[id]?.[skill];
    if(!entry?.attempts)return null;
    const accuracy=entry.success/entry.attempts;
    const graded=entry.gradeTotal?entry.gradeTotal/(entry.attempts*5):0;
    const hasGrades=entry.gradeTotal>0;
    const value=hasGrades?(accuracy*0.35+graded*0.65):accuracy;
    return Math.round(clamp(value*100,0,100));
  }

  label(score){
    if(score===null)return 'Not sampled';
    if(score>=80)return 'Strong';
    if(score>=60)return 'Developing';
    if(score>=40)return 'Fragile';
    return 'Needs practice';
  }

  nextSkill(id,available=['recognise','explain']){
    const permitted=available.filter(skill=>COMPETENCIES.some(item=>item.id===skill));
    if(!permitted.length)return 'recognise';
    const recognise=this.score(id,'recognise');
    if(recognise===null||recognise<55)return permitted.includes('recognise')?'recognise':permitted[0];
    const explain=this.score(id,'explain');
    if(permitted.includes('explain')&&(explain===null||explain<55))return 'explain';
    const higher=permitted.filter(skill=>!['recognise','explain'].includes(skill));
    if(higher.length){
      const unsampled=higher.find(skill=>this.score(id,skill)===null);
      if(unsampled)return unsampled;
      return [...higher].sort((a,b)=>this.score(id,a)-this.score(id,b))[0];
    }
    return [...permitted].sort((a,b)=>(this.score(id,a)??-1)-(this.score(id,b)??-1))[0];
  }

  aggregate(skill,ids){
    const scores=ids.map(id=>this.score(id,skill)).filter(score=>score!==null);
    if(!scores.length)return null;
    return Math.round(scores.reduce((sum,score)=>sum+score,0)/scores.length);
  }
}
