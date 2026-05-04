from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surplus', '0002_surpluslisting_latitude_surpluslisting_longitude'),
    ]

    operations = [
        migrations.AddField(
            model_name='surpluslisting',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
        migrations.AddField(
            model_name='surpluslisting',
            name='unit',
            field=models.CharField(
                max_length=20,
                default='porsi',
                choices=[
                    ('porsi', 'Porsi'),
                    ('kg', 'Kg'),
                    ('gram', 'Gram'),
                    ('liter', 'Liter'),
                    ('pcs', 'Pcs'),
                    ('bungkus', 'Bungkus'),
                ]
            ),
        ),
        migrations.AddField(
            model_name='transaction',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
        ),
    ]