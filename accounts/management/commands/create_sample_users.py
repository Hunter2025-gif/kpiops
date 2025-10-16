from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser and sample users for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip if users already exist',
        )

    def handle(self, *args, **options):
        # Create superuser
        try:
            if not User.objects.filter(username='admin').exists():
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@kampala-pharma.com',
                    password='admin123',
                    first_name='System',
                    last_name='Administrator',
                    role='admin',
                    employee_id='ADM001',
                    department='IT'
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully created superuser: {admin_user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Superuser "admin" already exists')
                )
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )

        # Create sample users for each role
        sample_users = [
            # Administrative and Quality Roles
            {
                'username': 'qa_user',
                'email': 'qa@kampala-pharma.com',
                'password': 'qa123',
                'first_name': 'QA',
                'last_name': 'Officer',
                'role': 'qa',
                'employee_id': 'QA001',
                'department': 'Quality Assurance'
            },
            {
                'username': 'regulatory_user',
                'email': 'regulatory@kampala-pharma.com',
                'password': 'reg123',
                'first_name': 'Regulatory',
                'last_name': 'Officer',
                'role': 'regulatory',
                'employee_id': 'REG001',
                'department': 'Regulatory Affairs'
            },
            {
                'username': 'store_manager',
                'email': 'store@kampala-pharma.com',
                'password': 'store123',
                'first_name': 'Store',
                'last_name': 'Manager',
                'role': 'store_manager',
                'employee_id': 'STR001',
                'department': 'Store Management'
            },
            {
                'username': 'qc_user',
                'email': 'qc@kampala-pharma.com',
                'password': 'qc123',
                'first_name': 'QC',
                'last_name': 'Analyst',
                'role': 'qc',
                'employee_id': 'QC001',
                'department': 'Quality Control'
            },
            # Production Operators - Ointment Workflow
            {
                'username': 'mixing_operator',
                'email': 'mixing@kampala-pharma.com',
                'password': 'mix123',
                'first_name': 'Mixing',
                'last_name': 'Operator',
                'role': 'mixing_operator',
                'employee_id': 'MIX001',
                'department': 'Production'
            },
            {
                'username': 'tube_filling_operator',
                'email': 'tubefill@kampala-pharma.com',
                'password': 'tube123',
                'first_name': 'Tube Filling',
                'last_name': 'Operator',
                'role': 'tube_filling_operator',
                'employee_id': 'TUBE001',
                'department': 'Production'
            },
            # Production Operators - Tablet Workflow
            {
                'username': 'granulation_operator',
                'email': 'granulation@kampala-pharma.com',
                'password': 'gran123',
                'first_name': 'Granulation',
                'last_name': 'Operator',
                'role': 'granulation_operator',
                'employee_id': 'GRAN001',
                'department': 'Production'
            },
            {
                'username': 'blending_operator',
                'email': 'blending@kampala-pharma.com',
                'password': 'blend123',
                'first_name': 'Blending',
                'last_name': 'Operator',
                'role': 'blending_operator',
                'employee_id': 'BLEND001',
                'department': 'Production'
            },
            {
                'username': 'compression_operator',
                'email': 'compression@kampala-pharma.com',
                'password': 'comp123',
                'first_name': 'Compression',
                'last_name': 'Operator',
                'role': 'compression_operator',
                'employee_id': 'COMP001',
                'department': 'Production'
            },
            {
                'username': 'coating_operator',
                'email': 'coating@kampala-pharma.com',
                'password': 'coat123',
                'first_name': 'Coating',
                'last_name': 'Operator',
                'role': 'coating_operator',
                'employee_id': 'COAT001',
                'department': 'Production'
            },
            {
                'username': 'sorting_operator',
                'email': 'sorting@kampala-pharma.com',
                'password': 'sort123',
                'first_name': 'Sorting',
                'last_name': 'Operator',
                'role': 'sorting_operator',
                'employee_id': 'SORT001',
                'department': 'Production'
            },
            # Production Operators - Capsule Workflow
            {
                'username': 'drying_operator',
                'email': 'drying@kampala-pharma.com',
                'password': 'dry123',
                'first_name': 'Drying',
                'last_name': 'Operator',
                'role': 'drying_operator',
                'employee_id': 'DRY001',
                'department': 'Production'
            },
            {
                'username': 'filling_operator',
                'email': 'filling@kampala-pharma.com',
                'password': 'fill123',
                'first_name': 'Filling',
                'last_name': 'Operator',
                'role': 'filling_operator',
                'employee_id': 'FILL001',
                'department': 'Production'
            },
            # Single Packing Operator for all packing types (blister, bulk, secondary)
            {
                'username': 'packing_operator',
                'email': 'packing@kampala-pharma.com',
                'password': 'pack123',
                'first_name': 'Packing',
                'last_name': 'Operator',
                'role': 'packing_operator',
                'employee_id': 'PACK001',
                'department': 'Packaging'
            },
            # Additional Support Operators
            {
                'username': 'dispensing_operator',
                'email': 'dispensing@kampala-pharma.com',
                'password': 'disp123',
                'first_name': 'Dispensing',
                'last_name': 'Operator',
                'role': 'dispensing_operator',
                'employee_id': 'DISP001',
                'department': 'Store'
            },
            {
                'username': 'equipment_operator',
                'email': 'equipment@kampala-pharma.com',
                'password': 'equip123',
                'first_name': 'Equipment',
                'last_name': 'Operator',
                'role': 'equipment_operator',
                'employee_id': 'EQUIP001',
                'department': 'Maintenance'
            },
            {
                'username': 'cleaning_operator',
                'email': 'cleaning@kampala-pharma.com',
                'password': 'clean123',
                'first_name': 'Cleaning',
                'last_name': 'Operator',
                'role': 'cleaning_operator',
                'employee_id': 'CLEAN001',
                'department': 'Maintenance'
            }
        ]

        for user_data in sample_users:
            try:
                if not User.objects.filter(username=user_data['username']).exists():
                    user = User.objects.create_user(**user_data)
                    self.stdout.write(
                        self.style.SUCCESS(f'Successfully created user: {user.username} ({user.get_role_display()})')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'User "{user_data["username"]}" already exists')
                    )
            except IntegrityError as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating user {user_data["username"]}: {e}')
                )

        self.stdout.write(
            self.style.SUCCESS('\n=== LOGIN CREDENTIALS ===')
        )
        self.stdout.write('Admin: username=admin, password=admin123')
        self.stdout.write('\n--- Quality & Regulatory ---')
        self.stdout.write('QA: username=qa_user, password=qa123')
        self.stdout.write('Regulatory: username=regulatory_user, password=reg123')
        self.stdout.write('QC: username=qc_user, password=qc123')
        
        self.stdout.write('\n--- Store Management ---')
        self.stdout.write('Store Manager: username=store_manager, password=store123')
        self.stdout.write('Dispensing: username=dispensing_operator, password=disp123')
        
        self.stdout.write('\n--- Ointment Production ---')
        self.stdout.write('Mixing: username=mixing_operator, password=mix123')
        self.stdout.write('Tube Filling: username=tube_filling_operator, password=tube123')
        
        self.stdout.write('\n--- Tablet Production ---')
        self.stdout.write('Granulation: username=granulation_operator, password=gran123')
        self.stdout.write('Blending: username=blending_operator, password=blend123')
        self.stdout.write('Compression: username=compression_operator, password=comp123')
        self.stdout.write('Coating: username=coating_operator, password=coat123')
        self.stdout.write('Sorting: username=sorting_operator, password=sort123')
        
        self.stdout.write('\n--- Capsule Production ---')
        self.stdout.write('Drying: username=drying_operator, password=dry123')
        self.stdout.write('Filling: username=filling_operator, password=fill123')
        
        self.stdout.write('\n--- Packing (All Types: Blister, Bulk, Secondary) ---')
        self.stdout.write('Packing: username=packing_operator, password=pack123')
        
        self.stdout.write('\n--- Maintenance ---')
        self.stdout.write('Equipment: username=equipment_operator, password=equip123')
        self.stdout.write('Cleaning: username=cleaning_operator, password=clean123')
        
        self.stdout.write(
            self.style.SUCCESS('\nAdmin panel: http://127.0.0.1:8000/admin/')
        )
