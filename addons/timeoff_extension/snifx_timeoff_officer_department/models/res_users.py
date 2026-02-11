# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    # Custom dropdown field for Time Off (Extra) access
    # This field syncs with the actual group assignment
    timeoff_extra_access = fields.Selection(
        selection=[
            ('none', ''),  # Empty/No access
            ('officer_dept', 'Officer: Manage Department Requests'),
        ],
        string='Time Off (Extra)',
        compute='_compute_timeoff_extra_access',
        inverse='_inverse_timeoff_extra_access',
        store=False,  # Computed field, not stored
        help='Extra Time Off access level for department-based officer management. Syncs with group assignment.'
    )
    
    @api.depends('groups_id')
    def _compute_timeoff_extra_access(self):
        """Compute Time Off (Extra) access level based on group membership"""
        officer_group = self.env.ref('snifx_timeoff_officer_department.group_timeoff_officer_department', raise_if_not_found=False)
        
        for user in self:
            if officer_group and officer_group in user.groups_id:
                user.timeoff_extra_access = 'officer_dept'
            else:
                user.timeoff_extra_access = 'none'
    
    def _inverse_timeoff_extra_access(self):
        """Update group membership based on Time Off (Extra) access level selection"""
        officer_group = self.env.ref('snifx_timeoff_officer_department.group_timeoff_officer_department', raise_if_not_found=False)
        
        if not officer_group:
            return
        
        for user in self:
            if user.timeoff_extra_access == 'officer_dept':
                # Add user to officer group
                if officer_group not in user.groups_id:
                    user.groups_id = [(4, officer_group.id)]
            else:  # 'none'
                # Remove user from officer group
                if officer_group in user.groups_id:
                    user.groups_id = [(3, officer_group.id)]
    
    timeoff_officer_assignment_ids = fields.One2many(
        'hr.timeoff.officer.assignment',
        'user_id',
        string='Time Off Officer Assignments',
        help='Department assignments for Time Off Officer role'
    )
    
    timeoff_officer_root_dept_ids = fields.Many2many(
        'hr.department',
        compute='_compute_timeoff_officer_root_dept_ids',
        string='Root Departments Managed',
        help='Root departments assigned to this officer (used in record rules with child_of)'
    )
    
    timeoff_officer_dept_ids = fields.Many2many(
        'hr.department',
        compute='_compute_timeoff_officer_dept_ids',
        string='Managed Departments',
        help='All departments this user manages as Time Off Officer (including sub-departments)'
    )
    
    is_timeoff_officer = fields.Boolean(
        compute='_compute_is_timeoff_officer',
        string='Is Time Off Officer',
        help='True if user has any active officer assignments'
    )
    
    @api.depends('timeoff_officer_assignment_ids', 
                 'timeoff_officer_assignment_ids.active',
                 'timeoff_officer_assignment_ids.department_id',
                 'timeoff_officer_assignment_ids.date_from',
                 'timeoff_officer_assignment_ids.date_to')
    def _compute_timeoff_officer_root_dept_ids(self):
        """Compute ROOT departments assigned to this user as officer"""
        today = fields.Date.today()
        
        for user in self:
            # Get active assignments for today
            active_assignments = user.timeoff_officer_assignment_ids.filtered(
                lambda a: a.active and
                (not a.date_from or a.date_from <= today) and
                (not a.date_to or a.date_to >= today)
            )
            
            # Get only the root departments (not the children)
            root_depts = active_assignments.mapped('department_id')
            user.timeoff_officer_root_dept_ids = [(6, 0, root_depts.ids)]
    
    @api.depends('timeoff_officer_assignment_ids', 
                 'timeoff_officer_assignment_ids.active',
                 'timeoff_officer_assignment_ids.department_id',
                 'timeoff_officer_assignment_ids.date_from',
                 'timeoff_officer_assignment_ids.date_to')
    def _compute_timeoff_officer_dept_ids(self):
        """Compute all departments managed by this user as officer"""
        Assignment = self.env['hr.timeoff.officer.assignment']
        
        for user in self:
            dept_ids = Assignment.get_user_assigned_departments(user.id)
            user.timeoff_officer_dept_ids = [(6, 0, dept_ids)]
    
    @api.depends('timeoff_officer_assignment_ids',
                 'timeoff_officer_assignment_ids.active')
    def _compute_is_timeoff_officer(self):
        """Check if user is an active time off officer"""
        Assignment = self.env['hr.timeoff.officer.assignment']
        
        for user in self:
            user.is_timeoff_officer = Assignment.is_user_officer(user.id)
