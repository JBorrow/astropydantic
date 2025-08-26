AstroPydantic
=============

An (**unofficial**) package providing pydantic typing support for astropy
unit types. Can be used to de(serialize) astropy quantities and units.

We provide two types:

- `AstroPydanticUnit`: an overlay for `astropy.units.UnitBase` (all unit types).
- `AstroPydanticQuantity`: an overlay for `astropy.units.Quantity`, including
  array types.

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