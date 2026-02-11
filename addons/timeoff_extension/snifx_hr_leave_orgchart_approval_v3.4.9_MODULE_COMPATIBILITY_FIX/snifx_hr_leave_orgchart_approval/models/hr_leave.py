# -*- coding: utf-8 -*-

import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    # CRITICAL FIX: Override name field to remove groups restriction
    # This allows all approvers (L1, L2, L3...) to see the description
    # Without this, L2+ approvers see ***** instead of actual description
    name = fields.Text(
        'Description',
        readonly=False,
        states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)]},
        groups=False,  # Remove groups restriction!
    )

    # Approval tracking
    approval_level_ids = fields.One2many(
        'leave.approval.level',
        'leave_id',
        string='Approval Levels'
    )
    current_approval_level = fields.Integer(
        string='Current Level',
        compute='_compute_current_approval_level',
        store=True
    )
    total_approval_levels = fields.Integer(
        string='Total Levels',
        compute='_compute_total_approval_levels',
        store=True
    )
    approval_progress = fields.Float(
        string='Approval Progress',
        compute='_compute_approval_progress',
        help="Percentage of approvals completed"
    )
    
    # States
    use_orgchart_approval = fields.Boolean(
        related='holiday_status_id.use_orgchart_approval',
        string='Use Org Chart Approval'
    )
    pending_approver_ids = fields.Many2many(
        'res.users',
        compute='_compute_pending_approver_ids',
        string='Pending Approvers'
    )
    user_has_pending_approval = fields.Boolean(
        string='User Has Pending Approval',
        compute='_compute_user_has_pending_approval',
        search='_search_user_has_pending_approval',
        help='True if current user has a pending approval level for this leave (computed per user, not stored)'
    )
    current_user_already_approved = fields.Boolean(
        string='Current User Already Approved',
        compute='_compute_current_user_already_approved',
        help='True if current user has already approved this leave (used to hide approve buttons)'
    )

    @api.depends('approval_level_ids.state', 'approval_level_ids.approver_id')
    def _compute_current_user_already_approved(self):
        """
        Check if current user has already approved this leave.
        Used to hide Approve/Refuse buttons in list view for records already approved by user.
        """
        current_user_id = self.env.uid
        for leave in self:
            # Check if any approval level has:
            # - approver_id = current user
            # - state = 'approved'
            leave.current_user_already_approved = any(
                level.approver_id.id == current_user_id and level.state == 'approved'
                for level in leave.approval_level_ids
            )

    @api.depends('approval_level_ids.state')
    def _compute_current_approval_level(self):
        for leave in self:
            approved_levels = leave.approval_level_ids.filtered(
                lambda l: l.state in ['approved', 'skipped']
            )
            leave.current_approval_level = len(approved_levels) + 1

    @api.depends('approval_level_ids')
    def _compute_total_approval_levels(self):
        for leave in self:
            leave.total_approval_levels = len(leave.approval_level_ids)

    @api.depends('current_approval_level', 'total_approval_levels')
    def _compute_approval_progress(self):
        for leave in self:
            if leave.total_approval_levels > 0:
                approved = leave.current_approval_level - 1
                leave.approval_progress = (approved / leave.total_approval_levels) * 100
            else:
                leave.approval_progress = 0.0

    @api.depends('approval_level_ids.state', 'approval_level_ids.is_current_level')
    def _compute_pending_approver_ids(self):
        for leave in self:
            pending_levels = leave.approval_level_ids.filtered(
                lambda l: l.state == 'pending' and l.is_current_level
            )
            leave.pending_approver_ids = pending_levels.mapped('approver_id')


    def _compute_user_has_pending_approval(self):
        """
        Compute if current user has a pending approval level for this leave.
        Used to filter "My Time Off Approvals" view.
        
        IMPORTANT: This field is user-specific and NOT STORED because:
        - The value is different for each user viewing the same record
        - Uses self.env.user which changes based on who is logged in
        - Cannot use @api.depends since value depends on current user, not just record data
        
        Example:
        - Same leave request (id=464)
        - For user 34 (L1 approver): user_has_pending_approval = True
        - For user 57 (L2 approver): user_has_pending_approval = False
        - This is IMPOSSIBLE with a stored field!
        
        The _search method below handles filtering in menu domains.
        """
        current_user = self.env.user
        for leave in self:
            # Check if current user has a pending approval level
            user_pending_level = leave.approval_level_ids.filtered(
                lambda l: l.approver_id == current_user 
                       and l.state == 'pending' 
                       and l.is_current_level
            )
            leave.user_has_pending_approval = bool(user_pending_level)
    
    def _search_user_has_pending_approval(self, operator, value):
        """
        Search method for user_has_pending_approval field.
        Allows filtering leaves where current user has pending approval.
        """
        current_user = self.env.user
        
        # Get all approval levels where current user is approver and state is pending
        pending_levels = self.env['leave.approval.level'].search([
            ('approver_id', '=', current_user.id),
            ('state', '=', 'pending'),
            ('is_current_level', '=', True)
        ])
        
        # Get leave IDs from these levels
        leave_ids = pending_levels.mapped('leave_id').ids
        
        # Handle operator
        if (operator == '=' and value) or (operator == '!=' and not value):
            return [('id', 'in', leave_ids)]
        else:
            return [('id', 'not in', leave_ids)]

    @api.model
    def create(self, vals):
        """Override create to generate approval chain"""
        leave = super(HrLeave, self).create(vals)
        
        # Generate approval levels if using org chart approval
        if leave.use_orgchart_approval and leave.state == 'confirm':
            leave._generate_approval_chain()
        
        return leave

    def write(self, vals):
        """Override write to handle state changes"""
        result = super(HrLeave, self).write(vals)
        
        # If state changes to confirm, generate approval chain
        if vals.get('state') == 'confirm':
            for leave in self:
                if leave.use_orgchart_approval and not leave.approval_level_ids:
                    leave._generate_approval_chain()
        
        return result

    def _generate_approval_chain(self):
        """Generate approval levels based on organization chart"""
        self.ensure_one()
        
        if self.approval_level_ids:
            raise UserError(_('Approval chain already generated for this leave request.'))
        
        # Get the approval chain from organization chart
        approval_chain = self._get_approval_chain_from_orgchart()
        
        if not approval_chain:
            raise UserError(_(
                'No approval chain could be determined from organization chart. '
                'Please ensure the employee has a manager assigned.'
            ))
        
        # Create approval level records
        # Officers (marked as tuples) are extracted but NOT added to chain
        ApprovalLevel = self.env['leave.approval.level']
        current_level = 0
        officer_ids = []
        
        for approver in approval_chain:
            # Check if this is the officers marker tuple
            if isinstance(approver, tuple) and approver[0] == 'officers':
                # Extract officer IDs for later notification
                officer_ids = approver[1]
                _logger.info(f"Officers will receive FYI notification: {officer_ids}")
                continue  # Skip - don't add to approval levels
            
            # Check if this is an officer (old format - shouldn't happen now)
            if isinstance(approver, tuple):
                user, role = approver
                # All officers share the same level
                if officer_level is None:
                    current_level += 1
                    officer_level = current_level
                ApprovalLevel.create({
                    'leave_id': self.id,
                    'level': officer_level,
                    'approver_id': user.id,
                    'state': 'pending',
                })
            else:
                # Regular approver - increment level
                current_level += 1
                
                # Check if this is self-approval with auto-approve enabled
                approver_employee = self.env['hr.employee'].search([
                    ('user_id', '=', approver.id)
                ], limit=1)
                
                is_self_approval = (approver_employee and approver_employee.id == self.employee_id.id)
                # Use sudo() to bypass security check (field has groups restriction)
                has_auto_approve = (approver_employee and approver_employee.sudo().auto_approve_as_top_management)
                
                # Auto-approve if:
                # 1. This is self-approval (employee submitting their own leave)
                # 2. AND employee has auto-approve enabled
                if is_self_approval and has_auto_approve:
                    # Auto-approve for employees with auto-approve enabled
                    _logger.info(f"✅ Auto-approving Level {current_level}: {approver.name} (Auto-approve enabled)")
                    approval_level = ApprovalLevel.create({
                        'leave_id': self.id,
                        'level': current_level,
                        'approver_id': approver.id,
                        'state': 'approved',  # Auto-approved!
                        'action_date': fields.Datetime.now(),
                        'comments': 'Auto-approved: Self-approval with auto-approve setting enabled',
                    })
                    
                    # Post message in chatter
                    self.message_post(
                        body=_('Level %s auto-approved: %s (Auto-approve setting enabled)') % (current_level, approver.name),
                        subtype_xmlid='mail.mt_note'
                    )
                else:
                    # Normal approval (requires manual action)
                    ApprovalLevel.create({
                        'leave_id': self.id,
                        'level': current_level,
                        'approver_id': approver.id,
                        'state': 'pending',
                    })
        
        # Send notification to first PENDING level (skip auto-approved levels)
        first_pending_level = self.approval_level_ids.filtered(lambda l: l.state == 'pending').sorted('level')
        if first_pending_level:
            first_pending_level[0]._send_notification()
            _logger.info(f"📧 Notification sent to Level {first_pending_level[0].level}: {first_pending_level[0].approver_id.name}")
        else:
            _logger.info("ℹ️ No pending levels - all levels auto-approved")
        
        # Post message with auto-approval info
        total_levels = len([a for a in approval_chain if not (isinstance(a, tuple) and a[0] == 'officers')])
        auto_approved_count = self.approval_level_ids.filtered(lambda l: l.state == 'approved').mapped('level')
        
        if auto_approved_count:
            self.message_post(
                body=_('Approval chain generated: %s levels (%s auto-approved for top management)') % (
                    total_levels, 
                    len(auto_approved_count)
                ),
                subtype_xmlid='mail.mt_comment'
            )
        else:
            self.message_post(
                body=_('Approval chain generated: %s levels') % total_levels,
                subtype_xmlid='mail.mt_comment'
            )
        
        # CRITICAL: If all levels are auto-approved, approve the leave immediately
        if not first_pending_level and auto_approved_count:
            _logger.info("✅ All approval levels auto-approved - approving leave automatically")
            # All levels approved, mark leave as approved
            self.write({
                'state': 'validate',  # Approved state
            })
            self.message_post(
                body=_('Time off request automatically approved (all approval levels auto-approved)'),
                subtype_xmlid='mail.mt_comment'
            )
            _logger.info(f"✅ Leave {self.id} auto-approved successfully")

    def _get_approval_chain_from_orgchart(self):
        """
        Get list of approvers from organization chart
        
        Two Modes:
        1. Organization Chart Mode (use_orgchart_approval = True):
           - Smart Detection based on subordinates
           - Manager (has team): 1 approval level
           - Staff (no team): 2 approval levels
        
        2. Simple Mode (use_orgchart_approval = False):
           - Direct manager only (1 level)
           - No org chart hierarchy lookup
        
        Returns list of res.users in order of approval
        """
        self.ensure_one()
        
        approvers = []
        leave_type = self.holiday_status_id
        employee_dept = self.employee_id.department_id
        
        # CHECK DEPARTMENT APPROVAL MODE
        # ==============================
        if employee_dept and not employee_dept.use_orgchart_approval:
            # SIMPLE MODE: Direct manager only
            _logger.info(f"📋 SIMPLE MODE: Department '{employee_dept.name}' uses direct manager approval only")
            
            direct_manager = self.employee_id.parent_id
            if direct_manager and direct_manager.user_id:
                approvers.append(direct_manager.user_id)
                _logger.info(f"✅ Added direct manager: {direct_manager.name}")
            else:
                _logger.warning(f"⚠️ No direct manager found for {self.employee_id.name}")
            
        else:
            # ORGANIZATION CHART MODE: Smart Detection
            _logger.info(f"🔍 ORG CHART MODE: Using smart detection for {self.employee_id.name}")
            
            # STEP 1: SMART DETECTION - Determine required levels
            # ====================================================
            subordinates_count = self.env['hr.employee'].search_count([
                ('parent_id', '=', self.employee_id.id)
            ])
            
            # Check if employee has force single level override
            # Use sudo() to bypass security check (field has groups restriction)
            if self.employee_id.sudo().force_single_approval_level:
                # OVERRIDE: Force single approval level
                required_levels = 1
                _logger.info(f"⚙️ OVERRIDE: {self.employee_id.name} has 'Force Single Approval Level' enabled → 1 approval level")
            elif subordinates_count > 0:
                # Has team = Manager level
                required_levels = 1
                _logger.info(f"🔍 SMART DETECTION: {self.employee_id.name} is a MANAGER "
                            f"({subordinates_count} subordinates) → 1 approval level")
            else:
                # No team = Staff level
                required_levels = 2
                _logger.info(f"🔍 SMART DETECTION: {self.employee_id.name} is STAFF "
                            f"(no subordinates) → 2 approval levels")
            
            # STEP 2: Build approval chain from org chart
            # ============================================
            current_employee = self.employee_id
            level = 0
            
            _logger.info(f"Building approval chain for {self.employee_id.name}")
            _logger.info(f"Required org chart levels: {required_levels}")
            
            while current_employee and level < required_levels:
                # Get direct manager
                manager = current_employee.parent_id
                
                if not manager:
                    _logger.info(f"No manager found at level {level + 1}, stopping")
                    break
                
                # Check if manager has a user account
                if manager.user_id:
                    if manager.user_id not in approvers:
                        approvers.append(manager.user_id)
                        level += 1
                        _logger.info(f"Added Level {level}: {manager.name} (from org chart)")
                else:
                    _logger.warning(f"Manager {manager.name} has no user account, skipping")
                
                # Move up one level for next iteration
                current_employee = manager
            
            _logger.info(f"Total org chart approvers added: {len(approvers)}")
        
        # STEP 3: Add optional approvers (NOT counted in levels)
        # ======================================================
        
        # Add Department Head (if enabled and not already in chain)
        if leave_type.require_department_head_approval:
            if self.employee_id.department_id and self.employee_id.department_id.manager_id:
                dept_head = self.employee_id.department_id.manager_id
                if dept_head.user_id and dept_head.user_id not in approvers:
                    approvers.append(dept_head.user_id)
                    _logger.info(f"Added Department Head: {dept_head.name}")
        
        # Add HR Manager (if enabled and not already in chain)
        if leave_type.require_hr_approval:
            hr_manager = self._get_hr_manager()
            if hr_manager and hr_manager not in approvers:
                approvers.append(hr_manager)
                _logger.info(f"Added HR Manager: {hr_manager.name}")
        
        # Add Time Off Officers (if enabled and not already in chain)
        # NOTE: Officers are NOT added to approval chain - they only get FYI notification
        # Leave is approved after manager levels complete
        officer_ids = []
        if leave_type.require_officer_final_approval:
            officers = self._get_time_off_officer()
            if officers:
                # Store officer IDs for later notification
                officer_ids = [o.id for o in officers]
                _logger.info(f"Found {len(officers)} Time Off Officers for FYI notification: {[u.name for u in officers]}")
            else:
                _logger.warning("No Time Off Officers found")
        
        # Store in approvers list as marker (will be filtered out during level creation)
        if officer_ids:
            approvers.append(('officers', officer_ids))  # Tuple marker
        
        # Add Top Management (if enabled)
        if leave_type.require_top_management:
            top_managers = self._get_top_management()
            for manager in top_managers:
                if manager not in approvers:
                    approvers.append(manager)
                    _logger.info(f"Added Top Management: {manager.name}")
        
        _logger.info(f"Final approval chain has {len(approvers)} approvers")
        
        return approvers
    
    def _get_time_off_officer(self):
        """
        Get Time Off Officers from employee's department ONLY (STRICT MODE)
        Returns: list of res.users from department ONLY
        
        STRICT MODE Logic:
        1. Check employee's department for assigned officers
        2. If found, use ONLY department officers (all of them, no limit)
        3. If NOT found or empty, return EMPTY LIST (no fallback)
        
        NO FALLBACK to company-wide officers or managers!
        This ensures notifications are sent ONLY when department explicitly assigns officers.
        This gives full control to administrators on a per-department basis.
        """
        self.ensure_one()
        
        officers = []
        
        # STRICT: Only check employee's department - NO FALLBACK!
        if self.employee_id.department_id:
            dept_officers = self.employee_id.department_id.notification_officer_ids
            
            if dept_officers:
                # Department has assigned officers - use them ALL (no limit)
                officers = list(dept_officers)
                _logger.info(f"✅ Using department officers for {self.employee_id.department_id.name}: "
                           f"{[u.name for u in officers]}")
                return officers
            else:
                # Department has NO officers - return empty (NO notification sent!)
                _logger.info(f"ℹ️ Department {self.employee_id.department_id.name} has no assigned officers. "
                           f"No officer notification will be sent (STRICT MODE - no fallback).")
                return []
        else:
            # Employee has no department - return empty (NO notification sent!)
            _logger.info(f"ℹ️ Employee {self.employee_id.name} has no department. "
                       f"No officer notification will be sent (STRICT MODE).")
            return []
    
    # NOTE: STRICT MODE - No fallback methods!
    # - No fallback to company-wide officers
    # - No fallback to Time Off Managers
    # - Empty department = No notification
    # This gives full per-department control to administrators

    def _get_hr_manager(self):
        """Get HR Manager user"""
        # Method 1: Get user with HR Manager group (most reliable)
        try:
            hr_managers = self.env.ref('hr_holidays.group_hr_holidays_manager').users
            if hr_managers:
                _logger.info(f"HR Manager from group: {hr_managers[0].name}")
                return hr_managers[0]  # Return first HR manager
        except Exception as e:
            _logger.warning(f"Could not get HR Manager from group: {e}")
        
        return False

    def _get_top_management(self):
        """Get top management users (CEO, CFO, etc.)"""
        top_managers = []
        
        # Get employees at top of org chart (no parent)
        top_employees = self.env['hr.employee'].search([
            ('parent_id', '=', False),
            ('user_id', '!=', False),
            ('company_id', '=', self.company_id.id)
        ])
        
        for employee in top_employees:
            if employee.user_id:
                top_managers.append(employee.user_id)
        
        return top_managers


    def _notify_officers_fyi(self, officer_ids=None):
        """Send FYI notification to officers after leave is approved
        
        IMPORTANT: Only sends to officers with Snifx group
        ("Officer with Balance (Enhanced)")
        
        Args:
            officer_ids: List of user IDs to notify
        """
        self.ensure_one()
        
        if not officer_ids:
            # Try to get from leave type config
            if self.holiday_status_id.require_officer_final_approval:
                officers = self._get_time_off_officer()
                officer_ids = [o.id for o in officers] if officers else []
        
        if not officer_ids:
            _logger.info("No officers selected for notification")
            return
        
        # Get selected officers
        officers = self.env['res.users'].browse(officer_ids)
        _logger.info(f"Officers selected in department: {officers.mapped('name')}")
        
        # CRITICAL FILTER: Only officers with Snifx group
        try:
            snifx_group = self.env.ref('snifx_timeoff_officer_department.group_timeoff_officer_department')
            snifx_officers = officers.filtered(
                lambda o: snifx_group in o.groups_id
            )
            
            # Log filtering results
            filtered_out = officers - snifx_officers
            if filtered_out:
                _logger.info(f"Filtered out non-Snifx officers (don't have 'Officer: Manage Department Requests' group): "
                           f"{filtered_out.mapped('name')}")
            
            if not snifx_officers:
                _logger.warning(f"No officers with Snifx group found! "
                              f"Selected officers: {officers.mapped('name')}, "
                              f"but none have 'Officer: Manage Department Requests' group.")
                return
            
            _logger.info(f"Sending notifications to Snifx officers only: {snifx_officers.mapped('name')}")
            
        except Exception as e:
            _logger.error(f"Error filtering Snifx officers: {e}")
            return
        
        # Send notification ONLY to Snifx officers (FYI only) via message
        for officer in snifx_officers:
            try:
                # Post message to notify officer
                self.message_post(
                    body=_('Time Off Approved - FYI<br/>'
                          'Leave for <strong>%s</strong> has been approved.<br/>'
                          'Type: %s<br/>'
                          'Period: %s to %s<br/>'
                          'Duration: %s days<br/>'
                          'This is for your information only.') % (
                              self.employee_id.name,
                              self.holiday_status_id.name,
                              self.date_from.strftime('%Y-%m-%d') if self.date_from else '',
                              self.date_to.strftime('%Y-%m-%d') if self.date_to else '',
                              self.number_of_days
                          ),
                    partner_ids=[officer.partner_id.id],
                    subtype_xmlid='mail.mt_note'
                )
                
                # Also create activity for visibility
                try:
                    self.activity_schedule(
                        'mail.mail_activity_data_todo',
                        user_id=officer.id,
                        summary=_('Time Off Approved - FYI: %s') % self.employee_id.name,
                        note=_('Leave for %s has been approved. This is for your information only.') % self.employee_id.name
                    )
                except Exception as activity_error:
                    _logger.debug(f"Activity creation failed for {officer.name}: {activity_error}")
                    pass  # Activity is optional, message is primary
                
                _logger.info(f"✅ Sent FYI notification to Snifx officer: {officer.name}")
            except Exception as e:
                _logger.error(f"❌ Could not send FYI to {officer.name}: {e}")

    def action_validate(self, *args, **kwargs):
        """
        Override to handle compatibility with other modules that pass parameters
        
        Some modules (like snifx_timeoff_officer_department) may pass additional
        parameters like check_state. We accept them and pass through to super().
        
        Args:
            *args: Variable positional arguments from other modules
            **kwargs: Variable keyword arguments from other modules
        
        Returns:
            Result from parent action_validate()
        """
        # Just pass everything through to parent
        return super(HrLeave, self).action_validate(*args, **kwargs)
    
    def _check_approval_completion(self):
        """Check if all approval levels are complete"""
        self.ensure_one()
        
        _logger.info(f"=== _check_approval_completion called for leave {self.id} ===")
        
        if not self.use_orgchart_approval:
            _logger.info(f"  Leave {self.id} does not use orgchart approval, skipping")
            return
        
        # Log all approval levels state
        _logger.info(f"  Checking approval levels for leave {self.id}:")
        for level in self.approval_level_ids:
            _logger.info(f"    Level {level.level}: {level.approver_id.name} - State: {level.state}")
        
        # Check if all levels are approved or skipped
        all_approved = all(
            level.state in ['approved', 'skipped']
            for level in self.approval_level_ids
        )
        
        _logger.info(f"  All levels approved? {all_approved}")
        
        if all_approved:
            _logger.info(f"  ✅ ALL LEVELS APPROVED! Calling action_validate() for leave {self.id}")
            # All levels approved - approve the leave
            # Use sudo to bypass standard manager validation
            # since we have our own approval chain
            self.sudo().action_validate()
            
            # Send FYI notification to officers
            # Get officer IDs from approval chain context
            officer_ids = []
            for level_record in self.approval_level_ids:
                # Officers should be stored somewhere - for now get from config
                pass
            
            # Call with officer IDs
            self._notify_officers_fyi(officer_ids=None)  # Will auto-detect from config
            
            # Post message
            try:
                self.sudo().message_post(
                    body=_('All approval levels completed. Leave request approved.'),
                    subtype_xmlid='mail.mt_comment'
                )
            except Exception as e:
                _logger.warning(f"Could not post completion message: {e}")
            
            # Notify employee
            self._send_approval_notification_to_employee()
        else:
            _logger.info(f"  ⏳ NOT all levels approved yet. Waiting for remaining approvals.")
            pending_levels = self.approval_level_ids.filtered(lambda l: l.state == 'pending')
            for level in pending_levels:
                _logger.info(f"    Pending: Level {level.level} - {level.approver_id.name}")

    def _send_approval_notification_to_employee(self):
        """Send notification to employee that leave is approved"""
        self.ensure_one()
        
        template = self.env.ref(
            'hr_leave_orgchart_approval.email_template_leave_approved',
            raise_if_not_found=False
        )
        
        if template and self.employee_id.user_id:
            template.send_mail(self.id, force_send=True)

    def action_approve(self):
        """Override to use approval levels"""
        if self.use_orgchart_approval:
            # Find current level and approve it
            current_level = self.approval_level_ids.filtered(
                lambda l: l.is_current_level and l.state == 'pending'
            )
            if current_level:
                return current_level[0].action_approve()
            else:
                raise UserError(_('No pending approval level found.'))
        else:
            # Use standard approval
            return super(HrLeave, self).action_approve()

    def action_refuse(self):
        """Override to handle rejection"""
        result = super(HrLeave, self).action_refuse()
        
        # Update all pending levels to rejected
        if self.use_orgchart_approval:
            self.approval_level_ids.filtered(
                lambda l: l.state == 'pending'
            ).write({'state': 'rejected'})
        
        return result

    def action_show_approval_levels(self):
        """Action to show approval levels in a form view"""
        self.ensure_one()
        
        return {
            'name': _('Approval Levels'),
            'type': 'ir.actions.act_window',
            'res_model': 'leave.approval.level',
            'view_mode': 'tree,form',
            'domain': [('leave_id', '=', self.id)],
            'context': {'default_leave_id': self.id},
        }
