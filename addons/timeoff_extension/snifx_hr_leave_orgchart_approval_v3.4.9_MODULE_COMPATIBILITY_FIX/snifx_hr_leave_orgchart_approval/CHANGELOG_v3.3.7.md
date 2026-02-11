# Version 3.3.7 - CRITICAL FIX: Stored Field for Sequential Approval

## 🚨 Critical Issue Fixed

### Problem in v3.3.5 and v3.3.6:

The `user_has_pending_approval` field was a **non-stored computed field**, causing:

**Issue 1: "My Time Off Approvals" menu empty for Level 2**
```
User experience:
- L1 approves request ✅
- L2 opens "My Time Off Approvals" menu
- Result: EMPTY! ❌ (no requests shown)

Meanwhile:
- L2 opens "My Pending Approvals" menu
- Result: Request shown ✅ (works!)
```

**Issue 2: Field not queryable**
```sql
-- This fails in v3.3.6:
SELECT user_has_pending_approval FROM hr_leave;
ERROR: column does not exist

-- Because field was computed on-the-fly, not stored!
```

**Root cause:**
```python
# v3.3.5 - NO decorator, NO storage
def _compute_user_has_pending_approval(self):
    # Never recomputes ❌

# v3.3.6 - Has decorator, but NOT stored
@api.depends(...)
def _compute_user_has_pending_approval(self):
    # Recomputes, but not in database ❌
```

---

## ✅ Fix in v3.3.7:

**Made field STORED in database:**

```python
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
    store=True,  # ← NOW STORED! ✅
)

@api.depends('approval_level_ids.state', 
             'approval_level_ids.is_current_level',
             'approval_level_ids.approver_id')
def _compute_user_has_pending_approval(self):
    # Stored + @api.depends = Perfect! ✅
```

**Benefits:**
- ✅ Field stored in database
- ✅ Automatically recomputes when dependencies change
- ✅ "My Time Off Approvals" menu works for ALL approval levels
- ✅ Queryable via SQL
- ✅ Better performance

---

## Impact

**Before (v3.3.6):**
```
Employee submits → L1 sees in "My Time Off Approvals" ✅
L1 approves → Field recomputes (but not stored)
L2 opens "My Time Off Approvals" → EMPTY! ❌
L2 opens "My Pending Approvals" → Shows request ✅ (workaround)

Problem: Inconsistent user experience!
```

**After (v3.3.7):**
```
Employee submits → L1 sees in "My Time Off Approvals" ✅
L1 approves → Field recomputes AND stores in DB ✅
L2 opens "My Time Off Approvals" → Shows request! ✅
L2 opens "My Pending Approvals" → Shows request ✅

Result: BOTH menus work perfectly! ✅
```

---

## Upgrade Instructions

### From v3.3.5 or v3.3.6:

1. **Backup database first!**
   ```bash
   sudo -u postgres pg_dump odoo_db > backup_before_v337.sql
   ```

2. **Uninstall current version:**
   ```
   Apps → Uninstall "Snifx HR Leave Orgchart Approval"
   ```

3. **Remove old files:**
   ```bash
   cd /opt/odoo/custom-addons/
   rm -rf snifx_hr_leave_orgchart_approval
   ```

4. **Install v3.3.7:**
   ```bash
   cd /opt/odoo/custom-addons/
   unzip snifx_hr_leave_orgchart_approval_v3.3.7_STORED_FIELD.zip
   chown -R odoo:odoo snifx_hr_leave_orgchart_approval
   sudo systemctl restart odoo
   ```

5. **Install module:**
   ```
   Apps → Update Apps List
   Apps → Install "Snifx HR Leave Orgchart Approval"
   ```

6. **IMPORTANT: Field will auto-populate!**
   ```
   The stored field will automatically compute for all existing records.
   No manual recompute needed!
   ```

7. **Verify:**
   ```
   - Login as Level 2 approver
   - Check "My Time Off Approvals" menu
   - Should see pending requests! ✅
   ```

---

## Technical Details

### Field Definition Changes:

**v3.3.5 (Broken):**
```python
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
)
# No decorator, no storage ❌
```

**v3.3.6 (Partially Fixed):**
```python
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
)

@api.depends(...)  # Has decorator ✅
def _compute_user_has_pending_approval(self):
    # But still not stored ❌
```

**v3.3.7 (Fully Fixed):**
```python
user_has_pending_approval = fields.Boolean(
    compute='_compute_user_has_pending_approval',
    store=True,  # ← KEY DIFFERENCE! ✅
)

@api.depends(...)  # Has decorator ✅
def _compute_user_has_pending_approval(self):
    # Stored + depends = Perfect! ✅
```

### Database Impact:

**v3.3.6:** Field not in database
```sql
\d hr_leave;
-- user_has_pending_approval: NOT PRESENT ❌
```

**v3.3.7:** Field in database
```sql
\d hr_leave;
Column                    | Type    | 
--------------------------|---------|
user_has_pending_approval | boolean | ← NOW IN DB! ✅
```

---

## Performance

**v3.3.6 (Non-stored):**
- Field computed every time record viewed
- Slow for large datasets
- Cannot use in database queries

**v3.3.7 (Stored):**
- Field computed once, then stored
- Fast - direct database lookup
- Can use in complex queries
- ✅ Better performance!

---

## Compatibility

- Odoo 18 CE
- Upgrades from v3.3.4, v3.3.5, v3.3.6
- Works with filter modification modules
- No data loss during upgrade

---

## Testing

**Test checklist:**

1. ✅ Create new request
2. ✅ L1 approves
3. ✅ L2 sees in "My Time Off Approvals"
4. ✅ L2 sees in "My Pending Approvals"
5. ✅ Both menus show same data
6. ✅ Field queryable via SQL
7. ✅ Auto-hide after L2 approves

---

**v3.3.7 is the DEFINITIVE FIX for sequential approval visibility!** ✅

**Upgrade immediately if using v3.3.5 or v3.3.6!** 🚀
