from django.test import TestCase

from jsonschemafield.fields import JSONSchemaField
from django.core import checks, exceptions

from jsonschemafield.models import JSONSchemaFieldTestModel


class JSONSchemaFieldTestCase(TestCase):
    """
    Performs tests on the `JSONSchemaField` class.

    See the json schema used with `JSONSchemaFieldTestModel.json_field_with_schema` for more
    information regarding the following tests.
    """

    def test_check_schema_attribute_missing_schema(self):
        """Ensure that Django's checks will detect missing schema."""
        json_field = JSONSchemaField()
        self.assertListEqual(
            json_field._check_schema_attribute(),
            [
                checks.Error(
                    "JSONSchemaFields must define a 'schema' attribute.", obj=json_field
                )
            ],
        )

    def test_check_schema_attribute_invalid_schema(self):
        """Ensure that Django's checks will detect invalid schema given to the field."""
        json_field = JSONSchemaField(schema="not a dict")
        self.assertListEqual(
            json_field._check_schema_attribute(),
            [
                checks.Error(
                    "Given 'schema' is not a valid json schema.", obj=json_field
                )
            ],
        )

        json_field = JSONSchemaField(
            schema={"properties": {"string_property": "invalid type dict"}}
        )
        self.assertListEqual(
            json_field._check_schema_attribute(),
            [
                checks.Error(
                    "Given 'schema' is not a valid json schema.", obj=json_field
                )
            ],
        )

    def test_save(self):
        """Try to save a model with a `JSONSchemaField`."""
        instance = JSONSchemaFieldTestModel(
            json_field_with_schema={
                "string_property": "foo",
                "boolean_property": True,
                "email_property": "foo@bar.com",
            }
        )
        instance.save()

        self.assertIsInstance(instance.json_field_with_schema, dict)
        self.assertDictEqual(
            instance.json_field_with_schema,
            {
                "string_property": "foo",
                "boolean_property": True,
                "email_property": "foo@bar.com",
            },
        )

    def test_save_validation(self):
        """
        Ensure that a validation error is raised when trying to save a model with a json value
        which do not respect the json schema of the field.
        """
        # Invalid type: not a boolean property.
        instance = JSONSchemaFieldTestModel(
            json_field_with_schema={
                "string_property": "foo",
                "boolean_property": "not_bool_property",
            }
        )
        with self.assertRaisesRegex(
            exceptions.ValidationError, "'not_bool_property' is not of type 'boolean'"
        ):
            instance.save()

        # Invalid format: not a valid email address.
        instance = JSONSchemaFieldTestModel(
            json_field_with_schema={
                "string_property": "foo",
                "email_property": "not_a_valid_email_address",
            }
        )
        with self.assertRaisesRegex(
            exceptions.ValidationError, "'not_a_valid_email_address' is not a 'email'"
        ):
            instance.save()
