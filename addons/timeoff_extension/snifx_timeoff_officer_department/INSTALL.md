# Installation Guide - Snifx Time Off Officer Balance v2.0.0

## 📋 Pre-Installation Checklist

Before installing, ensure you have:

- [x] Odoo 18.0 Community Edition installed and running
- [x] PostgreSQL 12+ database
- [x] Administrative access to Odoo
- [x] Backup of your database (highly recommended)
- [x] `hr_holidays` module installed and configured
- [x] At least one employee record with a department

---

## 🚀 Installation Steps

### Step 1: Download and Extract Module

1. Download the module package: `snifx_timeoff_officer_department-18.0.2.0.0.zip`
2. Extract to your Odoo addons directory:
   ```bash
   cd /opt/odoo/addons/
   unzip snifx_timeoff_officer_department-18.0.2.0.0.zip
   ```

3. Verify extraction:
   ```bash
   ls -la snifx_timeoff_officer_department/
   ```

   You should see:
   ```
   __init__.py
   __manifest__.py
   models/
   security/
   views/
   data/
   static/
   README.md
   ```

### Step 2: Set Correct Permissions

```bash
sudo chown -R odoo:odoo /opt/odoo/addons/snifx_timeoff_officer_department
sudo chmod -R 755 /opt/odoo/addons/snifx_timeoff_officer_department
```

### Step 3: Update Odoo Apps List

1. Restart Odoo service:
   ```bash
   sudo systemctl restart odoo
   # or
   sudo service odoo restart
   ```

2. Login to Odoo as Administrator

3. Go to **Apps** menu

4. Remove the "Apps" filter (click the ✖ on the search bar)

5. Click **Update Apps List**

6. Confirm the update

### Step 4: Install the Module

1. In Apps menu, search for: `Snifx Time Off Officer Balance`

2. You should see:
   ```
   Snifx Time Off Officer Balance - Enhanced
   Version: 18.0.2.0.0
   Author: Snifx Studio
   ```

3. Click **Install** button

4. Wait for installation to complete (should take 5-10 seconds)

5. Verify installation success (no error messages)

### Step 5: Verify Installation

#### Check Group Creation

1. Go to **Settings → Users & Companies → Groups**
2. Search for: `Officer with Balance`
3. You should see:
   ```
   Name: Officer with Balance (Enhanced)
   Category: Time Off
   Implied Groups: Officer: Manage all requests
   ```

#### Check Menu Access

1. Go to **Time Off** menu
2. You should see:
   - Time Off (standard)
   - My Team (standard)
   - **Reporting → Balance** (now visible)
   - **Configuration → Officer Assignments** (new menu)
   - **Configuration → Public Holidays** (now visible)

#### Check Database Tables

```sql
-- Connect to PostgreSQL
psql -U odoo -d your_database

-- Check if new table exists
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'hr_timeoff_officer_assignment';

-- Should return: hr_timeoff_officer_assignment
```

---

## 👥 Post-Installation Configuration

### Create First Officer Assignment

#### Example: Assign user "Andri" to manage "Technical" department

1. Go to **Settings → Users & Companies → Users**

2. Open user: **Andri Puji Astuti**

3. In **Access Rights** tab, enable:
   - ✅ Time Off / **Officer with Balance (Enhanced)**

4. Go to **Officer Assignments** tab

5. Click **Add a line**:
   - Department: **Technical**
   - Date From: (leave empty or set start date)
   - Date To: (leave empty for no expiry)
   - Active: ✅ (checked)

6. Click **Save**

7. Verify assignment created:
   ```
   Display Name: Andri Puji Astuti → Technical
   ```

### Test Officer Access

1. **Logout** from Administrator

2. **Login** as the officer user (Andri)

3. Verify access:

   **✅ Can Access:**
   - Time Off → My Team → Time Off Requests (see team requests)
   - Time Off → Reporting → Balance (see balance for Technical tree)
   - Employees (can see all, limited tabs)
   - Time Off → Configuration → Public Holidays

   **❌ Cannot Access:**
   - Time Off → Configuration → Officer Assignments (HR Manager only)
   - Employee → Private Information tab (hidden)

4. Test Approval:
   - Create a test leave request for an employee in Technical department
   - As Andri, go to Time Off → My Team → Time Off Requests
   - Open the request
   - Click **Approve** button
   - Should work without errors

5. Test Self-Approval Prevention:
   - As Andri, create a leave request for yourself
   - Try to approve it
   - Should show error: "You cannot approve your own leave request"

---

## 🔧 Advanced Configuration

### Multi-Company Setup

If you have multiple companies:

1. Ensure each user has correct company access:
   - Settings → Users → User Form
   - Allowed Companies: Select companies

2. Create company-specific assignments:
   - Each assignment is tied to one company
   - Officers only see data from their assigned companies

### Department Hierarchy Verification

Before creating assignments, verify your department tree:

1. Go to **Employees → Configuration → Departments**

2. Check hierarchy view:
   ```
   Technical
   ├── IT Infrastructure
   │   ├── IT Infrastructure Delivery
   │   └── IT Infrastructure Support
   ├── IT Service Management
   │   ├── IT Service Delivery
   │   └── IT Service Support
   ├── Maintenance
   ├── Project Management
   └── Technical Admin
   ```

3. Ensure parent-child relationships are correct

### Date-Based Assignments

For temporary assignments:

1. Create assignment with dates:
   - Date From: 2024-01-01
   - Date To: 2024-12-31

2. Officer will have access only during this period

3. System automatically checks dates on every operation

---

## 🐛 Common Installation Issues

### Issue 1: Module Not Found in Apps List

**Symptoms:**
- Module doesn't appear after updating apps list

**Solutions:**

1. Check addons path in Odoo config:
   ```bash
   grep addons_path /etc/odoo/odoo.conf
   ```

2. Verify module is in the correct directory

3. Check file permissions:
   ```bash
   ls -la /opt/odoo/addons/snifx_timeoff_officer_department/
   ```

4. Restart Odoo and try again

### Issue 2: Installation Error - Missing Dependencies

**Symptoms:**
```
Error: Module 'hr_holidays' not found
```

**Solutions:**

1. Install required modules first:
   - Go to Apps
   - Search and install: "Time Off"
   - Search and install: "Employees"

2. Then install this module

### Issue 3: Access Rights Error After Installation

**Symptoms:**
```
AccessError: You don't have access to this document
```

**Solutions:**

1. Logout and login again (to refresh permissions)

2. Clear browser cache

3. Verify group assignment:
   - Settings → Users → User Form
   - Access Rights → Time Off → Officer with Balance (Enhanced)

### Issue 4: Database Table Already Exists

**Symptoms:**
```
ERROR: relation "hr_timeoff_officer_assignment" already exists
```

**Solutions:**

This means you're upgrading from an older version or reinstalling.

1. Either:
   - Uninstall old version first, then install new
   - Or use upgrade procedure (see UPGRADE.md)

2. If you want clean install:
   ```sql
   -- Backup data first!
   DROP TABLE IF EXISTS hr_timeoff_officer_assignment CASCADE;
   ```

---

## ✅ Installation Verification Checklist

After installation, verify:

- [x] Module appears in Apps list as installed
- [x] New group "Officer with Balance (Enhanced)" exists
- [x] Menu "Officer Assignments" visible under Time Off → Configuration
- [x] Can create officer assignments
- [x] Officer can see assigned department's leave requests
- [x] Officer can approve leave requests (except own)
- [x] Officer can view balance reports
- [x] Officer can create public holidays
- [x] Officer can view all employees (limited tabs)
- [x] Private Information tab hidden for officers
- [x] No error messages in Odoo logs

---

## 📊 Performance Considerations

### For Large Databases

If you have 1000+ employees or 100+ departments:

1. **Database Indexes** (automatically created):
   - `idx_assignment_user` on `user_id`
   - `idx_assignment_dept` on `department_id`

2. **Recommended PostgreSQL Settings**:
   ```sql
   -- Increase work_mem for better query performance
   ALTER SYSTEM SET work_mem = '16MB';
   
   -- Reload configuration
   SELECT pg_reload_conf();
   ```

3. **Monitor Performance**:
   ```bash
   # Check slow queries
   tail -f /var/log/postgresql/postgresql-14-main.log | grep "duration:"
   ```

---

## 🔄 Next Steps

After successful installation:

1. ✅ Read [README.md](./README.md) for usage guide
2. ✅ Create officer assignments for your team
3. ✅ Train officers on how to use the system
4. ✅ Test approval workflows
5. ✅ Monitor system for first few days

---

## 📞 Support

If you encounter issues during installation:

1. Check Odoo logs:
   ```bash
   tail -f /var/log/odoo/odoo-server.log
   ```

2. Review this guide again

3. Contact support:
   - Email: support@snifx.example
   - Include: Odoo version, error messages, log files

---

**Installation Complete! Ready to use! 🎉**
