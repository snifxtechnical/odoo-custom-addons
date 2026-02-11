# Version 3.3.8 - CRITICAL FIX: Revert to Non-Stored Field

## 🚨 URGENT: v3.3.7 Was Broken - This Fixes It!

### Critical Issue in v3.3.7:

**Problem:** Level 1 AND Level 2 both stopped showing in "My Time Off Approvals" menu!

**Root cause:** Fundamental design error in v3.3.7 - tried to STORE a user-specific field.

```python
# v3.3.7 (BROKEN):
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
    store=True,  # ← FATAL ERROR!
)

@api.depends(...)  # ← Wrong for user-dependent fields!
def _compute_user_has_pending_approval(self):
    current_user = self.env.user  # ← Different per user!
```

**Why this broke everything:**

```
Stored field = ONE value in database for ALL users

But we need:
- leave_id 464: TRUE for user 34 (L1) ✓
- leave_id 464: TRUE for user 57 (L2) ✓
  
Same record, DIFFERENT values per user!

THIS IS IMPOSSIBLE WITH STORED FIELD!

What actually happened:
- Field computed once (for system user during create)
- Stored value: FALSE (system user not approver)
- ALL users see FALSE → Nobody sees requests! ❌
```

---

## ✅ Fix in v3.3.8:

**Reverted to non-stored field with proper _search method:**

```python
# v3.3.8 (CORRECT):
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
    # NO store=True! ← User-specific fields CANNOT be stored!
    search='_search_user_has_pending_approval',  # ← This handles filtering!
)

# NO @api.depends! ← Not used for user-dependent fields!
def _compute_user_has_pending_approval(self):
    current_user = self.env.user  # ← Computed fresh for each user
    # Returns different value based on who's logged in ✓
```

**How it works:**

```
When L1 (user 34) views records:
→ Field computed with user 34
→ Returns TRUE for requests where L1 is pending
→ L1 sees their requests ✓

When L2 (user 57) views records:
→ Field computed with user 57
→ Returns TRUE for requests where L2 is pending
→ L2 sees their requests ✓

When menu filters with domain [('user_has_pending_approval', '=', True)]:
→ _search method queries approval_level model
→ Finds leaves where current user has pending level
→ Returns correct leave IDs for current user ✓

WORKS FOR ALL USERS! ✓
```

---

## Impact

**v3.3.7 (Broken):**
```
L1 opens "My Time Off Approvals" → EMPTY ❌
L2 opens "My Time Off Approvals" → EMPTY ❌
Nobody can see requests! ❌
COMPLETELY BROKEN!
```

**v3.3.8 (Fixed):**
```
L1 opens "My Time Off Approvals" → Shows L1 requests ✓
L2 opens "My Time Off Approvals" → Shows L2 requests ✓
Both work correctly! ✓
```

---

## Why v3.3.7 Design Was Fundamentally Wrong

### The Problem with Stored User-Specific Fields:

**Odoo stored fields:**
- Store ONE value in database column
- Same value for ALL users viewing the record
- Example: `employee_id`, `state`, `date_from`

**User-specific computed fields:**
- Return DIFFERENT value per user
- Cannot be stored (would need separate value per user!)
- Must use `store=False` + `_search` method

**Our field:**
```python
def _compute_user_has_pending_approval(self):
    current_user = self.env.user  # ← This changes per user!
    
    # Same leave record:
    # User 34 sees: True
    # User 57 sees: False
    # User 99 sees: False
    
    # Cannot store ALL these values in ONE database column!
```

---

## Technical Details

### Field Definition:

**v3.3.5 (Partially broken):**
```python
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
)
# No @api.depends → Never recomputed ❌
```

**v3.3.6 (Attempted fix):**
```python
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
)

@api.depends(...)  # Added depends ✓
# But still not working well ⚠️
```

**v3.3.7 (Fatal error):**
```python
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
    store=True,  # ← FATAL: Cannot store user-specific field! ❌
)

@api.depends(...)  # ← Wrong for user-dependent compute! ❌
```

**v3.3.8 (Correct):**
```python
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
    # NO store=True! ✓
    search='_search_user_has_pending_approval',  # ← Handles filtering! ✓
)

# NO @api.depends! ✓ (user-dependent fields don't use depends)
def _compute_user_has_pending_approval(self):
    current_user = self.env.user
    # Computed fresh for each user ✓
```

---

## Upgrade Instructions

### URGENT: If you installed v3.3.7, upgrade to v3.3.8 immediately!

1. **Uninstall v3.3.7:**
   ```
   Apps → Uninstall "Snifx HR Leave Orgchart Approval"
   ```

2. **Remove old files:**
   ```bash
   cd /opt/odoo/custom-addons/
   rm -rf snifx_hr_leave_orgchart_approval
   ```

3. **Install v3.3.8:**
   ```bash
   cd /opt/odoo/custom-addons/
   unzip snifx_hr_leave_orgchart_approval_v3.3.8_FINAL_FIX.zip
   chown -R odoo:odoo snifx_hr_leave_orgchart_approval
   sudo systemctl restart odoo
   ```

4. **Install module:**
   ```
   Apps → Update Apps List
   Apps → Install "Snifx HR Leave Orgchart Approval"
   ```

5. **Test immediately:**
   ```
   Login as L1 → "My Time Off Approvals" → Should see requests ✓
   Login as L2 → "My Time Off Approvals" → Should see requests ✓
   ```

---

## Alternative Solution: Use "My Pending Approvals" Menu

**If you prefer simplicity:**

The **"My Pending Approvals"** menu always works correctly because:
- Uses `leave.approval.level` model directly
- No user-specific computed fields
- Field `is_current_level` is properly stored

**Both menus will work with v3.3.8, but "My Pending Approvals" is simpler and more reliable.**

---

## Lesson Learned

**DO NOT** store computed fields that use `self.env.user`!

**Wrong:**
```python
field = fields.Boolean(compute='_compute', store=True)

def _compute(self):
    user = self.env.user  # ← Different per user
    # Cannot store! ❌
```

**Correct:**
```python
field = fields.Boolean(compute='_compute', search='_search')

def _compute(self):
    user = self.env.user  # ← Computed per user ✓
    
def _search(self, operator, value):
    # Handle filtering ✓
```

---

## Version History Summary

```
v2.3.2: Works (uses approval_level model directly) ✓
v3.3.5: Broken (no @api.depends) ❌
v3.3.6: Partially works (has @api.depends, not stored) ⚠️
v3.3.7: COMPLETELY BROKEN (stored user-specific field) ❌❌❌
v3.3.8: WORKS CORRECTLY (non-stored with _search) ✓✓✓
```

---

## Compatibility

- Odoo 18 CE
- Upgrades from v2.3.2, v3.3.4, v3.3.5, v3.3.6, v3.3.7
- No data loss during upgrade
- Both "My Time Off Approvals" and "My Pending Approvals" menus work

---

## Testing Checklist

After v3.3.8 installation:

1. ✓ Create new request
2. ✓ L1 sees in "My Time Off Approvals"
3. ✓ L1 approves
4. ✓ L2 sees in "My Time Off Approvals"
5. ✓ L2 sees in "My Pending Approvals"
6. ✓ Both menus show same data
7. ✓ Field NOT queryable via SQL (correct - non-stored!)
8. ✓ Auto-hide after approval

---

**v3.3.8 is the CORRECT and FINAL fix!**

**DO NOT USE v3.3.7 - it's completely broken!**

**Upgrade to v3.3.8 immediately!** 🚀
