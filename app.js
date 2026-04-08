function el(id){return document.getElementById(id)}
const today = new Date().toISOString().slice(0,10);
el('date').value = today;

async function fetchJson(path){
  try{
    const r = await fetch(path);
    if(!r.ok) return [];
    return await r.json();
  }catch(e){
    return [];
  }
}

// expanded topic keywords to improve clustering
const TOPIC_KEYWORDS = {
  'Prime Video / Streaming': ['prime video','prime','twitch','stream','streaming','video','watch','primevideo','amazon prime'],
  'Entertainment & Media': ['movie','season','trailer','premier','premiere','festival','livestream','show','series','episode'],
  'Devices & Hardware': ['kindle','device','samsung','echo','fire','launch','hardware','tablet','speaker'],
  'Pricing & Promotions': ['price','discount','sale','offer','rollback','coupon','deal','promotion'],
  'Supply Chain & Logistics': ['delivery','fulfillment','logistics','supply','warehouse','pickup','shipping','inventory'],
  'Healthcare Services': ['pharmacy','clinic','health','covid','vaccine','telehealth','healthcare','pharmacy'],
  'Corporate Strategy': ['investor','annual','leadership','strategy','partnership','acquisition','merger','newsroom','company','press']
};

// Helen of Troy brand keywords (expand as needed)
const BRAND_KEYWORDS = {
  'OXO': ['oxo'],
  'Hydro Flask': ['hydro flask','hydroflask'],
  'Osprey': ['osprey'],
  'Braun': ['braun'],
  'PUR': ['pur'],
  'Honeywell': ['honeywell'],
  'Vicks': ['vicks'],
  'Hot Tools': ['hot tools','hottools'],
  'Drybar': ['drybar'],
  'Curlsmith': ['curlsmith'],
  'Revlon': ['revlon']
};

function classifyTopic(title, url){
  const text = (title + ' ' + (url||'')).toLowerCase();
  for(const [topic, kws] of Object.entries(TOPIC_KEYWORDS)){
    for(const k of kws){
      if(text.includes(k)) return topic;
    }
  }
  // fallback: choose domain path hint
  try{
    const u = new URL(url);
    const p = u.pathname.split('/').filter(Boolean);
    if(p.length) return p[0];
  }catch(e){}
  return 'Other';
}

function detectBrands(title, url){
  const text = (title + ' ' + (url||'')).toLowerCase();
  const found = new Set();
  for(const [brand, kws] of Object.entries(BRAND_KEYWORDS)){
    for(const kw of kws){
      // escape kw for safe regex, but fallback to includes
      try{
        const re = new RegExp(kw.replace(/[-/\\^$*+?.()|[\]{}]/g,'\\$&'), 'i');
        if(re.test(text)) found.add(brand);
      }catch(e){ if(text.includes(kw)) found.add(brand); }
    }
  }
  return Array.from(found);
}

function render(events, sortBy='relevance'){
  const container = el('events');
  container.innerHTML = '';
  if(!events || events.length===0){
    container.innerText = 'No events found for selection.';
    return;
  }

  // annotate events with topic and brands
  events.forEach(e => {
    e._topic = classifyTopic(e.title, e.source_url);
    e._brands = detectBrands(e.title, e.source_url);
  });

  // compute topic counts for relevance
  const topicCounts = {};
  events.forEach(e => topicCounts[e._topic] = (topicCounts[e._topic]||0)+1);

  // grouping by topic when relevance sort is selected
  if(sortBy === 'relevance'){
    const topics = Object.keys(topicCounts).sort((a,b)=>topicCounts[b]-topicCounts[a]);
    topics.forEach(topic => {
      const header = document.createElement('h3');
      header.innerText = `${topic} (${topicCounts[topic]})`;
      header.className = 'topic-header';
      container.appendChild(header);
      const list = document.createElement('div');
      list.className = 'topic-list';
      const items = events.filter(e=>e._topic===topic);
      items.sort((x,y)=> x.title.localeCompare(y.title));
      items.forEach(e=> list.appendChild(renderEvent(e)));
      container.appendChild(list);
    });
    // populate sidebar topics with counts
    populateSidebar(topics.map(t=>({topic:t,count:topicCounts[t]})));
    return;
  }

  // other sorts: flatten then sort
  let sorted = events.slice();
  if(sortBy==='retailer') sorted.sort((a,b)=> a.retailer.localeCompare(b.retailer));
  if(sortBy==='category') sorted.sort((a,b)=> a.category.localeCompare(b.category));
  if(sortBy==='title') sorted.sort((a,b)=> a.title.localeCompare(b.title));

  sorted.forEach(e=> container.appendChild(renderEvent(e)));
  populateSidebar(Object.keys(topicCounts).sort((a,b)=>topicCounts[b]-topicCounts[a]).map(t=>({topic:t,count:topicCounts[t]})));
}

function renderEvent(e){
  const d = document.createElement('div');
  d.className = 'event';
  const brands = (e._brands && e._brands.length)?` <span style="color:#0b5394">[${e._brands.join(', ')}]</span>`:'';
  d.innerHTML = `<div><strong>${e.retailer}</strong> — ${e.title} ${brands}</div><div class="meta"><a href="${e.source_url}" target="_blank">source</a> • ${e.category}</div>`;
  return d;
}

function populateBrandSelect(foundBrands){
  const sel = el('brand');
  // clear extras but keep 'all'
  sel.querySelectorAll('option:not([value="all"])').forEach(o=>o.remove());
  foundBrands.forEach(b=>{
    const opt = document.createElement('option');
    opt.value = b; opt.innerText = b; sel.appendChild(opt);
  });
}

function populateSidebar(topicList){
  const tdiv = el('topics');
  if(!tdiv) return;
  tdiv.innerHTML = '';
  topicList.forEach(item=>{
    const b = document.createElement('button');
    b.className = 'topic-btn';
    b.innerText = `${item.topic} (${item.count})`;
    b.onclick = ()=>{ el('retailer').value='all'; el('brand').value='all'; el('mode').value='daily'; el('sort').value='relevance'; filterByTopic(item.topic); };
    tdiv.appendChild(b);
  });
  // quick filters
  const q = el('quick-filters'); if(q){ q.innerHTML = ''; const quickAll = document.createElement('button'); quickAll.className='quick-btn'; quickAll.innerText='Clear Filters'; quickAll.onclick=()=>{ el('retailer').value='all'; el('brand').value='all'; load(); }; q.appendChild(quickAll); }
}

function filterByTopic(topic){ loadTopicFiltered(topic); }

async function loadTopicFiltered(topic){
  const date = el('date').value;
  let events = [];
  const candidates = [`/data/events/${date}.json`,`data/events/${date}.json`,`./data/events/${date}.json`,`../data/events/${date}.json`];
  for(const c of candidates){ const part = await fetchJson(c); if(part && part.length){ events = part; break; } }
  events.forEach(e => { e._topic = classifyTopic(e.title,e.source_url); e._brands = detectBrands(e.title,e.source_url); });
  const filtered = events.filter(e=> e._topic === topic);
  populateBrandSelect(Array.from(new Set(filtered.flatMap(e=>e._brands))));
  render(filtered, 'relevance');
}

function dateToStr(d){return d.toISOString().slice(0,10)}

async function load(){
  const date = el('date').value;
  const retailer = el('retailer').value;
  const mode = el('mode').value;
  const brand = el('brand')? el('brand').value : 'all';
  const sort = el('sort')? el('sort').value : 'relevance';
  el('status').innerText = 'Loading...';
  let events = [];
  if(mode==='daily'){
    const candidates = [
      `/data/events/${date}.json`,
      `data/events/${date}.json`,
      `./data/events/${date}.json`,
      `../data/events/${date}.json`
    ];
    for(const c of candidates){
      const part = await fetchJson(c);
      if(part && part.length){ events = part; break; }
    }
  } else {
    const start = new Date(date);
    for(let i=0;i<7;i++){
      const d = new Date(start);
      d.setDate(start.getDate()-i);
      const ds = dateToStr(d);
      const candidates = [
        `/data/events/${ds}.json`,
        `data/events/${ds}.json`,
        `./data/events/${ds}.json`,
        `../data/events/${ds}.json`
      ];
      let part = [];
      for(const c of candidates){
        part = await fetchJson(c);
        if(part && part.length) break;
      }
      events = events.concat(part);
    }
  }

  if(retailer && retailer!=='all'){
    events = events.filter(e => e.retailer===retailer);
  }

  if(brand && brand!=='all'){
    events = events.filter(e => {
      const b = detectBrands(e.title, e.source_url);
      return b.includes(brand);
    });
  }

  // populate brand select with discovered brands from this result set
  const discovered = Array.from(new Set(events.flatMap(e=>detectBrands(e.title,e.source_url))));
  if(discovered.length) populateBrandSelect(discovered);

  el('status').innerText = '';
  render(events, sort);
}

el('load').addEventListener('click', load);
// auto-load on any control change
['retailer','brand','sort','mode','date'].forEach(id=>{
  const c = el(id);
  if(c) c.addEventListener('change', load);
});
load();
