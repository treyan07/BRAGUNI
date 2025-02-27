# Generated by Django 5.1.1 on 2024-09-23 18:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("panel", "0005_alter_section_unique_together_studentenrollment"),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentSection",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("enrollment_date", models.DateTimeField(auto_now_add=True)),
                (
                    "section",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="panel.section"
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="panel.student"
                    ),
                ),
            ],
            options={
                "unique_together": {("student", "section")},
            },
        ),
        migrations.DeleteModel(
            name="StudentEnrollment",
        ),
    ]
