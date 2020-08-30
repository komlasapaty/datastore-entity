
""" Represents an entity value for a datastore entity's property """

class EntityValue:
    """
    This class serves as a way to mark your model
    attributes as a datastore entity property

    .. doctest::

        >>> from datastore_entity import DatastoreEntity, EntityValue
        >>> class User(DatastoreEntity):
                username = EntityValue(None)
                password = EntityValue(None)
    """

    def __init__(self, value=None):
        self.value = value