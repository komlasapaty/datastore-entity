"""
export GOOGLE_APPLICATION_CREDENTIALS="/code/auth/dev/datastore-and-storage-service-account.json"
"""
import datetime
import sys

#sys.path.append('/code/datastore-entity/datastore_entity')
#print(sys.path)

import pytest
#from flask_login import UserMixin

from datastore_entity import DatastoreEntity, DSEntityValue

class UserMissingKind(DatastoreEntity):
    username = DSEntityValue('foo')
    password = DSEntityValue(None)
    date_created = DSEntityValue(datetime.datetime.utcnow())

class UserMixin:
    is_active = True

class ThirdParty(DatastoreEntity, UserMixin):
    username = DSEntityValue('foo')
    password = DSEntityValue(None)
    date_created = DSEntityValue(datetime.datetime.utcnow())

    __kind__ = 'user'

#UserMissingKind()

class TestEntity:

    def test_missing_kind(self):
        """
        When no __kind__ name is provided, raise a value error
        """
        with pytest.raises(ValueError):
            user_missing_kind = UserMissingKind()
    
    def test_attrs_not_polluted_from_third_party_classes(self):
        """
        Attributes from other inherited classes should not pollute the lookup list for the model class
        """
        lookup_list = ['username','password','date_created']
        third_party = ThirdParty()
        assert sorted(lookup_list) == sorted(third_party.__datastore_properties_lookup__)
