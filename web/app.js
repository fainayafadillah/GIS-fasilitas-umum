const COLORS = {Kesehatan:'#e11d48',Pendidikan:'#2563eb',Ibadah:'#16a34a',Taman:'#ca8a04',Transportasi:'#7c3aed'};
const $ = s => document.querySelector(s);

Promise.all([
  fetch('data/facilities.geojson').then(r => r.json()),
  fetch('data/analysis.json').then(r => r.json())
]).then(([geo, an]) => init(geo, an)).catch(() => { $('#err').hidden = false; });

function init(geo, an) {
  const map = L.map('map').setView([-3.81, 102.27], 12);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {attribution: '&copy; OpenStreetMap'}).addTo(map);
  const pts = L.layerGroup().addTo(map), cov = L.layerGroup().addTo(map), gap = L.layerGroup();
  const active = new Set(Object.keys(COLORS));
  const s = an.ringkasan;

  // Kartu statistik
  const rata = Object.values(s.cakupan_persen).reduce((a, b) => a + b, 0) / 5;
  [['Total fasilitas', s.total], ['Kategori', 5], ['Rata-rata cakupan area', rata.toFixed(1) + '%'],
   ['Sel kurang layanan', `${s.sel_kurang_layanan}/${s.sel_total}`]]
    .forEach(([k, v]) => $('#stats').insertAdjacentHTML('beforeend', `<div class="card"><small>${k}</small><b>${v}</b></div>`));

  // Filter kategori
  Object.entries(COLORS).forEach(([k, c]) => {
    const l = document.createElement('label');
    l.innerHTML = `<input type="checkbox" checked><span class="dot" style="background:${c}"></span>${k} (${s.per_kategori[k]}) &middot; cakupan ${s.cakupan_persen[k]}%`;
    l.firstChild.onchange = e => { e.target.checked ? active.add(k) : active.delete(k); render(); };
    $('#chips').appendChild(l);
  });

  function render() {
    pts.clearLayers(); cov.clearLayers();
    const q = $('#search').value.toLowerCase(), km = +$('#radius').value;
    geo.features.forEach(f => {
      const p = f.properties;
      if (!active.has(p.kategori) || !p.nama.toLowerCase().includes(q)) return;
      const ll = [f.geometry.coordinates[1], f.geometry.coordinates[0]], c = COLORS[p.kategori];
      L.circleMarker(ll, {radius: 7, color: '#fff', weight: 1.5, fillColor: c, fillOpacity: .9})
        .bindPopup(`<b>${p.nama}</b><br>${p.kategori} &middot; ${p.kecamatan}`).addTo(pts);
      if ($('#tCov').checked) L.circle(ll, {radius: km * 1000, color: c, weight: 1, fillOpacity: .06}).addTo(cov);
    });
  }

  // Peta kesenjangan: sel makin merah = makin jauh dari fasilitas
  const {dlat, dlng} = an.meta;
  an.sel.forEach(c => {
    L.rectangle([[c.lat - dlat/2, c.lng - dlng/2], [c.lat + dlat/2, c.lng + dlng/2]],
      {stroke: false, fillColor: '#dc2626', fillOpacity: Math.min(c.skor / 2, .65)})
      .bindTooltip(c.kurang.length ? 'Kurang: ' + c.kurang.join(', ') : 'Layanan memadai').addTo(gap);
  });

  // Kandidat lokasi
  an.kandidat.forEach((k, i) => {
    const li = document.createElement('li');
    li.textContent = `Lokasi ${i + 1} (skor ${k.skor}) - kurang: ${k.kurang.join(', ') || '-'}`;
    li.onclick = () => { map.flyTo([k.lat, k.lng], 15); L.popup().setLatLng([k.lat, k.lng]).setContent('Kandidat lokasi ' + (i + 1)).openOn(map); };
    $('#cand').appendChild(li);
  });

  // Grafik per kecamatan
  new Chart($('#chart'), {
    type: 'bar',
    data: {labels: Object.keys(an.per_kecamatan),
      datasets: Object.keys(COLORS).map(k => ({label: k, backgroundColor: COLORS[k],
        data: Object.values(an.per_kecamatan).map(v => v[k] || 0)}))},
    options: {responsive: true, maintainAspectRatio: false,
      plugins: {title: {display: true, text: 'Jumlah fasilitas per kecamatan'}},
      scales: {x: {stacked: true}, y: {stacked: true, beginAtZero: true}}}
  });

  $('#search').oninput = render;
  $('#radius').oninput = e => { $('#rv').textContent = (+e.target.value).toFixed(1); render(); };
  $('#tCov').onchange = render;
  $('#tGap').onchange = e => e.target.checked ? gap.addTo(map) : map.removeLayer(gap);
  render();
}
