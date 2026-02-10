# Project Extensions

Folder **project_extension** berisi add-on kustom untuk meningkatkan fitur modul Proyek di Odoo 18.0.

## Tujuan

- Menambah field dan informasi tambahan pada Project dan Task.
- Mengotomasi update status tugas berdasarkan kondisi tertentu.
- Mendukung pelaporan proyek yang lebih detail.

## Daftar Add-on

- `maxcustom_project_fields`  
  Menambahkan field tambahan pada Project/Task (misalnya kategori, kompleksitas, owner bisnis).

- `maxcustom_project_task_autoprogress_done`  
  Mengotomasi perubahan status Task menjadi *Done* berdasarkan aturan tertentu
  (misalnya semua checklist selesai atau field tertentu terisi).

## Cara Penggunaan

1. Simpan modul pada path:  
   `addons/project_extension/<nama_addon>/`
2. Pastikan path `addons` sudah terdaftar di `addons_path` pada `odoo.conf`.
3. Restart Odoo dan buka menu Apps.
4. Install modul yang dibutuhkan saja (setiap modul bisa dipasang terpisah).
5. Lihat README di masing‑masing modul untuk contoh konfigurasi dan skenario penggunaan.

## Kompatibilitas

- Versi Odoo: **18.0 Community Edition**
- Versi modul mengikuti format `18.0.x.x.x` di `__manifest__.py`.
