const DAY=86400000;
export class SpacedRepetition {
  constructor(storageKey='cna-review-v1'){this.storageKey=storageKey;this.cards=this.load()}
  load(){try{return JSON.parse(localStorage.getItem(this.storageKey))||{}}catch{return {}}}
  save(){localStorage.setItem(this.storageKey,JSON.stringify(this.cards))}
  ensure(id){return this.cards[id]??={id,repetitions:0,interval:0,ease:2.5,due:Date.now(),lastReviewed:null}}
  grade(id,quality){const c=this.ensure(id);const q=Math.max(0,Math.min(5,quality));if(q<3){c.repetitions=0;c.interval=1}else{c.interval=c.repetitions===0?1:c.repetitions===1?6:Math.max(1,Math.round(c.interval*c.ease));c.repetitions+=1}c.ease=Math.max(1.3,c.ease+(0.1-(5-q)*(0.08+(5-q)*0.02)));c.lastReviewed=Date.now();c.due=Date.now()+c.interval*DAY;this.save();return c}
  add(id){const c=this.ensure(id);c.due=Math.min(c.due,Date.now());this.save();return c}
  due(ids=null){const allowed=ids?new Set(ids):null;return Object.values(this.cards).filter(c=>(!allowed||allowed.has(c.id))&&c.due<=Date.now()).sort((a,b)=>a.due-b.due)}
  countDue(ids=null){return this.due(ids).length}
  get(id){return this.cards[id]||null}
}
