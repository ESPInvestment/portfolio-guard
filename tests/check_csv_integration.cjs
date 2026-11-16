// Isolated UI integration test: mock Supabase completely, zero network writes.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('index.html','utf8');
const source = html.match(/<script type="module">([\s\S]*?)<\/script>/)[1]
  .replace(/^\s*import\s+\{createClient\}[^\n]*\n/,'');
const elements=new Map();
const el=id=>{
 if(!elements.has(id)) elements.set(id,{
  value:'',textContent:'',innerHTML:'',disabled:false,files:[],
  classList:{toggle(){}},addEventListener(){}
 });
 return elements.get(id);
};
const rows=[
 {isin:'FR0010524777',last_date:'2026-11-10',status:'active',distance_pct:10,weight_pct:10},
 {isin:'DE0009770206',last_date:null,status:'waiting',distance_pct:1,weight_pct:10}
];
const instruments=rows.map(p=>({isin:p.isin,name:p.isin,price_type:'CLOSE',currency:'EUR'}));
const calls=[];
const fakeClient={
 from(table){return {select(){return {order:async()=>({data:table==='pg_positions'?rows:instruments,error:null})}}}},
 async rpc(name,args){calls.push({name,args});return {data:'active',error:null}}
};
const ctx=vm.createContext({
 document:{getElementById:el},localStorage:{getItem(){return null},setItem(){}},
 Date,Number,String,Map,Set,console,
 confirm:()=>true
});
new vm.Script(source,{filename:'portfolio-guard-app.js'}).runInContext(ctx);
vm.runInContext('client=globalFakeClient', Object.assign(ctx,{globalFakeClient:fakeClient}));
async function test(){
 await vm.runInContext('refresh()',ctx);
 const csv='isin,date,price,source\nFR0010524777,2026-11-11,123.45,Official exchange';
 el('csv').files=[{size:csv.length,text:async()=>csv}];
 await el('previewcsv').onclick();
 assert.equal(el('importcsv').disabled,false,'valid CSV should enable import');
 assert.equal(calls.length,0,'preview must never write Supabase');
 await el('importcsv').onclick();
 assert.equal(calls.length,1,'confirmed import should write one price');
 assert.equal(calls[0].name,'pg_record_price');
 assert.equal(calls[0].args.p_isin,'FR0010524777');
 assert.equal(calls[0].args.p_date,'2026-11-11');
 assert.equal(calls[0].args.p_price,123.45);
 assert.equal(el('importcsv').disabled,true,'prevent accidental repeat import');
 const invalid='isin,date,price,source\nFR0010524777,2026-11-11,-1,Official exchange';
 el('csv').files=[{size:invalid.length,text:async()=>invalid}];
 await el('previewcsv').onclick();
 assert.equal(el('importcsv').disabled,true);
 assert.equal(calls.length,1);
 console.log('CSV UI mock integration PASS: preview read-only; confirmed valid import only; invalid CSV blocked');
}
test().catch(e=>{console.error(e);process.exitCode=1});
