# Testing Guide for Snifx Time Off Officer Balance v2.3.0

## 📋 Overview

This guide provides comprehensive testing scenarios to verify all functionality works correctly after upgrading to version **18.0.2.3.0**.

**Main Fix:** Officers can now create Public Holidays without "Access Denied to Project" errors.

---

## ⚙️ Pre-Testing Setup

### Required Test Users

Create or identify the following test users:

1. **Administrator** (built-in)
   - Group: Administration / Settings
   - Purpose: Verify base functionality

2. **HR Manager** (example: Fritz)
   - Group: Human Resources / Time Off Administrator
   - Purpose: Verify manager-level operations

3. **Time Off Officer** (example: Andri)
   - Group: Time Off / Officer with Balance (Enhanced)
   - Assigned to: At least one department tree
   - Purpose: Main testing user for officer capabilities

4. **Regular Employee** (example: Employee from assigned department)
   - Group: Human Resources / Officer
   - Purpose: Submit time off requests for officer approval

---

## 🧪 Test Scenarios

### 1️⃣ **Public Holiday Management** (PRIMARY FIX)

#### Test 1.1: Officer Creates Public Holiday

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Time Off > Public Holidays**
3. Click **New** button
4. Fill in form:
   - **Reason**: "Test Holiday - Thanksgiving 2024"
   - **Start Date**: 2024-11-28 08:00:00
   - **End Date**: 2024-11-28 23:59:59
   - **Company**: (leave default or select)
5. Click **Save**

**Expected Result:**
- ✅ Form saves successfully without errors
- ✅ No "Oh snap!" popup about project.project access
- ✅ Public holiday appears in list view
- ✅ Calendar view shows the holiday

**Failure Indicators:**
- ❌ "Access Denied to Project (project.project)" error
- ❌ "Access Denied to Resource Calendar" error
- ❌ Form fails to save

---

#### Test 1.2: Officer Edits Public Holiday

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Time Off > Public Holidays**
3. Open existing public holiday (created in Test 1.1)
4. Modify:
   - **Reason**: "Test Holiday - Updated Name"
5. Click **Save**

**Expected Result:**
- ✅ Changes saved successfully
- ✅ Updated name appears in list view

---

#### Test 1.3: Officer Deletes Public Holiday

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Time Off > Public Holidays**
3. Open test public holiday
4. Click **Action > Delete**
5. Confirm deletion

**Expected Result:**
- ✅ Record deleted successfully
- ✅ No longer appears in list view

---

#### Test 1.4: Officer Views Public Holidays in Calendar

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Time Off > Public Holidays**
3. Switch to **Calendar** view
4. Verify holidays display correctly

**Expected Result:**
- ✅ All public holidays visible in calendar
- ✅ Correct dates and names displayed
- ✅ Can navigate months/years

---

### 2️⃣ **Time Off Approval Workflow**

#### Test 2.1: Employee Submits Time Off Request

**Steps:**
1. Login as **Regular Employee**
2. Navigate to: **Time Off > My Time Off**
3. Click **New Time Off**
4. Fill in form:
   - **Time Off Type**: Annual Leave
   - **From**: Tomorrow
   - **To**: Tomorrow + 2 days
   - **Description**: "Family vacation"
5. Click **Save** then **Confirm**

**Expected Result:**
- ✅ Request created with state "To Approve"
- ✅ Activity created for eligible officers
- ✅ Request visible to officers

---

#### Test 2.2: Officer Sees Time Off Request

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Time Off > My Team's Time Off**
3. Locate the request from Test 2.1

**Expected Result:**
- ✅ Request visible in list (if employee is in assigned department)
- ✅ Request NOT visible if employee is outside assigned departments
- ✅ Can open request form

---

#### Test 2.3: Officer Approves Time Off Request

**Steps:**
1. Login as **Officer** (Andri)
2. Open time off request from Test 2.1
3. Verify buttons are visible:
   - **Approve** button
   - **Refuse** button
4. Click **Approve**

**Expected Result:**
- ✅ Request state changes to "Approved" or "Second Approval"
- ✅ Activity marked as done
- ✅ Employee receives notification (if email configured)

---

#### Test 2.4: Officer Cannot Approve Own Request

**Steps:**
1. Login as **Officer** (Andri)
2. Create time off request for self
3. Try to approve own request

**Expected Result:**
- ✅ Approve/Validate buttons should be hidden or disabled
- ✅ Or display error message preventing self-approval

---

### 3️⃣ **Department Hierarchy Display**

#### Test 3.1: Officer Assignment to Parent Department

**Setup:**
- Department Structure:
  - **Technical** (parent)
    - **IT Infrastructure** (child)
    - **IT Development** (child)
- Officer Andri assigned to: **Technical** department

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Time Off > My Team's Time Off**
3. Check visible employees

**Expected Result:**
- ✅ Can see employees from **Technical** department
- ✅ Can see employees from **IT Infrastructure** (child)
- ✅ Can see employees from **IT Development** (child)
- ✅ Cannot see employees from other departments (e.g., Marketing, Sales)

---

#### Test 3.2: Officer Assignment to Child Department

**Setup:**
- Officer Andri assigned to: **IT Infrastructure** only

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Time Off > My Team's Time Off**
3. Check visible employees

**Expected Result:**
- ✅ Can see employees from **IT Infrastructure**
- ✅ Cannot see employees from **IT Development**
- ✅ Cannot see employees from parent **Technical** department

---

#### Test 3.3: Multiple Department Assignments

**Setup:**
- Officer Andri assigned to:
  - **Technical** department
  - **Marketing** department

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Time Off > My Team's Time Off**
3. Check visible employees

**Expected Result:**
- ✅ Can see employees from **Technical** and all its children
- ✅ Can see employees from **Marketing** and all its children
- ✅ Cannot see employees from unassigned departments

---

### 4️⃣ **Activity Notifications**

#### Test 4.1: Officer Receives Activity on New Request

**Steps:**
1. Login as **Regular Employee**
2. Submit time off request (validation_type = 'hr')
3. Logout
4. Login as **Officer** (Andri)
5. Navigate to: **My Profile (top-right) > My Activities**

**Expected Result:**
- ✅ New activity appears: "Time Off Approval"
- ✅ Activity shows employee name and time off details
- ✅ Can click activity to open time off request
- ✅ Activity disappears after approval

---

#### Test 4.2: Multiple Officers Receive Same Activity

**Setup:**
- Two officers assigned to same department:
  - Officer Andri
  - Officer Fritz

**Steps:**
1. Employee submits time off request
2. Login as **Officer Andri** → check activities
3. Login as **Officer Fritz** → check activities

**Expected Result:**
- ✅ Both officers receive same activity
- ✅ When one officer approves, activity is marked done for both

---

#### Test 4.3: Activity for Two-Tier Approval

**Steps:**
1. Employee submits annual leave (validation_type = 'both')
2. Manager approves first tier
3. Login as **Officer** (Andri)
4. Check activities

**Expected Result:**
- ✅ Officer receives "Time Off Second Approve" activity
- ✅ Activity created only after manager approval

---

### 5️⃣ **Security Boundaries**

#### Test 5.1: Officer Cannot Modify Projects

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Project > All Projects** (if menu visible)
3. Try to:
   - Create new project
   - Edit existing project
   - Delete project

**Expected Result:**
- ✅ Cannot create projects (button hidden or disabled)
- ✅ Cannot edit projects (form is read-only or access denied)
- ✅ Cannot delete projects (action not available)
- ✅ Can VIEW projects (list view accessible)

---

#### Test 5.2: Officer Cannot Access Employee Private Info

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Employees**
3. Open any employee record
4. Check available tabs

**Expected Result:**
- ✅ **Resume** tab visible and accessible
- ✅ **Work Information** tab visible and accessible
- ❌ **Private Information** tab hidden
- ❌ **HR Settings** tab hidden

---

#### Test 5.3: Officer Cannot Modify Working Hours

**Steps:**
1. Login as **Officer** (Andri)
2. Try to navigate to: **Settings > Technical > Resources > Working Hours**
3. If accessible, try to edit

**Expected Result:**
- ✅ Can VIEW working hours (read access)
- ❌ Cannot CREATE new working hours
- ❌ Cannot EDIT existing working hours
- ❌ Cannot DELETE working hours

---

### 6️⃣ **Balance Report Access**

#### Test 6.1: Officer Views Balance Report

**Steps:**
1. Login as **Officer** (Andri)
2. Navigate to: **Time Off > Reporting > Time Off Summary**
3. Check visible employees in report

**Expected Result:**
- ✅ Report shows employees from assigned departments only
- ✅ Can filter by department
- ✅ Can export to Excel
- ✅ Balance data is accurate

---

### 7️⃣ **Multi-Company Scenarios** (if applicable)

#### Test 7.1: Officer in Multi-Company Environment

**Setup:**
- Company A and Company B exist
- Officer Andri assigned to department in Company A

**Steps:**
1. Login as **Officer** (Andri)
2. Switch to Company B (if possible)
3. Navigate to: **Time Off > My Team's Time Off**

**Expected Result:**
- ✅ Cannot see employees from Company B
- ✅ Can only manage departments in assigned company

---

## 🔍 Regression Testing

After all above tests pass, verify these still work:

### Existing Features
- ✅ Employee can request time off
- ✅ Manager can approve time off
- ✅ HR Manager can configure time off types
- ✅ Public holidays appear in employee calendars
- ✅ Time off dashboard statistics accurate
- ✅ Email notifications still sent (if configured)

---

## 📊 Test Results Template

Use this template to record your test results:

```
Test Date: ___________
Tester: ___________
Odoo Version: 18.0
Module Version: 18.0.2.3.0

| Test ID | Test Name | Status | Notes |
|---------|-----------|--------|-------|
| 1.1 | Officer Creates Public Holiday | ☐ Pass ☐ Fail | |
| 1.2 | Officer Edits Public Holiday | ☐ Pass ☐ Fail | |
| 1.3 | Officer Deletes Public Holiday | ☐ Pass ☐ Fail | |
| 1.4 | Officer Views Calendar | ☐ Pass ☐ Fail | |
| 2.1 | Employee Submits Request | ☐ Pass ☐ Fail | |
| 2.2 | Officer Sees Request | ☐ Pass ☐ Fail | |
| 2.3 | Officer Approves Request | ☐ Pass ☐ Fail | |
| 2.4 | Self-Approval Prevention | ☐ Pass ☐ Fail | |
| 3.1 | Parent Dept Assignment | ☐ Pass ☐ Fail | |
| 3.2 | Child Dept Assignment | ☐ Pass ☐ Fail | |
| 3.3 | Multiple Assignments | ☐ Pass ☐ Fail | |
| 4.1 | Officer Receives Activity | ☐ Pass ☐ Fail | |
| 4.2 | Multiple Officers Activity | ☐ Pass ☐ Fail | |
| 4.3 | Two-Tier Activity | ☐ Pass ☐ Fail | |
| 5.1 | Cannot Modify Projects | ☐ Pass ☐ Fail | |
| 5.2 | Cannot Access Private Info | ☐ Pass ☐ Fail | |
| 5.3 | Cannot Modify Working Hours | ☐ Pass ☐ Fail | |
| 6.1 | Balance Report Access | ☐ Pass ☐ Fail | |
| 7.1 | Multi-Company | ☐ Pass ☐ Fail | |

Overall Result: ☐ ALL PASS ☐ SOME FAILURES

Critical Failures (if any):
- ___________________________________
- ___________________________________
```

---

## 🐛 Troubleshooting

### Issue: "Access Denied to Project" still appears

**Possible Causes:**
1. Module not upgraded properly
2. Browser cache not cleared
3. Access rights not reloaded

**Solutions:**
```bash
# 1. Restart Odoo service
sudo systemctl restart odoo

# 2. Upgrade module with -u flag
./odoo-bin -u snifx_timeoff_officer_department -d your_database

# 3. Clear browser cache (Ctrl+Shift+Delete)
# 4. Logout and login again
```

---

### Issue: Officer doesn't see approve buttons

**Check:**
1. User has "Officer with Balance (Enhanced)" group
2. User has assignment to employee's department
3. Leave request state is 'confirm' or 'validate1'
4. Officer is not approving their own request

---

### Issue: Activities not created

**Check:**
1. Activity types exist: "Time Off Approval", "Time Off Second Approve"
2. Officer assignments are active
3. Employee's department matches officer assignment

---

## 📞 Support

If you encounter issues:

1. **Check Logs**: `/var/log/odoo/odoo-server.log`
2. **Enable Developer Mode**: Settings > Activate Developer Mode
3. **Check Access Rights**: Settings > Technical > Security > Access Rights
4. **Verify Record Rules**: Settings > Technical > Security > Record Rules

---

## ✅ Sign-Off

After completing all tests:

```
Tested by: ___________________
Date: ___________________
Signature: ___________________

☐ All critical tests PASSED
☐ Ready for PRODUCTION deployment
☐ Issues found (see notes above)
```

---

**Version**: 2.3.0  
**Document Date**: 2024-11-20  
**Last Updated**: 2024-11-20
