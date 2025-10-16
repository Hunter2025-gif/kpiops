# Copilot Instructions for Kampala Pharmaceutical Industries Operations System

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Context
This is a pharmaceutical operations management system for Kampala Pharmaceutical Industries. The system manages the complete production workflow from BMR creation to finished goods storage.

## Key Domain Knowledge

### Pharmaceutical Concepts
- **BMR (Batch Manufacturing Record)**: Critical document tracking all manufacturing steps, materials, and quality checks
- **Batch Numbers**: Format XXX-YYYY (e.g., 0012025 = 1st batch of 2025)  
- **Quality Control**: Testing phases that can approve/reject batches
- **Phase Rollback**: Failed QC sends batches back to previous phases

### Product Types & Workflows
- **Ointments**: Mixing → Tube Filling workflow
- **Tablets (Normal)**: Granulation → Blending → Compression → [Coating] → Blister Packing
- **Tablets (Type 2)**: Same as normal but uses Bulk Packing instead of Blister
- **Capsules**: Drying → Blending → Filling → Blister Packing

### User Roles
- Production Manager: Requests BMRs from QA, manages production planning
- QA: Creates BMRs, final quality reviews
- Regulatory: Approves/rejects BMRs
- Store Manager: Dispenses materials
- Various Operators: Handle specific production phases
- QC: Quality control testing and approvals

## Code Guidelines

### Django Patterns
- Use model inheritance for common fields
- Implement proper foreign key relationships
- Add `__str__` methods for all models
- Use Django admin for data management

### Workflow Engine
- Phases auto-trigger when previous completes
- Handle special routing (tablet coating, packing types)
- Implement rollback mechanisms for QC failures
- Track phase execution with timestamps and operators

### API Design
- Use Django REST Framework viewsets
- Implement role-based filtering in querysets
- Add proper serializers for different views (list, detail, create)
- Include audit fields in API responses

### Frontend Integration
- Use Bootstrap for responsive design
- Implement real-time updates for phase changes
- Show role-appropriate dashboards
- Display batch numbers prominently

## Database Considerations
- Use unique constraints for batch numbers
- Index frequently queried fields (status, dates, user roles)
- Implement soft deletes for audit trails
- Store phase-specific data in JSON fields when flexible

## Security & Compliance
- All BMR changes require electronic signatures
- Implement audit trails for regulatory compliance
- Use role-based permissions strictly
- Log all user actions with timestamps

When working on this project, prioritize pharmaceutical industry compliance, data integrity, and clear audit trails.
