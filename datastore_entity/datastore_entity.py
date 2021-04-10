""" Base class for the entity model """

from google.cloud import datastore

from .entity_value import EntityValue


class DatastoreEntity():
    """
    A base class representing a Google Cloud
    Datastore entity.
    This gives you useful ORM features while
    interacting with the Datastore service.

    Google Cloud Datastore is a NoSQL key/value
    store that provides SQL-like
    functionalities(eg querying using a 'table' name)
    A datastore entity belonging to a 'table'(ie a kind)
    can have varying column number, varying
    datatypes per columns.

    This class also provides useful operations while
    protecting the user from common mistakes.

    It helps you to specify your properties in a way
    that avoids common mistakes(eg. misspelling property name)
    while still allowing you to take full advantage of
    the flexibility datastore provides.

    See more examples here:
    https://www.aloudinthecloud.com/orm-patterns-with-google-cloud-firestore-in-datastore-mode.html

    .. doctest::

        >>> from datastore_entity import DatastoreEntity
        >>> class User(DatastoreEntity):
                # properties/attributes go here

    :param namespace: (Optional) datastore namespace to connect to
    :type namespace: str

    :param service_account_json_path: (Optional) path to service
                                      account file
    :type service_account_json_path: str

    :param conn: whether to connect when initializing model.
                 Useful for testing or for deferring connection
    :type conn: boolean

    :raises: :class: `ValueError` if ``__kind__`` is not provided
    """

    #: Required. Name of entity's kind.
    __kind__ = False

    #: Optional. A list of properties to exclude from datastore indexes.
    __exclude_from_index__ = []

    def __init__(self, **kwargs):
        namespace = kwargs.get('namespace', None)
        service_account_json_path = kwargs.get(
            'service_account_json_path', None)
        conn = kwargs.get('conn', True)
        
        if conn:
            if namespace and service_account_json_path:
                self.ds_client = datastore.Client(
                    namespace=namespace).from_service_account_json(
                        service_account_json_path)
            elif namespace:
                self.ds_client = datastore.Client(namespace=namespace)
            elif service_account_json_path:
                self.ds_client = datastore.Client().from_service_account_json(
                    service_account_json_path)
            else:
                self.ds_client = datastore.Client()
        else:
            self.ds_client = None

        self.key = None

        # lookup for entity properties
        # self.__datastore_properties_lookup__ = []

        # prepare the lookup list
        self._init_lookup_list()

        if not self.__kind__:
            raise ValueError(
                "You must specify the entity 'kind' using __kind__"
                )

    def connect(self, namespace=None, service_account_json_path=None):
        """
        Connect to datastore service.
        Useful when model is initialized without connection or you want to
        connect to a different namespace or connect using a different
        credential

        :param namespace: (Optional) datastore namespace to connect to
        :type namespace: str

        :param service_account_json_path: (Optional) path to service
                                        account file
        :type service_account_json_path: str

        :return: boolean

        """

        if namespace and service_account_json_path:
            self.ds_client = datastore.Client(
                namespace=namespace).from_service_account_json(
                    service_account_json_path)
        elif namespace:
            self.ds_client = datastore.Client(namespace=namespace)
        elif service_account_json_path:
            self.ds_client = datastore.Client().from_service_account_json(
                service_account_json_path)
        else:
            self.ds_client = datastore.Client()

        return True

    def _init_lookup_list(self, entity=None):
        """
        Retrieves object attributes that are used for

        datastore properties and populates the lookup list
        """

        # we first reset the lookup list
        self.__datastore_properties_lookup__ = []

        if entity:  # when creating object with entity result
            for k, v in entity.items():
                self.__datastore_properties_lookup__.append(k)
        else:
            attrs = dir(self)
            for attr in attrs:
                value = getattr(self, attr)
                if (isinstance(value, EntityValue) and
                    attr not in self.__datastore_properties_lookup__):
                    self.__datastore_properties_lookup__.append(attr)

    def _convert_to_dict(self):
        """
        Prepares the dictionary object with the fields for the entity

        returns a dictionary
        """

        self._init_lookup_list()
        
        d = {}
        for attr_name in self.__datastore_properties_lookup__:
            attr_value = getattr(self, attr_name)
            if isinstance(attr_value, EntityValue):
                d[attr_name] = attr_value.value
            else:
                # when obj is dynamically populated(by say, WTForms),
                # the instance will not be an EntityValue type
                d[attr_name] = attr_value

        return d

    def save(self, id=None, parent_or_ancestor=None,
             extra_props=None, excludes=None):
        """
        Performs an 'upsert' operation on datastore if 'id' is provided.

        Performs a new insert when 'id' is None

        :param id: the entity identifier. part of an entity's key
        :type id: int or str

        :param parent_or_ancestor: datastore key for entity's
                                   parent or ancestor
        :type parent_or_ancestor: datastore key

        :param extra_props: an optional additional properties to add to
                           entity not defined in model class
        :type extra_props: dict

        :param exclude: a list of property names defined in the model
                        class to exclude when saving an entity
        :type excludes: list

        :return: boolean

        """

        data = self._convert_to_dict()  # get the entity values as a dictionary

        # if the object has a key(ie called via .get_obj(), we will use that)
        if self.key:
            key = self.key
        elif id and parent_or_ancestor:
            key = self.ds_client.key(
                self.__kind__, id,
                parent=parent_or_ancestor)
        elif id:
            key = self.ds_client.key(self.__kind__, id)
        else:
            key = self.ds_client.key(self.__kind__)

        entity = datastore.Entity(
            key,
            exclude_from_indexes=self.__exclude_from_index__)

        # Add any additional properties not defined in model
        if extra_props:
            for k, v in extra_props.items():
                if k not in self.__datastore_properties_lookup__:
                    self.__datastore_properties_lookup__.append(k)
                data[k] = v

        # Exclude selected properties defined in model
        if excludes:
            for prop in excludes:
                # remove an attr if it also in lookup table
                if prop in self.__datastore_properties_lookup__:
                    self.__datastore_properties_lookup__.pop(
                        self.__datastore_properties_lookup__.index(prop))

                data.pop(prop, '')

        entity.update(data)

        self.ds_client.put(entity)

        return True

    def allocate_ids(self, incomplete_key, num_ids):
        """
        Calls Datastore's allocate_id() to allocate a list of
        datastore IDs that is guaranteed to be unique.

        :param incomplete_key: A partial datastore key as base for
                               allocated IDs
        :type incomplete_key: :class: `google.cloud.datastore.key.Key`

        :param num_ids: The number of IDs to allocate
        :type num_ids: int

        :returns: the complete key
        :rtype: list of :class:`google.cloud.datastore.key.Key`
        """
        return self.ds_client.allocate_ids(incomplete_key, num_ids)

    def get_client(self):
        """
        Return the datastore connection client

        :return: datastore connection client
        """

        return self.ds_client

    def find_by_key(self, key):
        """
        Performs a search for an entity using it's key

        `Note:` This returns the entity as-is, as
        opposed to returning it as a model instance

        To retrieve the entity as a model instance
        use ``get_obj_with_key() method``

        :param key: The datastore key
        :type key: :class: google.cloud.datastore.key.Key

        :return: The datastore entity
        :rtype: :class: `google.cloud.datastore.entity.Entity`
        """
        entity = self.ds_client.get(key)

        return entity

    def find_by_value(self, prop, val, comparator='=', limit=500):
        """
        Returns a list of entities meeting query requirements

        `Note:` This returns the entity as-is, as
        opposed to returning it as a model instance

        To retrieve the entity as a model instance
        use ``get_objects() method`` which also supports pagination

        :param prop: the entity property name
        :type prop: str

        :param val: the entity propery value
        :type val: any

        :param comparator: the query operator(=,=< etc)
        :type comparator: str

        :param limit: the number of entities to fetch
        :type limit: int

        :returns: one or more entities
        :rtype: list
        """
        query = self.ds_client.query(kind=self.__kind__)
        query.add_filter(prop, comparator, val)

        entities = list(query.fetch(limit=limit))

        return entities

    def find_via_parent_or_ancestor(self, parent_or_ancestor, limit=500):
        """
        Fetches entities using ancestor key

        :param parent_or_ancestor: datastore ancestor key
        :type parent_or_ancestor: :class: `google.cloud.datastore.key.Key`

        :param limit: number of entities to fetch. max of 500
        :type limit: int

        :return: one or more entities
        :rtype: list
        """

        query = self.ds_client.query(
            kind=self.__kind__,
            ancestor=parent_or_ancestor)

        query.add_filter('active', '=', True)

        entities = list(query.fetch(limit=limit))

        return entities

    def get_obj(self, prop, value):
        """
        Fetches a single entity and populates the class attributes with
        the matching entity properties and values

        returns object of the class with the entity KEY
        You can call this directly, or have your model wrap a method around
        this method passing in only the value(eg. obj.get(username))

        Note that this is called only once

        :param prop: the name of entity property to used for the query

        :type prop: str

        :param value: the value for the query
        :type value: int

        :return: a class object representing the entity
        """
        query = self.ds_client.query(kind=self.__kind__)
        query.add_filter(prop, '=', value)

        # reset the lookup list
        # self.__datastore_properties_lookup__ = []

        entities = list(query.fetch(limit=1))
        if entities:
            entity = entities[0]

            # generate and populate the class attributes with properties
            # and values of the fetched entity
            for k, v in entity.items():
                # don't populate the class attributes. they are just
                # blueprints for instantiation
                setattr(self, k, v)

            # prepare the lookup list using the entity property names retrieved
            self._init_lookup_list(entity)
            # we set the entity's key
            self.key = entity.key

            return self
        else:
            return None

    def get_obj_with_key(self, key):
        """
        Similar to get_obj(), but fetches entity using it's key.

        Fetching an entity using a key is strongly consistent so object
        is immediately available after saving it to datastore

        Retrieves an entity and populates the class attributes with
        the matching entity properties and values

        :param key: the datastore key
        :type key: datastore key

        :return: an object representing the entity
        :rtype: :class: `datastore_entity.datastore_entity.DatastoreEntity`
        """

        entity = self.ds_client.get(key)

        # reset the lookup list
        # self.__datastore_properties_lookup__ = []

        if entity:
            # get all properties. note that some properties may not be
            # defined in the class(ie added via extra_prop)
            for k, v in entity.items():
                setattr(self, k, v)

            # prepare the lookup list
            self._init_lookup_list(entity)

            # before we return the object, we set it's
            # key(to be used in updates)
            self.key = key

            return self
        else:
            return None

    def delete(self):
        """
        Deletes an entity

        :return: boolean

        """

        self.ds_client.delete(self.key)

        return True

    def generate_key(self, path):
        """
        :param path: a list with key path in the format ['kind','id',...]
        :type path: list

        :return: the generated datastore key
        :rtype: :class: google.cloud.datastore.key.Key
        """

        key = self.ds_client.key(*path)

        return key

    def get_objects(self, prop, value, limit=500, paginate=False, cursor=None):
        """
        Fetches a given number of entities and populates the class attributes
        with the matching entity properties and values

        :param prop: the name of the entity property
        :type prop: str

        :param value: the name of the property value
        :type value: any. allowed datastore types

        :param limit: the maximum number of entities to return.
                      Datastore supports a maximum of 500
        :type limit: int

        :paginate: whether to return a cursor to be used for pagination
        :type paginate: boolean

        :param cursor: the 'next' cursor to be used to fetch next set
                       of entities
        :type cursor: str. representing a datastore cursor

        :return: a two-element tuple. first element is a list
                        of entity objects and the second is the cursor
                        for pagination or None
        :rtype: tuple
        """
        next_cursor = None

        query = self.ds_client.query(kind=self.__kind__)
        query.add_filter(prop, '=', value)

        query_res = query.fetch(start_cursor=cursor, limit=limit)

        if paginate:
            query_res = query.fetch(start_cursor=cursor, limit=limit)
            current_page = next(query_res.pages)
            entities = list(current_page)
            next_cursor = query_res.next_page_token.decode('utf-8')
        else:
            entities = list(query.fetch(start_cursor=cursor, limit=limit))

        if entities:
            objs = []
            for entity in entities:

                # get all properties. note that properties may not be
                # defined in the class
                for k, v in entity.items():
                    setattr(self, k, v)

                self.key = entity.key

                objs.append(self)
            return (objs, next_cursor)
        else:
            return None

    def __str__(self):
        return f'<Entity Kind: {self.__kind__}>'

    def __repr__(self):
        return (
            f"<Entity Kind: '{self.__kind__}' ==> "
            f"{[attr for attr in self.__datastore_properties_lookup__]}>"
                )
