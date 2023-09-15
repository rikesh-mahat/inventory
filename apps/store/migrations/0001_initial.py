# Generated by Django 4.2.5 on 2023-09-15 05:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import utils.validations
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Warehouse',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modified_on', models.DateTimeField(auto_now=True)),
                ('zip_code', models.IntegerField(blank=True, null=True)),
                ('city', models.CharField(default='Lalitpur', max_length=50)),
                ('country', models.CharField(default='Nepal', max_length=50)),
                ('street', models.CharField(blank=True, max_length=50, null=True)),
                ('name', models.CharField(max_length=100)),
                ('phone', models.CharField(unique=True, validators=[utils.validations.validate_mobile_number])),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='%(app_label)s_%(class)s_modified_by', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
