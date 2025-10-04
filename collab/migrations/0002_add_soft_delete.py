# Generated migration for soft delete functionality

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('collab', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Soft delete flag'),
        ),
        migrations.AddField(
            model_name='page',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='When this object was soft deleted', null=True),
        ),
        migrations.AddField(
            model_name='page',
            name='deleted_by',
            field=models.ForeignKey(blank=True, help_text='User who soft deleted this object', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='page_deleted_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='character',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Soft delete flag'),
        ),
        migrations.AddField(
            model_name='character',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='When this object was soft deleted', null=True),
        ),
        migrations.AddField(
            model_name='character',
            name='deleted_by',
            field=models.ForeignKey(blank=True, help_text='User who soft deleted this object', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='character_deleted_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='story',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Soft delete flag'),
        ),
        migrations.AddField(
            model_name='story',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='When this object was soft deleted', null=True),
        ),
        migrations.AddField(
            model_name='story',
            name='deleted_by',
            field=models.ForeignKey(blank=True, help_text='User who soft deleted this object', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='story_deleted_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='essay',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Soft delete flag'),
        ),
        migrations.AddField(
            model_name='essay',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='When this object was soft deleted', null=True),
        ),
        migrations.AddField(
            model_name='essay',
            name='deleted_by',
            field=models.ForeignKey(blank=True, help_text='User who soft deleted this object', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='essay_deleted_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='image',
            name='is_deleted',
            field=models.BooleanField(default=False, help_text='Soft delete flag'),
        ),
        migrations.AddField(
            model_name='image',
            name='deleted_at',
            field=models.DateTimeField(blank=True, help_text='When this object was soft deleted', null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='deleted_by',
            field=models.ForeignKey(blank=True, help_text='User who soft deleted this object', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='image_deleted_set', to=settings.AUTH_USER_MODEL),
        ),
    ]