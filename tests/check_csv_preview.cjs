// Static and isolated CSV preview tests; no browser, secrets, network or Supabase.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const html = fs.readFileSync('index.html', 'utf8');
const sourceMatch = html.match(/<script type="module">([\s\S]*?)<\/script>/);
assert.ok(sourceMatch, 'Expected inline app module');
let source = sourceMatch[1].replace(/^\s*import\s+\{createClient\}[^\n]*\n/, '');
const elements = new Map();
function element(id) {
  if (!elements.has(id)) elements.set(id, {
    value: '', textContent: '', innerHTML: '', disabled: false,
    classList: { toggle() {} },
    addEventListener() {},
    files: [],
  });
  return elements.get(id);
}
const context = vm.createContext({
  document: { getElementById: element },
  localStorage: { getItem() { return null; }, setItem() {} },
  console,
  Date, Number, String, Map, Set,
  confirm() { return false; },
});
new vm.Script(source, { filename: 'portfolio-guard-inline.js' }).runInContext(context);
vm.runInContext("positions=[{isin:'FR0010524777',last_date:'2026-11-10'},{isin:'DE0009770206',last_date:null}]", context);
function check(csv, valid, invalid) {
  context.csvInput = csv;
  const parsed = vm.runInContext('previewCSV(csvInput)', context);
  assert.equal(parsed.result.length, valid, 'expected valid rows');
  assert.equal(parsed.issues.length, invalid, 'expected invalid rows');
}
check('isin,date,price,source\nFR0010524777,2026-11-11,123.45,Official exchange',1,0);
check('isin;date;price;source\nFR0010524777;2026-11-11;123.45;Official exchange',1,0);
check('isin,date,price,source\nFR0010524777,2026-11-11,123.45,Official exchange\nFR0010524777,2026-11-11,124,Official exchange',1,1);
check('isin,date,price,source\nUNKNOWN,2026-11-11,10,Official exchange',0,2);
check('isin,date,price,source\nFR0010524777,2026-11-09,10,Official exchange',0,2);
check('isin,date,price,source\nFR0010524777,2026-11-11,-10,Official exchange',0,2);
check('isin,date,price,source\nFR0010524777,2099-01-01,10,Official exchange',0,2);
check('isin,date,price,source\nFR0010524777,2026-11-11,10,"Official, exchange"',1,0);
console.log('Portfolio Guard CSV syntax + eight preview cases passed. No user data accessed.');
