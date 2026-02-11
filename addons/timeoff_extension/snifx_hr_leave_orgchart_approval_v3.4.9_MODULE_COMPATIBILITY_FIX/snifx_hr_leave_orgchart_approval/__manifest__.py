# -*- coding: utf-8 -*-
{
    'name': 'Snifx HR Leave Orgchart Approval',
    'version': '18.0.3.4.9',
    'category': 'Human Resources/Time Off',
    'summary': """
        Complete time off approval with smart detection and officer integration.
        Flexible modes, Snifx officer FYI notifications, organization chart based.
    """,
    'description': """
Snifx HR Leave Orgchart Approval
===============================================================

Complete time off approval solution integrating organization chart
with Snifx Time Off Officer Balance for enhanced flexibility.

Core Features:
--------------
* **Smart Detection**: Automatic detection of Manager vs Staff
  - Manager (has subordinates): 1 approval level
  - Staff (no subordinates): 2 approval levels

* **Flexible Approval Modes**:
  - Organization Chart Mode: Smart detection with hierarchy
  - Simple Mode: Direct manager only (for departments without org chart)

* **Snifx Officer Integration**:
  - Uses Snifx Time Off Officer Department for officer management
  - Advanced assignment system (date-based, department trees)
  - Filtered notifications (only Snifx group members receive FYI)
  - Department-level officer selection
  - View access via Snifx security rules

* **Sequential Approval**: Proper approval chain following hierarchy

* **Officer FYI Notifications**: Officers notified after approval
  (no approval power, information only)

* **User-Specific Pending Field**: user_has_pending_approval field
  allows filtering of requests pending for current user

* Approval delegation support
* Email notifications at each level
* Comprehensive approval tracking
* Dashboard for pending approvals
* Reports and analytics

How it Works:
-------------
1. Employee submits leave request
2. System automatically determines approval chain from org chart:
   - Smart detection identifies Manager vs Staff
   - Manager: 1 approval level (senior manager)
   - Staff: 2 approval levels (direct + senior manager)
3. Each level approves sequentially
4. Officers receive FYI notification after final approval
5. Top managers can self-approve via manual action
6. **Approval Levels Tab**: Requestors can view complete approval chain
   with real-time status updates (Pending/Approved/Refused)

Version 3.3.5 Changes (Clean Version):
---------------------------------------
* Removed redundant "Orgchart: Waiting For Me" filter
* Removed redundant "Orgchart Waiting For Me" menu  
* Kept core field: user_has_pending_approval (for custom filter integration)
* Kept all approval logic and functionality intact
* Use with snifx_modify_waiting_filter (admin-aware) module for best experience

This version is designed to work cleanly with the admin-aware "Waiting For Me"
filter module, eliminating UI redundancy while maintaining all core functionality.

Based on Odoo's native organization chart structure.
Compatible with Odoo 18 Community Edition.
    """,
    'author': 'Snifx Technical',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': [
        'hr',
        'hr_holidays',
        'hr_org_chart',  # Uses Odoo's built-in org chart
        'snifx_timeoff_officer_department',  # Snifx officer management
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/approval_security.xml',
        'security/approval_level_security.xml',
        'security/hr_leave_security.xml',
        'security/officer_leave_access.xml',
        'data/mail_activity_type.xml',
        'data/email_template.xml',
        'views/hr_leave_type_views.xml',
        'views/hr_leave_views.xml',
        'views/hr_employee_views.xml',
        'views/approval_level_views.xml',
        'views/hr_department_views.xml',
        'views/menu_views.xml',
    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'uninstall_hook': 'uninstall_hook',
}
