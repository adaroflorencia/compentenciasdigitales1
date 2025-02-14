# Generated by Django 5.1.4 on 2024-12-18 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('form', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='topicresult',
            name='total_questions',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='topicresult',
            name='level',
            field=models.CharField(default='A1', max_length=10),
        ),
        migrations.AlterField(
            model_name='topicresult',
            name='score',
            field=models.FloatField(default=0),
        ),
    ]
