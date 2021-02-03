# Datastore Entity

Datastore Entity package provides a simple ORM-like (think SQL-Alchemy) interface to [Google Cloud](https://cloud.google.com) NoSQL 
[Datastore](https://cloud.google.com/datastore/docs/datastore-api-tutorial#python) (Firestore in Datastore mode).

"_Google Cloud Firestore in Datastore mode is a NoSQL document database built for automatic scaling, high performance, and ease of application development._"

Datastore Entity allows you to represent your entities using Python classes.
You can then use familiar ORM patterns with popular packages like WTForms(eg. ```form.populate_obj(model)```) or 
Flask-Login(ie ```User``` model for authentication), to create, read, update and delete entities.

## Documentation
[Datastore Entity documentation](https://datastore-entity.readthedocs.io)

# Quick Start
As always, to connect to a Google Cloud Platform service from your local machine, you need to set up a service account key.
Use the environment variable **GOOGLE_APPLICATION_CREDENTIALS** to point to the JSON file
```shell
export GOOGLE_APPLICATION_CREDENTIALS="/code/auth/datastore-service-account.json"
```
See below for another method of connecting by manually specifying the location of the service account JSON file.

## Installation
Install the package using pip
```shell
pip install datastore-entity
```

# Usage Examples
Some examples ...
### Create A Model Class 
```python
from datastore_entity import DatastoreEntity, EntityValue

class User(DatastoreEntity):

    # specify a default value of 'None'
    username = EntityValue(None)
    # or provide no argument to imply 'None'
    password = EntityValue()
    # default value of 1
    active = EntityValue(1)
    date_created = EntityValue(datetime.datetime.utcnow())

    # specify the name of the entity kind. 
    # This is REQUIRED. Raises ValueError otherwise
    __kind__ = "user"

    # optionally add properties to exclude from datastore indexes 
    __exclude_from_index__ = ['password']

    # call the super class here
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    # other useful methods go here...
```

### Connecting To Datastore
```python
# connect to the default datastore namespace. 
user = User()  
# After connecting, you can retrieve an entity as an object 
# or populate attributes and save the entity

#connect to the 'custom' datastore namespace
user = User(namespace='custom')  

# connect using a service account JSON key (as opposed to using 
# the environment variable GOOGLE_APPLICATION_CREDENTIALS)
user = User(service_account_json_path='path/to/service/account.json') 
```

### Persist an entity
```python
# set object attribute
user.username = 'komla'
# save or update entity to datastore
user.save()

# save an entity with custom ID/Name
user.save(id='komla')
```

### Generate datastore key ###
```python
# Create a key by specifing a parent and descendant(s)
key_path = ['Client','foo','Department','bar']
ancestor_key = user.generate_key(key_path)

# then save an entity as a descendant of a parent entity
user.save(parent_or_ancestor=ancestor_key) 
```

### Retrieve an entity as an object
```python
# specify property name and value. See the Tips sections below!
user = User().get_obj('username','komla') 

# the 'key' attribute is the entity's datastore key
entity_key = user.key    

# get the entity's id or name
name = user.key.id_or_name

# get the entity's parent's key
parent_key = user.key.parent

```

## Tips
#### Using A Base Model
You can use a class to represent common properties/columns, then inherit it for your models
```python
class BaseModel(DatastoreEntity):
    date_created = EntityValue(datetime.datetime.utcnow())
    created_by = EntityValue('Admin')
    updated_by = EntityValue(None)

class User(BaseModel):
    username = EntityValue(None)
    password = EntityValue()
    email = EntityValue(None)

    # ...
```

#### Retrieving Entity As Object
Often, you'll have a property/column you use to fetch an entity (eg, username or email)
Instead of always specifying the property/column AND value using the provided ```get_obj()``` method, 
you can simplify this by wrapping your own method for your model around ```get_obj()```:
```python
def get(self, value):
    return self.get_obj('username',value)
```
Then you can grab your entity/object with ```user = User().get('komla')```

#### Dynamically Populating Additional Properties
You can add additional properties to an instance of entity on the fly.  
Apart from using the `extra_props` dictionary as keyword argument to the `save()` method, you can create additional  
entity properties with the following:
```
user = User()
user.type = EntityValue(3) # assign attribute value as a type of EntityValue
user.save()
```
The specific instance of the entity will now have `type` as a property.

#### Testing
To initialize your model without connecting to datastore(eg. for the purposes of testing),
pass in the ```conn``` argument as ```False```
```python
user = User(conn=False)
```

## Notes ##
There might be operations you want to perform that are not available via the interface provided.
To get a direct access to Datastore connection client, use the ```get_client()``` method.
```python
datastore_client = user.get_client()
# ... proceed with operation
```
