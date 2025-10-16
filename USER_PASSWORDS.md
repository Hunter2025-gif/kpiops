# 🔐 KAMPALA PHARMACEUTICAL INDUSTRIES - USER PASSWORDS

## Current System Users & Their Passwords

### 🔧 ADMIN ACCESS
```
Username: admin
Password: admin123
Role: Superuser (Full System Access)
```

### 👨‍💼 MANAGEMENT ROLES
```
Username: qa_officer
Password: qa123
Role: Quality Assurance Officer

Username: store_manager  
Password: store123
Role: Store Manager

Username: qa_user
Password: qa123
Role: QA User

Username: qc_user
Password: qc123
Role: Quality Control User

Username: regulatory_user
Password: regulatory123
Role: Regulatory Affairs User
```

### 👷‍♂️ PRODUCTION OPERATORS
```
Username: mixing_operator
Password: mixing123
Role: Mixing Operator

Username: granulation_operator
Password: granulation123
Role: Granulation Operator

Username: blending_operator
Password: blending123
Role: Blending Operator

Username: compression_operator
Password: compression123
Role: Compression Operator

Username: coating_operator
Password: coating123
Role: Coating Operator

Username: drying_operator
Password: drying123
Role: Drying Operator

Username: filling_operator
Password: filling123
Role: Filling Operator

Username: tube_filling_operator
Password: tube123
Role: Tube Filling Operator

Username: sorting_operator
Password: sorting123
Role: Sorting Operator
```

### 📦 PACKAGING OPERATORS
```
Username: packing_operator
Password: packing123
Role: Packing Operator

Username: blister_packing_operator
Password: blister123
Role: Blister Packing Operator

Username: bulk_packing_operator
Password: bulk123
Role: Bulk Packing Operator

Username: capsule_filling_operator
Password: capsule123
Role: Capsule Filling Operator
```

### 🧹 SUPPORT ROLES
```
Username: cleaning_operator
Password: cleaning123
Role: Cleaning Operator

Username: dispensing_operator
Password: dispensing123
Role: Dispensing Operator

Username: equipment_operator
Password: equipment123
Role: Equipment Operator
```

### 👨‍💼 SUPERVISORY ROLES
```
Username: production_supervisor
Password: production123
Role: Production Supervisor

Username: shift_supervisor
Password: shift123
Role: Shift Supervisor
```

## 🔄 Password Reset Options

### Option 1: Admin Panel Bulk Reset
1. Go to: http://127.0.0.1:8000/admin/accounts/customuser/
2. Select users you want to reset
3. Choose "Reset passwords to default (role123)" from Actions dropdown
4. Click "Go" - passwords will be reset to pattern: [role]123

### Option 2: Individual Password Reset
1. Go to user list in admin panel
2. Click on any user
3. Use the custom "Reset Password" link
4. Set custom password or use suggested default

### Option 3: Manual Password Change
1. Go to admin panel → Users
2. Click on user → Change password
3. Set any custom password you want

## 🔑 Password Patterns Used

- **Admin:** admin123
- **QA roles:** qa123
- **Store roles:** store123  
- **QC roles:** qc123
- **Regulatory:** regulatory123
- **Production operators:** [operation]123 (mixing123, coating123, etc.)
- **Supervisors:** [type]123 (production123, shift123)
- **Default fallback:** user123

## 🚀 Quick Login Test

1. **Start server:** `.\start_server.ps1`
2. **Login URL:** http://127.0.0.1:8000/accounts/login/
3. **Admin URL:** http://127.0.0.1:8000/admin/

### Test Different Roles:
- Login as `qa_officer` / `qa123` → QA Dashboard
- Login as `mixing_operator` / `mixing123` → Operator Dashboard
- Login as `store_manager` / `store123` → Store Dashboard
- Login as `admin` / `admin123` → Full Admin Access

## 🛡️ Security Notes

- All passwords follow the pattern: [role_prefix]123
- Passwords can be reset individually or in bulk via admin panel
- New password reset functionality added to admin interface
- Users are automatically redirected to role-appropriate dashboards after login

---
**System Status:** ✅ Ready for Production Testing
**Last Updated:** July 30, 2025
