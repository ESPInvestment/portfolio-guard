const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const zlib=require('node:zlib');
const {Inflate}=require('pako');
const html=fs.readFileSync('index.html','utf8');
const code=html.match(/<script type="module">([\s\S]*?)<\/script>/)[1]
  .replace(/^\s*import\s+\{createClient\}[^\n]*\n/,'');
const elements=new Map();
const getElementById=id=>{
 if(!elements.has(id))elements.set(id,{value:'',files:[],textContent:'',innerHTML:'',classList:{toggle(){}},addEventListener(){}});
 return elements.get(id);
};
const ctx=vm.createContext({
 document:{getElementById},localStorage:{getItem(){return null},setItem(){}},
 Date,Map,Set,String,Number,JSON,console,TextEncoder,TextDecoder,TextDecoderStream,
 ReadableStream,TransformStream,Uint8Array,Response
});
new vm.Script(code).runInContext(ctx);
const record=isin=>({instrumentIdentificationCode:isin,venueOfExecution:'XETA',priceCurrency:'EUR'});
const member1=zlib.gzipSync(JSON.stringify([record('FR0010524777')]));
const member2=zlib.gzipSync(JSON.stringify([record('IE00B3VWM098')]));
// Two RFC 1952 gzip members concatenated. We check the decompressor separately,
// as they represent two complete JSON arrays rather than a single valid daily JSON array.
const fixture=Buffer.concat([member1,member2]);
const file={stream(){return new ReadableStream({
 start(ctrl){for(let i=0;i<fixture.length;i+=9)ctrl.enqueue(new Uint8Array(fixture.subarray(i,i+9)));ctrl.close();}
})}};
ctx.file=file;ctx.Inflate=Inflate;
(async()=>{
 const stream=vm.runInContext('pakoGzipStream(file,Inflate)',ctx);
 const bytes=Buffer.from(await new Response(stream).arrayBuffer());
 const expected=Buffer.from(JSON.stringify([record('FR0010524777')])+JSON.stringify([record('IE00B3VWM098')]));
 assert.deepEqual(bytes,expected);
 assert.ok(html.includes("pako@2.2.0"));
 console.log('PASS concatenated gzip members decoded in browser streams without writes');
})().catch(e=>{console.error(e);process.exitCode=1;});
