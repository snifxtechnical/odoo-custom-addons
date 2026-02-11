# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
import logging

_logger = logging.getLogger(__name__)


class LeaveApprovalLevel(models.Model):
    _name = 'leave.approval.level'
    _description = 'Leave Approval Level'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'level, create_date'
    _rec_name = 'display_name'

    # Basic Info
    leave_id = fields.Many2one(
        'hr.leave',
        string='Leave Request',
        required=True,
        ondelete='cascade',
        index=True
    )
    employee_id = fields.Many2one(
        'hr.employee',
        related='leave_id.employee_id',
        string='Employee',
        store=True,
        readonly=True
    )
    leave_description = fields.Text(
        related='leave_id.name',
        string='Leave Description',
        readonly=True,
        help="Description of the leave request"
    )
    leave_date_from = fields.Datetime(
        related='leave_id.date_from',
        string='Date From',
        readonly=True
    )
    leave_date_to = fields.Datetime(
        related='leave_id.date_to',
        string='Date To',
        readonly=True
    )
    leave_type_id = fields.Many2one(
        related='leave_id.holiday_status_id',
        string='Time Off Type',
        readonly=True
    )
    
    # Approval Info
    level = fields.Integer(
        string='Approval Level',
        required=True,
        help="1 = Direct Manager, 2 = Manager's Manager, etc."
    )
    approver_id = fields.Many2one(
        'res.users',
        string='Approver',
        required=True,
        help="User who needs to approve at this level"
    )
    approver_employee_id = fields.Many2one(
        'hr.employee',
        string='Approver Employee',
        compute='_compute_approver_employee',
        store=True
    )
    
    # Status
    state = fields.Selection([
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('skipped', 'Skipped'),
        ('delegated', 'Delegated'),
    ], string='Status', default='pending', required=True, index=True)
    
    # Approval Details
    action_date = fields.Datetime(
        string='Action Date',
        readonly=True,
        help="When the approval/rejection was done"
    )
    comments = fields.Text(
        string='Comments',
        help="Approver's comments"
    )
    
    # Delegation
    delegated_to_id = fields.Many2one(
        'res.users',
        string='Delegated To',
        help="If approver delegates, who receives it"
    )
    original_approver_id = fields.Many2one(
        'res.users',
        string='Original Approver',
        help="Original approver if this was delegated"
    )
    
    # Computed
    display_name = fields.Char(
        string='Display Name',
        compute='_compute_display_name',
        store=True
    )
    is_current_level = fields.Boolean(
        string='Current Level',
        compute='_compute_is_current_level',
        store=True,
        help="Is this the current pending approval level?"
    )
    deadline = fields.Datetime(
        string='Approval Deadline',
        compute='_compute_deadline',
        store=True,
        help="Expected approval date"
    )
    is_overdue = fields.Boolean(
        string='Overdue',
        compute='_compute_is_overdue',
        store=True
    )
    
    # Activity tracking
    activity_ids = fields.One2many(
        'mail.activity',
        'res_id',
        string='Activities',
        domain=[('res_model', '=', 'leave.approval.level')]
    )

    @api.depends('level', 'approver_id', 'leave_id')
    def _compute_display_name(self):
        for record in self:
            if record.leave_id and record.approver_id:
                record.display_name = f"Level {record.level}: {record.approver_id.name} - {record.leave_id.employee_id.name}"
            else:
                record.display_name = f"Level {record.level}"

    @api.depends('approver_id')
    def _compute_approver_employee(self):
        for record in self:
            if record.approver_id:
                record.approver_employee_id = self.env['hr.employee'].search([
                    ('user_id', '=', record.approver_id.id)
                ], limit=1)
            else:
                record.approver_employee_id = False

    @api.depends('leave_id.approval_level_ids.state', 'level')
    def _compute_is_current_level(self):
        for record in self:
            if record.state == 'pending':
                # Check if all previous levels are approved
                previous_levels = record.leave_id.approval_level_ids.filtered(
                    lambda l: l.level < record.level
                )
                all_previous_approved = all(
                    l.state in ['approved', 'skipped'] for l in previous_levels
                )
                record.is_current_level = all_previous_approved
            else:
                record.is_current_level = False

    @api.depends('create_date', 'leave_id.holiday_status_id')
    def _compute_deadline(self):
        for record in self:
            if record.create_date and record.leave_id.holiday_status_id:
                # Default: 24 hours per level, or configured SLA
                hours = record.leave_id.holiday_status_id.approval_sla_hours or 24
                record.deadline = record.create_date + timedelta(hours=hours * record.level)
            else:
                record.deadline = False

    @api.depends('deadline', 'state')
    def _compute_is_overdue(self):
        now = fields.Datetime.now()
        for record in self:
            if record.state == 'pending' and record.deadline:
                record.is_overdue = now > record.deadline
            else:
                record.is_overdue = False

    def action_approve(self):
        """Approve the leave at this level (supports parallel approval)"""
        self.ensure_one()
        
        _logger.info(f"=== action_approve called for Level {self.level} (ID: {self.id}) ===")
        _logger.info(f"  Leave ID: {self.leave_id.id}")
        _logger.info(f"  Approver: {self.approver_id.name}")
        _logger.info(f"  Current user: {self.env.user.name}")
        _logger.info(f"  Level state before: {self.state}")
        _logger.info(f"  is_current_level: {self.is_current_level}")
        
        if self.state != 'pending':
            raise UserError(_('This approval has already been processed.'))
        
        if not self.is_current_level:
            raise UserError(_('Previous levels must be approved first.'))
        
        # Check if current user is the approver
        if self.env.user != self.approver_id and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            raise UserError(_('You are not authorized to approve this request.'))
        
        # Approve this record - use sudo to write (approver may not have direct write access)
        _logger.info(f"  ✅ Approving Level {self.level}...")
        self.sudo().write({
            'state': 'approved',
            'action_date': fields.Datetime.now(),
        })
        _logger.info(f"  Level {self.level} state after write: approved")
        
        # PARALLEL APPROVAL: If there are other approvers at same level, approve them too
        same_level_pending = self.env['leave.approval.level'].search([
            ('leave_id', '=', self.leave_id.id),
            ('level', '=', self.level),
            ('id', '!=', self.id),
            ('state', '=', 'pending')
        ])
        
        if same_level_pending:
            _logger.info(f"  Parallel approval: Auto-approving {len(same_level_pending)} other approvers at level {self.level}")
            same_level_pending.write({
                'state': 'approved',
                'action_date': fields.Datetime.now(),
                'comments': f'Auto-approved (parallel approval by {self.approver_id.name})'
            })
        
        # Post message - use sudo to avoid permission issues
        try:
            self.leave_id.sudo().message_post(
                body=_('Approved by %s (Level %s)') % (self.approver_id.name, self.level),
                subtype_xmlid='mail.mt_comment'
            )
        except Exception as e:
            _logger.warning(f"Could not post approval message: {e}")
        
        # Check if this was the final level - use sudo
        _logger.info(f"  Calling _check_approval_completion()...")
        self.leave_id.sudo()._check_approval_completion()
        
        # CRITICAL: Recompute user_has_pending_approval field to update filter
        _logger.info(f"  Recomputing user_has_pending_approval field...")
        self.leave_id.sudo()._compute_user_has_pending_approval()
        
        # Notify next level
        self._notify_next_level()
        
        _logger.info(f"=== action_approve completed for Level {self.level} ===")
        return True

    def action_reject(self):
        """Reject the leave at this level"""
        self.ensure_one()
        
        if self.state != 'pending':
            raise UserError(_('This approval has already been processed.'))
        
        if not self.is_current_level:
            raise UserError(_('Previous levels must be approved first.'))
        
        # Check if current user is the approver
        if self.env.user != self.approver_id and not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            raise UserError(_('You are not authorized to reject this request.'))
        
        # Use sudo to write (approver may not have direct write access)
        self.sudo().write({
            'state': 'rejected',
            'action_date': fields.Datetime.now(),
        })
        
        # Reject the entire leave request - use sudo as it may update other approval levels
        self.leave_id.sudo().action_refuse()
        
        # CRITICAL: Recompute user_has_pending_approval field to update filter
        _logger.info(f"  Recomputing user_has_pending_approval field after rejection...")
        self.leave_id.sudo()._compute_user_has_pending_approval()
        
        # Post message - use sudo to avoid permission issues
        try:
            self.leave_id.sudo().message_post(
                body=_('Rejected by %s (Level %s): %s') % (
                    self.approver_id.name,
                    self.level,
                    self.comments or 'No comment'
                ),
                subtype_xmlid='mail.mt_comment'
            )
        except Exception as e:
            _logger.warning(f"Could not post rejection message: {e}")
        
        return True

    def action_delegate(self, delegate_to_id):
        """Delegate approval to another user"""
        self.ensure_one()
        
        if self.state != 'pending':
            raise UserError(_('This approval has already been processed.'))
        
        delegate_to = self.env['res.users'].browse(delegate_to_id)
        
        self.write({
            'state': 'delegated',
            'delegated_to_id': delegate_to.id,
            'original_approver_id': self.approver_id.id,
            'approver_id': delegate_to.id,
        })
        
        # Post message - use sudo to avoid permission issues
        try:
            self.leave_id.sudo().message_post(
                body=_('Approval delegated from %s to %s (Level %s)') % (
                    self.original_approver_id.name,
                    delegate_to.name,
                    self.level
                ),
                subtype_xmlid='mail.mt_comment'
            )
        except Exception as e:
            _logger.warning(f"Could not post delegation message: {e}")
        
        # Notify delegated person
        self._send_notification()
        
        return True

    def action_skip(self):
        """Skip this level (e.g., approver is absent)"""
        self.ensure_one()
        
        # Only HR managers can skip
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
            raise UserError(_('Only HR Managers can skip approval levels.'))
        
        # Use sudo to write
        self.sudo().write({
            'state': 'skipped',
            'action_date': fields.Datetime.now(),
            'comments': 'Skipped by HR Manager: %s' % self.env.user.name
        })
        
        # Post message - use sudo to avoid permission issues
        try:
            self.leave_id.sudo().message_post(
                body=_('Level %s skipped by %s') % (self.level, self.env.user.name),
                subtype_xmlid='mail.mt_comment'
            )
        except Exception as e:
            _logger.warning(f"Could not post skip message: {e}")
        
        # Check if next level needs notification
        self._notify_next_level()
        
        return True

    def _send_notification(self):
        """Send email notification to approver"""
        self.ensure_one()
        
        template = self.env.ref(
            'hr_leave_orgchart_approval.email_template_approval_notification',
            raise_if_not_found=False
        )
        
        if template:
            try:
                template.send_mail(self.id, force_send=True)
            except Exception as e:
                _logger.warning(f"Failed to send email notification: {e}")
        
        # Create activity - with error handling
        try:
            activity_type = self.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
            if activity_type:
                self.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Leave Approval Required'),
                    note=_(
                        'Please review and approve/reject leave request from %s\n'
                        'From: %s\n'
                        'To: %s\n'
                        'Days: %s'
                    ) % (
                        self.employee_id.name,
                        self.leave_id.request_date_from,
                        self.leave_id.request_date_to,
                        self.leave_id.number_of_days
                    ),
                    user_id=self.approver_id.id
                )
        except Exception as e:
            # If activity creation fails, just log it (email is more important)
            _logger.warning(f"Failed to create activity: {e}")

    def _notify_next_level(self):
        """Notify the next level approver"""
        next_level = self.env['leave.approval.level'].search([
            ('leave_id', '=', self.leave_id.id),
            ('level', '=', self.level + 1),
            ('state', '=', 'pending')
        ], limit=1)
        
        if next_level:
            next_level._send_notification()

    @api.model
    def _cron_reminder_overdue(self):
        """Send reminders for overdue approvals"""
        overdue_approvals = self.search([
            ('state', '=', 'pending'),
            ('is_current_level', '=', True),
            ('is_overdue', '=', True)
        ])
        
        for approval in overdue_approvals:
            # Send reminder email
            template = self.env.ref(
                'hr_leave_orgchart_approval.email_template_overdue_reminder',
                raise_if_not_found=False
            )
            if template:
                template.send_mail(approval.id, force_send=True)

    def open_record(self):
        """
        Override default action when clicking record in tree view.
        Instead of opening approval level form, open the related HR Leave form.
        
        This provides better UX - users can see full request details with
        all approval levels, chatter, and can approve directly from there.
        
        Returns:
            dict: Action to open hr.leave form
        """
        self.ensure_one()
        
        # Build descriptive title
        title = _('Time Off Request - %s') % self.leave_id.employee_id.name
        
        return {
            'type': 'ir.actions.act_window',
            'name': title,
            'res_model': 'hr.leave',
            'res_id': self.leave_id.id,
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'from_approval_level': True,
                'active_id': self.leave_id.id,
                'default_id': self.leave_id.id,
            },
            'flags': {
                'form': {
                    'action_buttons': True,
                }
            }
        }

    def unlink(self):
        """Clean up activities and notifications before deleting"""
        # Clean activities linked to these approval levels
        activities = self.env['mail.activity'].search([
            ('res_model', '=', 'leave.approval.level'),
            ('res_id', 'in', self.ids)
        ])
        if activities:
            _logger.info(f"Cleaning {len(activities)} activities before deleting approval levels")
            activities.unlink()
        
        # Clean messages and notifications
        messages = self.env['mail.message'].search([
            ('model', '=', 'leave.approval.level'),
            ('res_id', 'in', self.ids)
        ])
        if messages:
            _logger.info(f"Cleaning {len(messages)} messages before deleting approval levels")
            messages.unlink()
        
        return super(LeaveApprovalLevel, self).unlink()
