# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Auto-approval for top management
    # Only HR Officers and above can see/edit this field
    auto_approve_as_top_management = fields.Boolean(
        string='Auto-Approve as Top Management',
        default=False,
        groups='hr.group_hr_user',  # Only HR Officers can access
        help='When enabled, this employee will automatically approve their own time-off requests '
             'without requiring manual approval. Typically used for top management (CEO, Director, etc.)'
    )
    
    # Override smart detection for specific employees
    # Only HR Officers and above can see/edit this field
    force_single_approval_level = fields.Boolean(
        string='Use Single Approval Level Only',
        default=False,
        groups='hr.group_hr_user',  # Only HR Officers can access
        help='When enabled, this employee will always require only 1 approval level (direct manager only), '
             'overriding the smart detection system. Useful for employees who do not need senior management approval.'
    )
    
    # Note: Delegation fields removed to avoid access errors
    # Can be re-added later with proper security if needed
    
    def get_effective_approver(self):
        """
        Get the effective approver (considering delegation)
        Returns user_id
        """
        self.ensure_one()
        return self.user_id
