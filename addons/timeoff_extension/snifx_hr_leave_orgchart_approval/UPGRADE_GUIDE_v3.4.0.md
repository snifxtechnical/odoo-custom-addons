# Quick Upgrade Guide - v3.4.0

## 🎯 What's New in v3.4.0

**One simple improvement:** Click approval level record → Opens full time off request directly!

**Before:** Click → Approval form → Click again → HR Leave form (2 clicks)
**Now:** Click → HR Leave form directly (1 click) ✅

---

## ⚡ Quick Upgrade (5 Minutes)

### **For UAT/Staging:**

```bash
# 1. Upload and extract
cd /opt/odoo/custom-addons/
unzip snifx_hr_leave_orgchart_approval_v3.4.0_PRODUCTION.zip
chown -R odoo:odoo snifx_hr_leave_orgchart_approval

# 2. Upgrade
systemctl stop odoo
sudo -u odoo python3.11 /opt/odoo/odoo/odoo-bin \
  -d odoouat -u snifx_hr_leave_orgchart_approval --stop-after-init
systemctl start odoo

# 3. Test
# Login as L2 approver → Click any pending request
# Should open HR Leave form directly ✅
```

---

### **For Production:**

```bash
# 1. Backup (always!)
sudo -u postgres pg_dump odooprod > /backup/backup_$(date +%Y%m%d).sql

# 2. Deploy
cd /opt/odoo/custom-addons/
unzip snifx_hr_leave_orgchart_approval_v3.4.0_PRODUCTION.zip
chown -R odoo:odoo snifx_hr_leave_orgchart_approval

# 3. Upgrade
systemctl stop odoo
sudo -u odoo python3.11 /opt/odoo/odoo/odoo-bin \
  -d odooprod -u snifx_hr_leave_orgchart_approval --stop-after-init
systemctl start odoo

# 4. Verify
# Click any approval level → Should open leave form ✅
```

---

## ✅ What Gets Installed

1. **New method:** `open_record()` in approval_level model
2. **New view:** Tree redirect configuration
3. **No data changes:** Pure functionality upgrade
4. **No breaking changes:** Everything else works the same

---

## 🧪 Quick Test

```
1. Login as approver with pending requests
2. Go to: Time Off → My Pending Approvals  
3. Click any record in the list
4. Expected: Opens HR Leave form (not approval level form)
5. Result: ✅ PASS
```

---

## 🔙 Rollback (If Needed)

**Super easy:**

```bash
# Disable redirect, keep v3.4.0
sudo -u odoo psql [database] -c \
  "UPDATE ir_ui_view SET active = FALSE \
   WHERE name = 'leave.approval.level.tree.open.leave';"
systemctl restart odoo
```

**Or restore from backup:**

```bash
systemctl stop odoo
sudo -u postgres psql [database] < /backup/backup_YYYYMMDD.sql
systemctl start odoo
```

---

## 📊 Version Comparison

| What | v3.3.9 | v3.4.0 |
|------|--------|--------|
| Filter works | ✅ | ✅ |
| Click behavior | Opens level form | Opens leave form ⭐ |
| UX | Good | Better ⭐ |
| Risk | - | Very Low |

---

## ❓ FAQ

**Q: Will this confuse users?**
A: No, it's more intuitive! Opens what they actually want to see.

**Q: Can I still access approval level form?**
A: Yes, via form view or direct link if needed.

**Q: Do I need to train users?**
A: No, behavior is self-explanatory.

**Q: Any risks?**
A: Very low - only changes click behavior, no data changes.

**Q: Can I deploy during business hours?**
A: Yes, no downtime required.

---

## 🎯 Recommendation

**Deploy:** During regular maintenance window  
**Test:** On UAT first (5 minutes)  
**Risk:** Very Low  
**User Impact:** Positive  
**Communication:** Optional (self-explanatory)

---

## 📞 Need Help?

**Issue:** Upgrade fails
**Check:** 
- Folder name: `snifx_hr_leave_orgchart_approval`
- Python version: 3.10+
- Check logs: `journalctl -u odoo -n 50`

**Issue:** Click still opens approval form
**Solution:**
- Clear browser cache (Ctrl+Shift+Delete)
- Verify view is active in database
- Restart Odoo

---

## ✅ Success Checklist

```
□ Backup database
□ Deploy to UAT first
□ Test click behavior
□ Verify HR Leave form opens
□ Deploy to production
□ Monitor for 1 hour
□ Celebrate improved UX! 🎉
```

---

**Version:** 18.0.3.4.0  
**Upgrade From:** v3.3.9, v3.3.8, earlier  
**Time Required:** 5-10 minutes  
**Risk Level:** Very Low ✅  
**User Training:** None needed ✅
