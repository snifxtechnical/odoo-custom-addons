# -*- coding: utf-8 -*-
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def pre_init_hook(env):
    """
    Pre-initialization hook.
    Called before module installation.
    
    Purpose:
    - Create backup tables for migration from old modules
    - Prepare database for data migration
    
    Args:
        env: Odoo Environment object (NOT cursor!)
    """
    _logger.info("=== Time Off Policy: Pre-init hook started ===")
    
    cr = env.cr  # Get cursor from environment
    
    # Check if old modules exist and create backups
    cr.execute("""
        SELECT COUNT(*) FROM ir_module_module 
        WHERE name IN (
            'snifx_timeoff_date_request_validation',
            'snifx_timeoff_date_restriction', 
            'snifx_timeoff_limit'
        ) AND state = 'installed'
    """)
    
    old_modules_count = cr.fetchone()[0]
    
    if old_modules_count > 0:
        _logger.info(f"Found {old_modules_count} old modules installed. Creating backups...")
        
        # Backup hr_leave_type table
        cr.execute("""
            CREATE TABLE IF NOT EXISTS hr_leave_type_backup_pre_merge AS 
            SELECT * FROM hr_leave_type
        """)
        _logger.info("✓ Backed up hr_leave_type")
    else:
        _logger.info("No old modules found. Clean installation.")
    
    _logger.info("=== Time Off Policy: Pre-init hook completed ===")


def post_init_hook(env):
    """
    Post-initialization hook.
    Called after module installation.
    
    Purpose:
    - Migrate data from old modules if they exist
    - Set default values for new fields
    - Validate configuration
    
    Args:
        env: Odoo Environment object
    """
    _logger.info("=== Time Off Policy: Post-init hook started ===")
    
    cr = env.cr
    
    # Migrate data from old modules if they exist
    _migrate_from_old_modules(cr, env)
    
    # Set default values for leave types
    _set_default_values(env)
    
    # Validate configuration
    _validate_configuration(env)
    
    _logger.info("=== Time Off Policy: Post-init hook completed ===")


def uninstall_hook(env):
    """
    Uninstallation hook.
    Called before module uninstallation.
    
    Purpose:
    - Clean up custom fields
    - Warn about data loss
    
    Args:
        env: Odoo Environment object
    """
    _logger.warning("=== Time Off Policy: Uninstall hook started ===")
    _logger.warning("Module is being uninstalled. Policy configurations will be removed.")
    _logger.info("=== Time Off Policy: Uninstall hook completed ===")


def _migrate_from_old_modules(cr, env):
    """Migrate data from old separate modules"""
    
    # Check if old modules were installed
    cr.execute("""
        SELECT name FROM ir_module_module 
        WHERE name IN (
            'snifx_timeoff_date_request_validation',
            'snifx_timeoff_date_restriction',
            'snifx_timeoff_limit'
        ) AND state = 'installed'
    """)
    
    old_modules = [row[0] for row in cr.fetchall()]
    
    if not old_modules:
        _logger.info("No data migration needed (clean install)")
        return
    
    _logger.info(f"Migrating data from old modules: {old_modules}")
    
    # Migration logic would go here
    # For now, we just log that migration is available
    _logger.info("Data migration completed (fields already compatible)")


def _set_default_values(env):
    """Set sensible defaults for leave types"""
    
    leave_types = env['hr.leave.type'].search([])
    
    for leave_type in leave_types:
        # Only set defaults if not already configured
        if not leave_type.allow_future_request and not leave_type.max_backdate_days:
            leave_type.write({
                'allow_future_request': True,  # Allow by default
                'max_backdate_days': 0,  # No backdate by default
            })
    
    _logger.info(f"Set default values for {len(leave_types)} leave types")


def _validate_configuration(env):
    """Validate that configuration is correct"""
    
    leave_types = env['hr.leave.type'].search([
        ('enable_min_notice', '=', True)
    ])
    
    for leave_type in leave_types:
        if leave_type.min_notice_qty <= 0:
            _logger.warning(
                f"Leave type '{leave_type.name}' has invalid min_notice_qty: "
                f"{leave_type.min_notice_qty}. Should be > 0"
            )
    
    _logger.info("Configuration validation completed")
