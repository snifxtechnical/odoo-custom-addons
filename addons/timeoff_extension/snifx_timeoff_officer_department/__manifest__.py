# -*- coding: utf-8 -*-
{
    "name": "Snifx Time Off Officer Department",
    "version": "18.0.1.0.0",
    "category": "Human Resources/Time Off",
    "summary": "Department-based Time Off Officer with Granular Access Control and Flexible Assignment",
    "description": """
Department-Based Time Off Officer Management
============================================

A professional Odoo 18 Community Edition module providing sophisticated department-level
delegation for time off management with granular access control.

Core Features
-------------
* **Department Tree Assignment**: Assign officers to specific department hierarchies with automatic subdepartment inclusion
* **Flexible Date-Based Control**: Configure active date ranges for temporary or permanent officer assignments
* **Granular Access Control**: Officers only view and approve requests from their assigned departments
* **Balance Reporting**: Dedicated balance views filtered by officer's assigned departments
* **Public Holidays Access**: Read-only public holiday viewing for officers
* **Seamless Integration**: Works with native Odoo Time Off dropdown without conflicts
* **Auto-Assignment**: Automatic group assignment when creating officer assignments
* **Audit Trail**: Track who approved what through Odoo's standard approval system

Business Benefits
-----------------
* **Scalable Delegation**: Distribute time off approval workload across department heads
* **Security & Privacy**: Strict department-based access prevents unauthorized data viewing
* **Organizational Flexibility**: Support complex organizational structures with nested departments
* **Compliance Ready**: Maintain approval trails and access logs for audit purposes
* **Reduced Administrator Burden**: Empower department managers while maintaining control

Technical Highlights
--------------------
* Department tree access via PostgreSQL's child_of operator for performance
* Custom permission checking integrated with Odoo's approval workflow
* Record rules ensure database-level security
* Compatible with Odoo's native Time Off categories
* Single public holiday menu in Configuration (no duplicates)
* Clean separation between officer and administrator permissions

Perfect For
-----------
* Mid to large organizations with multiple departments
* Companies requiring delegated time off approval workflows
* Organizations with complex hierarchical structures
* Teams needing department-level access segregation

Version: 1.0.0 - Initial Release
Tested on: Odoo 18.0 Community Edition
    """,
    "author": "Snifx Studio",
    "website": "https://snifx.example",
    "license": "LGPL-3",
    "depends": [
        "base",
        "hr",
        "hr_holidays",
    ],
    "data": [
        # Security
        "security/groups.xml",
        "security/ir.model.access.csv",
        "security/rules.xml",
        
        # Data
        "data/balance_menu_and_actions.xml",
        
        # Views
        "views/hr_leave_views.xml",
        "views/hr_timeoff_officer_assignment_views.xml",
        "views/res_users_views.xml",
        "views/resource_calendar_leaves_views.xml",
        "views/hr_employee_views.xml",
        "views/balance_tree_view.xml",
    ],
    "images": [
        "static/description/icon.png",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
