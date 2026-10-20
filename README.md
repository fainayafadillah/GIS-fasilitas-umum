# Sistem Pemetaan dan Analisis Lokasi Fasilitas Umum Berbasis GIS

## Konsep
Dashboard web yang memetakan fasilitas umum (kesehatan, pendidikan, ibadah, taman, transportasi)
dan menganalisis pemerataannya. Python menghitung jarak terdekat dan kesenjangan layanan,
hasilnya disajikan interaktif oleh dashboard (Leaflet + Chart.js).

Alur: generate_data.py -> facilities.geojson -> analysis.py -> analysis.json -> dashboard.

## Cara Menjalankan
    pip install -r requirements.txt
    python analysis/generate_data.py   # data sintetis (ganti dengan data asli bila ada)
    python analysis/analysis.py
    cd web && python -m http.server 8000   # buka http://localhost:8000

https://fainayafadillah.github.io/GIS-fasilitas-umum/

## Pengembangan Lanjutan
Data asli OpenStreetMap (Overpass API), analisis jaringan jalan, K-Means, backend Flask/FastAPI, deploy GitHub Pages.
