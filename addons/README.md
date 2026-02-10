# Addons Directory

Folder **addons** adalah root untuk semua add-on kustom yang digunakan bersama dengan Odoo standar.

## Struktur Sub-Folder

- `timeoff_extension/`
  Kumpulan modul yang memperluas fitur Time Off / HR Leave.

- `project_extension/`
  Kumpulan modul yang memperluas fitur Project dan Task management.

- `helpdesk_extension/`
  Kumpulan modul yang memperluas fitur Helpdesk / Ticketing.

Masing‑masing sub‑folder memiliki README sendiri yang menjelaskan modul di dalamnya secara lebih detail.

## Cara Menambahkan Modul Baru

1. Tentukan grup yang sesuai:
   - Modul terkait cuti → `timeoff_extension/`
   - Modul terkait proyek → `project_extension/`
   - Modul terkait helpdesk → `helpdesk_extension/`
2. Buat folder baru dengan nama teknis modul, misalnya:
   - `addons/project_extension/maxcustom_project_new_feature/`
3. Di dalam folder modul, buat struktur standar:
   - `__init__.py`
   - `__manifest__.py`
   - `models/`, `views/`, `security/`, `data/` (sesuai kebutuhan)
4. Update README di sub‑folder (misalnya `project_extension/README.md`) untuk menambahkan deskripsi modul baru.

## Kompatibilitas

Semua modul di dalam folder ini ditargetkan untuk:

- Odoo: **18.0 Community Edition**
- Versi modul mengikuti format `18.0.x.x.x` di `__manifest__.py`.

Jika ada modul untuk versi Odoo lain, gunakan branch berbeda (misalnya `19.0`) dan jaga agar isi `addons/` di setiap branch sesuai dengan versi target.
