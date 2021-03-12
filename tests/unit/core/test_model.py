from io import StringIO
from typing import Any

import pytest
from sqlalchemy.schema import MetaData, Table
from sqlalchemy.engine import create_engine

from blog_app.core.model import ModelMap, register_tables


@pytest.fixture
def metadata():
    return MetaData()


@pytest.fixture
def engine():
    def dump(sql, *args, **kwargs):
        print(f"{sql.compile(dialect=ngin.dialect)};", file=ngin.dump)

    ngin: Any = create_engine("mysql://", strategy="mock", executor=dump)
    ngin.dump = StringIO()

    return ngin


@pytest.fixture
def expected_table_names():
    return {"post", "comment", "reaction"}


def test_register_tables_returns_model_map(metadata, expected_table_names):
    model_map = register_tables(metadata)

    # check that it returns a dict of all the models
    assert isinstance(model_map, dict)
    assert model_map.keys() == expected_table_names
    assert all(isinstance(item, Table) for item in model_map.values())


def test_register_tables_adds_tables_to_metadata(
    metadata: MetaData, expected_table_names
):
    """Check that register_tables adds the expected tables to the passed metadata obj."""
    register_tables(metadata)
    assert {table.name for table in metadata.sorted_tables} == expected_table_names
