# 📖 Panduan Konfigurasi Detail
## Time Off - Company Policy Management

---

## Daftar Isi

1. [Pengenalan](#pengenalan)
2. [Akses Konfigurasi](#akses-konfigurasi)
3. [Field Reference](#field-reference)
4. [Skenario Konfigurasi](#skenario-konfigurasi)
5. [Best Practices](#best-practices)
6. [Troubleshooting](#troubleshooting)

---

## Pengenalan

Module ini menambahkan 3 kategori field pada **Time Off Types** untuk mengontrol kebijakan cuti perusahaan:

### Kategori Field

| Kategori | Jumlah Field | Fungsi Utama |
|----------|--------------|--------------|
| Date Restrictions | 2 | Kontrol tanggal masa depan/mundur |
| Minimum Notice | 13 | Persyaratan pemberitahuan advance |
| Working Days Limit | 2 | Batasan hari kerja berturut-turut |
| **Total** | **17** | **Complete policy control** |

---

## Akses Konfigurasi

### Menu Path

```
Time Off > Configuration > Time Off Types
```

### Steps

1. Click menu **Time Off**
2. Pilih **Configuration** > **Time Off Types**
3. Pilih leave type yang akan dikonfigurasi (atau Create New)
4. Scroll ke bawah, lihat section **Company Policy Settings**
5. Configure sesuai kebutuhan
6. Click **Save**

---

## Field Reference

### SECTION 1: Date Restrictions

#### 1.1. Allow Future Date Requests

**Type:** Boolean (Checkbox)  
**Default:** Checked (True)  
**Label:** "Allow Future Date Requests"

**Fungsi:**
- Mengizinkan/melarang karyawan mengajukan cuti untuk tanggal masa depan
- Jika unchecked: hanya boleh untuk hari ini atau sebelumnya

**Use Case:**
```
✓ Checked: Annual Leave, Sick Leave
✗ Unchecked: Retroactive corrections, Emergency today
```

**Validation:**
```python
if not allow_future_request and request_date > today:
    raise ValidationError("Tidak dapat mengajukan cuti masa depan")
```

---

#### 1.2. Maximum Backdate Days

**Type:** Integer  
**Default:** 0  
**Label:** "Maximum Backdate Days"  
**Range:** 0 - 365

**Fungsi:**
- Berapa hari ke belakang maksimal yang diperbolehkan
- `0` = tidak boleh backdate sama sekali
- `7` = boleh mundur maksimal 7 hari

**Use Case:**
```
0: Emergency Leave (tidak boleh mundur)
3: Sick Leave (dengan surat dokter)
7: Annual Leave (flexibility)
30: Correction/Admin (special cases)
```

**Validation:**
```python
if max_backdate_days == 0 and request_date < today:
    raise ValidationError("Tidak dapat backdate")

if request_date < (today - timedelta(days=max_backdate_days)):
    raise ValidationError(f"Maksimal mundur {max_backdate_days} hari")
```

---

### SECTION 2: Minimum Notice Requirement

#### 2.1. Enable Minimum Notice Requirement

**Type:** Boolean (Checkbox)  
**Default:** Unchecked (False)  
**Label:** "Enable Minimum Notice Requirement"

**Fungsi:**
- Master switch untuk mengaktifkan persyaratan minimum notice
- Jika unchecked: semua field notice lain disabled

**Note:** Harus dicheck dulu agar field lain muncul.

---

#### 2.2. Duration Threshold (Days)

**Type:** Float  
**Default:** 0.0  
**Label:** "Duration Threshold (Days)"  
**Range:** 0.0 - 365.0

**Fungsi:**
- Minimum notice hanya apply jika **durasi cuti ≥ threshold**
- `0` = apply untuk semua durasi
- `5` = hanya apply untuk cuti ≥ 5 hari

**Use Case:**
```
0.0: Semua cuti perlu notice (termasuk 1 hari)
3.0: Cuti 1-2 hari bebas, ≥3 hari perlu notice
5.0: Cuti pendek fleksibel, long leave perlu planning
```

**Logic:**
```python
if threshold_days > 0 and duration < threshold_days:
    return  # Skip validation, tidak perlu notice
```

---

#### 2.3. Use Business Days for Threshold

**Type:** Boolean (Checkbox)  
**Default:** Unchecked (False)  
**Label:** "Use Business Days for Threshold"

**Fungsi:**
- Threshold dihitung pakai hari kerja (bukan hari kalender)
- Jika checked: 5 days threshold = 5 hari kerja (~7 hari kalender)

**Use Case:**
```
Unchecked: Simple, pakai number_of_days
Checked: Lebih akurat, exclude weekend
```

---

#### 2.4. Minimum Notice Quantity

**Type:** Integer  
**Default:** 1  
**Label:** "Minimum Notice Quantity"  
**Range:** 1 - 999

**Fungsi:**
- Berapa banyak unit pemberitahuan yang diperlukan
- Dikombinasi dengan `min_notice_unit`

**Contoh:**
```
7 + Days = 7 hari sebelumnya
2 + Weeks = 2 minggu sebelumnya
5 + Business Days = 5 hari kerja sebelumnya
```

---

#### 2.5. Notice Unit

**Type:** Selection (Dropdown)  
**Options:**
- `days` = Calendar Days
- `business_days` = Business Days
- `weeks` = Weeks

**Fungsi:**
- Unit waktu untuk perhitungan notice

**Perbedaan:**

| Unit | Contoh | Exclude Weekend? | Exclude Holidays? |
|------|--------|------------------|-------------------|
| Calendar Days | 7 days = 7 hari | No | No |
| Business Days | 7 days = ~10 hari kalender | Yes | Optional |
| Weeks | 2 weeks = 14 hari | No | No |

**Recommendation:**
```
✓ Calendar Days: Simple, mudah dihitung
✓ Business Days: Lebih fair (exclude weekend)
✓ Weeks: Untuk long planning
```

---

#### 2.6. Exclude Public Holidays

**Type:** Boolean (Checkbox)  
**Default:** Checked (True)  
**Label:** "Exclude Public Holidays"  
**Visible:** Only when `Notice Unit = Business Days`

**Fungsi:**
- Saat menghitung business days, exclude hari libur nasional
- Menggunakan public holidays dari Resource Calendar

**Use Case:**
```
Checked: 7 business days = 7 hari kerja aktual (skip libur)
Unchecked: 7 business days = weekdays saja (bisa include libur)
```

---

#### 2.7. Scope Mode

**Type:** Selection (Dropdown)  
**Default:** Company-wide  
**Options:**
- `company` = Company-wide (semua karyawan)
- `department` = Specific Department
- `category` = Employee Category

**Fungsi:**
- Tentukan cakupan berlakunya rule ini

**Detail:**

**Company-wide:**
```
• Berlaku untuk SEMUA karyawan
• Paling sederhana
• Use case: Company-wide policy
```

**Specific Department:**
```
• Hanya untuk department tertentu
• Field department_id muncul
• Use case: IT perlu 14 hari, Sales perlu 7 hari
```

**Employee Category:**
```
• Hanya untuk category tertentu (Manager, Staff, etc)
• Field category_id muncul
• Use case: Manager perlu 21 hari, Staff perlu 7 hari
```

---

#### 2.8. Department (if scope = department)

**Type:** Many2one (Dropdown)  
**Model:** hr.department  
**Visible:** Only when `Scope = Specific Department`

**Fungsi:**
- Pilih department mana yang terkena rule ini

---

#### 2.9. Category (if scope = category)

**Type:** Many2one (Dropdown)  
**Model:** hr.employee.category  
**Visible:** Only when `Scope = Employee Category`

**Fungsi:**
- Pilih employee category mana yang terkena rule ini

---

#### 2.10. Exempt Groups

**Type:** Many2many (Tags)  
**Model:** res.groups  
**Label:** "Exempt Groups"

**Fungsi:**
- User groups yang **DIKECUALIKAN** dari rule
- Jika user ada di group ini, skip validation

**Use Case:**
```
Exempt: 
  • Time Off / Manager
  • Administration / Settings

Artinya: Managers dan Admins tidak perlu minimum notice
```

**Common Exempt Groups:**
```
• Time Off / Manager (bisa approve sendiri)
• HR / Officer (HR staff)
• Administration / Settings (super admin)
• Custom / Emergency Contact (khusus emergency)
```

---

#### 2.11. Grace Hours

**Type:** Integer  
**Default:** 0  
**Label:** "Grace Period (Hours)"  
**Range:** 0 - 72

**Fungsi:**
- Jam toleransi tambahan sebelum notice requirement berlaku
- Berguna untuk same-day atau near-deadline requests

**Contoh:**
```
Grace Hours: 3
Notice Required: 7 days

Artinya:
• Deadline = (start_date - 7 days)
• Tapi masih boleh submit sampai (deadline + 3 hours)
```

**Use Case:**
```
0: Strict, no tolerance
3: Beberapa jam toleransi (morning submission)
8: One working day tolerance
24: One full day tolerance
```

---

#### 2.12. Valid From

**Type:** Date  
**Optional:** Yes (kosongkan = no start limit)  
**Label:** "Valid From"

**Fungsi:**
- Tanggal mulai berlaku rule ini
- Jika kosong = selalu berlaku
- Jika diisi = hanya berlaku sejak tanggal ini

**Use Case:**
```
Valid From: 2025-06-01

Artinya: Rule mulai berlaku 1 Juni 2025
Sebelum tanggal ini, rule tidak apply
```

---

#### 2.13. Valid To

**Type:** Date  
**Optional:** Yes (kosongkan = no end limit)  
**Label:** "Valid To"

**Fungsi:**
- Tanggal akhir berlaku rule ini
- Jika kosong = berlaku selamanya
- Jika diisi = hanya berlaku sampai tanggal ini

**Use Case:**
```
Valid From: 2025-06-01
Valid To: 2025-08-31

Artinya: Rule hanya berlaku Juni-Agustus (peak season)
```

---

### SECTION 3: Batasan Hari Kerja Cuti

#### 3.1. Batasi Hari Kerja Cuti

**Type:** Boolean (Checkbox)  
**Default:** Unchecked (False)  
**Label:** "Batasi Hari Kerja Cuti"

**Fungsi:**
- Master switch untuk mengaktifkan batasan working days
- Jika unchecked: tidak ada batasan

---

#### 3.2. Maksimal Hari Kerja untuk Cuti

**Type:** Integer  
**Default:** 0  
**Label:** "Maksimal Hari Kerja untuk Cuti"  
**Range:** 0 - 365  
**Visible:** Only when `Batasi Hari Kerja Cuti` is checked

**Fungsi:**
- Maksimal hari kerja berturut-turut yang boleh diambil cuti
- `0` = unlimited (disable limit)
- `10` = maksimal 10 hari kerja

**Perhitungan:**
```
1. Cek Work Entries (paling akurat)
2. Fallback: Resource Calendar
3. Fallback: Simple weekday count
```

**Contoh:**
```
Request: 15 hari berturut (Mon-Fri x 3 weeks)
Working Days: 15 hari (skip Sat/Sun)

If max_working_days = 10:
  ❌ Validation Error: Melebihi batas 10 hari kerja
```

**Use Case:**
```
5: Short leave only
10: Standard vacation
20: Extended vacation
30: Sabbatical/unpaid
0: No limit (unlimited)
```

---

## Skenario Konfigurasi

### Skenario 1: Perusahaan Startup (Fleksibel)

**Context:**
- Karyawan sedikit
- Trust-based culture
- Perlu flexibility

**Config:**

```yaml
Annual Leave:
  Date Restrictions:
    Allow Future: ✓ Yes
    Max Backdate: 30 days (very flexible)
  
  Minimum Notice:
    Enable: ✗ No (or very short, 3 days)
  
  Working Days:
    Enable: ✓ Yes
    Max: 15 days
```

---

### Skenario 2: Perusahaan Besar (Structured)

**Context:**
- Banyak karyawan
- Need planning
- Multiple departments

**Config:**

```yaml
Annual Leave:
  Date Restrictions:
    Allow Future: ✓ Yes
    Max Backdate: 7 days
  
  Minimum Notice:
    Enable: ✓ Yes
    Threshold: 5 days (long leave only)
    Notice: 21 days (3 weeks)
    Unit: Calendar Days
    Scope: Company-wide
  
  Working Days:
    Enable: ✓ Yes
    Max: 20 days
```

---

### Skenario 3: Customer Service 24/7

**Context:**
- Shift-based
- Coverage critical
- Peak seasons

**Config:**

```yaml
Annual Leave:
  Date Restrictions:
    Allow Future: ✓ Yes
    Max Backdate: 3 days
  
  Minimum Notice:
    Enable: ✓ Yes
    Threshold: 3 days
    Notice: 14 days
    Unit: Business Days
    Scope: Department (Customer Service)
    
    # Peak Season (Dec-Jan)
    Valid From: 2025-12-01
    Valid To: 2026-01-31
    Notice Required: 30 days (during peak)
  
  Working Days:
    Enable: ✓ Yes
    Max: 10 days
```

---

### Skenario 4: Different Rules per Department

#### IT Department

```yaml
Threshold: 5 days
Notice: 14 days (project planning)
Scope: Department > IT
Max Working Days: 15
```

#### Sales Department

```yaml
Threshold: 3 days
Notice: 7 days (customer meetings)
Scope: Department > Sales
Max Working Days: 10
```

#### Operations

```yaml
Threshold: 2 days
Notice: 5 days (shift coverage)
Scope: Department > Operations
Max Working Days: 5
```

---

## Best Practices

### 1. Start Simple

```
1. Enable date restrictions first
2. Add minimum notice gradually
3. Fine-tune based on feedback
```

### 2. Communication

```
• Inform employees about new policies
• Explain the reasoning
• Provide examples
• Give grace period for adjustment
```

### 3. Balance

```
Too Strict:
  ❌ 30 days notice for all leaves
  ❌ No backdate at all
  ❌ Max 3 working days

Too Loose:
  ❌ No restrictions
  ❌ Unlimited backdate
  ❌ No planning required

Good Balance:
  ✓ 7-14 days notice for planned leaves
  ✓ 3-7 days backdate for emergencies
  ✓ 10-20 working days limit
```

### 4. Review Regularly

```
Quarterly Review:
  • Check denial rates
  • Collect feedback
  • Adjust thresholds
  • Update seasonal rules
```

---

## Troubleshooting

### Issue: Validation tidak berfungsi

**Check:**
1. Module installed correctly?
2. Leave type configuration saved?
3. User dalam exempt group?
4. Scope applicable untuk employee?

**Debug:**
```python
# Check employee info
employee = env['hr.employee'].browse(ID)
print(employee.department_id)  # Check department
print(employee.category_ids)    # Check categories
print(env.user.groups_id.mapped('name'))  # Check user groups
```

---

### Issue: Business days calculation salah

**Check:**
1. Resource Calendar configured?
2. Public holidays defined?
3. Work entries validated?

**Debug:**
```python
# Check calendar
calendar = employee.resource_calendar_id
print(calendar.attendance_ids)  # Check work hours
print(calendar.global_leave_ids)  # Check public holidays
```

---

### Issue: Seasonal policy tidak berlaku

**Check:**
1. Valid From / Valid To dates benar?
2. Today dalam range?
3. Other policies overriding?

**Debug:**
```python
from datetime import date
today = date.today()
print(f"Valid From: {leave_type.valid_from}")
print(f"Valid To: {leave_type.valid_to}")
print(f"Today: {today}")
print(f"In range: {leave_type.valid_from <= today <= leave_type.valid_to}")
```

---

**© 2025 Snifx Studio**
