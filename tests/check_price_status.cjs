const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const html=fs.readFileSync('index.html','utf8');
const match=html.match(/<script type="module">([\s\S]*?)<\/script>/);
assert.ok(match);
const code=match[1].replace(/^\s*import\s+\{createClient\}[^\n]*\n/,'');
const elements=new Map();
const el=id=>{if(!elements.has(id))elements.set(id,{value:'',textContent:'',innerHTML:'',disabled:false,files:[],classList:{toggle(){}},addEventListener(){}});return elements.get(id)};
const ctx=vm.createContext({document:{getElementById:el},localStorage:{getItem(){return null},setItem(){}},console,Date,Number,String,Map,Set});
new vm.Script(code).runInContext(ctx);
function state(last){
  ctx.fixture={last_date:last};
  return vm.runInContext("dataStatus(fixture,'2026-11-16').label",ctx);
}
assert.equal(state(null),'Kein Kurs erfasst');
assert.equal(state('2026-11-16'),'Kursdatum aktuell');
assert.equal(state('2026-11-14'),'Verzögert / Wochenende möglich');
assert.equal(state('2026-11-10'),'Veraltet – prüfen');
assert.equal(state('2026-11-17'),'Datum in der Zukunft – prüfen');
ctx.list=[{isin:'FR0010524777',last_date:'2026-11-13'}];
ctx.lookup={'FR0010524777':{name:'ETF Test',price_type:'CLOSE'}};
const rendered=vm.runInContext("renderPriceStatus(list,lookup,'2026-11-16')",ctx);
assert.ok(rendered.includes('FR0010524777'));
assert.ok(rendered.includes('Nicht in Positionsansicht verfügbar'));
assert.ok(rendered.includes('Verzögert / Wochenende möglich'));
assert.equal((html.match(/id="price-status-rows"/g)||[]).length,1);
console.log('PASS: read-only daily price overview, all status categories and source transparency');
