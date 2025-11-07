AstroPydantic
=============

An (**unofficial**) package providing pydantic typing support for astropy
unit types. Can be used to de(serialize) astropy quantities and units.

We provide three types:

- `AstroPydanticUnit`: an overlay for `astropy.units.UnitBase` (all unit types).
- `AstroPydanticQuantity`: an overlay for `astropy.units.Quantity`, including
  array types.
- `AstroPydanticTime`: an overlay for `astropy.time.Time`.

Installation
------------

The package can be installed from pypi:
```
pip install astropydantic
```

Example usage
-------------

### Units

```python
from astropydantic import AstroPydanticUnit
from pydantic import BaseModel

class MyModel(BaseModel):
  units: AstroPydanticUnit

my_model = MyModel(units="km")

print(my_model)
>>> units=Unit("km")
my_model.units.to("m")
>>> 1000.0
```

By default, strings are formatted according to the `vounit` specification. You can
change this to any supported configuration from astropy using the module-level
constant `UNIT_STRING_FORMAT`:

```python
import astropydantic
from astropydantic import AstroPydanticUnit
from pydantic import BaseModel

class MyModel(BaseModel):
  units: AstroPydanticUnit

my_model = MyModel(units="km / s")

print(my_model.model_dump_json())
>>> {"units":"km.s**-1"}

astropydantic.UNIT_STRING_FORMAT = "fits"
print(my_model.model_dump_json())
>>> {"units":"km s-1"}
```


### Quantities

Regular quantities are supported, and are converted from either strings or
dictionaries specified as `{"value": x, "unit": y}`:

```python
from astropydantic import AstroPydanticQuantity
from pydantic import BaseModel

class MyModel(BaseModel):
  a: AstroPydanticQuantity
  b: AstroPydanticQuantity 

my_model = MyModel(a="0.1 km", b={"value": [20.0, 30.0], "unit": "A"})

print(my_model)
>>> a=<Quantity 0.1 km> b=<Quantity [20., 30.] A>
```

You can enforce the type of the quantity by using the indexing syntax:

```python
from astropydantic import AstroPydanticQuantity
from pydantic import BaseModel
from astropy import units

class MyModel(BaseModel):
  a: AstroPydanticQuantity[units.m]

my_model = MyModel(a="0.1 km")

print(my_model)
>>> a=<Quantity 0.1 km> 

my_model = MyModel(a="10.0 g")
>>> Traceback (most recent call last):
>>>   File "<stdin>", line 1, in <module>
>>>     my_model = MyModel(a="10.0 g")
>>>   File "/Users/borrow-adm/Documents/Projects/astropydantic/.venv/lib/python3.13/site-packages/pydantic/main.py", line 253, in __init__
>>>     validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
>>> pydantic_core._pydantic_core.ValidationError: 1 validation error for MyModel
>>> a
>>>   Value error, 'g' (mass) and 'm' (length) are not convertible [type=value_error, input_value=<Quantity 10. g>, input_type=Quantity]
>>>     For further information visit https://errors.pydantic.dev/2.11/v/value_error
```

### Times

Times are handled similarly, with the output format (either `isot_X` where `X` is the precision,
or `datetime` for the native python datetime) determined by
`astropydantic.TIME_OUTPUT_FORMAT`:

```python
import astropydantic
import datetime
from pydantic import BaseModel
from astropydantic import AstroPydanticTime

class MyModel(BaseModel):
  a: AstroPydanticTime

model = MyModel(a=datetime.datetime.now())

print(model)
>>> a=<Time object: scale='utc' format='datetime' value=2025-08-26 12:24:00.143664>

>>> print(model.model_dump())
{'a': '2025-08-26T12:24:00.143664000'}
print(model.model_dump_json())
>>> {"a":"2025-08-26T12:24:00.143664000"}

astropydantic.TIME_OUTPUT_FORMAT = "datetime"
print(model.model_dump())
>>> {'a': datetime.datetime(2025, 8, 26, 12, 24, 0, 143664)}
print(model.model_dump_json())
>>> {"a":"2025-08-26T12:24:00.143664"}
```

The string format defaults to `isot_9`.

### Coordinates

Added in `0.0.3`, Coordinates are handled through the general `ICRS` or
`SkyCoord` interface. So far, only the `icrs` frame is supported.  You can
instantiate an `AstroPydanticICRS` either directly with an `ICRS` object, or a
`SkyCoord(frame="icrs")` object. However, after serialization, all values are
represented internally as `ICRS` objects. The individual `ra` and `dec` 
components of `ICRS` are internally treated as `AstroPydanticQuantity`
objects, with matching serialization rules.

```python
from astropy.coordinates import SkyCoord, ICRS
from astropy import units as u
from pydantic import BaseModel
from astropydantic import AstroPydanticICRS

class MyModel(BaseModel):
  a: AstroPydanticICRS

sky_coord = SkyCoord(ra=20.0, dec=10.0, unit="deg")
icrs = ICRS(ra=5.0 * u.deg, dec=-5.0 * u.deg)

model = MyModel(a=sky_coord)
print(model)
>>> a=<ICRS Coordinate: (ra, dec) in deg
    (20., 10.)>

model = MyModel(a=icrs)
print(model)
>>> a=<ICRS Coordinate: (ra, dec) in deg
    (5., -5.)>

print(model.model_dump())
>>> {'a': <ICRS Coordinate: (ra, dec) in deg
    (5., -5.)>}

print(model.model_dump_json())
>>> {"a":{"ra":{"value":5.0,"unit":"deg"},"dec":{"value":-5.0,"unit":"deg"}}}
```