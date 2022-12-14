# Generated by Django 4.1.2 on 2022-12-02 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60)),
                ('description', models.CharField(max_length=200, null=True)),
                ('link', models.CharField(max_length=200)),
                ('color1', models.CharField(max_length=20)),
                ('color2', models.CharField(max_length=20)),
                ('type', models.CharField(choices=[('Video', 'Video'), ('File', 'File'), ('Tool', 'Tool')], max_length=50)),
                ('tag', models.CharField(max_length=300)),
            ],
        ),
    ]
