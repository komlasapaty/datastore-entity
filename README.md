# Datastore Entity

DatastoreEntity package provides a simple ORM-like(think SQL-Alchemy) interface to [**Google Cloud**](https://cloud.google.com) NoSQL [**Datastore**](https://cloud.google.com/datastore/docs/datastore-api-tutorial#python)(Firestore in Datastore mode).

Google Cloud Firestore in Datastore mode is a NoSQL document database built for automatic scaling, high performance, and ease of application development. Datastore

DatastoreEntity package allows you to represent your datastore entities using Python classes.
You can then use familiar patterns with popular packages like WTForms(eg. ```form.populate_obj(model)```) or Flask-Login(ie User model for authentication), to create, read, update and delete entities.

## Documentation Link
Coming soon...

## Setup
As always, to connect to a Google Cloud Platform service from your local machine, you need to set up a service account key.
Use the environment variable **GOOGLE_APPLICATION_CREDENTIALS** to point to the JSON file
```
export GOOGLE_APPLICATION_CREDENTIALS="/code/auth/datastore-service-account.json"
```
See below for another method of connecting by manually specifying the location of the service account JSON file.


## Installation
Install the package using pip
```
pip install datastore-entity
```

# Usage Examples
Some useful examples after installation
### Create A Model Class 
```python
from datastore_entity import DatastoreEntity, DSEntityValue

class User(DatastoreEntity):

    username = DSEntityValue(None)  #specify a default value or provide no argument to imply 'None' value
    password = DSEntityValue()
    active = DSEntityValue(1)
    date_created = DSEntityValue(datetime.datetime.utcnow()) #from datetime module

    #specify the entity kind name. This is REQUIRED
    __kind__ = "User"

    #optionally add properties to exclude from datastore indexes here
    __exclude_from_index__ = []

    #Call the super class
    def __init__(self,namespace,service_account_json_path):
        super(User,self).__init__(namespace, namespace)

    # other useful methods go here...
```

### Connecting To Datastore
```python
user = User()  
#this connects to the default namespace. 
# After connecting, you can retrieve an entity as an object or populate attributes and save the entity

#connects to the 'custom' datastore namespace
user = User('custom')  

#connect using a service account JSON key (as opposed to using 
# the environment variable GOOGLE_APPLICATION_CREDENTIALS)
user = User(service_account_json_path='path/to/service/account.json') 
```

### Persist an entity
```python
#set object attribute
user.username = 'komla'
#save or update entity to datastore
user.save()

#save an entity with custom ID
user.save(id='komla')
```

### Generate datastore key ###
```python
#Create a key by specifing a parent and descendant(s)
key_path = ['Client','for','Department','sales']
ancestor_key = user.generate_key(key_path)

#then save an entity as a descendant of a parent entity
user.save(parent_or_ancestor=ancestor_key) 
```

### Retrieve an entity as an object
```python
#specify property name and value. See the Tips sections below!
user = User().get_obj('username','komla') 

#the 'key' attribute is the entity's datastore key
user.key             

```

## Tips
#### Using A Base Model
You can use a class to represent common properties/columns, then inherit it for your models
```python
class BaseModel(DatastoreEntity):
    date_created = DSEntityValue(datetime.datetime.utcnow())
    created_by = DSEntityValue(None)
    updated_by = DSEntityValue(None)

class User(BaseModel):
    username = DSEntityValue(None)

    #...
```

#### Retrieving Entity As Object
Often, you'll have a property/column you use to fetch an entity (eg, username or email)
Instead of always specifying the property/column and value using the provided ```get_obj()```, method, 
you can simplify this by wrapping your own method for your model around ```get_obj()```:
```python
def get(self, value):
    return self.get_obj('username',value)
```
Then you can grab your entity object with ```user = User().get('komla')```

## Limitations ##
There might be operations you want to perform that are not available via the interface provided.
To get a direct access to Datastore connection clients, use the ```get_client()``` method.
```python
datastore_client = user.get_client()
#... proceed with operation

```