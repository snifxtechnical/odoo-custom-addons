# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'
    
    # Override holiday_status_id field to make it readonly after submit
    holiday_status_id = fields.Many2one(
        'hr.leave.type',
        string="Time Off Type",
        required=True,  # Must be selected before saving
        default=lambda self: False,  # Force False/empty - no default!
        readonly=True,  # Default readonly
        states={
            'draft': [('readonly', False)],  # Editable only in draft
            'refuse': [('readonly', False)], # Editable if refused (to allow correction)
        },
        tracking=True,  # Track changes in chatter
        help="Time off type cannot be changed after submission."
    )
    
    @api.model
    def default_get(self, fields_list):
        """
        Override default_get to ensure time off type is empty
        This forces user to make conscious selection
        """
        res = super(HrLeave, self).default_get(fields_list)
        
        # Force holiday_status_id to be empty/False
        if 'holiday_status_id' in fields_list:
            res['holiday_status_id'] = False
        
        _logger.info("Leave creation: Time off type set to empty (user must select)")
        
        return res
    
    @api.constrains('holiday_status_id', 'state')
    def _check_timeoff_type_change_after_submit(self):
        """
        Prevent changing time off type after submission
        
        This ensures:
        1. Approval chain integrity
        2. Correct workflow followed
        3. Prevention of workflow bypass/abuse
        4. Accurate leave balance tracking
        """
        for leave in self:
            # Skip validation for new records (no origin)
            if not leave._origin:
                continue
            
            # Only check if state is beyond draft (submitted or later)
            if leave.state not in ('draft', 'refuse'):
                # Get original time off type
                original_type = leave._origin.holiday_status_id
                current_type = leave.holiday_status_id
                
                # Check if type was changed
                if original_type and original_type != current_type:
                    _logger.warning(
                        f"Attempt to change time off type blocked: "
                        f"Leave ID {leave.id}, User {self.env.user.name}, "
                        f"From '{original_type.name}' to '{current_type.name}'"
                    )
                    
                    raise ValidationError(_(
                        '⚠️ Time Off Type Change Not Allowed!\n\n'
                        'You cannot change the time off type after submission.\n\n'
                        'Current Type: %s\n'
                        'Attempted Change: %s\n\n'
                        'Reason: Changing the type after submission would break the approval workflow '
                        'and create inconsistencies in your leave balance.\n\n'
                        'If you need a different time off type:\n'
                        '1. Cancel this time off request\n'
                        '2. Create a new request with the correct type'
                    ) % (original_type.name, current_type.name))
    
    @api.onchange('holiday_status_id')
    def _onchange_holiday_status_id_warning(self):
        """
        Show warning if user tries to change time off type after submission
        This provides early feedback in the UI before validation error
        """
        if self._origin and self.state not in ('draft', 'refuse'):
            original_type = self._origin.holiday_status_id
            if original_type and original_type != self.holiday_status_id:
                return {
                    'warning': {
                        'title': _('Cannot Change Time Off Type'),
                        'message': _(
                            'Time off type cannot be changed after submission.\n'
                            'This change will not be saved.'
                        ),
                    }
                }
