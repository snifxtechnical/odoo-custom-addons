# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import logging

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _get_work_entries_data(self, employee, date_start, date_stop):
        """Get work entries with sudo() for read access - SAFE"""
        try:
            return self.env['hr.work.entry'].sudo().search([
                ('employee_id', '=', employee.id),
                ('date_start', '>=', date_start),
                ('date_stop', '<=', date_stop),
                ('state', '=', 'validated'),
            ])
        except:
            return self.env['hr.work.entry']

    def _calculate_business_days_between(self, date_from, date_to):
        """
        Calculate business days between two dates (EXCLUSIVE end date).
        
        Args:
            date_from: Start date (included)
            date_to: End date (EXCLUDED)
            
        Returns:
            int: Number of business days (Mon-Fri only)
        """
        days = 0
        current = date_from.date() if isinstance(date_from, datetime) else date_from
        end = date_to.date() if isinstance(date_to, datetime) else date_to
        
        # Count from date_from UP TO (but not including) date_to
        while current < end:  # Changed from <= to <
            if current.weekday() < 5:  # Monday=0, Friday=4
                days += 1
            current += timedelta(days=1)
        
        return days

    def _get_resource_calendar(self):
        self.ensure_one()
        return (self.employee_id.resource_calendar_id or 
                self.employee_id.company_id.resource_calendar_id or 
                self.env['resource.calendar'])

    def _calculate_notice_deadline(self, leave_type, request_date):
        """
        Calculate the deadline for minimum notice requirement.
        
        Args:
            leave_type: hr.leave.type record
            request_date: datetime.date object - the start date of the leave request
            
        Returns:
            datetime.date: The deadline date by which the request should have been submitted
        
        Note: Grace hours are NOT applied here. They're applied when comparing with current time.
        """
        # request_date is already a date object (converted in _validate_minimum_notice)
        if leave_type.min_notice_unit == 'weeks':
            return request_date - timedelta(weeks=leave_type.min_notice_qty)
        elif leave_type.min_notice_unit == 'business_days':
            deadline, days = request_date, leave_type.min_notice_qty
            while days > 0:
                deadline -= timedelta(days=1)
                if deadline.weekday() < 5:
                    days -= 1
            return deadline
        # Default: calendar days
        return request_date - timedelta(days=leave_type.min_notice_qty)

    def _is_user_exempt(self, leave_type):
        return bool(leave_type.exempt_group_ids & self.env.user.groups_id) if leave_type.exempt_group_ids else False

    def _is_rule_applicable(self, leave_type):
        self.ensure_one()
        if leave_type.scope_mode == 'department':
            return self.employee_id.department_id == leave_type.department_id
        elif leave_type.scope_mode == 'category':
            return leave_type.category_id in self.employee_id.category_ids
        return True

    def _is_within_validity_period(self, leave_type):
        today = fields.Date.today()
        return not ((leave_type.valid_from and today < leave_type.valid_from) or 
                   (leave_type.valid_to and today > leave_type.valid_to))

    @api.constrains('date_from', 'date_to', 'holiday_status_id', 'employee_id')
    def _check_time_off_policy(self):
        for leave in self:
            if leave.state in ('draft', 'confirm'):
                leave._validate_date_restrictions()
                leave._validate_minimum_notice()
                leave._validate_working_days_limit()

    def _validate_date_restrictions(self):
        self.ensure_one()
        if not self.date_from:
            return
        lt, today = self.holiday_status_id, fields.Date.today()
        rd = self.date_from.date() if isinstance(self.date_from, datetime) else self.date_from
        if not lt.allow_future_request and rd > today:
            raise ValidationError(_('Tidak dapat mengajukan cuti untuk tanggal masa depan.\nJenis: %s') % lt.name)
        if lt.max_backdate_days == 0 and rd < today:
            raise ValidationError(_('Tidak dapat mengajukan cuti tanggal mundur.\nJenis: %s') % lt.name)
        if lt.max_backdate_days > 0 and rd < (today - timedelta(days=lt.max_backdate_days)):
            raise ValidationError(_('Melebihi batas mundur %s hari') % lt.max_backdate_days)

    def _validate_minimum_notice(self):
        """
        Validate minimum notice requirement.
        
        FIXED: Properly handle datetime vs date comparison by converting both to date.
        Grace hours are applied by adjusting the current time before converting to date.
        """
        self.ensure_one()
        lt = self.holiday_status_id
        
        # Early returns for non-applicable cases
        if not lt.enable_min_notice or self._is_user_exempt(lt) or not self._is_rule_applicable(lt) or not self._is_within_validity_period(lt):
            return
        if lt.threshold_days > 0 and self.number_of_days < lt.threshold_days:
            return
        
        # Convert request date to date object
        rd = self.date_from.date() if isinstance(self.date_from, datetime) else self.date_from
        
        # Calculate deadline (returns date)
        deadline = self._calculate_notice_deadline(lt, rd)
        
        # Get current time and apply grace hours
        now = fields.Datetime.now()
        if lt.grace_hours > 0:
            now = now + timedelta(hours=lt.grace_hours)
        
        # CRITICAL FIX: Convert now to date for comparison
        # This ensures we're comparing date with date (not datetime with date)
        current_date = now.date()
        
        # Compare dates
        if current_date > deadline:
            raise ValidationError(
                _('Tidak memenuhi pemberitahuan minimum: %s %s sebelum tanggal cuti.\n'
                  'Deadline: %s\n'
                  'Tanggal pengajuan: %s') % (
                    lt.min_notice_qty,
                    dict(lt._fields['min_notice_unit'].selection)[lt.min_notice_unit],
                    deadline.strftime('%d/%m/%Y'),
                    current_date.strftime('%d/%m/%Y')
                )
            )

    def _validate_working_days_limit(self):
        """
        Validate working days limit.
        
        FIXED: Use Odoo's number_of_days directly instead of recalculating,
        which was causing double counting (4 days → 8 days).
        
        The issue was that number_of_days already correctly calculated by Odoo,
        but we were recalculating with inclusive end date logic causing 2x count.
        """
        self.ensure_one()
        lt = self.holiday_status_id
        
        if not lt.limit_by_working_days or lt.max_working_days <= 0:
            return
        
        # CRITICAL FIX: Use Odoo's calculation directly
        # Odoo already calculates number_of_days correctly considering:
        # - Work schedule
        # - Public holidays
        # - Half days
        # - Resource calendar
        
        # For working days limit, we use number_of_days from Odoo
        # This is already calculated correctly by hr.leave model
        working_days_requested = self.number_of_days
        
        # Validate against limit
        if working_days_requested > lt.max_working_days:
            raise ValidationError(
                _('Permintaan cuti melebihi batas hari kerja yang diizinkan.\n'
                  'Batas maksimal: %s hari kerja\n'
                  'Anda mengajukan: %s hari\n'
                  'Periode: %s s/d %s') % (
                    lt.max_working_days,
                    working_days_requested,
                    self.date_from.strftime('%d/%m/%Y') if isinstance(self.date_from, datetime) else self.date_from.strftime('%d/%m/%Y'),
                    self.date_to.strftime('%d/%m/%Y') if isinstance(self.date_to, datetime) else self.date_to.strftime('%d/%m/%Y')
                )
            )
