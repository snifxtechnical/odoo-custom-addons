# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError


class HrLeave(models.Model):
    _inherit = 'hr.leave'
    
    can_approve_as_officer = fields.Boolean(
        compute='_compute_can_approve_as_officer',
        string='Can Approve as Officer',
        help='True if current user can approve this leave as Time Off Officer'
    )
    
    officer_activity_created = fields.Boolean(
        string='Officer Activity Created',
        default=False,
        copy=False,
        help='Technical field to track if activity for officers has been created'
    )
    
    @api.depends('employee_id', 'employee_id.department_id', 'state')
    def _compute_can_approve_as_officer(self):
        """
        Check if current user can approve this leave request as officer
        Conditions:
        1. User must have Time Off Officer group
        2. Employee must be in officer's assigned department tree
        3. Leave must not belong to the officer themselves
        
        Note: We cache the department lookup to avoid repeated slow queries.
        Uses sudo() to allow all users to compute this field without access errors.
        """
        user = self.env.user
        
        # Check if user is officer - quick check without database access
        is_officer = user.has_group('snifx_timeoff_officer_department.group_timeoff_officer_department')
        
        if not is_officer:
            # Not an officer - set all to False without querying assignments
            for leave in self:
                leave.can_approve_as_officer = False
            return
        
        # User is officer - now get assignments with sudo() to avoid access errors
        Assignment = self.env['hr.timeoff.officer.assignment'].sudo()
        
        # Get officer's managed departments ONCE (cached for all records in this batch)
        managed_dept_ids = Assignment.get_user_assigned_departments(user.id)
        
        for leave in self:
            # Cannot approve own leave
            if leave.employee_id.user_id.id == user.id:
                leave.can_approve_as_officer = False
                continue
            
            # Check if employee's department is in managed tree
            if leave.employee_id.department_id.id in managed_dept_ids:
                leave.can_approve_as_officer = True
            else:
                leave.can_approve_as_officer = False
    
    def _get_eligible_officer_users(self):
        """
        Get all users with 'Officer with Balance (Enhanced)' group who have access
        to this leave request's employee department (including hierarchical departments).
        
        Returns:
            recordset: res.users recordset of eligible officers
        
        Note: Uses sudo() to allow activity creation without access restrictions.
        """
        self.ensure_one()
        
        if not self.employee_id.department_id:
            return self.env['res.users']
        
        # Use sudo() to access assignment model without permission issues
        Assignment = self.env['hr.timeoff.officer.assignment'].sudo()
        
        # Get all users with the officer group
        officer_group = self.env.ref('snifx_timeoff_officer_department.group_timeoff_officer_department')
        all_officers = officer_group.users
        
        if not all_officers:
            return self.env['res.users']
        
        # Get employee's department and all parent departments
        employee_dept = self.employee_id.department_id
        # Use parent_path for hierarchical check if available, otherwise use child_of
        relevant_dept_ids = self.env['hr.department'].search([
            ('id', 'parent_of', employee_dept.id)
        ]).ids
        
        eligible_officers = self.env['res.users']
        
        for officer in all_officers:
            # Skip if officer is the employee themselves
            if officer.id == self.employee_id.user_id.id:
                continue
            
            # Get departments assigned to this officer (with sudo)
            assigned_dept_ids = Assignment.get_user_assigned_departments(officer.id)
            
            # Check if any assigned department matches (considering hierarchy)
            if set(assigned_dept_ids) & set(relevant_dept_ids):
                eligible_officers |= officer
        
        return eligible_officers
    
        return eligible_officers
    
    def _create_officer_activities(self):
        """
        Create activities for eligible officers when HR Officer approval is needed.
        This complements the standard Odoo notification to 'responsible_ids'.
        
        Activities are created when:
        1. Leave requires HR Officer approval (validation_type = 'hr' or 'both')
        2. Leave state transitions to require officer approval
        3. Activities haven't been created yet (tracked by officer_activity_created)
        """
        ActivityType = self.env['mail.activity.type']
        
        for leave in self:
            # Skip if activities already created
            if leave.officer_activity_created:
                continue
            
            # Skip if no HR Officer approval needed
            validation_type = leave.holiday_status_id.leave_validation_type
            if validation_type not in ('hr', 'both'):
                continue
            
            # Determine which activity type to use based on approval flow
            if validation_type == 'hr':
                # Direct officer approval - use "Time Off Approval"
                activity_type = ActivityType.search([
                    ('name', '=', 'Time Off Approval'),
                    ('res_model', '=', 'hr.leave')
                ], limit=1)
            else:  # 'both'
                # Second tier approval - use "Time Off Second Approve"
                activity_type = ActivityType.search([
                    ('name', '=', 'Time Off Second Approve'),
                    ('res_model', '=', 'hr.leave')
                ], limit=1)
            
            if not activity_type:
                # Fallback to generic activity type if specific ones not found
                activity_type = ActivityType.search([
                    ('name', '=', 'Time Off Approval'),
                    ('res_model', '=', 'hr.leave')
                ], limit=1)
            
            if not activity_type:
                continue
            
            # Get eligible officers
            eligible_officers = leave._get_eligible_officer_users()
            
            # Also include users from responsible_ids if set
            responsible_officers = leave.holiday_status_id.responsible_ids
            all_notified_officers = eligible_officers | responsible_officers
            
            # Create one activity per officer
            for officer in all_notified_officers:
                # Check if activity already exists for this user
                existing_activity = self.env['mail.activity'].search([
                    ('res_id', '=', leave.id),
                    ('res_model_id', '=', self.env['ir.model']._get_id('hr.leave')),
                    ('user_id', '=', officer.id),
                    ('activity_type_id', '=', activity_type.id)
                ], limit=1)
                
                if existing_activity:
                    continue
                
                # Determine summary based on validation type
                if validation_type == 'hr':
                    summary = _('Time Off Approval for %s') % leave.employee_id.name
                else:
                    summary = _('Second Approval for %s') % leave.employee_id.name
                
                # Create activity
                self.env['mail.activity'].create({
                    'activity_type_id': activity_type.id,
                    'res_id': leave.id,
                    'res_model_id': self.env['ir.model']._get_id('hr.leave'),
                    'user_id': officer.id,
                    'summary': summary,
                    'note': _('Please review and approve this %s request.') % leave.holiday_status_id.name,
                })
            
            # Mark as created to avoid duplicates
            leave.officer_activity_created = True
    
    def _check_approval_update(self, state):
        """
        Override Odoo 18 standard check to allow Officers with Balance (Enhanced) group
        to approve leave requests for their assigned departments.
        
        Standard Odoo only allows:
        - hr_holidays.group_hr_holidays_manager (Time Off Manager)
        - hr_holidays.group_hr_holidays_user (Time Off Officer)
        
        We extend this to also allow:
        - snifx_timeoff_officer_department.group_timeoff_officer_department (Officer with Balance Enhanced)
        
        Note: Department-level access is still enforced by record rules.
        """
        user = self.env.user
        
        # Check if user is our custom Officer group
        is_custom_officer = user.has_group('snifx_timeoff_officer_department.group_timeoff_officer_department')
        
        if is_custom_officer:
            # Officers can approve, but not their own requests (checked in action_approve)
            # Record rules will ensure they can only access assigned departments
            return True
        
        # Fall back to standard Odoo check for other users
        return super(HrLeave, self)._check_approval_update(state)
    
    def _check_approval_update(self, state):
        """
        Override Odoo 18 permission check to allow Officers with Balance (Enhanced) group
        to approve leave requests.
        
        Standard Odoo only recognizes:
        - hr_holidays.group_hr_holidays_manager (Time Off Manager)
        - hr_holidays.group_hr_holidays_user (Time Off Officer - standard)
        
        We add recognition for:
        - snifx_timeoff_officer_department.group_timeoff_officer_department (Officer with Balance)
        
        Note: Department-based access control is enforced by record rules,
        not by this permission check.
        """
        current_user = self.env.user
        is_officer = current_user.has_group('snifx_timeoff_officer_department.group_timeoff_officer_department')
        is_manager = current_user.has_group('hr_holidays.group_hr_holidays_manager')
        
        if is_officer or is_manager:
            # Officer or Manager - allow approval
            # Record rules will restrict to assigned departments
            return
        
        # For non-officers, use standard Odoo check
        return super(HrLeave, self)._check_approval_update(state)
    
    def action_approve(self):
        """
        Override to add validation for officers and create activities
        for department-based officers when transitioning to HR Officer approval.
        
        Officers cannot approve their own leave requests
        
        Note: Authorization checks for departments are handled by record rules,
        so we don't need to check here to avoid performance issues.
        """
        user = self.env.user
        is_officer = user.has_group('snifx_timeoff_officer_department.group_timeoff_officer_department')
        
        if is_officer:
            # Check if trying to approve own leave
            own_leaves = self.filtered(lambda l: l.employee_id.user_id.id == user.id)
            if own_leaves:
                raise UserError(
                    _('You cannot approve your own leave request.\n'
                      'Please ask another officer or HR manager to approve it.')
                )
        
        # Call parent method first
        result = super(HrLeave, self).action_approve()
        
        # After approval, check if we need to create activities for officers
        # This happens when:
        # 1. Manager approves and next step is HR Officer (validation_type = 'both')
        # 2. State changes to 'confirm' waiting for HR Officer approval
        for leave in self:
            if leave.state == 'confirm' and leave.holiday_status_id.leave_validation_type == 'both':
                leave._create_officer_activities()
        
        return result
    
    def action_validate(self, check_state=True):
        """
        Override to add validation for officers
        Officers cannot validate their own leave requests
        
        Note: Authorization checks for departments are handled by record rules,
        so we don't need to check here to avoid performance issues.
        """
        user = self.env.user
        is_officer = user.has_group('snifx_timeoff_officer_department.group_timeoff_officer_department')
        
        if is_officer:
            # Check if trying to validate own leave
            own_leaves = self.filtered(lambda l: l.employee_id.user_id.id == user.id)
            if own_leaves:
                raise UserError(
                    _('You cannot validate your own leave request.\n'
                      'Please ask another officer or HR manager to validate it.')
                )
        
        return super(HrLeave, self).action_validate(check_state)
    
    @api.model_create_multi
    def create(self, vals_list):
        """
        Override create to trigger activity creation for direct HR Officer approval
        (when validation_type = 'hr')
        """
        leaves = super(HrLeave, self).create(vals_list)
        
        # Create activities for leaves that require direct HR Officer approval
        for leave in leaves:
            if leave.state == 'confirm' and leave.holiday_status_id.leave_validation_type == 'hr':
                leave._create_officer_activities()
        
        return leaves
    
    def write(self, vals):
        """
        Override write to trigger activity creation when state changes to 'confirm'
        and HR Officer approval is needed
        """
        result = super(HrLeave, self).write(vals)
        
        # Check if state changed to 'confirm' (waiting for approval)
        if 'state' in vals and vals['state'] == 'confirm':
            for leave in self:
                # Create activities if not already created
                if leave.holiday_status_id.leave_validation_type in ('hr', 'both'):
                    leave._create_officer_activities()
        
        return result
