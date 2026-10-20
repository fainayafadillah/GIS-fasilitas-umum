"""Analisis spasial: jarak terdekat, kesenjangan layanan, dan kandidat lokasi baru.
Hasil ditulis ke web/data/analysis.json untuk dibaca dashboard."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent / "web" / "data"
# Batas jarak layanan ideal (km) per kategori -- sesuaikan dengan standar/regulasi
BATAS = {"Kesehatan": 2.0, "Pendidikan": 1.5, "Ibadah": 1.0, "Taman": 2.0, "Transportasi": 1.0}
GRID = 20

def haversine(lat1, lng1, lat2, lng2):
    """Jarak (km) antar titik; mendukung broadcasting numpy."""
    p = np.pi / 180
    a = (np.sin((lat2 - lat1) * p / 2) ** 2 +
         np.cos(lat1 * p) * np.cos(lat2 * p) * np.sin((lng2 - lng1) * p / 2) ** 2)
    return 12742 * np.arcsin(np.sqrt(a))

geo = json.loads((ROOT / "facilities.geojson").read_text())
df = pd.DataFrame([{**f["properties"], "lng": f["geometry"]["coordinates"][0],
                    "lat": f["geometry"]["coordinates"][1]} for f in geo["features"]])

# 1) Grid analisis di atas area studi
pad = 0.01
lats = np.linspace(df.lat.min() - pad, df.lat.max() + pad, GRID)
lngs = np.linspace(df.lng.min() - pad, df.lng.max() + pad, GRID)
dlat, dlng = lats[1] - lats[0], lngs[1] - lngs[0]
glat, glng = np.meshgrid(lats, lngs, indexing="ij")
glat, glng = glat.ravel(), glng.ravel()

# 2) Jarak terdekat tiap sel ke tiap kategori
rasio, jarak = {}, {}
for kat, batas in BATAS.items():
    sub = df[df.kategori == kat]
    d = haversine(glat[:, None], glng[:, None], sub.lat.values[None, :], sub.lng.values[None, :])
    jarak[kat] = d.min(axis=1)
    rasio[kat] = jarak[kat] / batas

skor = pd.DataFrame(rasio).mean(axis=1)  # >1 berarti rata-rata di luar jangkauan ideal

cells = []
for i in range(len(glat)):
    kurang = [k for k in BATAS if rasio[k][i] > 1]
    cells.append({"lat": round(float(glat[i]), 5), "lng": round(float(glng[i]), 5),
                  "skor": round(float(skor[i]), 2), "kurang": kurang})

# 3) Kandidat lokasi: skor tertinggi, saling berjarak minimal 1.5 km
kandidat = []
for i in np.argsort(-skor.values):
    if all(haversine(glat[i], glng[i], k["lat"], k["lng"]) > 1.5 for k in kandidat):
        kandidat.append(cells[i])
    if len(kandidat) == 5:
        break

# 4) Ringkasan per kecamatan & cakupan per kategori
per_kec = df.groupby(["kecamatan", "kategori"]).size().unstack(fill_value=0)
per_kec = per_kec.reindex(columns=list(BATAS), fill_value=0)
cakupan = {k: round(float((jarak[k] <= BATAS[k]).mean() * 100), 1) for k in BATAS}

out = {
    "meta": {"dlat": float(dlat), "dlng": float(dlng), "batas_km": BATAS},
    "ringkasan": {"total": int(len(df)),
                  "per_kategori": {k: int(v) for k, v in df.kategori.value_counts().items()},
                  "cakupan_persen": cakupan,
                  "sel_kurang_layanan": int((skor > 1).sum()), "sel_total": len(cells)},
    "per_kecamatan": {k: {c: int(n) for c, n in v.items()} for k, v in per_kec.to_dict(orient="index").items()},
    "sel": cells, "kandidat": kandidat,
}
(ROOT / "analysis.json").write_text(json.dumps(out, ensure_ascii=False))
print("Cakupan (% area):", cakupan)
print("Kandidat lokasi:", [(k["lat"], k["lng"], k["skor"]) for k in kandidat])
