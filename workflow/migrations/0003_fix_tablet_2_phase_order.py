# Generated migration to fix tablet type 2 workflow phase order

from django.db import migrations

def fix_tablet_2_phase_order(apps, schema_editor):
    """Fix the phase order for tablet type 2 workflow"""
    ProductionPhase = apps.get_model('workflow', 'ProductionPhase')
    
    # Fix bulk_packing and secondary_packaging order for tablet workflows
    try:
        # Update bulk_packing to order 11
        bulk_phases = ProductionPhase.objects.filter(
            phase_name='bulk_packing',
            product_type__in=['tablet', 'tablet_2']
        )
        bulk_phases.update(phase_order=11)
        
        # Update secondary_packaging to order 12  
        secondary_phases = ProductionPhase.objects.filter(
            phase_name='secondary_packaging',
            product_type__in=['tablet', 'tablet_2']
        )
        secondary_phases.update(phase_order=12)
        
        print(f"Fixed phase order: bulk_packing=11, secondary_packaging=12")
        
    except Exception as e:
        print(f"Error fixing phase order: {e}")

def reverse_tablet_2_phase_order(apps, schema_editor):
    """Reverse the phase order fix (both back to 11)"""
    ProductionPhase = apps.get_model('workflow', 'ProductionPhase')
    
    try:
        # Revert both to order 11 (the problematic state)
        phases = ProductionPhase.objects.filter(
            phase_name__in=['bulk_packing', 'secondary_packaging'],
            product_type__in=['tablet', 'tablet_2']
        )
        phases.update(phase_order=11)
        
        print(f"Reverted phase order: both bulk_packing and secondary_packaging back to 11")
        
    except Exception as e:
        print(f"Error reverting phase order: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            fix_tablet_2_phase_order,
            reverse_tablet_2_phase_order,
        ),
    ]
