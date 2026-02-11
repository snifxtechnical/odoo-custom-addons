# Snifx - Waiting For Me Filter (Smart Domain)

## What This Module Does

SIMPLE approach - exactly as requested!

### Single Filter Modification

Modifies the standard Odoo "Waiting For Me" filter:

**BEFORE:**
```
Domain: [('state', '=', 'confirm')]
Shows: All requests in confirm state
```

**AFTER:**
```
Domain: [('user_has_pending_approval', '=', True)]
Shows: Only requests pending for current user
```

### Result

✅ ONE filter only: "Waiting For Me"
✅ Shows user-specific pending
✅ Auto-hide after approve
✅ No duplicate filters
✅ No groups complexity

### For Admin Overview

Admin users should use the **"To Approve"** filter which shows all pending requests.

Available filters after installation:
- "Waiting For Me" → User-specific pending (modified)
- "To Approve" → All pending (Odoo standard, for admin)

## Installation

```bash
cd /opt/odoo/custom-addons/
unzip snifx_waiting_filter_SIMPLE.zip
mv snifx_waiting_filter_CORRECT snifx_modify_waiting_filter
chown -R odoo:odoo snifx_modify_waiting_filter
sudo systemctl restart odoo
Apps → Install
```

## Prerequisites

Base module must be installed:
- snifx_hr_leave_orgchart_approval (v3.3.4 or v3.3.5)

Field must be recomputed:
- Settings → Recompute Fields
- Model: hr.leave
- Field: user_has_pending_approval

## What's Different from Previous Versions

**Previous (BROKEN):**
- Tried to create 2 filters with same name
- Used groups attribute
- Both filters appeared → conflict!

**This (CORRECT):**
- ONE filter only
- Simple domain modification
- No groups complexity
- Just works!

## Usage

**For Regular Users:**
```
Management → Time Off
Click: "Waiting For Me" filter
See: Only your pending requests
After approve: Request disappears (auto-hide)
```

**For Admin:**
```
Management → Time Off
Click: "To Approve" filter
See: All pending requests
Complete overview
```

## Benefits

✅ Clean UI (one modified filter)
✅ Simple implementation
✅ No conflicts
✅ Easy to understand
✅ Works reliably

## Compatibility

- Odoo 18 CE
- Works with v3.3.4 or v3.3.5 base module
- If using v3.3.4: "Orgchart: Waiting For Me" will still exist
- If using v3.3.5: Only this modified filter exists

## Recommendation

Best setup:
1. Use v3.3.5 base (no "Orgchart: Waiting For Me")
2. Install this module (modifies standard filter)

Result: Clean with ONE filter only!
