# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrDepartment(models.Model):
    _inherit = 'hr.department'
    
    # Organization Chart Approval Configuration
    use_orgchart_approval = fields.Boolean(
        string='Use Organization Chart Approval',
        default=True,
        help='If checked, leave approvals will use organization chart smart detection. '
             'If unchecked, only the direct manager will approve (simple 1-level approval).'
    )
    
    # Manual selection: Officers to notify
    notification_officer_ids = fields.Many2many(
        'res.users',
        'hr_department_notification_officer_rel',
        'department_id',
        'user_id',
        string='Notification Officers',
        help='Officers who will receive FYI notifications for this department (max 2 recommended). '
             'Select from officers with "Officer: Manage Department Requests" group.'
    )
    
    notification_officer_count = fields.Integer(
        compute='_compute_notification_count',
        string='Notification Count',
        store=False
    )
    
    @api.depends('notification_officer_ids')
    def _compute_notification_count(self):
        """Count selected notification officers"""
        for dept in self:
            dept.notification_officer_count = len(dept.notification_officer_ids)
    
    @api.onchange('notification_officer_ids')
    def _onchange_notification_officers(self):
        """Warn if more than 2 officers selected"""
        if len(self.notification_officer_ids) > 2:
            return {
                'warning': {
                    'title': 'Too Many Officers',
                    'message': 'More than 2 notification officers selected. '
                              'This may cause notification spam. '
                              'Recommended: Maximum 2 officers per department.'
                }
            }
