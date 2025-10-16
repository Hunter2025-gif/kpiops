#!/usr/bin/env python
"""
Script to create sample QC checkpoints for completed QC phases.
This will populate the PhaseCheckpoint table with realistic test data.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kampala_pharma.settings')
django.setup()

from workflow.models import BatchPhaseExecution, PhaseCheckpoint
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

def get_qc_test_templates():
    """Define typical QC tests for different phase types"""
    return {
        'post_mixing_qc': [
            {'name': 'Visual Inspection', 'expected': 'Uniform mixture, no lumps', 'specs': ['Pass', 'Fail']},
            {'name': 'Moisture Content (%)', 'expected': '< 3.0%', 'specs': ['1.5', '2.1', '2.8', '1.9', '2.3']},
            {'name': 'Particle Size (μm)', 'expected': '150-300 μm', 'specs': ['180', '220', '265', '195', '240']},
            {'name': 'pH Level', 'expected': '6.5-7.5', 'specs': ['6.8', '7.1', '7.0', '6.9', '7.2']},
        ],
        'post_blending_qc': [
            {'name': 'Blend Uniformity', 'expected': 'RSD < 5%', 'specs': ['2.1%', '3.4%', '2.8%', '4.2%', '1.9%']},
            {'name': 'Active Ingredient Content (mg)', 'expected': '95-105% of label claim', 'specs': ['98.5', '101.2', '99.8', '102.1', '97.3']},
            {'name': 'Bulk Density (g/mL)', 'expected': '0.45-0.65 g/mL', 'specs': ['0.52', '0.58', '0.49', '0.61', '0.55']},
            {'name': 'Flow Rate', 'expected': 'Good flow', 'specs': ['Pass', 'Pass', 'Pass', 'Pass', 'Pass']},
        ],
        'post_compression_qc': [
            {'name': 'Tablet Weight (mg)', 'expected': '±5% of target', 'specs': ['248', '252', '251', '249', '253']},
            {'name': 'Hardness (N)', 'expected': '60-120 N', 'specs': ['85', '92', '78', '105', '88']},
            {'name': 'Friability (%)', 'expected': '< 1.0%', 'specs': ['0.3', '0.5', '0.4', '0.7', '0.2']},
            {'name': 'Disintegration Time (min)', 'expected': '< 15 min', 'specs': ['8.5', '12.3', '9.1', '11.7', '10.2']},
            {'name': 'Thickness (mm)', 'expected': '3.8-4.2 mm', 'specs': ['3.9', '4.0', '4.1', '3.8', '4.0']},
        ],
        'quality_control': [
            {'name': 'Microbiological Test', 'expected': 'Total count < 1000 CFU/g', 'specs': ['<100', '250', '150', '80', '320']},
            {'name': 'Heavy Metals (ppm)', 'expected': '< 10 ppm', 'specs': ['2.1', '3.8', '1.5', '4.2', '2.9']},
            {'name': 'Dissolution Test (%)', 'expected': '> 80% in 30 min', 'specs': ['87%', '92%', '84%', '89%', '91%']},
            {'name': 'Content Uniformity', 'expected': 'AV < 15', 'specs': ['8.2', '12.1', '9.5', '11.3', '7.8']},
        ]
    }

def create_checkpoints_for_phase(phase_execution, test_templates):
    """Create checkpoint records for a specific phase execution"""
    qc_users = User.objects.filter(role='qc')
    if not qc_users.exists():
        print("No QC users found. Creating sample QC user...")
        qc_user = User.objects.create_user(
            username='qc_analyst1',
            email='qc@kampala-pharma.com',
            first_name='QC',
            last_name='Analyst',
            role='qc'
        )
    else:
        qc_user = qc_users.first()
    
    created_checkpoints = []
    
    for test in test_templates:
        # Determine if test passes or fails (90% pass rate)
        is_passing = random.random() < 0.9
        actual_value = random.choice(test['specs'])
        
        # For tests expecting "Pass/Fail", adjust based on is_passing
        if test['expected'] in ['Pass', 'Good flow', 'Uniform mixture, no lumps']:
            actual_value = 'Pass' if is_passing else 'Fail'
        
        checkpoint = PhaseCheckpoint.objects.create(
            phase_execution=phase_execution,
            checkpoint_name=test['name'],
            expected_value=test['expected'],
            actual_value=actual_value,
            is_within_spec=is_passing,
            checked_by=qc_user,
            checked_date=phase_execution.completed_date or timezone.now(),
            comments=f"Test performed according to SOP. {'Within specification.' if is_passing else 'Requires investigation.'}"
        )
        created_checkpoints.append(checkpoint)
    
    return created_checkpoints

def main():
    print("Creating QC checkpoints for completed QC phases...")
    
    # Get all completed QC phases
    qc_phases = BatchPhaseExecution.objects.filter(
        phase__phase_name__icontains='qc',
        status='completed'
    ).select_related('bmr', 'phase')
    
    print(f"Found {qc_phases.count()} completed QC phases")
    
    test_templates = get_qc_test_templates()
    total_checkpoints = 0
    
    for phase in qc_phases:
        # Check if checkpoints already exist for this phase
        existing_checkpoints = PhaseCheckpoint.objects.filter(phase_execution=phase).count()
        if existing_checkpoints > 0:
            print(f"Skipping {phase.bmr.batch_number} - {phase.phase.phase_name} (already has {existing_checkpoints} checkpoints)")
            continue
        
        # Determine which test template to use based on phase name
        template_key = None
        phase_name = phase.phase.phase_name.lower()
        
        if 'post_mixing_qc' in phase_name:
            template_key = 'post_mixing_qc'
        elif 'post_blending_qc' in phase_name:
            template_key = 'post_blending_qc'
        elif 'post_compression_qc' in phase_name:
            template_key = 'post_compression_qc'
        elif 'quality_control' in phase_name:
            template_key = 'quality_control'
        else:
            # Default to general quality control tests
            template_key = 'quality_control'
        
        if template_key and template_key in test_templates:
            print(f"Creating checkpoints for {phase.bmr.batch_number} - {phase.phase.phase_name}")
            checkpoints = create_checkpoints_for_phase(phase, test_templates[template_key])
            total_checkpoints += len(checkpoints)
            print(f"  Created {len(checkpoints)} checkpoints")
        else:
            print(f"No template found for phase: {phase.phase.phase_name}")
    
    print(f"\nCompleted! Created {total_checkpoints} total QC checkpoints.")
    
    # Verify the results
    total_checkpoints_db = PhaseCheckpoint.objects.count()
    passed_checkpoints = PhaseCheckpoint.objects.filter(is_within_spec=True).count()
    failed_checkpoints = PhaseCheckpoint.objects.filter(is_within_spec=False).count()
    
    print(f"\nDatabase Summary:")
    print(f"Total checkpoints: {total_checkpoints_db}")
    print(f"Passed checkpoints: {passed_checkpoints}")
    print(f"Failed checkpoints: {failed_checkpoints}")
    print(f"Pass rate: {(passed_checkpoints / total_checkpoints_db * 100):.1f}%" if total_checkpoints_db > 0 else "0%")

if __name__ == '__main__':
    main()