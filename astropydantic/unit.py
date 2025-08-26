from typing import Annotated, Any
from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler, TypeAdapter
from pydantic_core import core_schema
from astropy.units import Unit, UnitBase
from pydantic.json_schema import JsonSchemaValue

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
                core_schema.no_info_plain_validator_function(validate_from_string)
            ]
        ) 

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
                lambda instance: str(instance), when_used="json-unless-none"
            ),
        )
    

class AstroPydanticUnit(UnitBase, metaclass=_AstropyUnitPydanticTypeAnnotation):
    pass