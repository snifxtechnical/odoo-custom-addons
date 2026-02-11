Snifx Time Off Officer Balance - Enhanced
==========================================

Flexible Time Off Officer Assignment with Full Approval Capabilities

Features
--------

Flexible Officer Assignment
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Assignment Model**: Create flexible assignments mapping users to department trees
* **Multiple Assignments**: One officer can manage multiple department trees  
* **Date Range**: Optional date-based assignments (valid from/to)
* **Active Toggle**: Immediately enable/disable assignments
* **Duplicate Prevention**: Automatic validation to prevent conflicting assignments

Leave Approval Workflow
~~~~~~~~~~~~~~~~~~~~~~~~

* **Full Approval Rights**: Approve and validate leave requests
* **Department-Based**: Only for employees in assigned department trees
* **Self-Exclusion**: Officers cannot approve their own leave requests
* **Real-time Updates**: Automatically follows department hierarchy changes

Employee Access
~~~~~~~~~~~~~~~

* **View All Employees**: Officers can see all employees across departments
* **Limited Tabs**: Access restricted to Resume and Work Information tabs only
* **Privacy Protection**: Private Information and HR Settings tabs are hidden

Balance Reports
~~~~~~~~~~~~~~~

* **View Reports**: Access balance reports for assigned departments
* **Export Excel**: Export balance data to Excel
* **Filtered Data**: Automatically limited to managed department trees

Public Holidays Management
~~~~~~~~~~~~~~~~~~~~~~~~~~~

* **Full CRUD**: Create, read, update, and delete public holidays
* **Global Access**: Manage holidays for all employees
* **No Approval Required**: Direct creation without workflow

Security Features
~~~~~~~~~~~~~~~~~

* **Role-Based Access**: Separate permissions for officers and HR managers
* **Record Rules**: Dynamic filtering based on assignments
* **Field-Level Security**: Tab visibility controlled by groups
* **Audit Trail**: All assignments tracked with user and date info

Installation
------------

1. Copy module to addons directory
2. Restart Odoo server
3. Update Apps List
4. Install module from Apps menu
5. Assign "Officer with Balance (Enhanced)" group to users
6. Create officer assignments via Settings → Users

Configuration
-------------

Creating Officer Assignments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. Go to Settings → Users & Companies → Users
2. Open user who should be an officer
3. Enable "Officer with Balance (Enhanced)" in Access Rights
4. Go to Officer Assignments tab
5. Add assignment with department and date range
6. Save

Usage
-----

For Officers
~~~~~~~~~~~~

* Approve leave requests: Time Off → My Team → Time Off Requests
* View balance reports: Time Off → Reporting → Balance
* Create public holidays: Time Off → Configuration → Public Holidays
* View employees: Employees menu (limited tabs)

For HR Managers
~~~~~~~~~~~~~~~

* Manage assignments: Time Off → Configuration → Officer Assignments
* Full access to all features
* Can override officer restrictions

Requirements
------------

* Odoo 18.0 Community Edition
* PostgreSQL 12+
* Time Off module (hr_holidays)
* Employees module (hr)

Support
-------

For support, contact:

* Email: support@snifx.example
* Website: https://snifx.example

License
-------

LGPL-3

Credits
-------

Author: Snifx Studio

Maintainer: Snifx Studio
