const clamp=(value,min,max)=>Math.max(min,Math.min(max,value));

export class MasteryTracker {
  constructor(storageKey='cna-mastery-v1'){
    this.storageKey=storageKey;
    this.records=this.load();
  }

  load(){
    try{return JSON.parse(localStorage.getItem(this.storageKey))||{}}
    catch{return {}}
  }

  save(){localStorage.setItem(this.storageKey,JSON.stringify(this.records))}

  ensure(id){
    return this.records[id]??={
      id,
      quizAttempts:0,
      quizCorrect:0,
      reviewCount:0,
      reviewGradeTotal:0,
      lastSeen:null,
      lastFormat:0,
    };
  }

  recordQuiz(id,correct){
    const record=this.ensure(id);
    record.quizAttempts+=1;
    if(correct)record.quizCorrect+=1;
    record.lastSeen=Date.now();
    this.save();
    return record;
  }

  recordReview(id,grade){
    const record=this.ensure(id);
    record.reviewCount+=1;
    record.reviewGradeTotal+=clamp(Number(grade)||0,0,5);
    record.lastSeen=Date.now();
    record.lastFormat=(record.lastFormat+1)%3;
    this.save();
    return record;
  }

  hasEvidence(id){
    const record=this.records[id];
    return !!record&&(record.quizAttempts>0||record.reviewCount>0);
  }

  score(id,completed=false){
    const record=this.records[id];
    if(!record)return completed?45:0;
    const quiz=record.quizAttempts?record.quizCorrect/record.quizAttempts:0;
    const review=record.reviewCount?record.reviewGradeTotal/(record.reviewCount*5):0;
    const evidence=(record.quizAttempts?0.55:0)+(record.reviewCount?0.45:0);
    if(!evidence)return completed?45:0;
    const weighted=((record.quizAttempts?quiz*0.55:0)+(record.reviewCount?review*0.45:0))/evidence;
    const repetitionBonus=Math.min(12,record.reviewCount*2);
    return Math.round(clamp(weighted*88+repetitionBonus,0,100));
  }

  label(score){
    if(score>=80)return 'Strong';
    if(score>=60)return 'Developing';
    if(score>=40)return 'Fragile';
    return 'Needs retrieval';
  }

  weakest(ids,completedFn=()=>false,limit=5){
    return ids
      .filter(id=>this.hasEvidence(id)||completedFn(id))
      .map(id=>({id,score:this.score(id,completedFn(id))}))
      .sort((a,b)=>a.score-b.score||a.id.localeCompare(b.id))
      .slice(0,limit);
  }

  rankCards(cards,completedFn=()=>false){
    return [...cards].sort((a,b)=>{
      const scoreA=this.score(a.id,completedFn(a.id));
      const scoreB=this.score(b.id,completedFn(b.id));
      return scoreA-scoreB||a.due-b.due;
    });
  }

  retrievalFormat(id){
    return this.records[id]?.lastFormat||0;
  }
}
