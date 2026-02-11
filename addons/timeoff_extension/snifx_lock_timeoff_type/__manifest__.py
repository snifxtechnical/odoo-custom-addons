# -*- coding: utf-8 -*-
{
    'name': 'Lock Time Off Type After Submit',
    'version': '18.0.1.4.0',
    'category': 'Human Resources/Time Off',
    'summary': 'Prevent changing time off type after submission',
    'description': """
        Lock Time Off Type After Submit
        ================================
        
        Security & Workflow Enhancement:
        - Prevents users from changing time off type after submission
        - Forces users to select time off type before saving
        - Maintains approval chain integrity
        
        Features:
        ---------
        1. Time off type is REQUIRED (must be selected)
        2. Time off type DEFAULT is EMPTY (no pre-selection)
        3. Time off type is READONLY after submit (clean UI)
        4. Validation prevents changes after submission
        5. Clear error message to users (only when needed)
        
        Why This is Important:
        ----------------------
        Without this module, users could:
        - Submit sick leave → Gets approval chain A
        - Change to annual leave → Still has approval chain A
        - Bypass proper approval workflow
        - Manipulate leave balances
        
        With this module:
        - Time off type locked after submit ✓
        - Must cancel and resubmit to change type ✓
        - Approval chain integrity maintained ✓
        - Security enhanced ✓
    """,
    'author': 'Snifx Technical',
    'website': 'https://snifx.studio',
    'license': 'LGPL-3',
    'depends': [
        'hr_holidays',
    ],
    'data': [
        'views/hr_leave_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
