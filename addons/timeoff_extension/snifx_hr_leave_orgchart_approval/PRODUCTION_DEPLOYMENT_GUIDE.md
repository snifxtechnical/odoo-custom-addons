# Production Deployment Guide - v3.3.9

## 🎯 Overview

This guide provides step-by-step instructions for deploying v3.3.9 to production.

**What's New in v3.3.9:**
- Adds record rule for approval level read access
- Fixes "Waiting For Me" filter for L2+ approvers
- No code changes, only security rule addition

---

## ⚠️ Pre-Deployment Checklist

```
□ UAT testing completed successfully
□ Stakeholder approval obtained
□ Maintenance window scheduled
□ Users notified of planned downtime
□ Backup plan prepared
□ Rollback plan documented
□ Deployment team briefed
□ Production access verified
```

---

## 📅 Deployment Schedule

**Recommended Timing:**
- Off-peak hours (e.g., Saturday night, Sunday morning)
- Low transaction period
- When support team is available

**Estimated Duration:**
- Module upgrade: 5-10 minutes
- Testing: 10-15 minutes
- Total downtime: 15-25 minutes

---

## 🔐 Prerequisites

### **Access Requirements:**
- Root or sudo access to production server
- PostgreSQL superuser access
- Odoo file system access
- Ability to stop/start Odoo service

### **Tools Needed:**
- SSH client
- SCP/SFTP for file transfer
- Database backup storage (minimum 2GB free)
- Module package: `snifx_hr_leave_orgchart_approval_v3.3.9_PRODUCTION.zip`

---

## 📦 Deployment Steps

### **STEP 1: Pre-Deployment Backup** ⭐⭐⭐

**CRITICAL: Always backup before any changes!**

```bash
# 1. Create backup directory
sudo mkdir -p /backup/$(date +%Y%m%d)
cd /backup/$(date +%Y%m%d)

# 2. Backup PostgreSQL database
sudo -u postgres pg_dump odooprod > odooprod_backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup created
ls -lh odooprod_backup_*.sql
# Should show file size (e.g., 500M)

# 3. Backup current module files
cd /opt/odoo/custom-addons/
sudo tar -czf /backup/$(date +%Y%m%d)/snifx_hr_leave_orgchart_approval_backup.tar.gz \
  snifx_hr_leave_orgchart_approval/

# Verify module backup
ls -lh /backup/$(date +%Y%m%d)/snifx_hr_leave_orgchart_approval_backup.tar.gz

# 4. Document current state
sudo -u odoo psql odooprod -c \
  "SELECT name, latest_version FROM ir_module_module \
   WHERE name = 'snifx_hr_leave_orgchart_approval';" \
  > /backup/$(date +%Y%m%d)/current_version.txt

cat /backup/$(date +%Y%m%d)/current_version.txt
```

**Backup Verification:**
```bash
# Verify backup is valid
sudo -u postgres pg_restore -l odooprod_backup_*.sql | head -20
# Should show table list without errors
```

---

### **STEP 2: Upload New Module** ⭐⭐

```bash
# 1. Upload module package to server
# (Use scp, sftp, or your preferred method)
# Example with scp:
# scp snifx_hr_leave_orgchart_approval_v3.3.9_PRODUCTION.zip user@prodserver:/tmp/

# 2. Verify upload
ls -lh /tmp/snifx_hr_leave_orgchart_approval_v3.3.9_PRODUCTION.zip

# 3. Extract to custom-addons
cd /opt/odoo/custom-addons/

# Backup old version (again, just to be safe)
sudo mv snifx_hr_leave_orgchart_approval \
  snifx_hr_leave_orgchart_approval.old_$(date +%Y%m%d)

# Extract new version
sudo unzip /tmp/snifx_hr_leave_orgchart_approval_v3.3.9_PRODUCTION.zip

# Verify extraction
ls -la snifx_hr_leave_orgchart_approval/
# Should show all files including new security/approval_level_security.xml

# Set correct ownership
sudo chown -R odoo:odoo snifx_hr_leave_orgchart_approval

# Verify version
grep version snifx_hr_leave_orgchart_approval/__manifest__.py
# Should show: 'version': '18.0.3.3.9',
```

---

### **STEP 3: Stop Odoo Service** ⭐⭐⭐

```bash
# 1. Check current status
sudo systemctl status odoo

# 2. Stop Odoo gracefully
sudo systemctl stop odoo

# 3. Verify stopped
sudo systemctl status odoo
# Should show: inactive (dead)

# 4. Verify no processes running
ps aux | grep odoo
# Should show only grep process
```

---

### **STEP 4: Upgrade Module** ⭐⭐⭐

```bash
# Find correct Python version
# (Check which Python Odoo uses)
which python3.10 python3.11 python3.12

# Upgrade module (use correct Python version)
sudo -u odoo python3.11 /opt/odoo/odoo/odoo-bin \
  -d odooprod \
  -u snifx_hr_leave_orgchart_approval \
  --stop-after-init \
  --log-level=info \
  2>&1 | tee /tmp/upgrade_v339_$(date +%Y%m%d_%H%M%S).log

# Check last 50 lines of log for errors
tail -50 /tmp/upgrade_v339_*.log

# Look for these SUCCESS indicators:
# - "module snifx_hr_leave_orgchart_approval: loading..."
# - "module snifx_hr_leave_orgchart_approval: migration..."
# - "Modules loaded"
# - No "ERROR" or "CRITICAL" messages

# Check if security rule was created
sudo -u odoo psql odooprod -c \
  "SELECT name, perm_read, global FROM ir_rule \
   WHERE name = 'Time Off: Approval Level Approver Read Access';"

# Expected output:
#                          name                           | perm_read | global
# --------------------------------------------------------+-----------+--------
#  Time Off: Approval Level Approver Read Access          | t         | t
```

---

### **STEP 5: Start Odoo Service** ⭐⭐

```bash
# 1. Start Odoo
sudo systemctl start odoo

# 2. Wait for startup (usually 10-30 seconds)
sleep 15

# 3. Check status
sudo systemctl status odoo
# Should show: active (running)

# 4. Monitor logs for errors
sudo journalctl -u odoo -n 100 --no-pager

# Look for:
# ✅ "odoo.service.server: HTTP service (werkzeug) running on..."
# ✅ "odoo.modules.loading: Modules loaded"
# ❌ No ERROR or CRITICAL messages

# 5. Check if Odoo is responding
curl -I http://localhost:8069 | head -5
# Should show: HTTP/1.1 303 See Other
```

---

### **STEP 6: Verification & Testing** ⭐⭐⭐

**Database Verification:**

```bash
# 1. Check module version
sudo -u odoo psql odooprod -c \
  "SELECT name, state, latest_version FROM ir_module_module \
   WHERE name = 'snifx_hr_leave_orgchart_approval';"

# Expected:
#               name               |   state   | latest_version
# ----------------------------------+-----------+----------------
#  snifx_hr_leave_orgchart_approval | installed | 18.0.3.3.9

# 2. Check security rule exists
sudo -u odoo psql odooprod -c \
  "SELECT id, name, perm_read, global, active FROM ir_rule \
   WHERE name LIKE '%Approval Level Approver Read%';"

# Should show 1 row with perm_read = t, global = t, active = t

# 3. Check view priority (should still be 50)
sudo -u odoo psql odooprod -c \
  "SELECT name, priority FROM ir_ui_view \
   WHERE name = 'hr.leave.filter.modify.waiting';"

# Expected: priority = 50
```

**UI Testing:**

```bash
# Create test checklist
cat > /tmp/production_test_checklist.txt << 'EOF'
PRODUCTION TESTING CHECKLIST - v3.3.9

Test User: [L2 approver username]
Test Time: $(date)

□ 1. Login Successful
   URL: https://[your-domain]
   User: [L2 approver]
   Result: □ Success  □ Failed

□ 2. Navigate to Time Off Management
   Menu: Management → Time Off
   Result: □ Success  □ Failed

□ 3. Filter "Waiting For Me" Active
   Filter chip visible: □ Yes  □ No
   Result: □ Success  □ Failed

□ 4. Verify Leaves Visible
   Expected count: [X] leaves
   Actual count: ___ leaves
   Leave IDs visible: _______________
   Result: □ Success  □ Failed

□ 5. Open Leave Request
   Can open form: □ Yes  □ No
   Shows correct data: □ Yes  □ No
   Result: □ Success  □ Failed

□ 6. Test Approval Action
   "Approve" button visible: □ Yes  □ No
   Click approve: □ Success  □ Failed
   Leave disappears from filter: □ Yes  □ No
   Result: □ Success  □ Failed

□ 7. Test "My Pending Approvals" Menu
   Menu: Time Off → My Pending Approvals
   Shows leaves: □ Yes  □ No
   Count matches: □ Yes  □ No
   Result: □ Success  □ Failed

□ 8. Test as Different User
   Login as L1 approver: ___________
   Filter works: □ Yes  □ No
   Result: □ Success  □ Failed

OVERALL RESULT: □ ALL PASSED  □ ISSUES FOUND

Issues/Notes:
_____________________________________________
_____________________________________________

Tested by: ___________
Date/Time: ___________
EOF

cat /tmp/production_test_checklist.txt
```

**Perform Manual Testing:**

1. Login as L2 approver
2. Go to: Management → Time Off
3. Verify filter shows assigned leaves
4. Test approval functionality
5. Verify leave disappears after approval
6. Test "My Pending Approvals" menu
7. Test as L1 approver (if available)

---

### **STEP 7: Post-Deployment Monitoring** ⭐⭐

```bash
# 1. Monitor logs for 30 minutes
sudo journalctl -u odoo -f

# Look for:
# ❌ Errors or exceptions
# ❌ Performance issues
# ❌ Database errors
# ✅ Normal user activity

# 2. Check system resources
top
# Monitor CPU and memory usage

# 3. Check database connections
sudo -u odoo psql odooprod -c \
  "SELECT count(*) as active_connections FROM pg_stat_activity \
   WHERE datname = 'odooprod';"

# Normal: 5-20 connections

# 4. Test with multiple users
# Have 2-3 users test simultaneously

# 5. Monitor error logs
sudo tail -f /var/log/odoo/odoo-server.log
# (path may vary based on your setup)
```

---

## 🔙 Rollback Procedures

**If issues occur, follow these steps:**

### **Option 1: Disable Security Rule** (Quick Fix)

```bash
# Disable the new rule without full rollback
sudo -u odoo psql odooprod -c \
  "UPDATE ir_rule SET active = FALSE \
   WHERE name = 'Time Off: Approval Level Approver Read Access';"

# Restart Odoo
sudo systemctl restart odoo

# This reverts to v3.3.8 behavior
# Users can use "My Pending Approvals" menu as workaround
```

---

### **Option 2: Full Module Rollback**

```bash
# 1. Stop Odoo
sudo systemctl stop odoo

# 2. Restore old module files
cd /opt/odoo/custom-addons/
sudo rm -rf snifx_hr_leave_orgchart_approval
sudo mv snifx_hr_leave_orgchart_approval.old_$(date +%Y%m%d) \
  snifx_hr_leave_orgchart_approval

# OR extract from backup
cd /opt/odoo/custom-addons/
sudo rm -rf snifx_hr_leave_orgchart_approval
sudo tar -xzf /backup/$(date +%Y%m%d)/snifx_hr_leave_orgchart_approval_backup.tar.gz

# 3. Downgrade module
sudo -u odoo python3.11 /opt/odoo/odoo/odoo-bin \
  -d odooprod \
  -u snifx_hr_leave_orgchart_approval \
  --stop-after-init

# 4. Remove the security rule
sudo -u odoo psql odooprod -c \
  "DELETE FROM ir_rule \
   WHERE name = 'Time Off: Approval Level Approver Read Access';"

# 5. Start Odoo
sudo systemctl start odoo

# 6. Verify rollback
sudo -u odoo psql odooprod -c \
  "SELECT name, latest_version FROM ir_module_module \
   WHERE name = 'snifx_hr_leave_orgchart_approval';"
# Should show: 18.0.3.3.8
```

---

### **Option 3: Database Restore** (Emergency)

```bash
# ONLY if module rollback fails

# 1. Stop Odoo
sudo systemctl stop odoo

# 2. Restore database
cd /backup/$(date +%Y%m%d)

sudo -u postgres psql -c "DROP DATABASE IF EXISTS odooprod_temp;"
sudo -u postgres psql -c "CREATE DATABASE odooprod_temp;"
sudo -u postgres psql odooprod_temp < odooprod_backup_*.sql

# 3. Verify restore
sudo -u postgres psql odooprod_temp -c \
  "SELECT count(*) FROM hr_leave;"

# 4. If verified OK, swap databases
sudo -u postgres psql -c "ALTER DATABASE odooprod RENAME TO odooprod_broken;"
sudo -u postgres psql -c "ALTER DATABASE odooprod_temp RENAME TO odooprod;"

# 5. Start Odoo
sudo systemctl start odoo
```

---

## 📊 Success Criteria

**Deployment is successful if:**

```
✅ Module upgraded to v3.3.9 without errors
✅ Security rule created in database
✅ Odoo service running normally
✅ L2 approvers can see assigned leaves in filter
✅ "Waiting For Me" filter works for all levels
✅ "My Pending Approvals" menu still works
✅ Approval functionality works correctly
✅ No errors in logs
✅ System performance normal
✅ Users can work normally
```

---

## 📞 Support & Troubleshooting

### **Common Issues:**

**Issue 1: Module upgrade fails**
```
Error: "Module not found"
Solution: Verify folder name is exactly "snifx_hr_leave_orgchart_approval"
```

**Issue 2: Security rule not created**
```
Solution: Check upgrade log for XML parsing errors
Verify: security/approval_level_security.xml exists
```

**Issue 3: Filter still empty after upgrade**
```
Check: Security rule exists and active = TRUE
Check: User has correct groups
Check: Browser cache cleared
Try: Different browser or incognito mode
```

**Issue 4: Performance degradation**
```
Check: Database connections (should be < 50)
Check: CPU usage (should be < 80%)
Monitor: Query execution times
Consider: Database vacuum/analyze
```

---

## 📋 Post-Deployment Tasks

```
□ Document deployment completion
□ Notify users of completion
□ Update internal documentation
□ Keep backup for 7 days minimum
□ Monitor system for 24-48 hours
□ Schedule follow-up review
□ Archive deployment logs
□ Update version tracking
```

---

## 📄 Documentation & Logs

**Files to Archive:**

```
/backup/YYYYMMDD/odooprod_backup_*.sql           - Database backup
/backup/YYYYMMDD/snifx_hr_leave_*.tar.gz         - Module backup
/tmp/upgrade_v339_*.log                          - Upgrade log
/tmp/production_test_checklist.txt               - Test results
/var/log/odoo/odoo-server.log                    - Odoo logs (if exists)
```

**Keep for:** Minimum 30 days, preferably 90 days

---

## ✅ Deployment Completion

**Final Checklist:**

```
□ Deployment completed successfully
□ All tests passed
□ Users notified
□ Documentation updated
□ Backups archived
□ Monitoring in place
□ No critical issues
□ Support team briefed
```

---

**Deployment Date:** ___________
**Deployed By:** ___________
**Verified By:** ___________
**Status:** □ Success  □ Rolled Back  □ Issues

**Notes:**
_____________________________________________
_____________________________________________

---

## 🎉 Conclusion

This deployment adds critical read access for approval level approvers, resolving the filter visibility issue. The deployment is low-risk with comprehensive backup and rollback procedures.

**For questions or issues during deployment, contact:** ___________

---

**Version:** 18.0.3.3.9
**Document Version:** 1.0
**Last Updated:** January 21, 2026
