const today = new Date().toISOString().slice(0,10);
fetch(`../data/events/${today}.json`)
  .then(r => r.json())
  .then(events => {
    const el = document.getElementById('events');
    events.forEach(e => {
      const d = document.createElement('div');
      d.innerHTML = `<strong>${e.retailer}</strong>: ${e.title}`;
      el.appendChild(d);
    });
  })
  .catch(() => {
    document.getElementById('events').innerText = 'No data yet';
  });
