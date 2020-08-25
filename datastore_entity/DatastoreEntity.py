from google.cloud import datastore

class DSEntityValue:
    
    def __init__(self, value=None):
        self.value = value

class DatastoreEntity():
    """
    A base class representing a Google Cloud Datastore entity.
    This gives you useful ORM features while interacting with the Datastore service.
    
    It also provides useful operations while protecting the user from common mistakes.

    Google Cloud Datastore is a key/value store that provides SQL-like functionalities(eg querying using a 'table' name)
    A datastore entity belonging to a 'table'(a kind) can have varying column number, varying datatypes per columns.

    This base class helps you to specify your properties to avoid common mistakes while still allowing you to take full
    advantage of the flexibility datastore provides.

    """

    #A list of properties to exclude from datastore indexes
    __exclude_from_index__ = []


    def __init__(self,namespace=None,service_account_json_path=None):
        if namespace and service_account_json_path:
            self.ds_client = datastore.Client(namespace=namespace).from_service_account_json(service_account_json_path)
        elif namespace:
            self.ds_client = datastore.Client(namespace=namespace)
        elif service_account_json_path:
            self.ds_client = datastore.Client().from_service_account_json(service_account_json_path)
        else:
            self.ds_client = datastore.Client()
        
        self.key = None

        #lookup for entity properties
        self.__datastore_properties_lookup__ = []

        #prepare the lookup table
        self._init_lookup()


    def _init_lookup(self,entity=None):
        #once we initialize, we prepare the lookup list
        if entity: #when creating object with entity result
            for k,v in entity.items():
                self.__datastore_properties_lookup__.append(k)
        else:
            attrs = dir(self.__class__)
            count = 0
            for attr in attrs:
                count += 1
                value = getattr(self, attr)
                if isinstance(value, DSEntityValue):
                    self.__datastore_properties_lookup__.append(attr)


    def _convert_to_dict(self):
        """
        Prepares the dictionary object with the fields for the entity

        returns a dictionary
        """
        
        d = {}
        for attr in self.__datastore_properties_lookup__:
            value = getattr(self, attr)
            if isinstance(value, DSEntityValue):
                d[attr] = value.value
            else:
                d[attr] = value #when obj is populated by say, WTForms, the instance will not be a DSEntityValue type

        return d
    
    def get_props(self):
        return self.__datastore_properties_lookup__

    def save(self,id=None,parent_or_ancestor=None,extra_props=None,excludes=None):
        """
        Performs an 'upsert' operation on datastore if 'id' is provided.

        Performs a new insert when 'id' is None

        :param id: the enfity identifier. part of an entity's key

        :type id: int or string

        :param parent_or_ancestor: datastore key for entity's parent or ancestor

        :type parent_or_ancestor: datastore key

        :param extra_data: an optional additional properties to add to entity not defined in model class

        :type extra_data: dict

        :param exclude: a list of property names defined in the model class when saving an entity

        :type excludes: list
        """
        data = self._convert_to_dict() #get the entity values as a dictionary

        #if the object has a key(ie called via .get_obj(), we will use it)
        if self.key: 
            key = self.key
        elif id and parent_or_ancestor:
            key = self.ds_client.key(self.__kind__,id,parent=parent_or_ancestor)
        elif id:
            key = self.ds_client.key(self.__kind__,id)
        else:
            key = self.ds_client.key(self.__kind__)

        entity = datastore.Entity(key, exclude_from_indexes=self.__exclude_from_index__)

        #Add any additional properties not defined in model
        if extra_props:
            for k,v in extra_props.items(): #add the new attr to the lookup table
                if k not in self.__datastore_properties_lookup__:
                    self.__datastore_properties_lookup__.append(k)
                data[k] = v
        
        #Exclude selected properties defined in model
        if excludes:
            for prop in excludes:
                if prop in self.__datastore_properties_lookup__: #remove an attr if it also in lookup table
                    self.__datastore_properties_lookup__.pop(self.__datastore_properties_lookup__.index(prop))
                data.pop(prop,'')

        entity.update(data)

        self.ds_client.put(entity)

        return True
    

    def allocate_ids(self,incomplete_key,num_ids):
        """
        Calls Datastore's allocate_id() to allocate a list of datastore IDs that is guaranteed to be unique.

        :returns: list of datastore keys
        """

        return self.ds_client.allocate_ids(incomplete_key, num_ids)
    
    def get_client(self):
        """
        Return the datastore connection client
        """

        return self.ds_client

    def find_by_key(self, key):
        """
        Performs a search for an entity using a it's key(derived from the entity ID)
        Returns a single entity or None
        """
        #key = self.ds_client.key(self.__kind__,id)
        entity = self.ds_client.get(key)

        return entity
    
    def find_by_value(self, prop, val, comparator='=', limit=500):
        """
        Returns a list of entities meeting query requirements
        """
        query = self.ds_client.query(kind=self.__kind__)
        query.add_filter(prop,comparator,val)

        entities =  list(query.fetch(limit=limit))

        return entities
    
    def find_via_parent_or_ancestor(self,parent_or_ancestor,limit=500):
        """
        Fetches entities using ancestor key

        :param ancestor: datastore ancestor key
        :type ancestor: datastore key
        :param limit: number of entities to fetch. max of 500
        :param limit: int

        :return: a list of entity/entities
        """
        #ancestor_key = self.ds_client.key(ancestor['kind'],ancestor['id'])
        query = self.ds_client.query(kind=self.__kind__, ancestor=parent_or_ancestor)

        query.add_filter('active','=',True)
        
        entities =  list(query.fetch(limit=limit))

        return entities
    
    def get_obj(self, prop, value):
        """
        Fetches a single entity and populates the class attributes with the matching entity properties and values

        returns object of the class with the entity KEY
        You can call this directly, or have your model wrap a method around this method 
        passing in only the value(eg. obj.get(username))

        Note that this is called only once

        :param prop: the name of entity property to used for the query

        :type prop: str

        :param value: the value for the query
        :type value: int

        :return: a class object represensenting the entity
        """
        query = self.ds_client.query(kind=self.__kind__)
        query.add_filter(prop,'=',value)

        #reset the lookup list
        self.__datastore_properties_lookup__ = []

        entities =  list(query.fetch(limit=1))
        if entities:
            entity =  entities[0]

            #generate and populate the class attributes with properties and values of the fetched entity
            for k,v in entity.items():
                #setattr(self.__class__, k, v) 
                setattr(self, k, v) #don't populate the class attributes. they are just blueprints for instantiation
            
            #prepare the lookup list using the entity property names retrieved
            self._init_lookup(entity)
            #we set the entity's key
            self.key = entity.key

            return self
        else:
            return None

    def get_obj_with_key(self, key):
        """
        Similar to get_obj(), but fetches entity using it's key
        Retrieves an entity and populates the class attributes with the matching entity properties and values

        :param key: the datastore key
        :type key: datastore key

        :return: an object representing the entity
        """

        entity = self.ds_client.get(key)

        #reset the lookup list
        self.__datastore_properties_lookup__ = []
        
        if entity:

            #get all properties. note that some properties may not be defined in the class(ie added via extra_prop)
            for k,v in entity.items(): 
                #setattr(self.__class__, k, v)
                setattr(self, k, v)
            
            #prepare the lookup list
            self._init_lookup(entity)
            #before we return the object, we set it's key(to be used in updates)
            self.key = key

            return self
        else:
            return None
    
    def delete(self):
        """
        Deletes an entity

        """

        self.ds_client.delete(self.key)

        return True
    

    def generate_datastore_key(self,path):
        """
        :param path: a list with key path in the format ['kind','id',...]
        :type path: list

        :return: Datastore Key
        """

        key = self.ds_client.key(*path) #path_args
        
        return key
    
    def __repr__(self):
        return f"<Kind: '{self.__kind__}' ==> {[attr for attr in self.__datastore_properties_lookup__]}>"
    
    def get_objects(self, prop, value, limit=500, paginate=False, cursor=None):
        """
        Fetches a given number of entities and populates the class attributes with the matching entity properties and values


        :param prop: the name of the entity property

        :type prop: str 

        :param value: the name of the property value

        :type value: any. allowed datastore types

        :param limit: the maximum number of entities to return. Datastore supports a maximum of 500

        :type limit: int

        :paginate: whether to return a cursor to be used for pagination 

        :type paginate: boolean

        :param cursor: the 'next' cursor to be used to fetch next set of entities

        :type cursor: str. representing a datastore cursor

        :return: tuple. a two-element tuple. first element is a list of objects and the second is the cursor for pagination or None
        """
        next_cursor = None

        query = self.ds_client.query(kind=self.__kind__)
        query.add_filter(prop,'=',value)

        query_res =  query.fetch(start_cursor=cursor, limit=limit)


        if paginate:
            query_res =  query.fetch(start_cursor=cursor, limit=limit)
            current_page = next(query_res.pages)
            entities = list(current_page)
            next_cursor = query_res.next_page_token.decode('utf-8') #cursor is byte, convert to a string
        else:
            entities = list(query.fetch(start_cursor=cursor, limit=limit))


        if entities:
            objs = []
            #_fields = self.__get_cls_fields()
            for entity in entities:

                #for field in _fields:   
                for k,v in entity.items(): #get all properties. note that properties may not be defined in the class
                    #setattr(self.__class__, k, entity.get(k, None))
                    setattr(self, k, v)
                
                #before we return the object, we set it's key(to be used in updates)
                self.key = entity.key

                objs.append(self)
            return (objs,next_cursor)
        else:
            return None

