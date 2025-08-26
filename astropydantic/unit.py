from typing import Any

from astropy.units import Unit, UnitBase
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class _AstropyUnitPydanticTypeAnnotation(type):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        def validate_from_string(value: str) -> Unit:
            return Unit(s=value)

        from_string_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_string),
            ]
        )

        def serialize_to_string(value: Unit) -> str:
            # Must import every time in case someone has changed it!
            from astropydantic import UNIT_STRING_FORMAT

            return value.to_string(format=UNIT_STRING_FORMAT)

        return core_schema.json_or_python_schema(
            json_schema=from_string_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(UnitBase),
                    from_string_schema,
                ]
            ),
            # If we're just serializing to a dict, keep it as a Unit.
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_to_string, when_used="json-unless-none"
            ),
        )


class AstroPydanticUnit(UnitBase, metaclass=_AstropyUnitPydanticTypeAnnotation):
    pass
