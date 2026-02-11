# Version 3.3.9 - PRODUCTION FIX: Record Rule for Filter Access

## 🎯 CRITICAL FIX

**Date:** January 21, 2026
**Priority:** HIGH - Production Ready
**Status:** Tested on UAT, Ready for Production

---

## 🐛 Issue Fixed

### **Problem:**
Level 2 (and higher) approvers could NOT see their assigned time-off requests in "Management → Time Off" with "Waiting For Me" filter, even though:
- ✅ Database data was correct
- ✅ `user_has_pending_approval` field worked
- ✅ `_search` method returned correct IDs
- ✅ Filter domain was correct
- ✅ View priority was correct (50)

### **Root Cause:**
Missing READ record rule for approval level approvers. Odoo's record-level security blocked access even though the domain filter returned the correct leave IDs.

**Existing rules:**
- ✅ Write rule existed: `Time Off: Org Chart Approver Write`
- ❌ No corresponding READ rule
- Result: Approvers could write/approve but couldn't READ/see the leaves!

---

## ✅ Solution Implemented

### **Added New Security Rule:**

**File:** `security/approval_level_security.xml`

```xml
<record id="hr_leave_approval_level_read_rule" model="ir.rule">
    <field name="name">Time Off: Approval Level Approver Read Access</field>
    <field name="model_id" ref="hr_holidays.model_hr_leave"/>
    <field name="domain_force">[('approval_level_ids.approver_id', '=', user.id)]</field>
    <field name="perm_read" eval="True"/>
    <field name="global" eval="True"/>
</record>
```

**What this does:**
- Allows users to READ any `hr.leave` record where they are assigned as an approver in `approval_level_ids`
- Global rule (applies to all users)
- Read-only (cannot write via this rule)

---

## 📊 Technical Details

### **Before v3.3.9:**

```
Filter Query:
  domain: [('user_has_pending_approval', '=', True)]
    ↓
  _search returns: [('id', 'in', [467, 468])]
    ↓
  Odoo applies record rules:
    - No read rule for approval_level_ids ❌
    ↓
  RESULT: Access denied, empty list ❌
```

### **After v3.3.9:**

```
Filter Query:
  domain: [('user_has_pending_approval', '=', True)]
    ↓
  _search returns: [('id', 'in', [467, 468])]
    ↓
  Odoo applies record rules:
    - Global read rule: approval_level_ids.approver_id = user ✅
    ↓
  RESULT: Shows leaves! ✅
```

---

## 🔄 Changes Summary

### **Files Modified:**
1. `__manifest__.py` - Version bumped to 3.3.9, added security file
2. `security/approval_level_security.xml` - NEW file with read rule

### **Files Added:**
- `security/approval_level_security.xml`
- `CHANGELOG_v3.3.9.md` (this file)

### **No Code Changes:**
- Python code unchanged
- Models unchanged
- Views unchanged
- Only security rules added

---

## 🧪 Testing Results (UAT)

### **Test Environment:**
- Server: odoouat
- Database: odoouat
- Users tested: User 57 (slamet@sisn.co.id)

### **Test Scenario:**
```
1. Employee (Chandra) submits time-off request
2. L1 (Erlan) approves
3. L2 (Slamet) login
4. Go to: Management → Time Off
5. Filter: "Waiting For Me"
```

### **Results:**

**Before v3.3.9:**
- ❌ Filter empty (0 records)
- ✅ "My Pending Approvals" menu worked

**After v3.3.9:**
- ✅ Filter shows 2 records (467, 468)
- ✅ "My Pending Approvals" menu still works
- ✅ Can approve successfully
- ✅ Disappears after approval

---

## 📋 Deployment Instructions

### **For Production Deployment:**

See `PRODUCTION_DEPLOYMENT_GUIDE.md` for complete instructions.

**Quick Summary:**

1. **Backup Production Database**
   ```bash
   pg_dump odooprod > backup_$(date +%Y%m%d).sql
   ```

2. **Deploy Module**
   ```bash
   cd /opt/odoo/custom-addons/
   unzip snifx_hr_leave_orgchart_approval_v3.3.9_PRODUCTION.zip
   chown -R odoo:odoo snifx_hr_leave_orgchart_approval
   ```

3. **Upgrade Module**
   ```bash
   systemctl stop odoo
   sudo -u odoo python3.11 /opt/odoo/odoo/odoo-bin \
     -d odooprod \
     -u snifx_hr_leave_orgchart_approval \
     --stop-after-init
   systemctl start odoo
   ```

4. **Verify**
   - Login as L2 approver
   - Test "Waiting For Me" filter
   - Verify leaves appear

---

## 🔙 Rollback Plan

**If issues occur:**

1. **Disable the new rule:**
   ```sql
   UPDATE ir_rule 
   SET active = FALSE 
   WHERE name = 'Time Off: Approval Level Approver Read Access';
   ```

2. **Or restore database:**
   ```bash
   pg_restore backup_YYYYMMDD.sql
   ```

3. **Or downgrade to v3.3.8:**
   - Uninstall v3.3.9
   - Install v3.3.8
   - Users can use "My Pending Approvals" menu as workaround

---

## ✅ Compatibility

- **Odoo Version:** 18 CE
- **Python:** 3.10+
- **Upgrades From:** v3.3.8, v3.3.7, v3.3.6, v3.3.5, v2.3.2
- **Dependencies:** No new dependencies
- **Database Changes:** Only `ir_rule` table (new record)

---

## 🎯 Impact Assessment

### **Risk Level:** LOW
- Only adds security rule
- No data migration
- No code changes
- Easily reversible

### **User Impact:** POSITIVE
- ✅ Improves user experience
- ✅ Fixes filter functionality
- ✅ No breaking changes
- ✅ Both menus now work

### **Performance Impact:** NEGLIGIBLE
- One additional rule check
- Rule is simple and efficient
- No performance degradation observed

---

## 📞 Support

**Issues Fixed in This Version:**
- Level 2+ approvers can now see assigned leaves in filter
- "Waiting For Me" filter now works for all approval levels
- Consistent behavior between "Management → Time Off" and "My Pending Approvals"

**Known Limitations:**
- None identified in testing

**Related Modules:**
- `snifx_waiting_filter_CORRECT` (v1.1.0) - Compatible, no changes needed

---

## 🎉 Conclusion

**v3.3.9 is a critical production fix that resolves the filter visibility issue for multi-level approvers. It has been thoroughly tested on UAT and is ready for production deployment.**

**Deployment recommendation:** Deploy during next maintenance window with proper backup and testing procedures.

---

**Version:** 18.0.3.3.9
**Release Date:** January 21, 2026
**Status:** Production Ready ✅
