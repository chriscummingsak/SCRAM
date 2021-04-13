# Generated by Django 3.1.7 on 2021-04-13 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('route_manager', '0005_entry'),
    ]

    operations = [
        migrations.CreateModel(
            name='History',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('who', models.CharField(default='Unknown', max_length=30, verbose_name='Username')),
                ('why', models.CharField(max_length=200, verbose_name='Comment for the action')),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('entry', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='route_manager.entry')),
            ],
        ),
    ]
