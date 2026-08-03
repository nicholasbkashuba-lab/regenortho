const {chromium}=require('playwright-core');
const fs=require('fs');
(async()=>{
  const pages=fs.readFileSync('sitemap.xml','utf8').match(/<loc>(.*?)<\/loc>/g)
    .map(s=>s.replace(/<\/?loc>/g,''))
    .map(u=>u.replace(/^https?:\/\/[^/]+/,''))
    .map(p=>(p===''||p==='/')?'/index.html':p);
  const axe=fs.readFileSync('node_modules/axe-core/axe.min.js','utf8');
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome'});
  const pg=await b.newPage({viewport:{width:1280,height:900},reducedMotion:'reduce'});
  let total=0,bad=0; const tally={};
  for(const p of pages){
    try{ await pg.goto('http://localhost:8901'+p,{waitUntil:'networkidle',timeout:30000}); }
    catch(e){ console.log('LOAD FAIL',p,e.message.split('\n')[0]); continue; }
    await pg.waitForTimeout(350);
    await pg.addScriptTag({content:axe});
    const r=await pg.evaluate(()=>axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}}));
    total++;
    if(r.violations.length){bad++;
      r.violations.forEach(v=>{tally[v.id]=(tally[v.id]||0)+v.nodes.length});
      console.log('VIOLATION',p,r.violations.map(v=>`${v.id}(${v.nodes.length})`).join(' '));}
  }
  console.log(`\nRESULT: ${total-bad}/${total} pages clean, ${bad} with violations`);
  if(Object.keys(tally).length) console.log('by rule:',JSON.stringify(tally,null,1));
  await b.close();
})().catch(e=>{console.error('ERR',e.message);process.exit(1)});
