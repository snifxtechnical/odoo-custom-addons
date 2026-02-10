# Timeoff Extensions

Folder **timeoff_extension** berisi semua add-on kustom yang memperluas fitur Cuti (Time Off) di Odoo 18.0.

## Tujuan

- Menambah aturan dan kebijakan cuti sesuai regulasi internal perusahaan.
- Mengotomasi proses approval dan penggantian PIC saat karyawan cuti.
- Menyediakan laporan tambahan terkait pemakaian cuti.

## Daftar Add-on

- `snifx_timeoff_policy`  
  Menambahkan kebijakan cuti kustom (jenis cuti, perhitungan jatah, dan validasi khusus).

- `snifx_timeoff_pic_pengganti`  
  Mengelola otomatisasi penunjukan PIC pengganti ketika karyawan sedang cuti.

## Cara Penggunaan

1. Pastikan kode ada di path:  
   `addons/timeoff_extension/<nama_addon>/`
2. Tambahkan path `addons` ini ke konfigurasi `addons_path` di `odoo.conf`.
3. Restart Odoo, lalu install modul yang diinginkan dari Apps:
   - Cari berdasarkan nama modul, misalnya **Snifx Timeoff Policy**.
4. Ikuti dokumentasi masing‑masing modul (README di dalam folder modul) untuk konfigurasi detail.

## Kompatibilitas

- Versi Odoo: **18.0 Community Edition**
- Setiap modul menggunakan penomoran versi `18.0.x.x.x` di file `__manifest__.py`.
