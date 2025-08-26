from typing import Annotated, Any

from astropy.units import Quantity, Unit
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class _AstropyQuantityPydanticTypeAnnotation(type):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        dict_schema = core_schema.chain_schema(
            [
                core_schema.typed_dict_schema(
                    {
                        "value": core_schema.typed_dict_field(
                            core_schema.union_schema(
                                [
                                    core_schema.float_schema(),
                                    core_schema.list_schema(),
                                ]
                            )
                        ),
                        "unit": core_schema.typed_dict_field(core_schema.str_schema()),
                    }
                ),
                core_schema.no_info_plain_validator_function(
                    lambda d: Quantity(d["value"], unit=d["unit"])
                ),
            ]
        )

        def validate_from_string(value: str):
            return Quantity(value)

        def json_serialize_value(q: Quantity):
            # Serialize to the native types when going to JSON, numpy
            # arrays are not supported.
            # Must import every time in case someone has changed it!
            from astropydantic import UNIT_STRING_FORMAT

            return {
                "value": q.value.tolist(),
                "unit": q.unit.to_string(format=UNIT_STRING_FORMAT),
            }

        str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_string),
            ]
        )

        python_schema = core_schema.union_schema(
            [
                core_schema.is_instance_schema(Quantity),
                dict_schema,
                str_schema,
            ]
        )
        json_schema = core_schema.union_schema([dict_schema, str_schema])

        return core_schema.json_or_python_schema(
            json_schema=json_schema,
            python_schema=python_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                json_serialize_value, when_used="json-unless-none"
            ),
        )

    def __getitem__(cls, unit: Unit):
        """Implement support for AstroPydanticQuantity[<unit>]."""

        class _AstropyQuantityPydanticTypeAnnotationWithUnit:
            @classmethod
            def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any):
                base = (
                    _AstropyQuantityPydanticTypeAnnotation.__get_pydantic_core_schema__(
                        _source_type, _handler
                    )
                )
                with_unit = core_schema.chain_schema(
                    [
                        base,
                        core_schema.no_info_plain_validator_function(
                            lambda q: q.to(unit)
                        ),
                    ]
                )
                with_unit["serialization"] = base["serialization"]
                return with_unit

        return Annotated[Quantity, _AstropyQuantityPydanticTypeAnnotationWithUnit]


class AstroPydanticQuantity(Quantity, metaclass=_AstropyQuantityPydanticTypeAnnotation):
    pass
