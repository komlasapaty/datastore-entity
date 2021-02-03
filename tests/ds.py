#export GOOGLE_APPLICATION_CREDENTIALS="/code/auth/dev/datastore-and-storage-service-account.json"

from datastore_entity import DatastoreEntity, EntityValue
from google.cloud import datastore

import time

class User(DatastoreEntity):
    username = EntityValue(None)
    email = EntityValue(None)

    __kind__ = 'User'

    # call the super class here
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)


user = User(namespace="Tests")
# user.username = "Master"

# user.username = 'Seyram'
#t = user.save()

# print(user)
# print(user.username)
# print(f"Result: {t}")

#time.sleep(1)

# ds_client = datastore.Client(namespace='Tests')
# key = ds_client.key("User")
# entity = datastore.Entity(key=key)
# entity.update({'username':'Library'})
# ds_client.put(entity)

# u = user.get_obj('username', 'Komla')
# u.type = EntityValue(100)
# u.save()
# p = {"email":"komla@mail.com"}
# l = ['email']
# #u.save(extra_props=p)
# u.save(excludes=l)
# #print()

################################################
# ds_client = datastore.Client(namespace='Tests')

# query = ds_client.query(kind='User')
# query.add_filter('username','=','Komla')

# entities = list(query.fetch(limit=10))
# #print(f"Entities: {entities}")
# entity = entities[0]
# print(entity['extra'])

################################################
# user.name = EntityValue('Seyram Komla Sapaty')
# user.type = EntityValue(3)
# print("\n\n")
# user.save()