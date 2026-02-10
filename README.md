# odoo-custom-addons

Repository ini berisi kumpulan add-on kustom Odoo yang digunakan di lingkungan internal kami.
Saat ini fokus pada Odoo **18.0 Community Edition** dengan struktur monorepo untuk memudahkan maintenance lintas proyek dan versi.

## Struktur Repository

- `addons/`
  - `timeoff_extension/` – Add-on untuk modul Time Off (cuti).
  - `project_extension/` – Add-on untuk modul Project.
  - `helpdesk_extension/` – Add-on untuk modul Helpdesk / Ticketing.
- `scripts/` – Script bantu (deploy, backup, dll).
- `docker-compose.yml` – (Opsional) File untuk menjalankan environment Odoo lokal.

Detail masing‑masing grup add-on bisa dilihat pada README di dalam folder terkait.

## Versi Odoo & Branch

- Branch `18.0` → kode untuk Odoo 18.0 CE.
- Branch lain (misalnya `19.0`) akan dibuat ketika ada kebutuhan upgrade versi.

Setiap modul mengikuti format versi `18.0.x.x.x` di file `__manifest__.py`.

## Cara Menggunakan Repository Ini

1. Clone repository:
   ```bash
   git clone https://github.com/<org-atau-user>/odoo-custom-addons.git -b 18.0
