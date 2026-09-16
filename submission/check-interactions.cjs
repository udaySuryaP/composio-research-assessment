const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('submission/composio-assessment-uday.html','utf8');
const dataText=html.match(/<script id="matrix-data" type="application\/json">(.*?)<\/script>/s)[1];
const scripts=[...html.matchAll(/<script>(.*?)<\/script>/gs)];
const data=JSON.parse(dataText),rows=data.map(()=>({hidden:false}));
const elements={'matrix-data':{textContent:dataText},search:{value:''},category:{value:''},coverage:{value:''},count:{textContent:''}};
for(const id of ['search','category','coverage'])elements[id].addEventListener=(event,callback)=>{elements[id].callback=callback};
const document={getElementById:id=>elements[id],querySelectorAll:()=>rows};
const ctx=vm.createContext({document});vm.runInContext(scripts[0][1],ctx);
function run(q='',cat='',coverage=''){elements.search.value=q;elements.category.value=cat;elements.coverage.value=coverage;elements.search.callback();return rows.filter(r=>!r.hidden).length;}
assert.equal(run(),100);assert.equal(run('Shopify'),1);assert.equal(run('SHOPIFY'),1);assert.equal(run('no-such-app-unique'),0);
for(const cat of new Set(data.map(r=>r.category)))assert.equal(run('',cat),10);
assert.equal(run('','','partial'),22);assert.equal(run('','','unknown'),78);
assert.equal(run('Shopify',data.find(r=>r.app_name==='Shopify').category,'partial'),1);
assert.equal(run(),100);assert.equal(elements.count.textContent,'100 of 100 apps');
console.log('PASS: actual embedded JavaScript; search, case-insensitivity, empty result, all 10 category filters, both coverage filters, combined filters, reset and count');
