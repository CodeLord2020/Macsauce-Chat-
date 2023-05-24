# Generated by Django 4.1.7 on 2023-05-23 14:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chatapp', '0007_alter_inbox_messengers'),
    ]

    operations = [
        migrations.CreateModel(
            name='InboxMessengers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inbox', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chatapp.inbox')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='inbox',
            name='messengers',
            field=models.ManyToManyField(related_name='messenger_inbox', through='chatapp.InboxMessengers', to=settings.AUTH_USER_MODEL),
        ),
    ]
