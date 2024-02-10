from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from .fields import JSONSchemaField

JSON_FIELD_TEST_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "string_property": {"type": "string"},
        "boolean_property": {"type": "boolean"},
        "email_property": {"type": "string", "format": "email"},
    },
    "required": ["string_property"],
}


class JSONSchemaFieldTestModel(models.Model):
    """Test model used to test the `JSONSchemaField` class."""

    json_field_with_schema = JSONSchemaField(
        default=dict, schema=JSON_FIELD_TEST_SCHEMA
    )

    class Meta:
        # This model is a concrete model only during tests.
        # It avoids to generate a migration file for this model.
        abstract = not settings.IS_TESTING

    def save(self, *args, **kwargs):
        super().full_clean()
        super().save(*args, **kwargs)


class UserInformation(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    information = JSONSchemaField(
        schema={
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "object",
            "properties": {
                "name": {"type": "string", "maxLength": 255},
                "email": {"type": "string", "format": "email"},
                "centers_of_interest": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "maxLength": 255,
                    },
                },
            },
            "required": ["name", "email"],
            "additionalProperties": False,
        },
    )

    def save(self, *args, **kwargs):
        super().full_clean()
        super().save(*args, **kwargs)
