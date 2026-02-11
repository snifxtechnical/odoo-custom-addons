# Changelog - Snifx HR Leave Orgchart Approval

## [18.0.2.2.2] - 2024-12-17

### Fixed
- **XML View Error (Final Fix)**: Completely resolved field validation error
  - Created separate tree view for `leave.approval.level` model
  - Referenced external tree view via context instead of inline definition
  - Odoo 18 now properly validates field references
  - No more "Field 'level' does not exist" error

### Technical Details
- Approach: Separate view definition + context reference
- File: `leave_approval_level_view_tree_simple` tree view created
- Reference: Via `context={'tree_view_ref': '...'}`  
- Impact: No functional change, pure validation fix

---

## [18.0.2.2.1] - 2024-12-17

### Fixed (Attempted)
- Simplified field declarations in inline tree
- Still had validation issues in Odoo 18

---

## [18.0.2.2.0] - 2024-12-16

### Added
- **Approval Levels Tab**: Added notebook tab to hr.leave form view
  - Requestors can now see complete approval chain
  - Shows all approval levels with approver names
  - Real-time status display (Pending/Approved/Refused)
  - Color-coded status badges (Yellow/Green/Red)
  - Approval dates visible when completed
  - Read-only view for employees (cannot edit)
  - Automatically hidden if not using org chart approval

### Changed
- Enhanced hr_leave_views.xml with form view inheritance
- Updated manifest description to mention new UI feature

### Technical Details
- File: views/hr_leave_views.xml
- Added: `hr_leave_view_form_approval_levels_tab` view record
- XPath: Inserts notebook at end of sheet element
- Field: approval_level_ids displayed in tree view
- Decorations: Color coding based on approval state
- Readonly: True (employees can view only)

### User Impact
- **Before**: Requestors could only see "X levels" in chatter message
- **After**: Requestors can see full approval chain details:
  - Level 1: Fritz Erlangga (Pending)
  - Level 2: Slamet Chahyadi (Pending)
  - Level 3: Andrea Bastian (Pending)

### Benefits
- Complete transparency of approval workflow
- No need to ask "who's my next approver?"
- Clear visibility of approval progress
- Professional UI presentation
- Standard Odoo design pattern

---

## [18.0.2.1.0] - 2024-12-03

### Changed
- Updated dependency from `snifx_timeoff_officer_balance` to `snifx_timeoff_officer_department`
- Updated all group references to use new Snifx module
- Enhanced officer notification system

### Technical
- Breaking change: requires new Snifx officer module
- All references updated across models and views

---

## [18.0.2.0.0] - 2024-11-XX

### Added
- Top manager auto-approve functionality
- Flexible approval modes (Org Chart vs Simple)
- Snifx officer integration
- Department-level configuration
- Smart detection system

### Features
- Manager detection (1 approval level)
- Staff detection (2 approval levels)
- Sequential approval workflow
- Officer FYI notifications

---

## [18.0.1.0.0] - 2024-XX-XX

### Initial Release
- Organization chart based approval
- Multi-level approval system
- Basic officer notifications
