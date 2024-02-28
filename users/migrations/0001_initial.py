# Generated by Django 5.0.2 on 2024-02-27 11:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='certificate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('owner_id', models.IntegerField(default=-1)),
                ('doc_id', models.IntegerField(default=-1)),
                ('doc_desc', models.CharField(default='Untitled Certificate', max_length=150)),
                ('semester', models.IntegerField(default=-1)),
                ('year', models.IntegerField(default=1990)),
                ('hardcopy', models.BooleanField(default=False)),
                ('doc_loc', models.CharField(default='/', max_length=150)),
                ('verified', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='certificate_type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(default='Untitled Category', max_length=50)),
                ('identifier', models.IntegerField(default=-1)),
                ('title', models.CharField(default='Untitled Certificate', max_length=50)),
                ('grade', models.CharField(default='F', max_length=50)),
                ('score', models.IntegerField(default=0)),
                ('year_max', models.IntegerField(default=0)),
            ],
        ),
    ]
