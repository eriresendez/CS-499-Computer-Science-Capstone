from pymongo import MongoClient 
from bson.objectid import ObjectId

class AnimalShelter:
    """ CRUD operations for Animal collection in MongoDB """

    def __init__(self, username, password, host, port, database, collection): 

        # Connection Variables

        username = 'aacuser'
        password = 'ACC_USER_PASS'
        host = 'nv-desktop-services.apporto.com'
        port = 30258
        database = 'AAC'
        collection = 'animals'

        # Initialize Connection  

        self.client = MongoClient(f'mongodb://{username}:{password}@{host}:{port}')
        self.database = self.client[database]
        self.collection = self.database[collection]

    # Create Method to implemtnt the C in CRUD

    def create(self, data): 
        """ Insert new document into collection """ 
        #ensuring data is valid disctionary
        if data is not None and isinstance(data, dict):
            try: 
                inserted = self.collection.insert_one(data)
                if inserted.acknowledged:
                   #checing if the insert is acknowledged by MongoDB as this was causing issues
                   return True
                else:
                    print("Error inserting document: Insert not acknowledged")
                    return False
            except Exception as e: 
                print(f"Error querying documents: {e}")
                return [] # returns an empty list on failure
        else: 
            raise ValueError("Invalid data. Data parameter is empty and must be non-empty dictionary.")

    # Read method to imprement the R in CRUD

    def read(self, query):
        if query is not None and isinstance(query, dict):
            # ensuring query is a valid dictionary 
            try:  
                return list(self.collection.find(query))
            except Exception as e: 
                print(f"Error querying documents: {e}")
                return [] # returns an empty list on failure
        else:
            raise Exception("Invalid query. Data parameter is empty and myst be non-empty dictionary.")

            
    # UPDATE method to implement the U in CRUD
    
    def update(self, query, update_data, multiple=False):
        # updating one or more documents based on query
        if not isinstance(query, dict) or not isinstance(update_data, dict):
            raise ValueError("Invalid update. Query and update data must be non-empty dictionaries.")    
            
        try: 
            if multiple: 
                result = self.collection.update_many(query, {"$set": update_data})
            
            else: 
                result = self.collection.update_one(query, {"$set": update_data})
            
            return result.modified_count 
            # returns number of documents modified in the collection
        
        except Exception as e: 
            print(r"Error updating documents: {e}")
            return 0 
            # returning 0 if no documents were modified 
       
    
    # Deletetion method to implement the D in CRUD
    
    def delete(self, query, multiple=False):
        #detle one or many documents based on query
        if not isinstance(query, dict):
            raise ValueError("Invalid deletion. Query must be a non-empty dictionary.")
            
        try: 
            if multiple: 
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)
                
            return result.deleted_count
            # returns number of delted documents from collection
        
        except Exception as e:
            print(f"Error deleting documents: {e}")
            return 0
            #returning 0 if no documents were deleted form collection
            
            
