const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const html=fs.readFileSync('index.html','utf8');
const source=html.match(/<script type="module">([\s\S]*?)<\/script>/)[1]
 .replace(/^\s*import\s+\{createClient\}[^\n]*\n/,'');
const elements=new Map();
function getElementById(id){
 if(!elements.has(id))elements.set(id,{value:'',textContent:'',innerHTML:'',disabled:false,
  classList:{toggle(){}},addEventListener(){},files:[]});
 return elements.get(id);
}
const context=vm.createContext({document:{getElementById},localStorage:{getItem(){return null;},setItem(){}},console,Date,Number,String,Map,Set});
new vm.Script(source).runInContext(context);
context.items=[{isin:'DE0009770206'},{isin:'FR0010524777'}];
const actual=vm.runInContext('createDailyTemplate(items)',context);
assert.ok(actual.startsWith('\ufeffisin,date,price,source\r\n'));
assert.ok(actual.includes('DE0009770206,,,\r\n'));
assert.ok(actual.includes('FR0010524777,,,\r\n'));
assert.ok(!actual.includes('100.00'));
const lines=actual.replace(/^\ufeff/,'').trim().split('\r\n');
assert.equal(lines.length,3);
assert.throws(()=>vm.runInContext("createDailyTemplate([{isin:'DE0009770206'},{isin:'DE0009770206'}])",context),/Doppelte ISINs/);
console.log('PASS: CSV template has two distinct ISINs, no fabricated values, correct header');
