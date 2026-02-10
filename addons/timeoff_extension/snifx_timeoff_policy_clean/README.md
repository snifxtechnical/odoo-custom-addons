# Time Off - Company Policy Management

![Snifx Studio](static/description/icon.png)

**Version:** 18.0.1.0.0 (Base Release)  
**Author:** Snifx Studio  
**License:** LGPL-3  
**Odoo Version:** 18.0 Community & Enterprise

[![Status](https://img.shields.io/badge/status-stable-green.svg)](CHANGELOG.md)
[![Version](https://img.shields.io/badge/version-18.0.1.0.0-blue.svg)](CHANGELOG.md)

> 📢 **Important:** This is the base version 18.0.1.0.0. Check [CHANGELOG.md](CHANGELOG.md) for known issues and updates.
> 
> **Known Issues in v18.0.1.0.0:**
> - ⚠️ DateTime comparison error (fixed in v18.0.1.0.1)
> - ⚠️ Double counting in working days (fixed in v18.0.1.0.2)
> 
> **Recommendation:** Upgrade to latest version 18.0.1.0.2 for bug fixes.

---

## 📋 Deskripsi

Modul komprehensif untuk mengelola kebijakan cuti perusahaan di Odoo 18. Menggabungkan 3 fitur penting dalam satu addon terpadu:

1. **Pembatasan Tanggal** - Kontrol tanggal masa depan dan mundur
2. **Persyaratan Pemberitahuan Minimum** - Wajibkan advance notice
3. **Batasan Hari Kerja** - Limit hari kerja berturut-turut

---

## ✨ Fitur Utama

### 1. Pembatasan Tanggal (Date Restrictions)

**Fungsi:**
- Izinkan/blokir permintaan tanggal masa depan
- Batasi berapa hari mundur yang diperbolehkan
- Konfigurasi berbeda per jenis cuti

**Use Case:**
```
• Annual Leave: Boleh masa depan, maksimal mundur 7 hari
• Sick Leave: Boleh masa depan, maksimal mundur 3 hari
• Emergency Leave: Hanya hari ini, tidak boleh mundur
```

**Field:**
- `allow_future_request` (Boolean) - Izinkan tanggal masa depan
- `max_backdate_days` (Integer) - Maksimal hari mundur (0 = tidak boleh mundur)

---

### 2. Persyaratan Pemberitahuan Minimum (Minimum Notice)

**Fungsi:**
- Wajibkan karyawan mengajukan cuti X hari/minggu sebelumnya
- Threshold: hanya berlaku untuk cuti ≥ durasi tertentu
- Scope fleksibel: company-wide, per department, per kategori
- Pengecualian untuk user groups tertentu
- Grace period (jam toleransi tambahan)

**Use Case:**
```
• Long Leave (≥5 hari): Harus 14 hari sebelumnya
• Short Leave (<5 hari): Hanya 3 hari sebelumnya
• Department Head: Dikecualikan dari persyaratan
• Seasonal Policy: Hanya berlaku Juni-Agustus (peak season)
```

**Field:**
- `enable_min_notice` (Boolean) - Aktifkan persyaratan
- `threshold_days` (Float) - Durasi minimum untuk apply rule
- `use_business_days_for_threshold` (Boolean) - Gunakan hari kerja untuk threshold
- `min_notice_qty` (Integer) - Jumlah pemberitahuan (e.g., 7)
- `min_notice_unit` (Selection) - Unit: Calendar Days / Business Days / Weeks
- `exclude_public_holidays` (Boolean) - Exclude libur dari business days
- `scope_mode` (Selection) - Company / Department / Category
- `department_id` (Many2one) - Department spesifik (jika scope = department)
- `category_id` (Many2one) - Kategori karyawan (jika scope = category)
- `exempt_group_ids` (Many2many) - User groups yang dikecualikan
- `grace_hours` (Integer) - Jam toleransi tambahan
- `valid_from` (Date) - Tanggal mulai berlaku
- `valid_to` (Date) - Tanggal akhir berlaku

---

### 3. Batasan Hari Kerja (Working Days Limitation)

**Fungsi:**
- Batasi jumlah hari kerja berturut-turut yang boleh diambil cuti
- Perhitungan akurat via Work Entries
- Fallback ke Resource Calendar
- Exclude weekend & hari libur otomatis

**Use Case:**
```
• Annual Leave: Maksimal 20 hari kerja
• Unpaid Leave: Maksimal 10 hari kerja
• Study Leave: Maksimal 5 hari kerja
```

**Field:**
- `limit_by_working_days` (Boolean) - Aktifkan batasan
- `max_working_days` (Integer) - Maksimal hari kerja berturut-turut

**Perhitungan:**
1. **Primary:** Work Entries (paling akurat) - menggunakan entri kerja tervalidasi
2. **Secondary:** Resource Calendar - jika tidak ada work entries
3. **Tertiary:** Simple weekday count - fallback terakhir

---

## 📦 Instalasi

### Persyaratan
- Odoo 18.0 (Community atau Enterprise)
- Python 3.10+
- PostgreSQL 13+
- Module: `hr_holidays`, `hr_work_entry`

### Langkah Instalasi

1. **Copy addon ke folder addons**
   ```bash
   cp -r snifx_timeoff_policy /path/to/odoo/addons/
   ```

2. **Restart Odoo**
   ```bash
   sudo systemctl restart odoo
   ```

3. **Update Apps List**
   - Go to: Apps
   - Click: Update Apps List

4. **Install Module**
   - Search: "Time Off - Company Policy"
   - Click: Install

5. **Verifikasi**
   - Go to: Time Off > Configuration > Time Off Types
   - Buka salah satu leave type
   - Cek ada section: "Company Policy Settings"

---

## ⚙️ Konfigurasi

### A. Konfigurasi Dasar

**Lokasi:** Time Off > Configuration > Time Off Types

**Edit Leave Type** (contoh: Annual Leave)

#### 1. Date Restrictions

```
☑ Allow Future Date Requests: Yes
📅 Maximum Backdate Days: 7

Artinya:
• Karyawan boleh ajukan untuk tanggal masa depan
• Maksimal mundur 7 hari ke belakang
```

#### 2. Minimum Notice Requirement

```
☑ Enable Minimum Notice Requirement: Yes

Threshold Configuration:
  📊 Duration Threshold: 5.0 days
  ☐ Use Business Days for Threshold: No

Artinya: Rule ini hanya apply untuk cuti ≥ 5 hari

Minimum Notice Period:
  📅 Minimum Notice Quantity: 14
  📐 Notice Unit: Calendar Days
  ☑ Exclude Public Holidays: Yes (jika unit = Business Days)

Artinya: Harus mengajukan minimal 14 hari kalender sebelumnya

Policy Scope:
  🌍 Scope: Company-wide
  
Artinya: Berlaku untuk seluruh perusahaan

Additional Options:
  ⏰ Grace Hours: 0
  📅 Valid From: (kosongkan jika selalu berlaku)
  📅 Valid To: (kosongkan jika selalu berlaku)
```

#### 3. Batasan Hari Kerja Cuti

```
☑ Batasi Hari Kerja Cuti: Yes
📊 Maksimal Hari Kerja untuk Cuti: 20

Artinya:
• Maksimal 20 hari kerja berturut-turut
• Sabtu/Minggu & libur tidak dihitung
```

---

### B. Contoh Konfigurasi per Jenis Cuti

#### Annual Leave (Cuti Tahunan)

```yaml
Date Restrictions:
  Allow Future: ✓ Yes
  Max Backdate: 7 days

Minimum Notice:
  Enable: ✓ Yes
  Threshold: 5 days (hanya untuk cuti ≥5 hari)
  Notice Required: 14 days
  Unit: Calendar Days
  Scope: Company-wide

Working Days Limit:
  Enable: ✓ Yes
  Max Days: 20 working days
```

**Behavior:**
- Boleh ajukan masa depan
- Boleh mundur maksimal 7 hari
- Jika durasi ≥5 hari, harus 14 hari sebelumnya
- Maksimal 20 hari kerja berturut-turut

---

#### Sick Leave (Cuti Sakit)

```yaml
Date Restrictions:
  Allow Future: ✓ Yes
  Max Backdate: 3 days

Minimum Notice:
  Enable: ✗ No (sakit = mendadak)

Working Days Limit:
  Enable: ✓ Yes
  Max Days: 5 working days
```

**Behavior:**
- Boleh ajukan masa depan (jika sudah tahu sakit)
- Boleh mundur maksimal 3 hari (dengan surat dokter)
- Tidak perlu advance notice (emergency)
- Maksimal 5 hari kerja

---

#### Emergency Leave (Cuti Darurat)

```yaml
Date Restrictions:
  Allow Future: ✗ No
  Max Backdate: 0 days

Minimum Notice:
  Enable: ✗ No (darurat)

Working Days Limit:
  Enable: ✓ Yes
  Max Days: 3 working days
```

**Behavior:**
- Hanya untuk hari ini/mendatang dekat
- Tidak boleh mundur
- Tidak perlu advance notice
- Maksimal 3 hari kerja

---

### C. Scope Configuration

#### Company-wide Policy

```
Scope: Company-wide
```
Berlaku untuk **semua karyawan** di perusahaan.

---

#### Department-specific Policy

```
Scope: Specific Department
Department: Technical Department
```
Hanya berlaku untuk karyawan di **Technical Department**.

**Use Case:**
```
• IT Department: Notice 7 hari (project-based)
• Sales Department: Notice 14 hari (customer-facing)
• Operations: Notice 3 hari (shift-based)
```

---

#### Category-specific Policy

```
Scope: Employee Category
Category: Manager
```
Hanya berlaku untuk karyawan dengan kategori **Manager**.

**Use Case:**
```
• Manager: Notice 21 hari (critical role)
• Staff: Notice 7 hari (regular)
• Intern: Notice 3 hari (short-term)
```

---

### D. User Group Exemptions

**Exempt Groups:** Pilih user groups yang **dikecualikan** dari rule.

**Contoh:**
```
Exempt Groups: 
  • Time Off / Manager
  • Administration / Settings

Artinya:
• Users dalam group ini TIDAK perlu minimum notice
• Berguna untuk: Management, HR, Emergency contacts
```

---

### E. Seasonal/Time-bound Policies

**Valid From / Valid To:** Set periode berlaku.

**Contoh:**
```
Valid From: 2025-06-01
Valid To: 2025-08-31

Artinya:
• Rule hanya berlaku Juni-Agustus (peak season)
• Di luar periode ini, rule tidak apply
```

**Use Case:**
```
• Peak Season: Notice 30 hari (busy period)
• Regular Season: Notice 14 hari (normal)
• Low Season: Notice 7 hari (quiet period)
```

---

## 🧪 Testing & Validation

### Test 1: Date Restrictions

**Setup:**
```
Annual Leave:
  Allow Future: No
  Max Backdate: 0
```

**Test:**
1. Login sebagai karyawan
2. Create time off request
3. Select date: Tomorrow
4. Save & Submit

**Expected Result:**
```
❌ ValidationError:
"Tidak dapat mengajukan cuti untuk tanggal masa depan.
Jenis cuti 'Annual Leave' tidak mengizinkan permintaan tanggal masa depan."
```

---

### Test 2: Minimum Notice

**Setup:**
```
Annual Leave:
  Enable Notice: Yes
  Threshold: 3 days
  Notice: 7 days
  Unit: Calendar Days
```

**Test:**
1. Login sebagai karyawan
2. Create time off request
3. Duration: 5 days (≥ threshold)
4. Start date: 3 days from now (< 7 days notice)
5. Save & Submit

**Expected Result:**
```
❌ ValidationError:
"Permintaan cuti tidak memenuhi persyaratan pemberitahuan minimum.
Diperlukan: 7 Calendar Days sebelum tanggal cuti"
```

---

### Test 3: Working Days Limit

**Setup:**
```
Annual Leave:
  Enable Limit: Yes
  Max Working Days: 10
```

**Test:**
1. Login sebagai karyawan
2. Create time off request
3. Duration: 15 consecutive days (= 11 working days)
4. Save & Submit

**Expected Result:**
```
❌ ValidationError:
"Permintaan cuti melebihi batas hari kerja.
Batas: 10 hari, Diminta: 11 hari"
```

---

## 🔧 Troubleshooting

### Issue: ValidationError tidak muncul

**Penyebab:** Module belum fully loaded

**Solusi:**
```bash
./odoo-bin -u snifx_timeoff_policy -d your_database --stop-after-init
sudo systemctl restart odoo
```

---

### Issue: Access Error on work entries

**Penyebab:** User tidak punya akses ke hr.work.entry

**Solusi:**
Sudah ditangani! Module menggunakan `sudo()` untuk read-only access.
Jika masih error, pastikan version 18.0.1.0.0 atau lebih baru.

---

### Issue: Validation tidak sesuai harapan

**Check:**
1. Leave type configuration benar?
2. User dalam exempt groups?
3. Scope applicable untuk employee ini?
4. Within validity period?

**Debug Mode:**
```python
# Lihat log untuk detail
tail -f /var/log/odoo/odoo-server.log | grep -i "policy"
```

---

## 📊 FAQ

**Q: Apakah bisa berbeda per leave type?**  
A: Ya! Setiap leave type bisa punya policy berbeda.

**Q: Bagaimana jika karyawan perlu emergency leave?**  
A: Set grace_hours atau exempt user groups tertentu.

**Q: Apakah business days exclude weekend?**  
A: Ya, otomatis exclude Sabtu/Minggu dan hari libur di calendar.

**Q: Bisa setup policy seasonal?**  
A: Ya, gunakan valid_from dan valid_to.

**Q: Manager perlu notice juga?**  
A: Tergantung, bisa exempt via user groups.

---

## 📞 Support

**Author:** Snifx Studio  
**License:** LGPL-3  
**Version:** 18.0.1.0.0

**Issues?**
- Check logs: `/var/log/odoo/odoo-server.log`
- Review configuration: Time Off Types
- Verify user permissions: Settings > Users

---

## 📝 Changelog

### Version 18.0.1.0.0 (2025-11-25)

**Initial Release:**
- ✅ Date Restrictions (2 fields)
- ✅ Minimum Notice Requirement (13 fields)
- ✅ Working Days Limitation (2 fields)
- ✅ Unified configuration interface
- ✅ Indonesian error messages
- ✅ Triple fallback for working days calculation
- ✅ Migration support from separate addons
- ✅ Complete documentation

---

## 📝 Changelog

Untuk riwayat perubahan lengkap, lihat [CHANGELOG.md](CHANGELOG.md)

### Version 18.0.1.0.0 (Current - Base Release)
- ✅ Initial release with 3 main features
- ✅ 17 configuration fields
- ✅ Complete validation logic
- ✅ Indonesian localization

**Known Issues:**
- ⚠️ DateTime comparison error when submitting requests
- ⚠️ Working days calculation may double count

**Upgrade Recommended:** Version 18.0.1.0.2 available with fixes

---

**© 2025 Snifx Studio. All rights reserved.**
