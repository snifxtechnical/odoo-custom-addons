# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    # Organization Chart Approval Settings
    use_orgchart_approval = fields.Boolean(
        string='Use Organization Chart Approval',
        default=False,
        help="Enable multi-level approval based on organization chart hierarchy"
    )
    
    orgchart_approval_levels = fields.Integer(
        string='Number of Approval Levels',
        default=2,
        help="How many levels up in the org chart need to approve (e.g., 2 = Direct Manager + Manager's Manager)"
    )
    
    require_department_head_approval = fields.Boolean(
        string='Require Department Head Approval',
        default=False,
        help="Add department head to approval chain regardless of org chart levels"
    )
    
    require_hr_approval = fields.Boolean(
        string='Require HR Manager Approval',
        default=False,
        help="Add HR Manager as final approver"
    )
    
    require_officer_final_approval = fields.Boolean(
        string='Require Time Off Officer Final Approval',
        default=False,
        help="Add Time Off Officer as final approver (from employee's department)"
    )
    
    require_top_management = fields.Boolean(
        string='Require Top Management Approval',
        default=False,
        help="Require approval from top management (CEO, etc.) for this leave type"
    )
    
    # SLA Settings
    approval_sla_hours = fields.Float(
        string='Approval SLA (Hours)',
        default=24.0,
        help="Expected time for each approval level in hours"
    )
    
    # Auto-approval settings
    auto_approve_if_manager_absent = fields.Boolean(
        string='Auto-approve if Manager Absent',
        default=False,
        help="Automatically approve level if approver is on leave"
    )
    
    skip_manager_if_subordinate = fields.Boolean(
        string='Skip Manager if Subordinate',
        default=True,
        help="Skip approval level if approver is a subordinate of the employee"
    )

    @api.constrains('orgchart_approval_levels')
    def _check_approval_levels(self):
        for record in self:
            if record.use_orgchart_approval and record.orgchart_approval_levels < 1:
                raise ValidationError(_('Number of approval levels must be at least 1.'))
            if record.orgchart_approval_levels > 10:
                raise ValidationError(_('Number of approval levels cannot exceed 10.'))

    @api.onchange('use_orgchart_approval')
    def _onchange_use_orgchart_approval(self):
        """Disable standard validation if using org chart"""
        if self.use_orgchart_approval:
            self.validation_type = 'no_validation'

    def get_approval_chain_preview(self, employee_id):
        """
        Preview approval chain for a specific employee
        Used in UI to show who will approve
        """
        self.ensure_one()
        
        if not self.use_orgchart_approval:
            return []
        
        # Create temporary leave record (not saved) to get chain
        temp_leave = self.env['hr.leave'].new({
            'employee_id': employee_id,
            'holiday_status_id': self.id,
        })
        
        chain = temp_leave._get_approval_chain_from_orgchart()
        
        # Return list of dicts with user info
        return [{
            'level': idx + 1,
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'employee_name': user.employee_id.name if user.employee_id else '',
            'job_title': user.employee_id.job_title if user.employee_id else '',
        } for idx, user in enumerate(chain)]
