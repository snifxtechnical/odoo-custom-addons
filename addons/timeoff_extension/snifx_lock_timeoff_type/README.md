# Lock Time Off Type After Submit

**Version:** 18.0.1.0.0  
**Author:** Snifx Technical  
**Category:** Human Resources / Time Off

---

## 🎯 Problem Solved

### **The Issue:**

When users submit time off requests, they can later change the time off type (e.g., from Sick Leave to Annual Leave). This causes:

❌ Approval chain becomes invalid  
❌ Wrong workflow is followed  
❌ Leave balances become incorrect  
❌ Security risk - users can bypass approval rules  

### **Example Scenario Without This Module:**

```
1. User submits "Sick Leave" for 3 days
   → Approval chain: Manager only (sick leave policy)
   
2. After submission, user changes to "Annual Leave"
   → Approval chain: Still manager only (outdated!)
   → SHOULD BE: Manager + Director (annual leave policy)
   
3. Result: Wrong approval flow! ❌
```

---

## ✅ Solution

This module **LOCKS the time off type field after submission**.

### **How It Works:**

```
Draft State:
├─ Time off type: ✓ Required
├─ Time off type: ✓ Editable
└─ User must select before saving

After Submit (Confirm/Validate):
├─ Time off type: ✓ Readonly (locked)
├─ Time off type: ✗ Cannot be changed
└─ Clear error if change attempted

Refused State:
├─ Time off type: ✓ Editable again
└─ User can correct and resubmit
```

---

## 🚀 Features

### **1. Required Field**
- Time off type MUST be selected before saving
- Cannot create leave request without type
- Forces users to think before submitting

### **2. Readonly After Submit**
- Field becomes locked after submission
- Visual indicator shows field is locked
- Prevents accidental changes

### **3. Validation**
- Backend validation prevents changes via code
- Security: Cannot bypass via API or import
- Clear error message to users

### **4. User-Friendly Messages**
- Info box in draft: "Select carefully, cannot change later"
- Warning box after submit: "Locked to maintain workflow integrity"
- Clear error if change attempted

---

## 📦 Installation

```bash
# 1. Extract module
cd /opt/odoo/custom-addons/
unzip snifx_lock_timeoff_type.zip

# 2. Set permissions
chown -R odoo:odoo snifx_lock_timeoff_type

# 3. Stop Odoo
systemctl stop odoo

# 4. Install module
sudo -u odoo python3.11 /opt/odoo/odoo/odoo-bin \
  -d YOUR_DATABASE \
  -i snifx_lock_timeoff_type \
  --stop-after-init

# 5. Start Odoo
systemctl start odoo

# 6. Clear browser cache
# Press Ctrl+Shift+R
```

---

## 🎯 Usage

### **Creating Time Off (Draft State):**

1. Go to **Time Off → My Time Off → New**
2. **Select Time Off Type** (required field - marked with *)
3. Fill other fields (dates, reason, etc.)
4. Click **Save**

✅ Time off type can still be changed while in draft

---

### **After Submission:**

1. Click **Submit to Manager/Submit**
2. Time off type field becomes **readonly** (locked icon)
3. Info message: "Time off type is locked"

❌ Cannot change time off type anymore

---

### **If Wrong Type Selected:**

**Option 1: Cancel and Recreate** (Recommended)
1. Click **Cancel**
2. Delete the request
3. Create new request with correct type

**Option 2: Refuse and Edit** (If already approved at some level)
1. Ask approver to **Refuse** the request
2. Request returns to draft state
3. Edit time off type
4. Resubmit

---

## 📊 Technical Details

### **Modified Fields:**

```python
holiday_status_id = fields.Many2one(
    required=True,  # Must be selected
    readonly=True,  # Default readonly
    states={
        'draft': [('readonly', False)],   # Editable in draft
        'refuse': [('readonly', False)],  # Editable if refused
    },
)
```

### **Validation:**

```python
@api.constrains('holiday_status_id', 'state')
def _check_timeoff_type_change_after_submit(self):
    # Checks if type changed after submission
    # Raises ValidationError if yes
    # Logs attempt for security audit
```

### **States Affected:**

| State | Can Edit Type? | Notes |
|-------|---------------|-------|
| **draft** | ✅ Yes | Normal editing |
| **confirm** | ❌ No | Locked |
| **validate** | ❌ No | Locked |
| **validate1** | ❌ No | Locked |
| **refuse** | ✅ Yes | Allow correction |

---

## ⚠️ Important Notes

### **1. Existing Leaves**

Existing time off requests are NOT affected:
- Leaves created before module installation: Still work
- No data migration needed
- Lock only applies to NEW changes

### **2. Administrator Override**

**Question:** Can admin bypass the lock?

**Answer:** NO! Security validation applies to everyone, including:
- ❌ Administrators
- ❌ System users
- ❌ API calls
- ❌ Data imports

**Why:** To maintain data integrity and audit trail.

If admin really needs to change (very rare):
1. Uninstall this module temporarily
2. Make change
3. Reinstall module

### **3. Integration with Other Modules**

Compatible with:
- ✅ snifx_hr_leave_orgchart_approval
- ✅ snifx_timeoff_alternate_approval
- ✅ snifx_timeoff_officer_department
- ✅ Any custom approval modules

No conflicts expected!

---

## 🎯 Benefits

### **For HR/Management:**

```
✅ Approval workflow integrity maintained
✅ Correct policies always followed
✅ Accurate leave balance tracking
✅ Prevention of abuse/manipulation
✅ Clear audit trail
✅ Compliance with company policies
```

### **For Users:**

```
✅ Clear indication of what can/cannot be changed
✅ Prevents accidental mistakes
✅ Forces careful selection
✅ Easy to understand error messages
```

### **For IT/Developers:**

```
✅ Clean implementation
✅ No modification to core Odoo
✅ Easy to maintain
✅ Well documented
✅ Logging for security audit
```

---

## 🔍 Testing Checklist

After installation, test these scenarios:

```
☐ Create leave in draft → Can select type
☐ Change type in draft → Works
☐ Submit leave → Type becomes locked
☐ Try to change type after submit → Error message
☐ Cancel leave → Can edit again
☐ Refuse leave → Can edit type
☐ Edit type in refused → Resubmit works
☐ Approval workflow → Correct chain used
```

---

## 🆘 Troubleshooting

### **Issue: Field not locked after submit**

**Check:**
```bash
# 1. Module installed?
sudo -u odoo psql DATABASE -c "SELECT name, state FROM ir_module_module WHERE name = 'snifx_lock_timeoff_type';"

# Should show: installed

# 2. Clear browser cache
# Ctrl+Shift+R

# 3. Check logs
tail -50 /var/log/odoo/odoo.log | grep lock
```

---

### **Issue: Can still change type**

**Possible causes:**
1. Using old browser tab (before module install)
2. Cache not cleared
3. Custom module overriding field

**Solution:**
- Close all Odoo tabs
- Clear cache (Ctrl+Shift+R)
- Restart Odoo
- Try again in new tab

---

### **Issue: Error message not clear**

**Current error message includes:**
- ✅ Current type
- ✅ Attempted type
- ✅ Reason why blocked
- ✅ Steps to resolve

If you want different message, edit:
`models/hr_leave.py` → `_check_timeoff_type_change_after_submit()`

---

## 📝 Changelog

### **v1.0.0 (2026-01-29)**

Initial release:
- ✅ Lock time off type after submission
- ✅ Required field validation
- ✅ Backend security validation
- ✅ User-friendly messages
- ✅ UI indicators (info/warning boxes)
- ✅ Logging for security audit
- ✅ Complete documentation

---

## 👥 Support

**Author:** Snifx Technical  
**Website:** https://snifx.studio  
**Version:** 18.0.1.0.0  
**License:** LGPL-3

---

## ✅ Summary

**This module SOLVES a real security and workflow problem by:**

```
✓ Locking time off type after submission
✓ Maintaining approval chain integrity
✓ Preventing workflow bypass
✓ Ensuring accurate leave balances
✓ Providing clear user feedback
✓ Security for all users (including admin)
```

**Install this module to protect your time off workflow!** 🛡️
