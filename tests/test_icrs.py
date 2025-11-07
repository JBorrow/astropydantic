"""
Tests for ICRS serialization
"""

import pytest
from astropy import units as u
from astropy.coordinates import ICRS, SkyCoord
from pydantic import BaseModel

from astropydantic.icrs import AstroPydanticICRS


def test_icrs_serialization():
    class TestModel(BaseModel):
        x: AstroPydanticICRS

    m = TestModel(x=ICRS(ra=20.0 * u.deg, dec=10.0 * u.deg))

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)

    reconstituted = TestModel.model_validate_json(json)

    assert reconstituted.x.ra == m.x.ra
    assert reconstituted.x.dec == m.x.dec


def test_skycoord_serialization():
    class TestModel(BaseModel):
        x: AstroPydanticICRS

    coordinate = SkyCoord(ra=20.0 * u.deg, dec=10.0 * u.deg, frame="icrs")

    m = TestModel(x=coordinate)

    serialized = m.model_dump()
    TestModel.model_validate(serialized)

    json = m.model_dump_json()
    TestModel.model_validate_json(json)

    reconstituted = TestModel.model_validate_json(json)

    assert reconstituted.x.ra == m.x.ra
    assert reconstituted.x.dec == m.x.dec


def test_skycoord_failure():
    class TestModel(BaseModel):
        x: AstroPydanticICRS

    coordinate = SkyCoord(ra=20.0 * u.deg, dec=10.0 * u.deg, frame="fk5")

    with pytest.raises(TypeError):
        TestModel(x=coordinate)
