from typing import Annotated, Any

from astropy.time import Time, TimeBase
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class _AstropyTimePydanticTypeAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls, _source_type: Any, _handler: GetCoreSchemaHandler
    ) -> CoreSchema:
        from_string = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(lambda s: Time(s)),
            ]
        )

        from_datetime = core_schema.chain_schema(
            [
                core_schema.datetime_schema(),
                core_schema.no_info_plain_validator_function(lambda d: Time(d)),
            ]
        )

        def serialize(v: Time):
            from astropydantic import TIME_OUTPUT_FORMAT, TIME_OUTPUT_SCALE

            fmt = TIME_OUTPUT_FORMAT
            try:
                v = getattr(v, TIME_OUTPUT_SCALE)
            except AttributeError:
                raise ValueError(f"Unsupported TIME_OUTPUT_SCALE: {TIME_OUTPUT_SCALE}")

            # handle special case of precision with isot
            if "iso" in fmt:
                fmt, _, precision = fmt.partition("_")
                precision = int(precision)
                v = Time(v, precision=precision, copy=False)

            try:
                return getattr(v, fmt)
            except AttributeError:
                raise ValueError(
                    f"Unsupported TIME_OUTPUT_FORMAT: {TIME_OUTPUT_FORMAT}"
                )

        return core_schema.json_or_python_schema(
            python_schema=core_schema.union_schema(
                [core_schema.is_instance_schema(TimeBase), from_string, from_datetime]
            ),
            json_schema=core_schema.union_schema([from_string, from_datetime]),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize,
            ),
        )


AstroPydanticTime = Annotated[Time, _AstropyTimePydanticTypeAnnotation]
