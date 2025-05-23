# Generated by Django 5.1.6 on 2025-05-07 01:28

from django.db import migrations
from django.contrib.auth.models import Group

def create_groups(apps, schema_editor):
    Group.objects.bulk_create([
        Group(name='teacher'),
        Group(name='student'),
        # Add more groups as needed
    ])

def delete_groups(apps, schema_editor):
    Group.objects.filter(name__in=['group1', 'group2']).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0009_answer_editing_question_editing_quiz_editing_and_more'),
    ]

    operations = [
        migrations.RunPython(create_groups, reverse_code=delete_groups),
    ]