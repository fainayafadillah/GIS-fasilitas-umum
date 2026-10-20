"""Membuat data SINTETIS fasilitas umum (GeoJSON) di sekitar Kota Bengkulu.
Ganti dengan data asli (OpenStreetMap / Dinas terkait) bila sudah tersedia."""
import json, random
from pathlib import Path

random.seed(42)
KEC = {  # titik pusat kecamatan (perkiraan)
    "Teluk Segara": (-3.79, 102.25), "Ratu Samban": (-3.80, 102.26),
    "Gading Cempaka": (-3.83, 102.29), "Selebar": (-3.77, 102.31),
    "Muara Bangkahulu": (-3.77, 102.28), "Kampung Melayu": (-3.88, 102.31),
}
KAT = {  # kategori: (jumlah, awalan nama)
    "Kesehatan": (25, ["Puskesmas", "Klinik", "RS"]),
    "Pendidikan": (35, ["SDN", "SMPN", "SMAN"]),
    "Ibadah": (35, ["Masjid", "Gereja", "Musala"]),
    "Taman": (12, ["Taman", "Lapangan"]),
    "Transportasi": (13, ["Halte", "Terminal"]),
}
feats = []
for kat, (n, names) in KAT.items():
    for i in range(1, n + 1):
        kec = random.choice(list(KEC))
        lat0, lng0 = KEC[kec]
        lat, lng = random.gauss(lat0, 0.012), random.gauss(lng0, 0.012)
        feats.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lng, 5), round(lat, 5)]},
            "properties": {"nama": f"{random.choice(names)} {kec.split()[0]} {i}",
                           "kategori": kat, "kecamatan": kec},
        })
out = Path(__file__).resolve().parent.parent / "web" / "data" / "facilities.geojson"
out.write_text(json.dumps({"type": "FeatureCollection", "features": feats}, ensure_ascii=False))
print(f"{len(feats)} fasilitas ditulis ke {out}")
