# IPD — AI "Early Sepsis Radar" berbasis Catatan Dokter (Teks Bebas) + Tren Vital

## Judul kerja
**Evaluasi sistem peringatan dini sepsis berbasis LLM pada pasien rawat inap penyakit dalam non-ICU: studi komparatif terhadap NEWS2/qSOFA dan clinical judgement.**

## Pertanyaan penelitian (format PICO)
Pada pasien rawat inap penyakit dalam non-ICU, apakah sistem LLM yang membaca progres note dokter (teks bebas) dan tren lab/vital secara real-time dapat mempercepat terapi antibiotik serta menurunkan luaran buruk sepsis dibanding pendekatan konvensional (NEWS2/qSOFA + clinical judgement)?

## PICO (versi operasional)

### P — Population
- Pasien dewasa (>=18 tahun) yang dirawat di bangsal penyakit dalam (non-ICU).
- Kriteria inklusi disarankan:
  - Rawat inap >24 jam.
  - Tersedia progres note harian dan data vital serial.
- Kriteria eksklusi disarankan:
  - Sepsis/ syok sepsis saat admisi.
  - DNR/comfort care only sejak awal.
  - Transfer langsung ke ICU <6 jam setelah admisi.

### I — Intervention
- **AI early sepsis radar** berbasis LLM yang:
  - Mengekstrak sinyal risiko dari progres note dokter (teks bebas).
  - Menggabungkan tren vital/lab (mis. suhu, RR, HR, MAP, laktat, leukosit, kreatinin, bilirubin, trombosit).
  - Menghasilkan **alert risiko sepsis** + rekomendasi **sepsis bundle** (mis. kultur, laktat ulang, cairan, antibiotik empiris sesuai kebijakan lokal).
- Integrasi ke alur klinis:
  - Alert tampil pada dashboard/EMR dan notifikasi tim jaga.
  - Cutoff risiko ditetapkan pra-implementasi.

### C — Comparator
- Tata laksana standar:
  - Skor konvensional (NEWS2 dan/atau qSOFA).
  - Clinical judgement tanpa bantuan radar AI.

### O — Outcomes
#### Outcome primer
- **Time-to-antibiotic** (menit/jam dari waktu kriteria sepsis terpenuhi sampai dosis antibiotik pertama).

#### Outcome sekunder
- Insiden **syok sepsis** selama perawatan.
- **ICU transfer** setelah onset kecurigaan sepsis.
- **Length of stay (LOS)** rumah sakit.
- **Mortalitas 28 hari**.

#### Outcome eksploratori (disarankan)
- Sensitivitas, spesifisitas, AUROC, PPV/NPV alert AI.
- False alert rate per 100 patient-days.
- Bundle adherence rate.
- Antibiotic overuse (days-of-therapy).

## Rancangan studi yang direkomendasikan
- **Pragmatis, quasi-experimental (before–after)** atau **stepped-wedge cluster** per bangsal.
- Analisis utama:
  - Cox/accelerated failure time untuk time-to-antibiotic.
  - Regresi logistik/mixed-effects untuk syok sepsis, ICU transfer, mortalitas.
  - Penyesuaian confounder: usia, komorbid (CCI), sumber infeksi, severity awal, penggunaan vasopressor awal.

## Definisi operasional penting
- **Waktu nol (T0):** pertama kali pasien memenuhi kriteria kecurigaan sepsis terstandar (mis. infeksi tersangka + disfungsi organ).
- **Alert positif:** skor risiko melewati ambang yang ditentukan sebelum studi.
- **Antibiotik tepat waktu:** pemberian <=1 jam atau <=3 jam (sesuai guideline lokal yang dipilih konsisten).

## Catatan implementasi
- Gunakan **human-in-the-loop**: keputusan final tetap dokter penanggung jawab.
- Audit bias model antar subkelompok (usia lanjut, CKD, keganasan, imunokompromais).
- Pastikan governance privasi data, logging alert, dan mekanisme override klinis.

## Ringkasan satu kalimat (siap pakai untuk proposal)
Pada pasien rawat inap penyakit dalam non-ICU, sistem LLM yang memproses catatan klinis teks bebas dan tren vital/lab diperkirakan mempercepat pemberian antibiotik dan memperbaiki luaran sepsis dibanding NEWS2/qSOFA serta clinical judgement standar.
