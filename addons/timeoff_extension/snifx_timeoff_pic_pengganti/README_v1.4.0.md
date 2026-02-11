# Time Off - PIC Pengganti v1.4.0
## Comprehensive Fix for "Missing Record" Error

---

## 🎯 WHAT'S NEW IN v1.4.0

### Critical Fixes:
1. **✅ Fixes CURRENT orphaned data** via `post_init_hook`
   - Automatically cleans existing orphaned records on install/upgrade
   - No manual SQL queries needed
   - No manual cache clearing required

2. **✅ Prevents FUTURE orphaned data** via enhanced `unlink()`
   - Comprehensive cleanup of mail.message, mail.activity, mail.followers
   - Proper logging for debugging
   - Safe for Admin and Officer All Employee users

3. **✅ Proper logging**
   - Detailed logs in Odoo server log
   - Track what's being cleaned and how many records

---

## 🐛 PROBLEM SOLVED

### Issue:
```
Error: "Missing Record (hr.leave(5,), User: 2)"
```

**Who affected?**
- ✅ Admin users (global access)
- ✅ Officer All Employee (global access)
- ❌ Regular employees (department-scoped, filtered out)

**Where it appears?**
- Employees → Organization Chart
- Inbox/Notifications

**Root cause:**
- Orphaned `mail.message` records referencing deleted `hr.leave` records
- Admin/Officer load ALL employees → load messages → try to access deleted record → ERROR
- Regular employees don't see cross-department data → no error

---

## 📦 INSTALLATION INSTRUCTIONS

### Step 1: Backup (RECOMMENDED)
```bash
# Backup database
sudo -u postgres pg_dump your_database_name > /tmp/backup_before_v1.4.0.sql

# Backup current module
cd /opt/odoo/addons
sudo cp -r snifx_timeoff_pic_pengganti /tmp/snifx_timeoff_pic_pengganti_backup
```

### Step 2: Stop Odoo
```bash
sudo systemctl stop odoo
```

### Step 3: Replace Module
```bash
cd /opt/odoo/addons

# Remove old version
sudo rm -rf snifx_timeoff_pic_pengganti

# Extract v1.4.0
sudo unzip /tmp/snifx_timeoff_pic_pengganti-18_0_1_4_0.zip

# Rename directory (remove version suffix)
sudo mv snifx_timeoff_pic_pengganti_v1_4_0 snifx_timeoff_pic_pengganti

# Fix permissions
sudo chown -R odoo:odoo snifx_timeoff_pic_pengganti
```

### Step 4: Upgrade Module
```bash
# Upgrade module (this will trigger post_init_hook automatically)
sudo -u odoo /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf \
     -u snifx_timeoff_pic_pengganti \
     --stop-after-init
```

**CRITICAL**: Watch the log output! You should see:
```
================================================================================
Starting orphaned data cleanup for Time Off - PIC Pengganti v1.4.0
================================================================================
Checking for orphaned mail.message records...
Found X orphaned mail.message records. Cleaning up...
✅ Cleaned X orphaned mail.message records
...
Cleanup completed! Total records cleaned: X
================================================================================
```

### Step 5: Start Odoo
```bash
sudo systemctl start odoo
```

### Step 6: Test (Admin User)
```
1. Login as Admin or Officer All Employee
2. Open Employees → Organization Chart
3. Expected: ✅ NO ERROR!
4. Test creating and deleting Time Off
5. Expected: ✅ Smooth deletion, no errors
```

---

## 🔍 VERIFICATION

### Check Odoo Server Log:
```bash
sudo tail -n 100 /var/log/odoo/odoo.log | grep -A 10 "orphaned data cleanup"
```

You should see detailed cleanup statistics.

### Verify No More Orphaned Data:
```sql
-- Run this in PostgreSQL
-- Should return 0 for all

-- Check mail.message
SELECT COUNT(*) 
FROM mail_message 
WHERE model = 'hr.leave' 
  AND res_id NOT IN (SELECT id FROM hr_leave);
-- Expected: 0

-- Check mail.activity
SELECT COUNT(*) 
FROM mail_activity 
WHERE res_model = 'hr.leave' 
  AND res_id NOT IN (SELECT id FROM hr_leave);
-- Expected: 0

-- Check mail.followers
SELECT COUNT(*) 
FROM mail_followers 
WHERE res_model = 'hr.leave' 
  AND res_id NOT IN (SELECT id FROM hr_leave);
-- Expected: 0
```

---

## 📊 EXPECTED RESULTS

### Immediate (After Installation):
- ✅ All existing orphaned data cleaned automatically
- ✅ No "Missing Record" errors in Org Chart
- ✅ Admin and Officer users can navigate freely
- ✅ No manual intervention needed

### Future (After v1.4.0 is active):
- ✅ Every Time Off deletion triggers comprehensive cleanup
- ✅ No orphaned mail.message, mail.activity, or mail.followers
- ✅ Safe for all user types (Admin, Officer, Regular employee)
- ✅ Proper logging for troubleshooting

---

## 🆚 COMPARISON: v1.3.7 vs v1.4.0

| Feature | v1.3.7 | v1.4.0 |
|---------|--------|--------|
| Fix CURRENT orphaned data | ❌ NO | ✅ YES (auto via hook) |
| Prevent FUTURE orphaned data | ⚠️ Partial | ✅ YES (comprehensive) |
| Clean mail.message | ❌ NO | ✅ YES |
| Clean mail.activity | ✅ YES | ✅ YES |
| Clean mail.followers | ❌ NO | ✅ YES |
| Logging | ❌ NO | ✅ YES (detailed) |
| Auto-fix on install | ❌ NO | ✅ YES |
| Manual SQL needed | ✅ YES | ❌ NO |
| Cache clearing needed | ✅ YES | ❌ NO |
| Downtime | ~7 min | ~3 min |

---

## 🐛 TROUBLESHOOTING

### If error persists after installation:

1. **Check if post_init_hook ran:**
   ```bash
   sudo grep "orphaned data cleanup" /var/log/odoo/odoo.log
   ```
   If you don't see cleanup logs, the hook didn't run.

2. **Manually trigger hook (if needed):**
   ```bash
   # Upgrade module again
   sudo systemctl stop odoo
   sudo -u odoo /opt/odoo/odoo-bin -c /etc/odoo/odoo.conf \
        -u snifx_timeoff_pic_pengganti \
        --stop-after-init
   sudo systemctl start odoo
   ```

3. **Check specific orphaned record:**
   ```sql
   -- Find orphaned messages for specific hr.leave ID (e.g., 5)
   SELECT * FROM mail_message 
   WHERE model = 'hr.leave' AND res_id = 5;
   
   -- If found, delete manually:
   DELETE FROM mail_message 
   WHERE model = 'hr.leave' AND res_id = 5;
   ```

4. **Clear browser cache (last resort):**
   ```
   Admin user:
   1. Ctrl+Shift+Delete
   2. Select "All time"
   3. Clear "Cached images and files"
   4. Restart browser
   5. Test again
   ```

---

## 📝 CHANGELOG

### v1.4.0 (Current) - COMPREHENSIVE FIX
- **NEW**: post_init_hook for automatic cleanup of existing orphaned data
- **ENHANCED**: unlink() now cleans mail.message (critical for Org Chart error)
- **ADDED**: Comprehensive cleanup of mail.followers
- **ADDED**: Detailed logging for all cleanup operations
- **FIXED**: "Missing Record" error for Admin and Officer All Employee users
- **IMPROVED**: No manual intervention needed (SQL queries, cache clearing)

### v1.3.7 (Previous)
- Basic cleanup of mail.activity
- Attempted cleanup of employee.current_leave_id
- Missing: mail.message cleanup (root cause)
- Missing: post_init_hook (existing data not cleaned)
- Required: Manual SQL and cache clearing

---

## ✅ SUCCESS CRITERIA

After v1.4.0 installation, you should have:

1. **✅ Zero orphaned records** in database
2. **✅ No "Missing Record" errors** in Org Chart
3. **✅ Detailed cleanup logs** in Odoo server log
4. **✅ Future deletions** handled automatically
5. **✅ Admin/Officer users** can navigate freely
6. **✅ No manual maintenance** required

---

## 📞 SUPPORT

If issues persist after v1.4.0:
1. Check Odoo server log for cleanup details
2. Run verification SQL queries
3. Provide log output for further analysis

**Expected**: v1.4.0 will resolve the issue **immediately** upon installation with **zero manual intervention**.

---

## 🎯 TECHNICAL DETAILS

### Why v1.4.0 Works:

**Current Issue Root Cause:**
```
Admin opens Org Chart
→ Loads ALL employees (global access)
→ Loads mail.message for employees
→ mail.message references deleted hr.leave(5)
→ Odoo tries to load hr.leave(5)
→ Record doesn't exist
→ ERROR: "Missing Record (hr.leave(5,), User: 2)"
```

**v1.4.0 Solution:**
```
Install v1.4.0
→ post_init_hook runs automatically
→ Deletes ALL orphaned mail.message (including hr.leave(5))
→ Deletes ALL orphaned mail.activity
→ Deletes ALL orphaned mail.followers
→ Restart Odoo
→ Admin opens Org Chart
→ Loads employees
→ Loads mail.message (now clean)
→ ✅ NO ERROR!
```

**Future Deletions:**
```
User deletes Time Off
→ unlink() method triggered
→ Cleans mail.message (before deletion)
→ Cleans mail.activity (before deletion)
→ Cleans mail.followers (before deletion)
→ Deletes hr.leave record
→ ✅ No orphaned data left behind
```

---

## 🔒 SAFETY

- ✅ Backup recommended but not required
- ✅ Only deletes orphaned references (not valid data)
- ✅ Uses sudo() for proper permission handling
- ✅ Comprehensive logging for audit trail
- ✅ Tested cleanup logic
- ✅ No breaking changes to existing functionality

---

**Version:** 18.0.1.4.0  
**Author:** Snifx Studio  
**License:** LGPL-3  
**Odoo Version:** 18 Community Edition  
**Module:** snifx_timeoff_pic_pengganti
