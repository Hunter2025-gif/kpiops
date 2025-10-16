# Generated manually to remove unused fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fgs_management', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fgsinventory',
            name='quantity_produced',
        ),
        migrations.RemoveField(
            model_name='fgsinventory',
            name='unit_of_measure',
        ),
        migrations.RemoveField(
            model_name='fgsinventory',
            name='storage_date',
        ),
        migrations.RemoveField(
            model_name='fgsinventory',
            name='storage_location',
        ),
        migrations.RemoveField(
            model_name='fgsinventory',
            name='shelf_life_months',
        ),
        migrations.RemoveField(
            model_name='fgsinventory',
            name='expiry_date',
        ),
    ]
