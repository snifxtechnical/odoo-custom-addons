# Quick Start - v3.3.9 Production Deployment

## 📦 What's in This Package

```
snifx_hr_leave_orgchart_approval/
├── PRODUCTION_DEPLOYMENT_GUIDE.md    ← Full deployment guide
├── CHANGELOG_v3.3.9.md                ← What changed
├── EMERGENCY_SQL_FIX.md               ← Alternative quick fix
├── QUICK_START.md                     ← This file
└── [module files...]
```

---

## 🎯 What Does v3.3.9 Fix?

**Problem:** Level 2+ approvers couldn't see their assigned time-off requests in "Management → Time Off" filter.

**Fix:** Adds read access record rule for approval level approvers.

**Impact:** ✅ Positive - No breaking changes, only adds missing security rule.

---

## ⚡ Quick Deployment (5 Minutes)

**For experienced admins who just need the commands:**

```bash
# 1. Backup
sudo -u postgres pg_dump odooprod > /backup/backup_$(date +%Y%m%d).sql

# 2. Deploy module
cd /opt/odoo/custom-addons/
sudo unzip /path/to/snifx_hr_leave_orgchart_approval_v3.3.9_PRODUCTION.zip
sudo chown -R odoo:odoo snifx_hr_leave_orgchart_approval

# 3. Upgrade
sudo systemctl stop odoo
sudo -u odoo python3.11 /opt/odoo/odoo/odoo-bin \
  -d odooprod -u snifx_hr_leave_orgchart_approval --stop-after-init
sudo systemctl start odoo

# 4. Verify
sudo -u odoo psql odooprod -c \
  "SELECT name FROM ir_rule WHERE name LIKE '%Approval Level%';"

# Done! Test the filter.
```

---

## 📋 Deployment Options

### **Option A: Proper Module Upgrade** (Recommended)

**Best for:** Scheduled maintenance, proper deployments

**Read:** `PRODUCTION_DEPLOYMENT_GUIDE.md`

**Time:** 15-25 minutes with testing

**Risk:** Low

---

### **Option B: Emergency SQL Fix**

**Best for:** Urgent production fix, can't wait for maintenance window

**Read:** `EMERGENCY_SQL_FIX.md`

**Time:** 2-3 minutes

**Risk:** Medium (temporary fix, needs follow-up)

---

## ✅ Success Checklist

After deployment, verify:

```
□ Module version shows 18.0.3.3.9
□ Security rule exists in database
□ L2 approver can see leaves in filter
□ "Waiting For Me" filter works
□ "My Pending Approvals" menu works
□ Approval functionality works
□ No errors in logs
```

---

## 🔙 Rollback

**If something goes wrong:**

```bash
# Quick rollback: Disable new rule
sudo -u odoo psql odooprod -c \
  "UPDATE ir_rule SET active = FALSE \
   WHERE name LIKE '%Approval Level%';"
sudo systemctl restart odoo

# Full rollback: See PRODUCTION_DEPLOYMENT_GUIDE.md
```

---

## 📞 Support

**Issue:** Filter still empty after deployment
**Solution:** 
1. Verify security rule exists and active = TRUE
2. Clear browser cache completely
3. Try incognito mode
4. Check user groups

**Issue:** Module upgrade fails
**Solution:**
1. Check folder name is exactly: `snifx_hr_leave_orgchart_approval`
2. Verify Python version (need 3.10+)
3. Check upgrade logs for specific errors

---

## 📊 Version Information

| Item | Value |
|------|-------|
| Module Version | 18.0.3.3.9 |
| Previous Version | 18.0.3.3.8 |
| Release Date | January 21, 2026 |
| Odoo Version | 18 CE |
| Python Required | 3.10+ |
| Breaking Changes | None |
| Data Migration | None |

---

## 🎯 Testing Before Production

**Strongly recommended:**

1. Deploy to UAT/staging first
2. Test with actual approvers
3. Verify filter works for all levels
4. Test approval workflow end-to-end
5. Only then deploy to production

---

## 📖 Full Documentation

- **Complete Deployment:** `PRODUCTION_DEPLOYMENT_GUIDE.md` (18 pages)
- **Technical Changes:** `CHANGELOG_v3.3.9.md`
- **Emergency Fix:** `EMERGENCY_SQL_FIX.md`
- **Module README:** `README.md`

---

## ⚠️ Important Reminders

1. ✅ **Always backup before deployment**
2. ✅ **Test on UAT first**
3. ✅ **Schedule during low-traffic time**
4. ✅ **Have rollback plan ready**
5. ✅ **Monitor after deployment**

---

## 🚀 Ready to Deploy?

**Checklist before starting:**

```
□ Read PRODUCTION_DEPLOYMENT_GUIDE.md
□ UAT testing completed
□ Backup ready
□ Maintenance window scheduled
□ Rollback plan prepared
□ Support team available
```

**All checked? Let's go!** 🎯

**Start here:** `PRODUCTION_DEPLOYMENT_GUIDE.md` - Step 1

---

**Questions?** Review the full deployment guide or emergency fix guide based on your needs.

**Good luck with your deployment!** 🎉
