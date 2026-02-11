# Quick Start Guide - v2.3.0

## 🚀 Fast Installation

### For New Installations

1. **Upload Module**
   ```bash
   # Copy to Odoo addons folder
   cp -r snifx_timeoff_officer_department /opt/odoo/addons/
   
   # Set permissions
   chown -R odoo:odoo /opt/odoo/addons/snifx_timeoff_officer_department
   ```

2. **Restart Odoo**
   ```bash
   sudo systemctl restart odoo
   ```

3. **Install Module**
   - Go to **Apps** menu
   - Remove "Apps" filter
   - Search "Snifx Time Off Officer Balance"
   - Click **Install**

4. **Configure Officers**
   - Go to **Time Off > Configuration > Officer Assignments**
   - Click **New**
   - Select **User** and **Department**
   - Save

---

### For Upgrading from v2.2.3 → v2.3.0

1. **Backup Database**
   ```bash
   pg_dump your_database > backup_before_230.sql
   ```

2. **Upload New Version**
   ```bash
   # Replace old version
   rm -rf /opt/odoo/addons/snifx_timeoff_officer_department
   cp -r snifx_timeoff_officer_department /opt/odoo/addons/
   chown -R odoo:odoo /opt/odoo/addons/snifx_timeoff_officer_department
   ```

3. **Restart Odoo**
   ```bash
   sudo systemctl restart odoo
   ```

4. **Upgrade Module**
   - Go to **Apps** menu
   - Remove "Apps" filter
   - Search "Snifx Time Off Officer Balance"
   - Click **Upgrade** button

5. **Clear Browser Cache**
   - Press `Ctrl + Shift + Delete`
   - Clear all cached data
   - Close and reopen browser

6. **Test Immediately**
   - Login as Officer user
   - Go to **Time Off > Public Holidays**
   - Click **New**
   - Fill: Name, Start Date, End Date
   - Click **Save**
   - ✅ Should save without "Access Denied" error!

---

## 🔧 Quick Configuration

### Step 1: Assign Groups to Users

1. Go to **Settings > Users & Companies > Users**
2. Open user (e.g., Andri)
3. **Access Rights** tab
4. Under **TIME OFF** section:
   - ✅ Check **Officer with Balance (Enhanced)**
5. Save

### Step 2: Create Officer Assignment

1. Go to **Time Off > Configuration > Officer Assignments**
2. Click **New**
3. Fill in:
   - **Officer**: Select user (e.g., Andri)
   - **Department**: Select department (e.g., Technical)
   - **Active**: ✅ Checked
   - **Date From**: (optional) Leave empty for permanent
   - **Date To**: (optional) Leave empty for permanent
4. Save

### Step 3: Test Public Holiday Creation

1. **Logout** and **Login as Officer** (Andri)
2. Go to **Time Off > Public Holidays**
3. Click **New**
4. Fill:
   - **Reason**: "New Year 2025"
   - **Start Date**: 2025-01-01 00:00:00
   - **End Date**: 2025-01-01 23:59:59
5. Click **Save**
6. ✅ **Success!** No errors should appear

---

## ✅ What's Fixed in v2.3.0

### Primary Fix: Public Holiday Creation
**Before v2.3.0:**
```
❌ Officer clicks "Save" on Public Holiday
❌ Error: "Access Denied to Project (project.project)"
❌ Cannot create public holidays
```

**After v2.3.0:**
```
✅ Officer clicks "Save" on Public Holiday
✅ Record saves successfully
✅ Public holiday created!
```

### Root Cause
Odoo 18 with `hr_timesheet` and `project_timesheet_holidays` installed creates implicit relationships between `resource.calendar.leaves` and `project.project`. Officers need READ access to related models.

### Solution Applied
Added READ-only access to:
- ✅ `project.project`
- ✅ `resource.calendar`
- ✅ `resource.resource`

**Security Note:** Officers can only VIEW these models, not MODIFY them.

---

## 🧪 Quick Verification Tests

### Test 1: Public Holiday (Critical)
```
1. Login as Officer
2. Time Off > Public Holidays > New
3. Fill: Name, Start Date, End Date
4. Save
Expected: ✅ Saves without errors
```

### Test 2: Time Off Approval
```
1. Employee submits time off
2. Login as Officer
3. Time Off > My Team's Time Off
4. Open request > Click Approve
Expected: ✅ Request approved
```

### Test 3: Activity Notification
```
1. Employee submits time off
2. Login as Officer
3. Click profile icon (top-right) > My Activities
Expected: ✅ Activity appears for pending approval
```

### Test 4: Department Hierarchy
```
1. Assign Officer to parent department "Technical"
2. Login as Officer
3. Time Off > My Team's Time Off
Expected: ✅ See employees from "Technical" and all child departments
```

---

## 🆘 Troubleshooting

### Issue: Still getting "Access Denied" error

**Solution 1: Force Reload Access Rights**
```bash
# Restart Odoo with update flag
sudo systemctl stop odoo
/opt/odoo/odoo-bin -u snifx_timeoff_officer_department -d your_database --stop-after-init
sudo systemctl start odoo
```

**Solution 2: Clear All Caches**
```python
# In Odoo shell or debug mode
self.env['ir.model.access'].clear_caches()
self.env['ir.rule'].clear_caches()
```

**Solution 3: Verify Access Rights**
```
Settings > Technical > Security > Access Rights
Search: "OfficerBalance"
Verify these exist:
- OfficerBalance read project.project (READ=1)
- OfficerBalance read resource.calendar (READ=1)
- OfficerBalance read resource.resource (READ=1)
```

---

### Issue: Officer doesn't see approve buttons

**Check:**
1. User has "Officer with Balance (Enhanced)" group
2. Officer assignment exists and is active
3. Leave request is in "To Approve" state
4. Officer is not approving their own request

---

### Issue: No activities created

**Check:**
1. Activity types exist:
   - "Time Off Approval"
   - "Time Off Second Approve"
2. Officer assignments are active (checkbox checked)
3. Employee department matches officer assignment

---

## 📊 System Requirements

- **Odoo**: 18.0 Community Edition
- **Python**: 3.10 or higher
- **PostgreSQL**: 12 or higher
- **RAM**: Minimum 2GB (4GB recommended)
- **Disk**: 100MB for module + database growth

---

## 🔗 Additional Resources

- **Full Documentation**: See `README.md`
- **Installation Guide**: See `INSTALL.md`
- **Testing Guide**: See `TESTING_GUIDE.md`
- **Changelog**: See `CHANGELOG.md`
- **Upgrade Guide**: See `UPGRADE.md`

---

## 📞 Support

**Email**: support@snifx.example  
**Website**: https://snifx.example

---

## ✅ Success Checklist

After installation, verify:

- ☐ Module appears in Apps list
- ☐ Officer group exists in user settings
- ☐ Officer assignments menu visible
- ☐ **Public holiday creation works (CRITICAL)**
- ☐ Approve buttons visible to officers
- ☐ Activities created for officers
- ☐ Department hierarchy filtering works
- ☐ Officers cannot modify projects
- ☐ Officers cannot approve own requests

---

**Version**: 2.3.0  
**Release Date**: 2024-11-20  
**Status**: STABLE - Production Ready ✅
