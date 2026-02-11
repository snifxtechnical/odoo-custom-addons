# Emergency SQL Fix - Alternative to Module Upgrade

## ⚠️ When to Use This

**Use this ONLY if:**
- You cannot upgrade the module immediately
- Need urgent production fix
- Module upgrade causes issues

**DO NOT use if:**
- You can upgrade module normally
- This is initial deployment
- You have time for proper upgrade

---

## 🚨 CRITICAL: Always Backup First!

```bash
# MANDATORY backup before any SQL changes
sudo -u postgres pg_dump odooprod > /backup/odooprod_emergency_backup_$(date +%Y%m%d_%H%M%S).sql
```

---

## ✅ Option 1: Add Global Read Rule (Recommended)

**This adds a new global rule without modifying existing rules:**

```bash
sudo -u odoo psql odooprod << 'EOF'
-- Check if rule already exists
SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN 'Rule already exists!'
        ELSE 'Safe to proceed'
    END as status
FROM ir_rule
WHERE name = 'Time Off: Approval Level Read Access';

-- If safe to proceed, add rule:
INSERT INTO ir_rule (
    name,
    model_id,
    domain_force,
    perm_read,
    perm_write,
    perm_create,
    perm_unlink,
    active,
    global
)
SELECT 
    'Time Off: Approval Level Read Access',
    m.id,
    '[(''approval_level_ids.approver_id'', ''='', user.id)]',
    TRUE,
    FALSE,
    FALSE,
    FALSE,
    TRUE,
    TRUE
FROM ir_model m
WHERE m.model = 'hr.leave'
  AND NOT EXISTS (
      SELECT 1 FROM ir_rule 
      WHERE name = 'Time Off: Approval Level Read Access'
  );

-- Verify created
SELECT 
    id,
    name,
    perm_read,
    global,
    active
FROM ir_rule
WHERE name = 'Time Off: Approval Level Read Access';

\echo ''
\echo '✅ Rule created!'
\echo 'Now restart Odoo'
EOF

# Restart Odoo
sudo systemctl restart odoo
```

---

## ✅ Option 2: Extend Existing Validator Rule

**This modifies the existing "Access for Validators" rule:**

```bash
sudo -u odoo psql odooprod << 'EOF'
-- Backup existing rule first
CREATE TABLE IF NOT EXISTS ir_rule_emergency_backup AS
SELECT * FROM ir_rule 
WHERE name = 'HR Leave: Access for Validators';

-- Update rule to include approval_level approvers
UPDATE ir_rule
SET domain_force = '[''|'',
    (''validation_status_ids.user_id'', ''='', user.id),
    (''approval_level_ids.approver_id'', ''='', user.id)
]'
WHERE name = 'HR Leave: Access for Validators';

-- Verify update
SELECT 
    name,
    domain_force
FROM ir_rule
WHERE name = 'HR Leave: Access for Validators';

\echo ''
\echo '✅ Rule updated!'
\echo 'Now restart Odoo'
EOF

# Restart Odoo
sudo systemctl restart odoo
```

---

## 🔧 Verification After Fix

```bash
# 1. Check rule exists
sudo -u odoo psql odooprod -c \
  "SELECT name, perm_read, global FROM ir_rule \
   WHERE name LIKE '%Approval Level%' OR name LIKE '%Validators%';"

# 2. Test filter
echo "Login as L2 approver and test 'Waiting For Me' filter"

# 3. Monitor logs
sudo journalctl -u odoo -f
```

---

## 🔙 Rollback Emergency Fix

### **To Rollback Option 1:**

```bash
sudo -u odoo psql odooprod << 'EOF'
-- Disable the rule
UPDATE ir_rule
SET active = FALSE
WHERE name = 'Time Off: Approval Level Read Access';

-- Or delete it completely
-- DELETE FROM ir_rule
-- WHERE name = 'Time Off: Approval Level Read Access';

\echo 'Rule disabled/removed'
EOF

sudo systemctl restart odoo
```

---

### **To Rollback Option 2:**

```bash
sudo -u odoo psql odooprod << 'EOF'
-- Restore from backup
UPDATE ir_rule
SET domain_force = backup.domain_force
FROM ir_rule_emergency_backup backup
WHERE ir_rule.name = 'HR Leave: Access for Validators'
  AND backup.name = 'HR Leave: Access for Validators';

-- Verify restored
SELECT name, domain_force 
FROM ir_rule 
WHERE name = 'HR Leave: Access for Validators';

\echo 'Rule restored'
EOF

sudo systemctl restart odoo
```

---

## ⚠️ Important Notes

1. **These are temporary fixes** - Upgrade to v3.3.9 module as soon as possible
2. **Emergency fixes may be overwritten** during future module upgrades
3. **Document what you did** for future reference
4. **Test thoroughly** after applying fix
5. **Keep backup** for at least 7 days

---

## 📊 Comparison: SQL Fix vs Module Upgrade

| Aspect | SQL Fix | Module Upgrade |
|--------|---------|----------------|
| Speed | ⚡ Immediate | ⏱️ 15-25 min |
| Risk | ⚠️ Medium | ✅ Low |
| Permanence | ⚠️ May be lost | ✅ Permanent |
| Documentation | ❌ Manual | ✅ In module |
| Support | ⚠️ Limited | ✅ Full |
| Rollback | ⚠️ Manual | ✅ Easy |

**Recommendation:** Use SQL fix only for emergency, then upgrade to v3.3.9 properly.

---

## 🎯 Which Option to Choose?

**Choose Option 1 (New Rule) if:**
- ✅ Want minimal changes
- ✅ Don't want to modify existing rules
- ✅ Easier to rollback
- ✅ Cleaner separation

**Choose Option 2 (Extend Existing) if:**
- ✅ Want consolidated rules
- ✅ Prefer fewer total rules
- ✅ Existing rule already well-configured

**Both work equally well - pick based on your preference!**

---

## 📞 After Emergency Fix

**Next steps:**
1. Monitor system for 24 hours
2. Schedule proper module upgrade
3. Plan maintenance window
4. Deploy v3.3.9 module
5. Remove emergency SQL fix (if option 1)
6. Document what was done

---

**Emergency fixes are meant to be temporary!**
**Always follow up with proper module deployment!**
