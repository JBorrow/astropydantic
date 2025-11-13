from typing import Any

from astropy.coordinates import ICRS, SkyCoord
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

from .quantity import AstroPydanticQuantity


class _AstropyICRSPydanticTypeAnnotation(type(ICRS)):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        quantity_schema = _handler.generate_schema(AstroPydanticQuantity)

        dict_schema = core_schema.chain_schema(
            [
                core_schema.typed_dict_schema(
                    {
                        "ra": core_schema.typed_dict_field(quantity_schema),
                        "dec": core_schema.typed_dict_field(quantity_schema),
                    }
                ),
                core_schema.no_info_plain_validator_function(
                    lambda x: ICRS(ra=x["ra"], dec=x["dec"])
                ),
            ]
        )

        def validate_skycoord(x: Any) -> ICRS:
            """Convert SkyCoord -> ICRS, or passthrough if already ICRS."""
            if isinstance(x, ICRS):
                return x
            if isinstance(x, SkyCoord):
                return ICRS(ra=x.ra, dec=x.dec)
            return x

        def json_serialize_value(c: ICRS):
            # Serialize to the native types whne going to JSON.
            from astropydantic import UNIT_STRING_FORMAT

            return {
                "ra": {
                    "value": c.ra.value,
                    "unit": c.ra.unit.to_string(format=UNIT_STRING_FORMAT),
                },
                "dec": {
                    "value": c.dec.value,
                    "unit": c.dec.unit.to_string(format=UNIT_STRING_FORMAT),
                },
            }

        str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
            ]
        )

        python_schema = core_schema.chain_schema(
            [
                core_schema.union_schema(
                    [
                        core_schema.is_instance_schema(ICRS),
                        core_schema.is_instance_schema(SkyCoord),
                        dict_schema,
                        str_schema,
                    ]
                ),
                core_schema.no_info_plain_validator_function(validate_skycoord),
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


class AstroPydanticICRS(ICRS, metaclass=_AstropyICRSPydanticTypeAnnotation):
    pass
