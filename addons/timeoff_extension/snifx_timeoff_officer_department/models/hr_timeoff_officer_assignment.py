# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class HrTimeoffOfficerAssignment(models.Model):
    _name = 'hr.timeoff.officer.assignment'
    _description = 'Time Off Officer Assignment'
    _order = 'user_id, department_id'
    _rec_name = 'display_name'

    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        ondelete='cascade',
        index=True,
        help='User who will act as Time Off Officer for the assigned department'
    )
    
    department_id = fields.Many2one(
        'hr.department',
        string='Department',
        required=True,
        ondelete='cascade',
        index=True,
        help='Department tree that this officer will manage (includes all sub-departments)'
    )
    
    active = fields.Boolean(
        string='Active',
        default=True,
        help='If inactive, user will immediately lose access to this department tree'
    )
    
    date_from = fields.Date(
        string='Valid From',
        help='Start date of this assignment (optional)'
    )
    
    date_to = fields.Date(
        string='Valid To',
        help='End date of this assignment (optional)'
    )
    
    notes = fields.Text(
        string='Notes',
        help='Additional information about this assignment'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Company',
        default=lambda self: self.env.company,
        required=True
    )
    
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    
    @api.depends('user_id', 'department_id', 'active')
    def _compute_display_name(self):
        """Compute display name for the assignment"""
        for record in self:
            if record.user_id and record.department_id:
                status = '' if record.active else ' [Inactive]'
                record.display_name = f"{record.user_id.name} → {record.department_id.name}{status}"
            else:
                record.display_name = 'New Assignment'
    
    @api.constrains('user_id', 'department_id', 'active')
    def _check_duplicate_assignment(self):
        """Prevent duplicate assignments for same user and department"""
        for record in self:
            if record.active:
                duplicate = self.search([
                    ('id', '!=', record.id),
                    ('user_id', '=', record.user_id.id),
                    ('department_id', '=', record.department_id.id),
                    ('active', '=', True),
                    ('company_id', '=', record.company_id.id)
                ], limit=1)
                
                if duplicate:
                    raise ValidationError(
                        _('Assignment already exists for user "%s" and department "%s".\n'
                          'Please deactivate the existing assignment first.') % 
                        (record.user_id.name, record.department_id.name)
                    )
    
    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        """Validate date range"""
        for record in self:
            if record.date_from and record.date_to:
                if record.date_to < record.date_from:
                    raise ValidationError(
                        _('End date cannot be earlier than start date.')
                    )
    
    def name_get(self):
        """Custom name_get for better display"""
        result = []
        for record in self:
            name = record.display_name or f"{record.user_id.name} - {record.department_id.name}"
            result.append((record.id, name))
        return result
    
    @api.model
    def get_user_assigned_departments(self, user_id=None):
        """
        Get all department IDs assigned to a user (including children)
        This is used by security rules and domain computations
        
        :param user_id: User ID to check (default: current user)
        :return: List of department IDs
        """
        if user_id is None:
            user_id = self.env.user.id
        
        today = fields.Date.today()
        
        # Get active assignments for the user
        assignments = self.search([
            ('user_id', '=', user_id),
            ('active', '=', True),
            ('company_id', '=', self.env.company.id),
            '|',
            ('date_from', '=', False),
            ('date_from', '<=', today),
            '|',
            ('date_to', '=', False),
            ('date_to', '>=', today)
        ])
        
        # Get root department IDs
        root_dept_ids = assignments.mapped('department_id').ids
        
        if not root_dept_ids:
            return []
        
        # Get all child departments (recursive)
        all_dept_ids = self.env['hr.department'].search([
            ('id', 'child_of', root_dept_ids)
        ]).ids
        
        return all_dept_ids
    
    @api.model
    def is_user_officer(self, user_id=None):
        """
        Check if user has any active officer assignments
        
        :param user_id: User ID to check (default: current user)
        :return: Boolean
        """
        dept_ids = self.get_user_assigned_departments(user_id)
        return bool(dept_ids)
    
    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-assign Officer group when creating assignments"""
        records = super().create(vals_list)
        
        # Auto-assign Officer with Balance group to users with assignments
        for record in records:
            if record.user_id and record.active:
                self._ensure_officer_group(record.user_id)
        
        return records
    
    def write(self, vals):
        """Override write to auto-assign/remove Officer group based on assignments"""
        result = super().write(vals)
        
        # If active status or user changed, update group membership
        if 'active' in vals or 'user_id' in vals:
            for record in self:
                if record.user_id:
                    self._ensure_officer_group(record.user_id)
        
        return result
    
    def unlink(self):
        """Override unlink to check if we should remove Officer group"""
        # Store user IDs before deleting records
        user_ids = self.mapped('user_id.id')
        
        result = super().unlink()
        
        # Check each user and remove group if no more assignments
        for user_id in user_ids:
            user = self.env['res.users'].browse(user_id)
            if user.exists():
                self._ensure_officer_group(user)
        
        return result
    
    def _ensure_officer_group(self, user):
        """
        Ensure user has Officer group if they have active assignments,
        or remove it if they don't have any active assignments.
        
        :param user: res.users record
        """
        officer_group = self.env.ref('snifx_timeoff_officer_department.group_timeoff_officer_department')
        
        # Check if user has any active assignments
        has_assignments = self.search_count([
            ('user_id', '=', user.id),
            ('active', '=', True)
        ]) > 0
        
        # Add or remove group based on assignments
        if has_assignments:
            # Add group if not already in it
            if officer_group not in user.groups_id:
                user.sudo().write({
                    'groups_id': [(4, officer_group.id)]
                })
        else:
            # Remove group if no active assignments
            if officer_group in user.groups_id:
                user.sudo().write({
                    'groups_id': [(3, officer_group.id)]
                })
