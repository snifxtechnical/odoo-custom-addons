import logging
from odoo import api, fields, models
from odoo.tools import format_date

_logger = logging.getLogger(__name__)

class HrLeave(models.Model):
    _inherit = "hr.leave"

    # Original field - stores hr.employee reference (for backend use)
    pic_pengganti_id = fields.Many2one("hr.employee", string="PIC Pengganti", tracking=True)
    
    # New field - uses hr.employee.public for selection (avoids restricted fields!)
    # This is what users interact with in the UI
    pic_pengganti_public_id = fields.Many2one(
        "hr.employee.public",
        string="Select PIC Pengganti",
        help="Select a substitute person in charge during your time off",
        tracking=False  # Don't track this helper field
    )
    
    @api.onchange('pic_pengganti_public_id')
    def _onchange_pic_pengganti_public(self):
        """
        Sync selection from hr.employee.public to hr.employee.
        
        Why this works:
        - hr.employee.public doesn't have current_leave_id field
        - No restricted field access during selection
        - hr.employee and hr.employee.public share same IDs
        - We can safely convert between them
        
        Security: Uses sudo() for the conversion only, not for user selection.
        User can only SELECT from hr.employee.public (no restrictions).
        We just store it as hr.employee reference.
        """
        if self.pic_pengganti_public_id:
            # IDs are the same, just convert the model reference
            # Use sudo() ONLY for this internal conversion
            self.pic_pengganti_id = self.env['hr.employee'].sudo().browse(
                self.pic_pengganti_public_id.id
            )
    
    @api.onchange('pic_pengganti_id')
    def _onchange_pic_pengganti_private(self):
        """
        Reverse sync: If pic_pengganti_id is set programmatically,
        update the public field too (for UI display).
        """
        if self.pic_pengganti_id and not self.pic_pengganti_public_id:
            # Sync to public field for display
            self.pic_pengganti_public_id = self.env['hr.employee.public'].browse(
                self.pic_pengganti_id.id
            )

    def _snifx_email_from(self):
        self.ensure_one()
        emp = self.employee_id
        return emp.work_email or (emp.user_id and emp.user_id.email) or (emp.company_id and emp.company_id.email) or "noreply@example.com"

    def _snifx_email_to(self):
        self.ensure_one()
        pic = self.pic_pengganti_id
        if not pic:
            return False
        email = (pic.user_id and pic.user_id.email) or False
        if not email:
            priv_pid = getattr(pic, 'private_address_id', False) or getattr(pic, 'address_home_id', False)
            email = (priv_pid and priv_pid.email) or False
        email = email or pic.work_email or False
        return email

    def _snifx_partner_ids(self):
        self.ensure_one()
        pic = self.pic_pengganti_id
        if not pic:
            return []
        partner = (pic.user_id and pic.user_id.partner_id) or False
        if not partner:
            partner = getattr(pic, 'private_address_id', False) or getattr(pic, 'address_home_id', False) or False
        return [partner.id] if partner else []

    def _snifx_build_body(self, is_reminder=False):
        self.ensure_one()
        dfrom = self.request_date_from or (self.date_from and self.date_from.date())
        dto = self.request_date_to or (self.date_to and self.date_to.date())
        dur = getattr(self, 'number_of_days_display', False) or getattr(self, 'number_of_days', 0.0) or 0.0
        lang = self.env.user.lang or 'en_US'
        dfmt = format_date(self.env, dfrom, lang_code=lang) if dfrom else ''
        tfmt = format_date(self.env, dto, lang_code=lang) if dto else ''
        return f"""<div>
            <p>Yth. <strong>{self.pic_pengganti_id.name or ''}</strong>,</p>
            <p>{'Pengingat' if is_reminder else 'Notifikasi'}: Anda {'akan menjadi' if is_reminder else 'ditunjuk sebagai'} <strong>PIC Pengganti</strong> untuk karyawan <strong>{self.employee_id.name or ''}</strong>.</p>
            <ul>
                <li>Tanggal: <strong>{dfmt}</strong>{(' s.d. ' + tfmt) if (dfmt and tfmt and dfmt != tfmt) else ''}</li>
                <li>Durasi: <strong>{dur} hari</strong></li>
                <li>Jenis Cuti: <strong>{self.holiday_status_id.display_name if self.holiday_status_id else ''}</strong></li>
            </ul>
            <p>Terima kasih.</p>
        </div>"""

    def _snifx_log_activity(self, email_values, is_reminder=False):
        for rec in self:
            try:
                act_type = rec.env.ref('mail.mail_activity_data_todo', raise_if_not_found=False)
                assigned_uid = (rec.pic_pengganti_id.user_id and rec.pic_pengganti_id.user_id.id) or rec.env.user.id
                act_vals = {
                    'res_model_id': rec.env['ir.model']._get_id('hr.leave'),
                    'res_id': rec.id,
                    'activity_type_id': act_type.id if act_type else False,
                    'summary': 'Email PIC {}terkirim'.format('(Reminder) ' if is_reminder else ''),
                    'note': (
                        "<p>Sistem mencatat bahwa email PIC {}terbentuk.</p>"
                        "<p><strong>From:</strong> {}</p>"
                        "<p><strong>To:</strong> {}</p>"
                    ).format('(Reminder) ' if is_reminder else '', email_values.get('email_from') or '-', email_values.get('email_to') or '-'),
                    'user_id': assigned_uid,
                    'date_deadline': fields.Date.context_today(rec),
                }
                rec.env['mail.activity'].create(act_vals)
            except Exception:
                rec.message_post(body="(Info) Email PIC {}terbentuk.".format('Reminder ' if is_reminder else ''))

    def _snifx_send_pic_mail(self, is_reminder=False):
        for rec in self:
            if not (rec.pic_pengganti_id and rec.employee_id):
                continue
            template_xmlid = "snifx_timeoff_pic_pengganti.mail_template_pic_pengganti"
            template = rec.env.ref(template_xmlid, raise_if_not_found=False)
            if not template:
                continue
            email_values = {
                "email_from": rec._snifx_email_from(),
                "email_to": rec._snifx_email_to(),
                "partner_ids": [(6, 0, rec._snifx_partner_ids())],
                "body_html": rec._snifx_build_body(is_reminder=is_reminder),
            }
            template.sudo().send_mail(rec.id, force_send=True, email_values=email_values)
            rec._snifx_log_activity(email_values=email_values, is_reminder=is_reminder)

    def unlink(self):
        """
        Override unlink to perform COMPREHENSIVE cleanup before deleting Time Off records.
        
        This prevents "Missing Record" errors for Admin and Officer users who have
        global access to all employees across departments.
        
        v1.4.0 COMPREHENSIVE CLEANUP:
        =============================
        1. mail.message - Critical! Prevents Org Chart errors when Admin views employees
        2. mail.activity - Cleans notifications/activities
        3. mail.followers - Cleans subscription records
        
        Why this is needed:
        - Admin/Officer All Employee see ALL employees (global scope)
        - When Time Off is deleted, orphaned mail.message still references it
        - Org Chart loads employee → loads messages → tries to access deleted hr.leave
        - Result: "Missing Record (hr.leave(X), User: Y)" error
        - Regular employees don't see this because department-scoped access filters it out
        
        Note: employee.current_leave_id is a computed field (store=False) in Odoo 18,
        so it's automatically recomputed and doesn't need manual cleanup.
        """
        if not self:
            return super(HrLeave, self).unlink()
        
        leave_ids = self.ids
        records_to_delete = len(leave_ids)
        
        _logger.info(f"Starting comprehensive cleanup for {records_to_delete} Time Off record(s): {leave_ids}")
        
        # Cleanup 1: mail.message (CRITICAL for Org Chart error)
        # This is the primary cause of "Missing Record" errors for Admin users
        orphaned_messages = self.env['mail.message'].sudo().search([
            ('model', '=', 'hr.leave'),
            ('res_id', 'in', leave_ids)
        ])
        
        if orphaned_messages:
            message_count = len(orphaned_messages)
            _logger.info(f"Deleting {message_count} mail.message record(s) for hr.leave {leave_ids}")
            orphaned_messages.unlink()
            _logger.info(f"✅ Cleaned {message_count} mail.message records")
        else:
            _logger.debug(f"No mail.message records found for hr.leave {leave_ids}")
        
        # Cleanup 2: mail.activity (notifications)
        orphaned_activities = self.env['mail.activity'].sudo().search([
            ('res_model', '=', 'hr.leave'),
            ('res_id', 'in', leave_ids)
        ])
        
        if orphaned_activities:
            activity_count = len(orphaned_activities)
            _logger.info(f"Deleting {activity_count} mail.activity record(s) for hr.leave {leave_ids}")
            orphaned_activities.unlink()
            _logger.info(f"✅ Cleaned {activity_count} mail.activity records")
        else:
            _logger.debug(f"No mail.activity records found for hr.leave {leave_ids}")
        
        # Cleanup 3: mail.followers (subscriptions)
        orphaned_followers = self.env['mail.followers'].sudo().search([
            ('res_model', '=', 'hr.leave'),
            ('res_id', 'in', leave_ids)
        ])
        
        if orphaned_followers:
            follower_count = len(orphaned_followers)
            _logger.info(f"Deleting {follower_count} mail.followers record(s) for hr.leave {leave_ids}")
            orphaned_followers.unlink()
            _logger.info(f"✅ Cleaned {follower_count} mail.followers records")
        else:
            _logger.debug(f"No mail.followers records found for hr.leave {leave_ids}")
        
        # Note: employee.current_leave_id is computed (store=False), so no DB cleanup needed
        # Odoo will automatically recompute this field next time it's accessed
        
        _logger.info(f"Comprehensive cleanup completed for hr.leave {leave_ids}. Proceeding with deletion.")
        
        # Now safe to delete the Time Off records
        return super(HrLeave, self).unlink()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        return records

    def write(self, vals):
        prev_states = {rec.id: rec.state for rec in self}
        res = super().write(vals)
        if "state" in vals:
            approved_states = {"validate", "validate1"}
            to_send = self.filtered(lambda r: r.state in approved_states and prev_states.get(r.id) != r.state and r.pic_pengganti_id)
            if to_send:
                to_send._snifx_send_pic_mail(is_reminder=False)
        return res
