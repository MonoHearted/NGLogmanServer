# Generated by Django 2.1.5 on 2019-01-15 19:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nglogman', '0003_auto_20190115_0001'),
    ]

    operations = [
        migrations.DeleteModel(
            name='LGNode',
        ),
        migrations.RemoveField(
            model_name='task',
            name='owner',
        ),
        migrations.DeleteModel(
            name='Task',
        ),
    ]
