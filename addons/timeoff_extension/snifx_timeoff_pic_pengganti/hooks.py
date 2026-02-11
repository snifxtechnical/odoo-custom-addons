# -*- coding: utf-8 -*-
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    Post-installation hook to clean up EXISTING orphaned data AND old rules.
    
    VERSION: 1.13.0 - hr.employee.public Solution (PERFECT FIX!)
    
    This fixes CURRENT "Missing Record" errors AND deletes old conflicting rules.
    
    Cleanup targets:
    1. mail.message - Messages referencing deleted hr.leave records
    2. mail.activity - Activities/notifications for deleted hr.leave records
    3. mail.followers - Followers of deleted hr.leave records
    4. OLD PIC PENGGANTI RULES - Conflicting security rules from previous versions
    
    v1.13.0 KEY INNOVATION:
    - Uses hr.employee.public model for PIC selection
    - hr.employee.public does NOT have current_leave_id field
    - No restricted field access = No access errors!
    - Field restrictions maintained (security preserved)
    - All users can select PIC (functionality works)
    - ✅ PERFECT SOLUTION!
    
    This is the SAME approach Odoo's Employees menu uses for regular users!
    
    This hook runs automatically on module install/upgrade.
    """
    _logger.warning("=" * 80)
    _logger.warning("🚀 POST_INIT_HOOK TRIGGERED - Time Off PIC Pengganti v1.13.0")
    _logger.warning("=" * 80)
    _logger.info("Starting orphaned data cleanup for Time Off - PIC Pengganti v1.13.0")
    
    # NEW: Delete old conflicting rules FIRST
    _logger.warning("🔧 STEP 0: Deleting old conflicting PIC Pengganti rules...")
    try:
        cr.execute("""
            DELETE FROM ir_rule 
            WHERE name IN (
                'Employee: Read for PIC Pengganti (Department Tree)',
                'Time Off: Read for PIC Pengganti (Department Tree)',
                'Employee: Read Access for PIC Pengganti Selection'
            )
        """)
        deleted_rules = cr.rowcount
        _logger.warning(f"✅ Deleted {deleted_rules} old conflicting rules")
    except Exception as e:
        _logger.error(f"❌ Error deleting old rules: {e}")
    
    _logger.info("Starting orphaned data cleanup for Time Off - PIC Pengganti v1.13.0")
    
    # Cleanup 1: Orphaned mail.message
    _logger.info("Checking for orphaned mail.message records...")
    cr.execute("""
        SELECT COUNT(*) 
        FROM mail_message 
        WHERE model = 'hr.leave' 
          AND res_id NOT IN (SELECT id FROM hr_leave)
    """)
    orphaned_messages_count = cr.fetchone()[0]
    
    if orphaned_messages_count > 0:
        _logger.warning(f"Found {orphaned_messages_count} orphaned mail.message records. Cleaning up...")
        cr.execute("""
            DELETE FROM mail_message 
            WHERE model = 'hr.leave' 
              AND res_id NOT IN (SELECT id FROM hr_leave)
        """)
        _logger.info(f"✅ Cleaned {orphaned_messages_count} orphaned mail.message records")
    else:
        _logger.info("✅ No orphaned mail.message records found")
    
    # Cleanup 2: Orphaned mail.activity
    _logger.info("Checking for orphaned mail.activity records...")
    cr.execute("""
        SELECT COUNT(*) 
        FROM mail_activity 
        WHERE res_model = 'hr.leave' 
          AND res_id NOT IN (SELECT id FROM hr_leave)
    """)
    orphaned_activities_count = cr.fetchone()[0]
    
    if orphaned_activities_count > 0:
        _logger.warning(f"Found {orphaned_activities_count} orphaned mail.activity records. Cleaning up...")
        cr.execute("""
            DELETE FROM mail_activity 
            WHERE res_model = 'hr.leave' 
              AND res_id NOT IN (SELECT id FROM hr_leave)
        """)
        _logger.info(f"✅ Cleaned {orphaned_activities_count} orphaned mail.activity records")
    else:
        _logger.info("✅ No orphaned mail.activity records found")
    
    # Cleanup 3: Orphaned mail.followers
    _logger.info("Checking for orphaned mail.followers records...")
    cr.execute("""
        SELECT COUNT(*) 
        FROM mail_followers 
        WHERE res_model = 'hr.leave' 
          AND res_id NOT IN (SELECT id FROM hr_leave)
    """)
    orphaned_followers_count = cr.fetchone()[0]
    
    if orphaned_followers_count > 0:
        _logger.warning(f"Found {orphaned_followers_count} orphaned mail.followers records. Cleaning up...")
        cr.execute("""
            DELETE FROM mail_followers 
            WHERE res_model = 'hr.leave' 
              AND res_id NOT IN (SELECT id FROM hr_leave)
        """)
        _logger.info(f"✅ Cleaned {orphaned_followers_count} orphaned mail.followers records")
    else:
        _logger.info("✅ No orphaned mail.followers records found")
    
    # Summary
    total_cleaned = orphaned_messages_count + orphaned_activities_count + orphaned_followers_count
    _logger.warning("=" * 80)
    _logger.warning(f"✅ CLEANUP COMPLETED! Total records cleaned: {total_cleaned}")
    _logger.warning("Summary:")
    _logger.warning(f"  - mail.message: {orphaned_messages_count}")
    _logger.warning(f"  - mail.activity: {orphaned_activities_count}")
    _logger.warning(f"  - mail.followers: {orphaned_followers_count}")
    _logger.warning("=" * 80)
    
    if total_cleaned > 0:
        _logger.warning("⚠️  IMPORTANT: After Odoo restarts, Admin users should:")
        _logger.warning("   1. Refresh their browser (F5)")
        _logger.warning("   2. Test Employees → Org Chart")
        _logger.warning("   3. Verify 'Missing Record' error is gone")
    else:
        _logger.warning("✅ Database is clean! No orphaned data found.")
    
    _logger.warning("=" * 80)
    _logger.warning("🎉 POST_INIT_HOOK COMPLETED SUCCESSFULLY - v1.13.0")
    _logger.warning("=" * 80)
