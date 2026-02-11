# Snifx HR Leave Orgchart Approval

Complete time off approval solution for Odoo 18 CE integrating organization chart hierarchy with Snifx Time Off Officer Department.

## Features

### 🔍 Smart Detection
- **Manager Detection**: Automatically identifies employees with subordinates
  - Managers (has team): 1 approval level
  - Staff (no team): 2 approval levels
- **Dynamic Adjustment**: Adapts based on actual reporting structure

### ⚙️ Flexible Approval Modes

#### Organization Chart Mode (Default)
- Uses smart detection based on subordinates
- Follows actual reporting hierarchy
- Automatically adjusts when structure changes

#### Simple Mode
- Direct manager approval only (1 level)
- Perfect for departments without defined org chart
- Toggle via department configuration

### 🤝 Snifx Officer Integration
- **Advanced Assignment System**: 
  - Date-based officer assignments
  - Department tree coverage (parent covers children)
  - Multiple assignments per officer
- **Filtered Notifications**: 
  - Only officers with Snifx group receive FYI
  - Department-level selection (choose 1-2 per dept)
  - No approval power (information only)
- **Enhanced Security**:
  - View access via Snifx rules
  - Permission-based visibility
  - Audit trail for assignments

### 📊 Approval Flow
1. Employee submits leave request
2. System detects employee type (Manager/Staff)
3. Builds approval chain from org chart
4. Sequential approval process
5. Officers notified after final approval (FYI)

### 📋 Approval Levels Visibility (New in v18.0.2.2.0)
- **Transparent Approval Chain**: Requestors can view complete approval workflow
- **Real-Time Status**: See who needs to approve and current status
- **Color-Coded Display**: Yellow (Pending), Green (Approved), Red (Refused)
- **User-Friendly Tab**: Easy access via "Approval Levels" tab on leave form
- **Read-Only View**: Employees can see but not edit approval chain

### 🔝 Top Manager Handling
- Top managers (no parent manager) can self-approve
- Manual approval action available
- Maintains accountability with audit trail

## Installation

### Prerequisites
1. Odoo 18 Community Edition
2. **Snifx Time Off Officer Department** module (recommended for officer features)
3. HR Holidays (standard Odoo module)

### Steps
```bash
# 1. Install Snifx module (if using officer features)
cd /opt/odoo/custom-addons
unzip snifx_timeoff_officer_department*.zip
chown -R odoo:odoo snifx_timeoff_officer_department
sudo systemctl restart odoo
# Apps → Install "Snifx Time Off Officer Department"

# 2. Install this module
unzip snifx_hr_leave_orgchart_approval*.zip
chown -R odoo:odoo snifx_hr_leave_orgchart_approval
sudo systemctl restart odoo
# Apps → Install "Snifx HR Leave Orgchart Approval"
```

## Configuration

### 1. Configure Time Off Types
```
Time Off → Configuration → Time Off Types → [Select Type]
└─ Organization Chart Approval:
    ✅ Enable Org Chart Approval
    ✅ + Time Off Officer (if using Snifx)
```

### 2. Configure Departments

#### For Departments with Org Chart:
```
HR → Configuration → Departments → [Department]
├─ ✅ Use Organization Chart Approval (checked)
└─ Notification Officers: [Select 1-2 from Snifx officers]
```

#### For Departments without Org Chart:
```
HR → Configuration → Departments → [Department]
├─ ☐ Use Organization Chart Approval (unchecked)
└─ All employees → Direct manager only
```

### 3. Configure Officers (Snifx - Optional)
```
Settings → Users → [Officer User]
├─ Access Rights:
│  └─ ✅ Officer: Manage Department Requests
└─ Officer Assignments tab:
    └─ Add departments with date ranges
```

## Usage Examples

### Example 1: Mid-Level Manager
```
Employee: Sayfrudin (Team Leader)
├─ Manager: Andrea
├─ Subordinates: 3
└─ Creates leave → 1 level

Approval: Andrea → Approved ✅
```

### Example 2: Staff under Top Manager
```
Employee: Miftahul (Sales Staff)
├─ Manager: Andrea (TOP)
├─ Subordinates: 0
└─ Creates leave → 1 level (Andrea is top)

Approval: Andrea → Approved ✅
```

### Example 3: Staff under Manager
```
Employee: Andi (under Sayfrudin)
├─ Manager: Sayfrudin
├─ Grandparent: Andrea
├─ Subordinates: 0
└─ Creates leave → 2 levels ✅

Approval: Sayfrudin → Andrea → Approved ✅
```

### Example 4: Top Manager Self-Approve
```
Employee: Andrea (Sales Director, TOP)
├─ Manager: None
├─ Subordinates: 6
└─ Creates leave

Can self-approve via:
- Manual "Approve" button
- Maintains audit trail
```

## Department Configuration Matrix

| Department | Org Chart Mode | Result |
|------------|----------------|---------|
| Sales | ✅ Enabled | Smart detection, self-approve for top |
| IT | ✅ Enabled | 2 levels for staff, 1 for managers |
| Back Office | ☐ Disabled | Direct manager only (simple) |
| Finance | ✅ Enabled | Adapts to structure |

## Notification Flow

### Officer Selection Priority:
1. Officers selected in department → Filtered by Snifx group
2. If none selected → Auto-select from Snifx assignments
3. Officers receive FYI (cannot approve, information only)

### Filtering Rules:
- ✅ Selected in department.notification_officer_ids
- ✅ Has "Officer: Manage Department Requests" group
- ❌ Not selected → No notification
- ❌ No Snifx group → No notification (even if selected)

## Troubleshooting

### Issue: Staff only getting 1 level instead of 2
**Cause**: Manager is top-level (no parent)
**Expected**: System can only find managers that exist

### Issue: Officers not receiving notifications
**Check**:
1. Officer has Snifx group
2. Officer selected in department
3. Leave is approved (FYI sent after approval)

### Issue: Top manager cannot approve
**Solution**: Top managers can use manual "Approve" button

## Technical Details

### Models Extended
- `hr.leave` - Approval chain generation
- `hr.leave.type` - Org chart configuration
- `hr.department` - Approval mode, officer selection
- `res.users` - Integration with Snifx (optional)

### Security Rules
- Snifx assignment-based view access (optional)
- Department notification-based FYI (optional)
- Approver write access
- Combined permission system

### Dependencies
```python
'depends': [
    'hr_holidays',
    'hr',
    'hr_org_chart',
]
```

## Version History

### 18.0.2.0.0 (Current)
- Rebranded with Snifx naming
- Enhanced Snifx integration documentation
- Department configuration modes
- Filtered notifications

### 18.0.1.0.0
- Initial release
- Smart detection
- Basic Snifx integration

## Support

For issues or questions:
- Check logs: `/var/log/odoo/odoo.log`
- Look for: "SMART DETECTION", "Snifx officers"
- Verify org chart in: Employees → Org Chart

## License

LGPL-3

## Author

Snifx Technical
