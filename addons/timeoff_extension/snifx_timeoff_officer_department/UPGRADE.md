# Upgrade Guide - v1.0.2 → v2.0.0

## 🔄 Overview

This guide helps you upgrade from **Snifx Time Off Officer Balance v1.0.2** to **v2.0.0 Enhanced**.

### Major Changes in v2.0.0

| Feature | v1.0.2 | v2.0.0 |
|---------|--------|--------|
| Assignment Model | ❌ No (hardcoded to user's dept) | ✅ Yes (flexible) |
| Multiple Depts | ❌ No | ✅ Yes |
| Approval Rights | ❌ No (read-only) | ✅ Yes (full approval) |
| Public Holidays | ❌ No | ✅ Yes |
| View All Employees | ❌ No | ✅ Yes (limited tabs) |
| Self-Approval Block | ❌ No | ✅ Yes |
| Date-Based Assignments | ❌ No | ✅ Yes |

---

## ⚠️ Important Warnings

### Breaking Changes

1. **New Assignment Model**: Officers must be manually assigned after upgrade
2. **Access Rights Changed**: Officers now have write permissions on leaves
3. **Record Rules Modified**: New domain logic based on assignments
4. **Group Name Changed**: "Officer with Balance" → "Officer with Balance (Enhanced)"

### Data Migration Required

- **No automatic migration** from old user.department_id to new assignment model
- You must **manually create assignments** for existing officers
- Old v1.0.2 record rules will be replaced

---

## 📋 Pre-Upgrade Checklist

Before starting upgrade:

- [x] **BACKUP YOUR DATABASE** (critical!)
- [x] Backup Odoo filestore
- [x] Test upgrade on staging/development environment first
- [x] Document current officer users and their departments
- [x] Schedule upgrade during low-usage period
- [x] Notify users about temporary downtime

### Backup Commands

```bash
# Database backup
pg_dump -U odoo -d your_database > backup_before_upgrade_$(date +%Y%m%d).sql

# Filestore backup
tar -czf filestore_backup_$(date +%Y%m%d).tar.gz /opt/odoo/.local/share/Odoo/filestore/

# Config backup
cp /etc/odoo/odoo.conf /etc/odoo/odoo.conf.backup
```

---

## 🚀 Upgrade Procedure

### Step 1: Document Current Officers

Before upgrade, list all users with v1.0.2 officer group:

```sql
-- SQL to find current officers
SELECT 
    u.id,
    u.login,
    u.name as user_name,
    e.id as employee_id,
    e.name as employee_name,
    d.id as dept_id,
    d.name as dept_name,
    d.parent_id
FROM res_users u
JOIN res_groups_users_rel gu ON u.id = gu.uid
JOIN res_groups g ON gu.gid = g.id
LEFT JOIN hr_employee e ON e.user_id = u.id
LEFT JOIN hr_department d ON e.department_id = d.id
WHERE g.name = 'Officer with Balance'
ORDER BY u.name;
```

**Save this output!** You'll need it for Step 4.

### Step 2: Uninstall Old Version

1. Go to **Apps**
2. Remove "Apps" filter
3. Search: `Snifx Time Off Officer Balance`
4. Click **Uninstall**
5. Confirm uninstall
6. Wait for completion

### Step 3: Install New Version

1. Upload new module folder to addons directory:
   ```bash
   cd /opt/odoo/addons/
   rm -rf snifx_timeoff_officer_department/
   unzip snifx_timeoff_officer_department-18.0.2.0.0.zip
   chown -R odoo:odoo snifx_timeoff_officer_department/
   ```

2. Restart Odoo:
   ```bash
   sudo systemctl restart odoo
   ```

3. Go to **Apps** → **Update Apps List**

4. Search and install: `Snifx Time Off Officer Balance - Enhanced`

### Step 4: Migrate Officer Assignments

For each officer from Step 1, create an assignment:

#### Via UI (Recommended)

1. Go to **Settings → Users & Companies → Users**

2. Open the officer user

3. **Access Rights** tab:
   - ✅ Enable: Officer with Balance (Enhanced)

4. **Officer Assignments** tab:
   - Click **Add a line**
   - Department: Select the department from Step 1 output
   - Active: ✅ checked
   - Save

#### Via SQL (Bulk Creation)

```sql
-- Example: Create assignments for all old officers
-- ADJUST THIS BASED ON YOUR STEP 1 OUTPUT

INSERT INTO hr_timeoff_officer_assignment 
(user_id, department_id, active, company_id, create_date, create_uid, write_date, write_uid)
SELECT 
    u.id as user_id,
    e.department_id,
    TRUE as active,
    u.company_id,
    NOW() as create_date,
    1 as create_uid,  -- admin user id
    NOW() as write_date,
    1 as write_uid
FROM res_users u
JOIN res_groups_users_rel gu ON u.id = gu.uid
JOIN res_groups g ON gu.gid = g.id
JOIN hr_employee e ON e.user_id = u.id
WHERE g.name = 'Officer with Balance (Enhanced)'
  AND e.department_id IS NOT NULL
ON CONFLICT DO NOTHING;
```

**⚠️ Warning**: Test SQL on staging first!

### Step 5: Verify Upgrade

#### Test Each Officer

For each migrated officer:

1. **Login as officer**

2. **Check Access**:
   - ✅ Time Off → My Team → Time Off Requests (can see team requests)
   - ✅ Can open and approve leave requests
   - ✅ Cannot approve own leave (verify error shows)
   - ✅ Time Off → Reporting → Balance (see balance)
   - ✅ Employees (see all, limited tabs)
   - ✅ Configuration → Public Holidays (can create)

3. **Check Assignments**:
   - Settings → Users → User Form
   - Officer Assignments tab shows correct department

#### Check Data Integrity

```sql
-- Verify all assignments created
SELECT COUNT(*) FROM hr_timeoff_officer_assignment WHERE active = TRUE;

-- Check for officers without assignments
SELECT u.name, u.login
FROM res_users u
JOIN res_groups_users_rel gu ON u.id = gu.uid
JOIN res_groups g ON gu.gid = g.id
LEFT JOIN hr_timeoff_officer_assignment a ON a.user_id = u.id AND a.active = TRUE
WHERE g.name = 'Officer with Balance (Enhanced)'
  AND a.id IS NULL;
  
-- Should return 0 rows if all officers have assignments
```

### Step 6: Clean Up Old Data (Optional)

If upgrade successful and tested:

```sql
-- Remove old group membership if duplicate
-- (Usually Odoo handles this automatically)

-- Check for duplicate groups
SELECT g.name, COUNT(*)
FROM res_groups g
WHERE g.name LIKE '%Officer%Balance%'
GROUP BY g.name;
```

---

## 🔍 Post-Upgrade Verification

### Functionality Checklist

Test the following as an officer:

- [x] Can view leave requests for assigned departments
- [x] Can approve leave requests (not own)
- [x] Error shown when trying to approve own leave
- [x] Can validate leave requests
- [x] Can view balance reports (filtered correctly)
- [x] Can export balance to Excel
- [x] Can view all employees
- [x] Private Information tab is hidden
- [x] Can create public holidays
- [x] Can edit/delete public holidays
- [x] Assignment shows in User → Officer Assignments tab

### Performance Check

```sql
-- Check query performance for leave requests
EXPLAIN ANALYZE
SELECT * FROM hr_leave
WHERE employee_id IN (
    SELECT e.id FROM hr_employee e
    JOIN hr_department d ON e.department_id = d.id
    WHERE d.id IN (1, 2, 3)  -- Replace with actual dept IDs
);
```

Should use indexes efficiently.

---

## 🐛 Troubleshooting

### Issue 1: Officer Has No Access After Upgrade

**Symptoms:**
- Officer can't see any leave requests
- Balance report is empty

**Solutions:**

1. Check assignment exists:
   ```sql
   SELECT * FROM hr_timeoff_officer_assignment 
   WHERE user_id = X;  -- Replace X with user ID
   ```

2. Create missing assignment (see Step 4)

3. Verify group assignment:
   - Settings → Users → Access Rights
   - Officer with Balance (Enhanced) should be checked

4. Logout and login again

### Issue 2: Officer Can Still See Private Information Tab

**Symptoms:**
- Employee form shows all tabs

**Solutions:**

1. Clear browser cache completely

2. Check if user also has HR Manager group (which overrides):
   ```sql
   SELECT g.name 
   FROM res_groups g
   JOIN res_groups_users_rel gu ON g.id = gu.gid
   WHERE gu.uid = X;  -- Replace X with user ID
   ```

3. If user needs HR Manager, that's expected (HR Manager sees all)

### Issue 3: Duplicate Assignment Error

**Symptoms:**
```
ValidationError: Assignment already exists
```

**Solutions:**

Check for duplicates:
```sql
SELECT user_id, department_id, COUNT(*)
FROM hr_timeoff_officer_assignment
WHERE active = TRUE
GROUP BY user_id, department_id
HAVING COUNT(*) > 1;
```

Deactivate duplicates:
```sql
-- Keep only the latest
UPDATE hr_timeoff_officer_assignment
SET active = FALSE
WHERE id NOT IN (
    SELECT MAX(id) FROM hr_timeoff_officer_assignment
    WHERE active = TRUE
    GROUP BY user_id, department_id
);
```

### Issue 4: Old Record Rules Still Active

**Symptoms:**
- Officers can see employees they shouldn't

**Solutions:**

1. Go to **Settings → Technical → Security → Record Rules**

2. Search for: `Officer`

3. Check active rules:
   - Should have NEW rules (v2.0.0) with assignment logic
   - Should NOT have OLD rules (v1.0.2) with user.employee_ids.department_id

4. Deactivate old rules if found:
   - Open rule
   - Uncheck Active
   - Save

---

## 🔄 Rollback Procedure

If upgrade fails and you need to rollback:

### Step 1: Restore Database

```bash
# Stop Odoo
sudo systemctl stop odoo

# Restore database
psql -U odoo -d your_database < backup_before_upgrade_YYYYMMDD.sql

# Start Odoo
sudo systemctl start odoo
```

### Step 2: Restore Filestore

```bash
# Extract backup
tar -xzf filestore_backup_YYYYMMDD.tar.gz -C /

# Fix permissions
chown -R odoo:odoo /opt/odoo/.local/share/Odoo/filestore/
```

### Step 3: Reinstall v1.0.2

1. Upload old module back to addons
2. Restart Odoo
3. Update apps list
4. Install old version

---

## 📊 Upgrade Statistics

Track your upgrade:

```sql
-- Officers migrated
SELECT COUNT(*) as total_officers
FROM res_users u
JOIN res_groups_users_rel gu ON u.id = gu.uid
JOIN res_groups g ON gu.gid = g.id
WHERE g.name = 'Officer with Balance (Enhanced)';

-- Assignments created
SELECT COUNT(*) as total_assignments
FROM hr_timeoff_officer_assignment
WHERE active = TRUE;

-- Departments managed
SELECT COUNT(DISTINCT department_id) as total_departments
FROM hr_timeoff_officer_assignment
WHERE active = TRUE;

-- Leave requests accessible to officers
SELECT COUNT(*) as accessible_leaves
FROM hr_leave l
JOIN hr_employee e ON l.employee_id = e.id
WHERE e.department_id IN (
    SELECT department_id FROM hr_timeoff_officer_assignment WHERE active = TRUE
);
```

---

## 📞 Support

If you need help with upgrade:

1. **Documentation**: Re-read this guide carefully
2. **Logs**: Check Odoo logs for errors
3. **SQL**: Review queries before running
4. **Backup**: Ensure you have backups before proceeding
5. **Contact**: support@snifx.example with:
   - Odoo version
   - Error messages
   - Steps already tried
   - Database size (# of employees, departments)

---

## ✅ Upgrade Success Criteria

Upgrade is successful when:

- [x] All officers have assignments created
- [x] Officers can approve leaves (except own)
- [x] Balance reports show correct data
- [x] Public holidays can be created
- [x] Employee tabs are hidden correctly
- [x] No errors in Odoo logs
- [x] All tests pass (see verification checklist)
- [x] Users report no access issues

---

**Upgrade Complete! Enjoy the enhanced features! 🎉**
