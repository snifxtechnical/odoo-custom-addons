# -*- coding: utf-8 -*-

from odoo import api, fields, models


class ResourceCalendarLeaves(models.Model):
    _inherit = 'resource.calendar.leaves'
    
    @api.model
    def default_get(self, fields_list):
        """
        Override default_get to use sudo() context for Officers (READ operation).
        This fixes issues when form loads with computed fields that check project access.
        
        Note: Officers can VIEW public holidays but cannot CREATE/EDIT/DELETE them.
        Only Administrators can manage public holidays.
        """
        user = self.env.user
        is_officer = user.has_group('snifx_timeoff_officer_department.group_timeoff_officer_department')
        
        if is_officer:
            # Use sudo() to bypass access checks on related models during default value computation
            res = super(ResourceCalendarLeaves, self.sudo()).default_get(fields_list)
            return res
        else:
            return super(ResourceCalendarLeaves, self).default_get(fields_list)
    
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """
        Override fields_get to use sudo() context for Officers (READ operation).
        This ensures Officers can see field definitions without access errors.
        """
        user = self.env.user
        is_officer = user.has_group('snifx_timeoff_officer_department.group_timeoff_officer_department')
        
        if is_officer:
            return super(ResourceCalendarLeaves, self.sudo()).fields_get(allfields, attributes)
        else:
            return super(ResourceCalendarLeaves, self).fields_get(allfields, attributes)
    
    def read(self, fields=None, load='_classic_read'):
        """
        Override read to use sudo() context for Officers (READ operation).
        This ensures Officers can read public holiday records with related project fields.
        
        Officers can VIEW public holidays but cannot CREATE/EDIT/DELETE them.
        """
        user = self.env.user
        is_officer = user.has_group('snifx_timeoff_officer_department.group_timeoff_officer_department')
        
        if is_officer:
            # For Officers, use sudo() to bypass related model access checks for reading
            return super(ResourceCalendarLeaves, self.sudo()).read(fields, load)
        else:
            # For non-officers, use standard flow
            return super(ResourceCalendarLeaves, self).read(fields, load)

