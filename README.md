# Kampala Pharmaceutical Industries - Operations Management System

A comprehensive pharmaceutical production workflow management system built with Django, designed specifically for Kampala Pharmaceutical Industries operations department.

## 🏥 System Overview

This system manages the complete pharmaceutical production workflow from BMR (Batch Manufacturing Record) creation to finished goods storage, with automatic phase triggering and role-based dashboards.

### 🔄 Product Workflows

#### **Ointments Flow:**
BMR Creation → Regulatory Approval → Material Dispensing → Mixing → QC Testing → Tube Filling → Packaging Material Release → Secondary Packaging → Final QA → Finished Goods Store

#### **Tablets Flow (Normal & Type 2):**
BMR Creation → Regulatory Approval → Material Dispensing → Granulation → Blending → Compression → QC Testing → Sorting → [Coating (if coated)] → Packaging Material Release → [Blister/Bulk Packing] → Secondary Packaging → Final QA → Finished Goods Store

#### **Capsules Flow:**
BMR Creation → Regulatory Approval → Material Dispensing → Drying → Blending → QC Testing → Filling → Sorting → Packaging Material Release → Blister Packing → Secondary Packaging → Final QA → Finished Goods Store

## 👥 User Roles & Dashboards

- **QA (Quality Assurance)** - Creates BMRs, Final QA reviews
- **Regulatory** - BMR approvals  
- **Store Manager** - Material dispensing
- **Various Operators** - Mixing, Granulation, Blending, Compression, Coating, Drying, Filling, Tube Filling, Sorting
- **QC (Quality Control)** - Quality testing and approvals
- **Packaging Store** - Material release
- **Packing Supervisor** - Secondary packaging operations
- **Admin** - System oversight and Django administration

## 🔧 Key Features

### **BMR Management**
- Manual batch number entry by QA (XXX-YYYY format, e.g., 0012025)
- Product selection with auto-populated details
- Material requirements tracking
- Electronic signatures and approvals

### **Workflow Automation**
- Automatic phase triggering upon completion
- Product-type specific routing
- Quality control checkpoints with approval/rejection
- Rollback mechanisms for failed phases

### **Dashboard System**
- Role-based access control
- Real-time phase updates
- User activity history
- Notification system

### **Product Management**
- Support for Ointments, Tablet Normal, Tablet 2, and Capsules
- Coating status tracking for tablets
- Ingredient and specification management

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- pip

### Quick Start

1. **Clone/Setup the project:**
   ```bash
   cd "C:\Users\Ronald\Desktop\new system"
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv pharma_env
   pharma_env\Scripts\activate  # Windows
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Setup production phases:**
   ```bash
   python manage.py setup_phases
   ```

7. **Start development server:**
   ```bash
   python manage.py runserver
   ```

8. **Access the system:**
   - Admin Panel: http://127.0.0.1:8000/admin/
   - Login with the superuser credentials created in step 5

## 📋 Initial Data Setup

### 1. Create Users
In Django Admin, create users for different roles:
- Set appropriate roles (qa, regulatory, store_manager, etc.)
- Add employee IDs and departments

### 2. Add Products
Create products with:
- Product codes and names
- Product types (ointment, tablet_normal, tablet_2, capsule)
- For tablets: specify coating status and subtype
- Manufacturing instructions and specifications

### 3. Create BMRs
QA users can create BMRs by:
- Selecting products (details auto-populate)
- Setting batch sizes and dates
- Adding material requirements
- Submitting for regulatory approval

## 🔄 Workflow Process

### BMR Creation (QA Dashboard)
1. QA selects product from dropdown
2. Product details auto-populate (name, type, coating status, etc.)
3. QA manually enters batch number in format XXXYYYY (e.g., 0012025)
4. QA fills batch information and material requirements
5. Submits BMR for regulatory approval

### Regulatory Approval 
1. Regulatory reviews submitted BMRs
2. Can approve or reject with comments
3. Approved BMRs trigger automatic workflow creation

### Production Phases
1. Each phase automatically activates when previous completes
2. Operators start/complete phases in their dashboards
3. QC checkpoints can approve or reject (triggers rollback)
4. Special routing for tablet coating based on product attributes

## 📊 Batch Number Format

Batch numbers must be manually entered by QA officers in the format: **XXXYYYY**
- **XXX**: Sequential batch number (001, 002, 003...)
- **YYYY**: Year (2025)
- **Example**: 0012025 (1st batch of 2025)
- **Validation**: System validates format but QA controls the numbering

## 🏗️ System Architecture

### Backend (Django)
- **accounts/** - User management and authentication
- **products/** - Product master data and specifications  
- **bmr/** - Batch Manufacturing Records
- **workflow/** - Production phases and execution tracking
- **dashboards/** - User dashboards and notifications

### Database Models
- Custom User model with role-based permissions
- Product catalog with tablet-specific attributes
- BMR with manual batch numbering by QA
- Workflow engine with phase dependencies
- Audit trails and electronic signatures

## 🔒 Security Features

- Role-based access control
- Electronic signatures for BMR approvals
- Audit trails for all operations
- Session tracking for compliance

## 🎯 Future Enhancements

- Real-time WebSocket updates
- Advanced reporting and analytics
- Mobile app support
- Integration with laboratory systems
- Barcode scanning for materials

## 📞 Support

For technical support or feature requests, contact the development team.

---

**Kampala Pharmaceutical Industries Operations Department**  
*Ensuring Quality Through Technology*
