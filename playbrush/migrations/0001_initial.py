# Generated by Django 3.2 on 2021-06-14 20:47

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Files',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('csv1', models.FileField(upload_to='data/')),
                ('csv2', models.FileField(upload_to='data/')),
                ('created', models.DateTimeField(auto_now_add=True, null=True)),
            ],
        ),
    ]