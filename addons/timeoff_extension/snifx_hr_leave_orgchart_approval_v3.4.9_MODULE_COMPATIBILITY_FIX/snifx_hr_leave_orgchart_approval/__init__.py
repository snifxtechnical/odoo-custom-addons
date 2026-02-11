# -*- coding: utf-8 -*-

from . import models

import logging
_logger = logging.getLogger(__name__)

def uninstall_hook(env):
    """
    Cleanup hook called when module is uninstalled.
    Removes all custom rules, actions, menus, and fields to prevent orphaned data.
    """
    _logger.info("Starting snifx_hr_leave_orgchart_approval uninstall cleanup...")
    
    # 1. Delete custom ir.rules that reference our fields
    try:
        rules = env['ir.rule'].sudo().search([
            '|', '|', '|',
            ('name', 'ilike', 'orgchart'),
            ('name', 'ilike', 'approval_level'),
            ('domain_force', 'ilike', 'approval_level_ids'),
            ('domain_force', 'ilike', 'use_orgchart_approval')
        ])
        if rules:
            _logger.info(f"Deleting {len(rules)} custom rules...")
            rules.unlink()
    except Exception as e:
        _logger.warning(f"Could not delete custom rules: {e}")
    
    # 2. Delete custom actions
    try:
        actions = env['ir.actions.act_window'].sudo().search([
            '|', '|', '|', '|',
            ('name', 'ilike', 'approval level'),
            ('res_model', '=', 'leave.approval.level'),
            ('name', 'ilike', 'my time off approval'),
            ('name', 'ilike', 'orgchart waiting'),
            ('name', 'ilike', 'snifx')
        ])
        if actions:
            _logger.info(f"Deleting {len(actions)} custom actions...")
            actions.unlink()
    except Exception as e:
        _logger.warning(f"Could not delete custom actions: {e}")
    
    # 3. Delete custom menu items
    try:
        menus = env['ir.ui.menu'].sudo().search([
            '|', '|', '|', '|',
            ('name', 'ilike', 'approval level'),
            ('name', 'ilike', 'my pending approval'),
            ('name', 'ilike', 'my time off approval'),
            ('name', 'ilike', 'orgchart waiting'),
            ('name', 'ilike', 'snifx')
        ])
        if menus:
            _logger.info(f"Deleting {len(menus)} custom menus...")
            menus.unlink()
    except Exception as e:
        _logger.warning(f"Could not delete custom menus: {e}")
    
    # 4. Delete custom filters
    try:
        filters = env['ir.filters'].sudo().search([
            ('model_id', 'in', ['hr.leave', 'leave.approval.level'])
        ])
        if filters:
            _logger.info(f"Deleting {len(filters)} custom filters...")
            filters.unlink()
    except Exception as e:
        _logger.warning(f"Could not delete custom filters: {e}")
    
    _logger.info("snifx_hr_leave_orgchart_approval uninstall cleanup completed!")
