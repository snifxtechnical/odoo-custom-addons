# -*- coding: utf-8 -*-
{
    "name": "Time Off - Company Policy Management",
    "summary": """
        Comprehensive time off policy management for company regulations.
        Control dates, require advance notice, and limit working days.
    """,
    "description": """
        Time Off Company Policy Management
        ===================================
        
        Kelola kebijakan cuti perusahaan dengan lengkap dan fleksibel.
        Gabungan dari 3 addon menjadi satu solusi terpadu.
        
        Fitur Utama
        -----------
        
        **1. Pembatasan Tanggal (Date Restrictions)**
           • Kontrol permintaan tanggal masa depan
           • Batasi mundur maksimal (backdate limit)
           • Konfigurasi per jenis cuti
        
        **2. Persyaratan Pemberitahuan Minimum (Minimum Notice)**
           • Wajibkan pemberitahuan sebelum cuti
           • Threshold durasi (hanya untuk cuti ≥ X hari)
           • Pilihan unit: hari kalender, hari kerja, minggu
           • Scope: company-wide, per department, per kategori
           • Pengecualian user group
           • Grace period (jam toleransi)
           • Periode validitas kebijakan
        
        **3. Batasan Hari Kerja (Working Days Limitation)**
           • Batasi hari kerja berturut-turut
           • Integrasi dengan Work Entries
           • Fallback ke Resource Calendar
           • Exclude weekend & hari libur
        
        Keunggulan
        ----------
        • ✅ Interface terpadu untuk semua kebijakan
        • ✅ Konfigurasi fleksibel per jenis cuti
        • ✅ Error messages dalam Bahasa Indonesia
        • ✅ Validasi otomatis saat submit
        • ✅ Triple fallback untuk perhitungan hari kerja
        • ✅ Support migrasi dari addon terpisah
        
        Kompatibilitas
        ---------------
        • Odoo 18.0 Community & Enterprise
        • Python 3.10+
        • PostgreSQL 13+
        
        Dokumentasi
        -----------
        Dokumentasi lengkap tersedia di folder doc/ dalam addon ini.
        
        Author: Snifx Studio
        License: LGPL-3
        Version: 18.0.1.0.0
    """,
    "version": "18.0.1.0.0",
    "category": "Human Resources/Time Off",
    "author": "Snifx Studio",
    "website": "https://snifx.studio",
    "license": "LGPL-3",
    "depends": [
        "hr_holidays",
        "hr_work_entry",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_leave_type_views.xml",
        "data/time_off_policy_data.xml",
    ],
    "demo": [],
    "images": ["static/description/icon.png"],
    "pre_init_hook": "pre_init_hook",
    "post_init_hook": "post_init_hook",
    "uninstall_hook": "uninstall_hook",
    "installable": True,
    "application": False,
    "auto_install": False,
    "price": 0.00,
    "currency": "EUR",
}
