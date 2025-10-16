# Kampala Pharmaceutical Industries - Operations System

## System Overview

This Django-based pharmaceutical operations system is designed specifically for Kampala Pharmaceutical Industries' operations department. It provides role-based dashboards and workflow management for different user types in pharmaceutical production.

## ✅ System Status: READY TO USE

The system is now fully operational with:
- ✅ All user roles and permissions configured
- ✅ Manual batch number entry (as requested)
- ✅ Role-based dashboards for all user types
- ✅ Home page that routes users to their appropriate dashboard
- ✅ Virtual environment and easy startup scripts
- ✅ Database migrations completed
- ✅ Admin interface configured

## User Roles Supported

### Quality Assurance (QA)
- **Role**: `qa`
- **Dashboard**: QA Dashboard with BMR management, batch tracking
- **Responsibilities**: Create and manage BMRs, quality control oversight

### Production Manager
- **Role**: `production_manager`
- **Dashboard**: Production Manager Dashboard with BMR request functionality
- **Responsibilities**: Production planning, BMR requests to QA, production oversight

### Regulatory Affairs
- **Role**: `regulatory`
- **Dashboard**: Regulatory dashboard for compliance tracking
- **Responsibilities**: Regulatory compliance, documentation oversight

### Store Manager
- **Role**: `store_manager`
- **Dashboard**: Inventory and materials management
- **Responsibilities**: Raw materials, inventory control

### Quality Control (QC)
- **Role**: `qc`
- **Dashboard**: Testing and quality control dashboard
- **Responsibilities**: Product testing, quality verification

### Production Operators
Multiple operator roles with specialized dashboards:
- **Mixing Operator** (`mixing_operator`)
- **Granulation Operator** (`granulation_operator`)
- **Blending Operator** (`blending_operator`)
- **Compression Operator** (`compression_operator`)
- **Coating Operator** (`coating_operator`)
- **Drying Operator** (`drying_operator`)
- **Tube Filling Operator** (`tube_filling_operator`)
- **Filling Operator** (`filling_operator`)

### Packaging Team
- **Blister Packing** (`blister_packing_operator`)
- **Bulk Packing** (`bulk_packing_operator`)
- **Packing Operator** (`packing_operator`)

## Starting the System

### Option 1: Using Scripts (Recommended)
```powershell
# Activate environment and start server
.\start_server.ps1
```

### Option 2: Manual Steps
```powershell
# Activate virtual environment
.\activate_env.ps1

# Start Django server
python manage.py runserver
```

### Option 3: Batch File (Windows)
```cmd
start_server.bat
```

## Accessing the System

1. **Server URL**: http://127.0.0.1:8000/
2. **Admin Panel**: http://127.0.0.1:8000/admin/
3. **Default Login**: Use the superuser account created during setup

## Key Features

### 1. Manual Batch Number Entry
- **Requirement Met**: Batch numbers must be entered manually by QA (not auto-generated)
- **Validation**: System ensures batch numbers are unique and follow proper format
- **Location**: BMR creation form requires manual batch number input

### 2. Role-Based Dashboard Access
- **Home Page**: Automatically routes users to their role-specific dashboard
- **Access Control**: Users can only access dashboards appropriate to their role
- **Navigation**: Easy navigation between different sections

### 3. Batch Manufacturing Records (BMR)
- **Creation**: QA can create new BMRs with manual batch numbers
- **Tracking**: Full lifecycle tracking from creation to completion
- **Status Management**: Draft, submitted, approved, rejected states

### 4. Production Workflow
- **Phase Management**: Different production phases with role-specific access
- **Status Tracking**: Real-time status updates for each production phase
- **Quality Gates**: QA and QC checkpoints throughout the process

## Admin Interface

### Creating Users
1. Access admin at http://127.0.0.1:8000/admin/
2. Go to "Users" under "ACCOUNTS"
3. Add new user with appropriate role
4. Set permissions as needed

### Managing Products
1. Access "Products" section
2. Add pharmaceutical products with specifications
3. Configure production phases and requirements

### BMR Management
1. View all BMRs in the admin interface
2. Track status and phase completions
3. Generate reports and analytics

## File Structure

```
kampala_pharma/
├── accounts/           # User management and roles
├── products/          # Product master data
├── bmr/              # Batch Manufacturing Records
├── workflow/         # Production workflow engine
├── dashboards/       # Role-based dashboard views
├── templates/        # HTML templates
├── static/          # CSS, JS, images
├── kampala_pharma/  # Main Django settings
├── activate_env.ps1 # Environment activation script
├── start_server.ps1 # Server startup script
└── README.md        # This file
```

## Database

- **Engine**: SQLite (for development)
- **Migrations**: All applied and ready
- **Data**: Sample data loaded for testing

## API Endpoints (Future Enhancement)

The system is designed to support REST API endpoints for:
- BMR management
- Workflow operations
- Dashboard data
- User management

## Support and Maintenance

### Troubleshooting
1. **Server won't start**: Check if virtual environment is activated
2. **Database errors**: Run `python manage.py migrate`
3. **Permission issues**: Check user roles in admin interface
4. **Template errors**: Ensure templates directory is configured

### Backup
- Regular database backups recommended
- Export user data and BMR records periodically

### Updates
- Keep Django and dependencies updated
- Test changes in development environment first

## Security Notes

- Change default admin credentials in production
- Use proper database (PostgreSQL/MySQL) for production
- Enable HTTPS for production deployment
- Regular security updates for all dependencies

---

**System Developed for**: Kampala Pharmaceutical Industries Operations Department  
**Version**: 1.0  
**Status**: Production Ready  
**Last Updated**: {{ current_date }}
