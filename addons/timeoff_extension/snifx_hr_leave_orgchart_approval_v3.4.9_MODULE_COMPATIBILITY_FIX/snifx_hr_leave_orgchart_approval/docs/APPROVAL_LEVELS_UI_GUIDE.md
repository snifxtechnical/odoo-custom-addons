# How to View Approval Levels

## For Requestors (Employees)

After creating a leave request, you can now see who will approve your leave:

### Steps:

1. **Navigate to your leave**
   - Go to: Time Off → My Time Off
   - Click on your leave request

2. **Click the "Approval Levels" tab**
   - You will see a tab labeled "Approval Levels"
   - Click on this tab to expand

3. **View your approval chain**
   - You will see a table with:
     - **Level**: Approval level number (1, 2, 3...)
     - **Approver**: Name of the person who needs to approve
     - **Status**: Current state (Pending/Approved/Refused)
     - **Approval Date**: Date when approved (if completed)

### Example:

```
Level │ Approver          │ Status  │ Approval Date
──────┼───────────────────┼─────────┼──────────────
  1   │ Fritz Erlangga    │ Pending │ -
  2   │ Slamet Chahyadi   │ Pending │ -
  3   │ Andrea Bastian    │ Pending │ -
```

### Color Coding:

- **Yellow/Orange** (Pending): Waiting for approval
- **Green** (Approved): Level has been approved ✓
- **Red** (Refused): Level was refused ✗

### Real-Time Updates:

The approval status updates automatically:
- When Level 1 approves, status changes to "Approved" (green)
- Next level remains "Pending" (yellow)
- When all levels approve, all show "Approved" (green)

### Benefits:

✓ Know exactly who needs to approve
✓ See current approval progress
✓ Track when each level was approved
✓ No need to ask "who's next?"
✓ Complete transparency

---

## For Managers (Approvers)

When you receive a leave to approve, you can also see the complete approval chain:

1. Open the leave request
2. Click "Approval Levels" tab
3. See where you are in the chain
4. Know if there are more approvals needed

Example:
```
Level │ Approver          │ Status   │ Approval Date
──────┼───────────────────┼──────────┼──────────────
  1   │ You (Fritz)       │ Pending  │ -            ← You are here
  2   │ Slamet Chahyadi   │ Pending  │ -            ← Next approver
```

After you approve:
```
Level │ Approver          │ Status   │ Approval Date
──────┼───────────────────┼──────────┼──────────────
  1   │ You (Fritz)       │ Approved │ 2024-12-16   ✓ Done!
  2   │ Slamet Chahyadi   │ Pending  │ -            ← Waiting
```

---

## For Officers

Officers can also view the approval chain for leaves in their departments:

1. Navigate to: Time Off → All Time Off
2. Filter by your department
3. Open any leave request
4. Click "Approval Levels" tab
5. See complete approval history

This helps officers:
- Understand approval workflow
- Track approval progress
- Answer employee questions
- Monitor compliance

---

## Troubleshooting

### "I don't see the Approval Levels tab"

**Possible reasons:**
1. Leave is not using organization chart approval
   - Check: Time Off Type settings
   - Ensure "Use Organization Chart Approval" is enabled
   
2. Module not upgraded
   - Contact your administrator
   - Module version should be 18.0.2.2.0 or higher

3. Browser cache
   - Try: Ctrl+F5 to refresh
   - Or: Clear browser cache

### "The tab is empty"

**Possible reasons:**
1. Approval chain not generated yet
   - Try: Refresh the page
   - Or: Contact administrator

2. Leave just submitted
   - Wait a few seconds
   - Refresh the page

### "I can't edit the approval levels"

**This is correct!** The approval levels are read-only for security:
- Only the system can create/modify approval levels
- Employees can VIEW only
- This prevents tampering with approval workflow

---

## Technical Notes (for Administrators)

### Feature Details:
- **Module**: snifx_hr_leave_orgchart_approval v18.0.2.2.0
- **View**: hr_leave_view_form_approval_levels_tab
- **Field**: approval_level_ids (One2many)
- **Access**: Read-only for all users
- **Visibility**: Only when use_orgchart_approval = True

### Installation:
1. Upgrade module to version 18.0.2.2.0
2. Restart Odoo
3. Clear browser cache
4. Feature automatically available

### No configuration needed!
- The tab appears automatically
- Works for all users
- No additional setup required

---

For support or questions, contact your system administrator.
