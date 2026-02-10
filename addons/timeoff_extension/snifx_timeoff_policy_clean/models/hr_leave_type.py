# -*- coding: utf-8 -*-
from odoo import fields, models


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    # ==========================================================================
    # CATEGORY 1: DATE RESTRICTIONS (from snifx_timeoff_date_restriction)
    # ==========================================================================
    
    allow_future_request = fields.Boolean(
        string='Allow Future Date Requests',
        default=True,
        help='If unchecked, employees cannot submit leave requests for future dates'
    )
    
    max_backdate_days = fields.Integer(
        string='Maximum Backdate Days',
        default=0,
        help='Maximum number of days in the past that leave can be requested. '
             '0 means no backdating allowed.'
    )

    # ==========================================================================
    # CATEGORY 2: REQUEST VALIDATION (from snifx_timeoff_date_request_validation)
    # ==========================================================================
    
    enable_min_notice = fields.Boolean(
        string='Enable Minimum Notice',
        default=False,
        help='Require minimum advance notice for leave requests above threshold'
    )
    
    threshold_days = fields.Float(
        string='Threshold (Days)',
        default=3.0,
        help='Minimum leave duration to trigger notice requirement'
    )
    
    use_business_days_for_threshold = fields.Boolean(
        string='Use Business Days for Threshold',
        default=False,
        help='Calculate threshold using business days instead of calendar days'
    )
    
    min_notice_qty = fields.Integer(
        string='Minimum Notice Quantity',
        default=7,
        help='Required advance notice quantity'
    )
    
    min_notice_unit = fields.Selection(
        [
            ('days', 'Calendar Days'),
            ('business_days', 'Business Days'),
            ('weeks', 'Weeks'),
        ],
        string='Notice Unit',
        default='days',
        help='Unit for minimum notice period'
    )
    
    exclude_public_holidays = fields.Boolean(
        string='Exclude Public Holidays',
        default=True,
        help='Exclude public holidays when calculating business days'
    )
    
    scope_mode = fields.Selection(
        [
            ('company', 'Company-wide'),
            ('department', 'Specific Department'),
            ('category', 'Employee Category'),
        ],
        string='Scope',
        default='company',
        help='Policy application scope'
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        help='Specific department for policy (if scope is department)'
    )
    
    category_id = fields.Many2one(
        'hr.employee.category',
        string='Employee Tag',
        help='Employee category for policy (if scope is category)'
    )
    
    exempt_group_ids = fields.Many2many(
        'res.groups',
        'hr_leave_type_exempt_groups_rel',
        'leave_type_id',
        'group_id',
        string='Exempt Groups',
        help='User groups exempt from minimum notice requirement'
    )
    
    grace_hours = fields.Integer(
        string='Grace Period (Hours)',
        default=0,
        help='Additional hours tolerance before notice requirement kicks in'
    )
    
    valid_from = fields.Date(
        string='Valid From',
        help='Policy effective start date (leave blank for no restriction)'
    )
    
    valid_to = fields.Date(
        string='Valid To',
        help='Policy effective end date (leave blank for no restriction)'
    )

    # ==========================================================================
    # CATEGORY 3: WORKING DAYS LIMIT (from snifx_timeoff_limit)
    # ==========================================================================
    
    limit_by_working_days = fields.Boolean(
        string='Batasi Hari Kerja Cuti',
        default=False,
        help='Aktifkan untuk membatasi jumlah hari kerja yang dapat diambil cuti secara berturut-turut'
    )
    
    max_working_days = fields.Integer(
        string='Maksimal Hari Kerja untuk Cuti',
        default=0,
        help='Jumlah maksimal hari kerja berturut-turut yang diizinkan untuk jenis cuti ini. '
             'Contoh: Jika diset 10, maka karyawan hanya boleh cuti maksimal 10 hari kerja berturut-turut. '
             'Dihitung dari work entries atau resource calendar (hari kerja, bukan hari kalender).'
    )
