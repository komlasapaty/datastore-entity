"""
Test cases for entity value module
"""

from datastore_entity import EntityValue


def test_none_value():
    """
    Check that when EntityValue is initialized without a
    value, it defaults to `None`
    """
    entity_value = EntityValue()
    assert entity_value.value is None

def test_value_passed():
    """
    Check that the value passed to EntityValue is what is returned
    """
    value = "foobar"
    entity_value = EntityValue(value)
    assert entity_value.value == value