# Generated by Django 2.1.2 on 2018-10-21 15:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alias',
            name='oldpcr_id',
        ),
        migrations.RemoveField(
            model_name='alias',
            name='semester',
        ),
        migrations.RemoveField(
            model_name='course',
            name='credits',
        ),
        migrations.RemoveField(
            model_name='course',
            name='oldpcr_id',
        ),
        migrations.RemoveField(
            model_name='instructor',
            name='oldpcr_id',
        ),
        migrations.RemoveField(
            model_name='section',
            name='oldpcr_id',
        ),
        migrations.AlterField(
            model_name='review',
            name='instructor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='courses.Instructor'),
        ),
    ]
