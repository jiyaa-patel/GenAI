# Generated manually to fix UUID compatibility with admin log

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_managers_remove_user_last_login_at_and_more'),
        ('admin', '0001_initial'),
    ]

    operations = [
        # Clear existing admin log entries since they have invalid user references
        migrations.RunSQL(
            "DELETE FROM django_admin_log;",
            reverse_sql="-- No reverse operation needed"
        ),
        
        # Drop the existing foreign key constraint
        migrations.RunSQL(
            "ALTER TABLE django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_fkey;",
            reverse_sql="-- No reverse operation needed"
        ),
        
        # Drop the existing column
        migrations.RunSQL(
            "ALTER TABLE django_admin_log DROP COLUMN IF EXISTS user_id;",
            reverse_sql="-- No reverse operation needed"
        ),
        
        # Add the new UUID column
        migrations.RunSQL(
            "ALTER TABLE django_admin_log ADD COLUMN user_id UUID;",
            reverse_sql="ALTER TABLE django_admin_log DROP COLUMN IF EXISTS user_id;"
        ),
        
        # Add the foreign key constraint
        migrations.RunSQL(
            "ALTER TABLE django_admin_log ADD CONSTRAINT django_admin_log_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;",
            reverse_sql="ALTER TABLE django_admin_log DROP CONSTRAINT IF EXISTS django_admin_log_user_id_fkey;"
        ),
    ]
