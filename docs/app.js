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

function render(events){
  const container = el('events');
  container.innerHTML = '';
  if(!events || events.length===0){
    container.innerText = 'No events found for selection.';
    return;
  }
  events.forEach(e => {
    const d = document.createElement('div');
    d.className = 'event';
    d.innerHTML = `<div><strong>${e.retailer}</strong> — ${e.title}</div><div class="meta"><a href="${e.source_url}" target="_blank">source</a> • ${e.category}</div>`;
    container.appendChild(d);
  });
}

function dateToStr(d){return d.toISOString().slice(0,10)}

async function load(){
  const date = el('date').value;
  const retailer = el('retailer').value;
  const mode = el('mode').value;
  el('status').innerText = 'Loading...';
  let events = [];
  if(mode==='daily'){
    // try several possible locations depending on how docs are served
    const candidates = [
      `/data/events/${date}.json`,
      `data/events/${date}.json`,
      `../data/events/${date}.json`,
      `./data/events/${date}.json`
    ];
    for(const c of candidates){
      const part = await fetchJson(c);
      if(part && part.length){ events = part; break; }
    }
  } else {
    // weekly: gather 7 days ending at date
    const start = new Date(date);
    for(let i=0;i<7;i++){
      const d = new Date(start);
      d.setDate(start.getDate()-i);
      const ds = dateToStr(d);
      // try root and docs-relative locations for each day
      const candidates = [
        `/data/events/${ds}.json`,
        `data/events/${ds}.json`,
        `../data/events/${ds}.json`,
        `./data/events/${ds}.json`
      ];
      let part = [];
      for(const c of candidates){
        part = await fetchJson(c);
        if(part && part.length) break;
      }
      events = events.concat(part);
    }
  }

  // filter by retailer
  if(retailer && retailer!=='all'){
    events = events.filter(e => e.retailer===retailer);
  }

  el('status').innerText = '';
  render(events);
}

el('load').addEventListener('click', load);

// auto-load today's daily on open
load();
