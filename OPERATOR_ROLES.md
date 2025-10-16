# Operator Roles - Kampala Pharmaceutical Industries

## Production Workflow-Based User Roles

### 🏛️ **Administrative & Quality Roles**
- **Admin** (`admin`) - System Administrator
- **QA** (`qa`) - Quality Assurance Officer (BMR creation)
- **Regulatory** (`regulatory`) - Regulatory Affairs Officer
- **QC** (`qc`) - Quality Control Analyst (testing and approval)

### 🏪 **Store Management**
- **Store Manager** (`store_manager`) - Materials and Inventory Management
- **Dispensing Operator** (`dispensing_operator`) - Material Dispensing

### 🏭 **Production Operators by Workflow**

#### **Ointment Production Workflow**
1. **Mixing Operator** (`mixing_operator`) - Raw material mixing
2. **Tube Filling Operator** (`tube_filling_operator`) - Tube filling operations

#### **Tablet Production Workflow (Normal & Type 2)**
1. **Granulation Operator** (`granulation_operator`) - Wet/dry granulation
2. **Blending Operator** (`blending_operator`) - Final blending operations
3. **Compression Operator** (`compression_operator`) - Tablet compression
4. **Coating Operator** (`coating_operator`) - Tablet coating (optional for some products)
5. **Sorting Operator** (`sorting_operator`) - Product sorting and inspection

#### **Capsule Production Workflow**
1. **Drying Operator** (`drying_operator`) - Material drying operations
2. **Blending Operator** (`blending_operator`) - Shared with tablet workflow
3. **Filling Operator** (`filling_operator`) - Capsule filling operations

### 📦 **Single Packing Operation**
- **Packing Operator** (`packing_operator`) - Handles ALL packing types:
  - Blister Packing (for tablets/capsules)
  - Bulk Packing (Type 2 tablets)
  - Secondary Packing (final packaging)

### 🔧 **Maintenance & Support**
- **Equipment Operator** (`equipment_operator`) - Equipment operations and maintenance
- **Cleaning Operator** (`cleaning_operator`) - Cleaning and sanitation

## Sample Login Credentials

### **Administrative Access**
```
Admin: username=admin, password=admin123
```

### **Quality & Regulatory**
```
QA: username=qa_user, password=qa123
Regulatory: username=regulatory_user, password=reg123
QC: username=qc_user, password=qc123
```

### **Store Management**
```
Store Manager: username=store_manager, password=store123
Dispensing: username=dispensing_operator, password=disp123
```

### **Ointment Production**
```
Mixing: username=mixing_operator, password=mix123
Tube Filling: username=tube_filling_operator, password=tube123
```

### **Tablet Production**
```
Granulation: username=granulation_operator, password=gran123
Blending: username=blending_operator, password=blend123
Compression: username=compression_operator, password=comp123
Coating: username=coating_operator, password=coat123
Sorting: username=sorting_operator, password=sort123
```

### **Capsule Production**
```
Drying: username=drying_operator, password=dry123
Filling: username=filling_operator, password=fill123
```

### **Packing (All Types)**
```
Packing: username=packing_operator, password=pack123
```

### **Maintenance**
```
Equipment: username=equipment_operator, password=equip123
Cleaning: username=cleaning_operator, password=clean123
```

## Workflow Phase Assignments

### **Product Type → Workflow → Operators**

#### **Ointments**
- Mixing → Tube Filling → Packing

#### **Tablets (Normal)**
- Granulation → Blending → Compression → [Coating] → Sorting → Packing (Blister)

#### **Tablets (Type 2)**
- Granulation → Blending → Compression → [Coating] → Sorting → Packing (Bulk)

#### **Capsules**
- Drying → Blending → Filling → Packing (Blister)

### **Role-Based Dashboard Access**
- **QA** → BMR creation and management
- **Regulatory** → Compliance and approvals
- **Store Manager** → Inventory and materials
- **QC** → Testing and quality control
- **Production Operators** → Phase-specific production tasks
- **Packing Operator** → All packing operations (blister, bulk, secondary)
- **Maintenance** → Equipment and cleaning operations

## Key Features

### **Simplified Role Structure**
- ✅ **Removed**: Weighing, Validation, Production Supervisor, Shift Supervisor
- ✅ **Consolidated**: All packing operations under single Packing Operator role
- ✅ **Workflow-aligned**: Each role matches your described production phases

### **Single Packing Dashboard**
- **Packing Operator** handles:
  - Blister Packing (tablets, capsules)
  - Bulk Packing (Type 2 tablets)
  - Secondary Packing (final packaging)
- **Dashboard shows**: All packing tasks regardless of type
- **Flexibility**: Can be assigned to different packing phases as needed

### **Maintenance Roles**
- **Equipment Operator**: Equipment setup, operation, basic maintenance
- **Cleaning Operator**: Line clearance, equipment cleaning, sanitation

---

**Total Operator Roles**: 18 streamlined roles matching your exact workflow requirements
**Packing Consolidation**: Single operator for all packing types (blister, bulk, secondary)
**Workflow Compliance**: Each role maps directly to production phases you described
