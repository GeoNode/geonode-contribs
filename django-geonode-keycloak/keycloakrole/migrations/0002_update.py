from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('keycloakrole', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name="KeycloakRole",
            name="keycloak_id",
            field=models.CharField(max_length=36, unique=True),
        ),
        migrations.RenameField(
            model_name="KeycloakRole",
            old_name="keycloak_id",
            new_name="uid",
        ),
        migrations.AddField(
            model_name="KeycloakRole",
            name="description",
            field=models.TextField(null=True),
        ),
    ]
