
""" Represents an entity value for a datastore entity's property """

class DSEntityValue:
    """
    This class serves as a way to mark your model
    attributes as a datastore entity property

    .. doctest::

        >>> from datastore_entity import DatastoreEntity
        >>> from datastore_entity import DSEntityValue
        >>> class User(DatastoreEntity):
                username = DSEntityValue(None)
                password = DSEntityValue(None)
    """

    def __init__(self, value=None):
        self.value = value