# Snifx Time Off Officer Department

## Overview

**Snifx Time Off Officer Department** is a professional Odoo 18 Community Edition module that provides sophisticated department-level delegation for time off management. This module enables organizations to distribute approval workflows across department heads while maintaining strict access control and audit compliance.

### Version Information
- **Version**: 1.0.0 (Initial Release)
- **Odoo Version**: 18.0 Community Edition
- **License**: LGPL-3
- **Author**: Snifx Studio

---

## Key Features

### 🎯 Core Functionality

#### Department Tree Assignment
- Assign time off officers to specific department hierarchies
- Automatic inclusion of all subdepartments
- Support for multiple department assignments per officer
- PostgreSQL `child_of` operator ensures efficient hierarchical queries

#### Flexible Date-Based Control
- Configure active date ranges for each assignment
- Support temporary assignments (start date + end date)
- Support permanent assignments (start date only)
- Automatic activation/deactivation based on current date

#### Granular Access Control
- Officers only view leave requests from assigned departments
- Strict database-level security via Odoo record rules
- Cannot approve their own leave requests
- Read-only access to public holidays

#### Balance Reporting
- Dedicated balance views filtered by assigned departments
- Real-time balance calculations
- Department-tree-based filtering

#### Seamless Integration
- Works with native Odoo "Time Off" dropdown
- Custom "Time Off (Extra)" dropdown for convenience
- No conflicts with Odoo's standard Time Off groups
- Clean single Public Holidays menu in Configuration

---

## Business Benefits

### For Organizations
✅ **Scalable Delegation**: Distribute approval workload across department heads  
✅ **Security & Privacy**: Prevent unauthorized access to employee data  
✅ **Compliance Ready**: Maintain complete approval trails and access logs  
✅ **Reduced Admin Burden**: Empower managers while maintaining oversight  

### For Department Managers
✅ **Focused View**: See only relevant department requests  
✅ **Easy Assignment**: Use intuitive dropdown or dedicated tab  
✅ **Balance Visibility**: Monitor department time off balances  
✅ **Self-Service**: No administrator intervention needed for routine approvals  

### For HR Administrators
✅ **Centralized Control**: Configure all assignments from one place  
✅ **Audit Trail**: Track who approved what and when  
✅ **Flexible Configuration**: Adjust assignments as organization changes  
✅ **Clean Interface**: No UI conflicts or duplicates  

---

## Installation

### Prerequisites
- Odoo 18.0 Community Edition
- Modules: `base`, `hr`, `hr_holidays` (all standard Odoo modules)

### Installation Steps

1. **Download and Extract**
```bash
cd /opt/odoo/addons/
unzip snifx_timeoff_officer_department-18_0_1_0_0.zip
```

2. **Set Permissions**
```bash
chown -R odoo:odoo snifx_timeoff_officer_department
```

3. **Restart Odoo**
```bash
sudo systemctl restart odoo
```

4. **Activate Developer Mode** (temporary, for installation only)
   - Go to Settings
   - Scroll to bottom
   - Click "Activate Developer Mode"

5. **Update Apps List**
   - Go to Apps menu
   - Click "Update Apps List"
   - Search for "Snifx Time Off Officer Department"

6. **Install Module**
   - Click "Install" button
   - Wait for installation to complete

7. **Deactivate Developer Mode** (optional)
   - Module is now accessible without Developer Mode

---

## Configuration

### Step 1: Configure Department Structure

Ensure your department hierarchy is properly configured:

1. Go to **Employees > Configuration > Departments**
2. Create/verify department structure with parent-child relationships
3. Ensure each employee is assigned to a department

**Example Structure:**
```
Company
├── Sales Department (ROOT)
│   ├── Sales Team A
│   └── Sales Team B
├── IT Department (ROOT)
│   ├── Development
│   └── Infrastructure
└── HR Department (ROOT)
```

### Step 2: Create Officer Users

1. Go to **Settings > Users & Companies > Users**
2. Create or select user who will be a Time Off Officer
3. Ensure user has basic employee access
4. **Do NOT manually assign any Time Off groups yet** (will be auto-assigned)

### Step 3: Assign Officer to Departments

There are **TWO methods** to assign officers:

#### Method A: Using Officer Assignments Tab (Recommended)

1. Go to **Settings > Users & Companies > Users**
2. Open the user who will be an officer
3. Click **"Officer Assignments"** tab
4. Click **"Add a line"**
5. Configure assignment:
   - **Department**: Select ROOT department (e.g., "Sales Department")
   - **Date From**: Start date (required)
   - **Date To**: End date (optional, leave empty for permanent)
   - **Active**: Check to activate (checked by default)
6. Click **"Save"**

**Result**: User automatically gets "Officer: Manage Department Requests" group

#### Method B: Using Access Rights Dropdown

1. Go to **Settings > Users & Companies > Users**
2. Open the user
3. Click **"Access Rights"** tab
4. Scroll to **"HUMAN RESOURCES EXTRA"** section
5. **Time Off (Extra)** dropdown: Select **"Officer: Manage Department Requests"**
6. **Save**
7. Go to **"Officer Assignments"** tab and add department assignments

**Note**: Both methods sync perfectly. Changes in one reflect in the other.

### Step 4: Verify Officer Access

1. **Logout** and **login as the officer user**
2. Go to **Time Off** menu
3. Officer should see:
   - ✅ Leave requests from assigned department tree only
   - ✅ Balance report filtered to assigned departments
   - ✅ Public holidays (read-only)
   - ❌ Cannot see other departments' requests
   - ❌ Cannot see their own requests in approval view

---

## Usage Guide

### For Time Off Officers

#### Viewing Leave Requests

1. Go to **Time Off > My Team**
2. View requests from assigned department tree
3. Use filters to narrow down requests
4. Click on request to see details

#### Approving/Refusing Requests

1. Open leave request
2. Review request details:
   - Employee information
   - Leave type
   - Date range
   - Number of days
3. Click **"Approve"** or **"Refuse"**
4. Add comment if refusing (recommended)

#### Viewing Department Balances

1. Go to **Time Off > Reporting > Balance**
2. View filtered list of employees in assigned departments
3. See current balance for each leave type
4. Use for planning and capacity management

#### Viewing Public Holidays

1. Go to **Time Off > Configuration > Public Holidays**
2. View list of public holidays
3. See holiday dates and companies affected
4. **Note**: Officers can only VIEW, not create/edit/delete

### For HR Administrators

#### Managing Officer Assignments

**Add New Assignment:**
1. User form > Officer Assignments tab > Add a line
2. Fill in department, dates, active status
3. Save

**Modify Assignment:**
1. Open existing assignment line
2. Change department or dates
3. Save

**Deactivate Assignment:**
1. Find assignment line
2. Uncheck "Active" checkbox
3. Save

**Remove Assignment:**
1. Find assignment line
2. Click trash icon
3. Save

#### Monitoring Officer Activity

1. Use Odoo's standard approval logs
2. Each approval shows:
   - Who approved (officer name)
   - When approved (timestamp)
   - What was approved (request details)

---

## Technical Architecture

### Module Structure

```
snifx_timeoff_officer_department/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── hr_employee.py                    # Employee access rules
│   ├── hr_leave.py                       # Leave approval logic
│   ├── hr_timeoff_officer_assignment.py  # Assignment model
│   ├── res_users.py                      # User extensions
│   └── resource_calendar_leaves.py       # Public holidays
├── security/
│   ├── groups.xml                        # Officer group definition
│   ├── ir.model.access.csv              # Model access rights
│   └── rules.xml                         # Record rules
├── views/
│   ├── balance_tree_view.xml            # Balance report view
│   ├── hr_employee_views.xml            # Employee form extensions
│   ├── hr_leave_views.xml               # Leave request views
│   ├── hr_timeoff_officer_assignment_views.xml
│   ├── res_users_views.xml              # User form extensions
│   └── resource_calendar_leaves_views.xml
├── data/
│   └── balance_menu_and_actions.xml     # Menu items
└── static/
    └── description/
        └── icon.png
```

### Security Implementation

#### Group Definition
- **Name**: Officer: Manage Department Requests
- **Category**: (Uncategorized - prevents checkbox conflicts)
- **Access**: Via "Time Off (Extra)" dropdown only

#### Record Rules

1. **Officer See Own Department Leaves**
   - Domain: `[('employee_id.department_id', 'child_of', officer's assigned root departments)]`
   - Permissions: Read, Write (via approval), Create (no), Unlink (no)

2. **Officer View Department Employees**
   - Domain: `[('department_id', 'child_of', officer's assigned root departments)]`
   - Permissions: Read-only (limited fields)

3. **Officer View Public Holidays**
   - Domain: `[]` (all)
   - Permissions: Read-only

---

## Permissions Matrix

| Action | Officer | Manager | Administrator |
|--------|---------|---------|---------------|
| View assigned dept requests | ✅ | ✅ | ✅ |
| View other dept requests | ❌ | ✅ | ✅ |
| Approve assigned dept requests | ✅ | ✅ | ✅ |
| Approve other dept requests | ❌ | ✅ | ✅ |
| Approve own requests | ❌ | ❌ | ✅ |
| View assigned dept balances | ✅ | ✅ | ✅ |
| View all balances | ❌ | ✅ | ✅ |
| View public holidays | ✅ | ✅ | ✅ |
| Manage public holidays | ❌ | ✅ | ✅ |
| Configure assignments | ❌ | ❌ | ✅ |

---

## Troubleshooting

### Issue: Officer Cannot See Any Requests

**Possible Causes & Solutions:**

1. **No Active Assignments**
   - Check: Officer Assignments tab
   - Fix: Add or activate assignment

2. **Date Range Issue**
   - Check: Current date is between date_from and date_to
   - Fix: Adjust date range or remove date_to

3. **No Employees in Department**
   - Fix: Assign employees to departments

### Issue: "Time Off (Extra)" Field Not Visible

- This field should be visible WITHOUT Developer Mode in v1.0.0
- If not visible: Check module is properly installed

---

## FAQ

### Q: Can one officer be assigned to multiple departments?
**A:** Yes! Officers can have multiple assignments to different department trees.

### Q: Can officers approve their own leave requests?
**A:** No. This is prevented by design for compliance reasons.

### Q: What happens if date_to is in the past?
**A:** Assignment becomes inactive automatically.

### Q: Can officers see employee personal information?
**A:** Officers have limited read access - only Resume and Work Information tabs.

---

## Changelog

### Version 1.0.0 (2024-12-08) - Initial Release

**Features:**
- Department-based officer assignment system
- Flexible date-based access control
- Balance reporting for assigned departments
- Public holidays read access for officers
- Auto-group assignment via Officer Assignments tab
- Clean "Time Off (Extra)" dropdown integration
- Single Public Holidays menu (no duplicates)

**Security:**
- Strict record rules for department isolation
- Custom approval permission checking
- Self-approval prevention
- Read-only public holidays access

---

## License

This module is licensed under LGPL-3.

Copyright (c) 2024 Snifx Studio

---

## Credits

**Author**: Snifx Studio  
**Maintainer**: Snifx Technical Team  

---

**Enjoy streamlined time off management with department-level delegation!** 🎉
