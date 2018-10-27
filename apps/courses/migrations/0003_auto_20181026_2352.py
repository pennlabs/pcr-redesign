# Generated by Django 2.1.2 on 2018-10-26 23:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_auto_20181021_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alias',
            name='department',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='aliases', to='courses.Department'),
        ),
        migrations.AlterField(
            model_name='section',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sections', to='courses.Course'),
        ),
        migrations.AlterField(
            model_name='section',
            name='instructors',
            field=models.ManyToManyField(related_name='sections', to='courses.Instructor'),
        ),
    ]
