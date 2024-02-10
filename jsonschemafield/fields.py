from django.db import models
from django.core import checks, exceptions

from jsonschema import SchemaError
from jsonschema import exceptions as jsonschema_exceptions
from jsonschema import validate
from jsonschema.validators import validator_for


class JSONSchemaField(models.JSONField):
    """
    JSONField with a schema validation by using `python-jsonschema`.
    Cf: https://python-jsonschema.readthedocs.io/en/stable/validate/
    """

    def __init__(self, *args, **kwargs):
        self.schema = kwargs.pop("schema", None)
        super().__init__(*args, **kwargs)

    @property
    def _has_valid_schema(self):
        """Check that the given `schema` is a valid json schema."""
        if not isinstance(self.schema, dict):
            return False

        schema_cls = validator_for(self.schema)
        try:
            schema_cls.check_schema(self.schema)
        except SchemaError:
            return False
        return True

    def check(self, **kwargs):
        return [*super().check(**kwargs), *self._check_schema_attribute()]

    def _check_schema_attribute(self):
        """Ensure that the given schema is a valid json schema during Django's checks."""
        if self.schema is None:
            return [
                checks.Error(
                    "JSONSchemaFields must define a 'schema' attribute.", obj=self
                )
            ]
        elif not self._has_valid_schema:
            return [
                checks.Error("Given 'schema' is not a valid json schema.", obj=self)
            ]
        else:
            return []

    def validate(self, value, model_instance):
        """Validate the content of the json field."""
        super().validate(value, model_instance)
        schema_cls = validator_for(self.schema)
        try:
            validate(
                instance=value,
                schema=self.schema,
                format_checker=schema_cls.FORMAT_CHECKER,
            )
        except jsonschema_exceptions.ValidationError as e:
            raise exceptions.ValidationError(
                "Invalid json content: %(value)s",
                code="invalid_content",
                params={"value": e.message},
            )
