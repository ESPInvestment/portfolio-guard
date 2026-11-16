const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const html=fs.readFileSync('index.html','utf8');
const script=html.match(/<script type="module">([\s\S]*?)<\/script>/)[1].replace(/^\s*import\s+\{createClient\}[^\n]*\n/,'');
const elements=new Map(),getElementById=id=>{
 if(!elements.has(id))elements.set(id,{value:'',innerHTML:'',textContent:'',files:[],classList:{toggle(){}},addEventListener(){}});
 return elements.get(id);
};
const ctx=vm.createContext({document:{getElementById},localStorage:{getItem(){return null},setItem(){}},console,Date,Map,Set,JSON,Number,String});
new vm.Script(script).runInContext(ctx);
ctx.data='[{"isin":"FR0010524777","trade":"123.45"},{"isin":"OTHER"},{"isin":"LU0321465469"}]';
const parsed=vm.runInContext('parseXetraSample(data)',ctx);
assert.equal(parsed.records,3);
assert.equal(parsed.count.FR0010524777,1);
assert.equal(parsed.count.LU0321465469,1);
assert.equal(parsed.count.IE00B3VWM098,0);
ctx.nested='{"postTrade":[{"instrumentIdentificationCode":"FR0010524777","trades":[{"price":"23.12"}]},{"instrumentIdentificationCode":"IE00B3VWM098"}],"metadata":{"venue":"XETA"}}';
const nested=vm.runInContext('parseXetraSample(nested)',ctx);
assert.equal(nested.count.FR0010524777,1);
assert.equal(nested.count.IE00B3VWM098,1);
assert.ok(nested.commonFields.some(x=>x[0]==='instrumentIdentificationCode'));
assert.ok(nested.arrays>=1);
assert.equal(nested.rootKeys[0],'postTrade');
assert.equal(nested.codedRecords,2);
assert.equal(nested.identifierTypes[0][0],'Nicht angegeben');
assert.equal(nested.exampleCodes.length,2);
ctx.rich='[{"instrumentIdentificationCode":"OTHER","instrumentIdentificationCodeType":"ISIN","venueOfExecution":"XETA","priceCurrency":"EUR"},{"instrumentIdentificationCode":"FR0010524777","instrumentIdentificationCodeType":"ISIN","venueOfExecution":"XETA","priceCurrency":"EUR"}]';
const rich=vm.runInContext('parseXetraSample(rich)',ctx);
assert.equal(rich.codedRecords,2);
assert.equal(rich.identifierTypes[0][0],'ISIN');
assert.equal(rich.venues[0][0],'XETA');
assert.equal(rich.currencies[0][0],'EUR');
assert.equal(rich.count.FR0010524777,1);

ctx.zero='{"data":[{"instrumentIdentificationCode":"OTHER"}]}';
const empty=vm.runInContext('parseXetraSample(zero)',ctx);
assert.equal(Object.values(empty.count).reduce((a,b)=>a+b,0),0);
assert.ok(empty.commonFields.some(x=>x[0]==='instrumentIdentificationCode'));

assert.ok(html.includes('id="xetrafile"'));
assert.ok(html.includes('id="inspectxetra"'));
assert.ok(html.includes('DecompressionStream'));
assert.ok(!script.includes("savePrice(result"));
console.log('PASS Xetra inspector: local ISIN counting, no price extraction or writes');

const fake=[
 {name:'one.json',size:300},
 {name:'two.json',size:200},
 {name:'bad.json',size:100}
];
const sample1={records:2,arrays:1,codedRecords:2,count:{FR0010524777:1},keys:{FR0010524777:['instrumentIdentificationCode']},identifierTypes:[['ISIN',2]],venues:[['XETA',2]],currencies:[['EUR',2]],commonFields:[['instrumentIdentificationCode',2]]};
const sample2={records:1,arrays:1,codedRecords:1,count:{FR0010524777:1,IE00B3VWM098:1},keys:{IE00B3VWM098:['instrumentIdentificationCode']},identifierTypes:[['ISIN',1]],venues:[['XETA',1]],currencies:[['EUR',1]],commonFields:[['instrumentIdentificationCode',1]]};
ctx.samples=[sample1,sample2];
ctx.files=fake;
ctx.reader=async file=>{if(file.name==='bad.json')throw Error('Invalid JSON');return ctx.samples[file.name==='one.json'?0:1];};
(async ()=>{
 const agg=await vm.runInContext('scanXetraFiles(files,reader)',ctx);
 assert.equal(agg.files,3);
 assert.equal(agg.success,2);
 assert.equal(agg.failures.length,1);
 assert.equal(agg.count.FR0010524777,2);
 assert.equal(agg.count.IE00B3VWM098,1);
 assert.equal(agg.codedRecords,3);
 assert.equal(agg.venues[0][1],3);
 assert.ok(html.includes('id="xetrafile" type="file" multiple'));
 console.log('PASS multi-file Xetra aggregation and error handling');
})().catch(error=>{console.error(error);process.exitCode=1;});
