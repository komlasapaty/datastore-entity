"""
To connect to google cloud datastore service, set up the GOOGLE_APPLICATION_CREDENTIALS 
environment variable with service account key file
Example:
    export GOOGLE_APPLICATION_CREDENTIALS="/code/auth/dev/datastore-service-account.json"
"""
import datetime
import sys

#sys.path.append('/code/datastore-entity/datastore_entity')

import pytest

from datastore_entity import DatastoreEntity, EntityValue

class ModelMissingKind(DatastoreEntity):
    username = EntityValue('foo')
    password = EntityValue(None)
    date_created = EntityValue(datetime.datetime.utcnow())

#As thirdparty class
class UserMixin:
    is_active = True

class ThirdParty(DatastoreEntity, UserMixin):
    username = EntityValue('foo')
    password = EntityValue(None)
    date_created = EntityValue(datetime.datetime.utcnow())

    __kind__ = 'user'

class Entity(DatastoreEntity):
    updated_by = EntityValue(None)
    created_by = EntityValue()
    extra_prop = "Extra"

    __kind__ = 'my_entity'

class TestEntity:

    def test_missing_kind(self):
        """
        When no __kind__ name is provided for a model class, raise ValueError
        """
        with pytest.raises(ValueError):
            user_missing_kind = ModelMissingKind(conn=False)
    
    def test_attrs_declared_as_property_names_are_returned(self):
        """
        Ensure attributes marked as 'EntityValue' are the only ones in property lookup list
        """
        #lookup_list = ['username','password','date_created']
        third_party = Entity(conn=False)
        assert "extra_prop" not in third_party.__datastore_properties_lookup__
    
    def test_attrs_not_polluted_from_third_party_classes(self):
        """
        Attributes from other inherited classes should not pollute the lookup list for the model class
        """
        lookup_list = ['username','password','date_created']
        third_party = ThirdParty()
        assert sorted(lookup_list) == sorted(third_party.__datastore_properties_lookup__)
    
    def test_attr_dsentityvalue_instance(self):
        """
        Attribute must be an instance of EntityValue at initialization
        """
        user = ThirdParty(conn=False)
        assert isinstance(user.username, EntityValue)
    
    def test_do_not_connect_when_conn_is_false(self):
        """
        Don't connect to datastore on model initialization when 'conn' argument
        is False
        """
        entity = Entity(conn=False)
        assert entity.get_client() is None
    
    def test_lazy_connection(self):
        """
        Connect to datastore using .connect()
        """
        entity = Entity(conn=False)
        assert entity.connect() == True
    

class TestEntityValue:
    def test_none_value(self):
        """
        Check that when EntityValue is initialized without a value, it defaults to `None`
        """
        entity_value = EntityValue()
        assert entity_value.value is None
    
    def test_value_passed(self):
        """
        Check that the value passed to EntityValue is what is returned
        """
        value = "foobar" 
        entity_value = EntityValue(value)
        assert entity_value.value == value