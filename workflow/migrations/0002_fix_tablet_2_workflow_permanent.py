"""
Permanent fix for tablet_2 workflow order
This migration ensures bulk_packing always comes before secondary_packaging
"""

from django.db import migrations

def fix_tablet_2_phase_order(apps, schema_editor):
    """Permanently fix the phase order for tablet_2 products"""
    ProductionPhase = apps.get_model('workflow', 'ProductionPhase')
    
    # Define the correct phase order for tablet_2
    tablet_2_phases = [
        ('bmr_creation', 1),
        ('regulatory_approval', 2),
        ('material_dispensing', 3),
        ('granulation', 4),
        ('blending', 5),
        ('compression', 6),
        ('post_compression_qc', 7),
        ('sorting', 8),
        ('coating', 9),  # May be skipped for uncoated tablets
        ('packaging_material_release', 10),
        ('bulk_packing', 11),  # CRITICAL: This must come before secondary_packaging
        ('secondary_packaging', 12),  # CRITICAL: This must come after bulk_packing
        ('final_qa', 13),
        ('finished_goods_store', 14),
    ]
    
    # Update each phase with the correct order
    for phase_name, order in tablet_2_phases:
        ProductionPhase.objects.filter(
            product_type='tablet_2',
            phase_name=phase_name
        ).update(phase_order=order)
    
    # Also fix regular tablet phases to be consistent
    tablet_phases = [
        ('bmr_creation', 1),
        ('regulatory_approval', 2),
        ('material_dispensing', 3),
        ('granulation', 4),
        ('blending', 5),
        ('compression', 6),
        ('post_compression_qc', 7),
        ('sorting', 8),
        ('coating', 9),  # May be skipped for uncoated tablets
        ('packaging_material_release', 10),
        ('blister_packing', 11),  # Normal tablets use blister packing
        ('secondary_packaging', 12),
        ('final_qa', 13),
        ('finished_goods_store', 14),
    ]
    
    # Update regular tablet phases
    for phase_name, order in tablet_phases:
        ProductionPhase.objects.filter(
            product_type='tablet',
            phase_name=phase_name
        ).update(phase_order=order)

def reverse_fix(apps, schema_editor):
    """Reverse migration - not implemented as this is a permanent fix"""
    pass

class Migration(migrations.Migration):
    
    dependencies = [
        ('workflow', '0001_initial'),  # Adjust this to your latest migration
    ]
    
    operations = [
        migrations.RunPython(fix_tablet_2_phase_order, reverse_fix),
    ]
