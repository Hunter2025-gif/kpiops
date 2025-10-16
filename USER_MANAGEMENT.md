# User Management Guide

## Creating Users in Admin Panel

### Step 1: Access Admin Panel
1. Go to http://127.0.0.1:8000/admin/
2. Login with admin credentials (see below)

### Step 2: Navigate to Users
1. Look for "ACCOUNTS" section in the admin panel
2. Click on "Custom users" or "Users"
3. Click "Add Custom user" button

### Step 3: Fill User Information
**Required Fields:**
- Username: Unique identifier for login
- Email: User's email address
- First name: User's first name
- Last name: User's last name
- Role: Select from dropdown (qa, regulatory, store_manager, etc.)
- Employee ID: Unique employee identifier
- Department: User's department
- Password: Set a secure password

**Optional Fields:**
- Phone number
- Signature upload
- Additional permissions

### Available User Roles
- **qa**: Quality Assurance Officer
- **regulatory**: Regulatory Affairs Officer
- **store_manager**: Store Manager
- **qc**: Quality Control Analyst
- **mixing_operator**: Mixing Operator
- **granulation_operator**: Granulation Operator
- **blending_operator**: Blending Operator
- **compression_operator**: Compression Operator
- **coating_operator**: Coating Operator
- **drying_operator**: Drying Operator
- **tube_filling_operator**: Tube Filling Operator
- **filling_operator**: Filling Operator
- **packaging_store**: Packaging Store Staff
- **packing_supervisor**: Packing Supervisor
- **sorting_operator**: Sorting Operator

## Sample Login Credentials

### Admin Account
- **Username**: admin
- **Password**: admin123
- **Role**: System Administrator

### Test Users
- **QA Officer**: username=`qa_user`, password=`qa123`
- **Regulatory**: username=`regulatory_user`, password=`reg123`
- **Store Manager**: username=`store_manager`, password=`store123`
- **QC Analyst**: username=`qc_user`, password=`qc123`
- **Production Operator**: username=`mixing_operator`, password=`mix123`

## Troubleshooting

### If users section is not visible:
1. Ensure you're logged in as admin/superuser
2. Check that the accounts app is properly installed
3. Verify admin.py is correctly configured

### If creating user fails:
1. Check that all required fields are filled
2. Ensure username and employee_id are unique
3. Verify password meets requirements
4. Check that the role is selected from the dropdown

### If login fails:
1. Verify username and password
2. Check that user account is active
3. Ensure user has appropriate permissions

## User Permissions

### Standard Users
- Can access their role-specific dashboard
- Can view and edit data relevant to their role
- Cannot access admin panel unless staff status is enabled

### Staff Users
- Have admin panel access
- Can manage data within their department
- Can create/edit records they have permission for

### Superusers
- Full system access
- Can create/modify any user
- Can access all admin functions
- Can modify system settings

## Security Notes
- Change default passwords immediately
- Use strong passwords for all accounts
- Regularly review user permissions
- Disable inactive user accounts
- Monitor login activities through UserSession model
