# -*- coding: utf-8 -*-
{
    'name': 'Snifx - Waiting For Me Filter (Smart Domain)',
    'version': '18.0.1.1.0',
    'category': 'Human Resources/Time Off',
    'summary': 'Modify "Waiting For Me" filter - smart for both admin and users',
    'description': """
        Modifies the standard Odoo "Waiting For Me" filter with smart behavior:
        
        SINGLE FILTER - SMART BEHAVIOR:
        - Same filter name: "Waiting For Me"
        - Uses user_has_pending_approval field
        - Shows user-specific pending for everyone
        - Admin can use "To Approve" filter for overview
        
        SIMPLE APPROACH:
        - No groups complexity
        - No duplicate filters
        - Just works!
        
        RESULT:
        ✅ One "Waiting For Me" filter only
        ✅ Shows user-specific pending
        ✅ Auto-hide after approve
        ✅ Clean & simple
        
        Note: Admin users should use "To Approve" filter for complete overview.
    """,
    'author': 'Snifx Technical',
    'website': 'https://www.snifx.com',
    'depends': ['snifx_hr_leave_orgchart_approval'],
    'data': [
        'views/hr_leave_views_inherit.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
