# Helpdesk Extensions

Folder **helpdesk_extension** berisi add-on yang memperluas fitur Helpdesk / Ticketing di Odoo 18.0.

## Tujuan

- Menambah struktur tipe tiket dan kategori layanan.
- Menyederhanakan alur kerja agent helpdesk.
- Menyediakan data tambahan untuk analisis performa support.

## Daftar Add-on

- `snifx_helpdesk_extension`  
  Penyesuaian field, tampilan, dan workflow pada tiket Helpdesk sesuai kebutuhan internal.

- `helpdesk_type`  
  Menambahkan tipe/kategori tiket (misalnya Incident, Service Request, Change) sehingga laporan ticket lebih terstruktur.

## Cara Penggunaan

1. Pastikan kode tersimpan di:  
   `addons/helpdesk_extension/<nama_addon>/`
2. Tambahkan path `addons` ke `addons_path` di `odoo.conf` bila belum.
3. Restart Odoo, lalu dari Apps install modul yang diperlukan.
4. Ikuti panduan di README masing‑masing modul untuk konfigurasi SLA, tipe tiket, dan role pengguna.

## Kompatibilitas

- Versi Odoo: **18.0 Community Edition**
- Versi modul mengikuti format `18.0.x.x.x` di file `__manifest__.py`.
