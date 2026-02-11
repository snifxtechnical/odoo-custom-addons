# -*- coding: utf-8 -*-

from odoo import api, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        """
        Override to hide sensitive tabs for Time Off Officers
        Officers can only see: Resume and Work Information tabs
        """
        res = super(HrEmployee, self).fields_view_get(
            view_id=view_id, 
            view_type=view_type, 
            toolbar=toolbar, 
            submenu=submenu
        )
        
        # Check if user is Time Off Officer (but not HR Manager)
        user = self.env.user
        is_officer = user.has_group('snifx_timeoff_officer_department.group_timeoff_officer_department')
        is_hr_manager = user.has_group('hr_holidays.group_hr_holidays_manager')
        
        # Only apply restrictions to officers who are not HR managers
        if is_officer and not is_hr_manager and view_type == 'form':
            # Note: The actual tab hiding is done in XML views with groups_id
            # This method can be extended for additional runtime restrictions if needed
            pass
        
        return res
