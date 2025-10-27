import jwt
import datetime
import bcrypt
import json
from pymongo import MongoClient
from pymongo.errors import OperationFailure, ConnectionFailure
from bson import ObjectId
import pandas as pd
from functools import wraps

class AnimalShelter:
    """ CRUD operations with authentication and analytics using MongoDB """
    
    def __init__(self, username='', password='', host='localhost', port=27017, db='AAC', collection='animals'):
        """
        Initialize database connection with flexible authentication
        Supports both authenticated and non-authenticated MongoDB instances
        """
        self.connection_successful = False
        self.auth_enabled = False
        
        try:
            print(f"Attempting to connect to MongoDB at {host}:{port}...")
            
            # Try connection without authentication first
            try:
                self.client = MongoClient(
                    host=host,
                    port=port,
                    serverSelectionTimeoutMS=5000  # 5 second timeout
                )
                # Test connection
                self.client.admin.command('ping')
                print("MongoDB connection successful (no authentication)")
                self.connection_successful = True
                self.auth_enabled = False
                
            except (OperationFailure, ConnectionFailure) as e:
                # If no-auth fails, try WITH authentication
                if username and password:
                    print(f"Trying authenticated connection...")
                    self.client = MongoClient(
                        host=host,
                        port=port,
                        username=username,
                        password=password,
                        authSource='admin',
                        serverSelectionTimeoutMS=5000
                    )
                    # Test connection
                    self.client.admin.command('ping')
                    print("MongoDB connection successful (with authentication)")
                    self.connection_successful = True
                    self.auth_enabled = True
                else:
                    raise Exception("Authentication required but no credentials provided")
            
            # Set up database and collections
            self.database = self.client[db]
            self.collection = self.database[collection]
            self.users_collection = self.database['users']
            self.audit_log_collection = self.database['audit_logs']
            
            # Initialize default users and indexes
            self._initialize_default_users()
            self._create_audit_indexes()
            
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            print("Running in DEMO MODE with mock data...")
            self.client = None
            self.database = None
            self.collection = None
            self.users_collection = None
            self.audit_log_collection = None
            self.connection_successful = False
            self.auth_enabled = False
        
        # JWT secret key for token generation and validation
        self.secret_key = 'grazioso-salvare-secret-key-2025-enhanced'

    def _create_audit_indexes(self):
        """ Create indexes for audit logging performance """
        try:
            if self.audit_log_collection is not None:
                self.audit_log_collection.create_index([("timestamp", -1)])
                self.audit_log_collection.create_index([("username", 1), ("timestamp", -1)])
                print("Audit indexes created successfully")
        except Exception as e:
            print(f"Warning: Could not create audit indexes: {e}")

    def _log_audit_event(self, username, action, details):
        """ Log security and operational events """
        try:
            if self.audit_log_collection is not None:
                audit_record = {
                    'username': username,
                    'action': action,
                    'details': details,
                    'timestamp': datetime.datetime.utcnow(),
                    'ip_address': 'system'
                }
                self.audit_log_collection.insert_one(audit_record)
        except Exception as e:
            print(f"Warning: Could not log audit event: {e}")

    def _initialize_default_users(self):
        """ Create default users if not existing """
        if not self.connection_successful:
            print("Skipping user initialization - running in demo mode")
            return
            
        try:
            default_users = [
                {
                    'username': 'admin',
                    'password': bcrypt.hashpw('admin234'.encode('utf-8'), bcrypt.gensalt()),
                    'role': 'admin',
                    'email': 'admin@grazioso.org',
                    'created_at': datetime.datetime.utcnow(),
                    'active': True
                },
                {
                    'username': 'user',
                    'password': bcrypt.hashpw('user123'.encode('utf-8'), bcrypt.gensalt()),
                    'role': 'viewer', 
                    'email': 'user@grazioso.org',
                    'created_at': datetime.datetime.utcnow(),
                    'active': True
                },
                {
                    'username': 'analyst',
                    'password': bcrypt.hashpw('analyst456'.encode('utf-8'), bcrypt.gensalt()),
                    'role': 'analyst',
                    'email': 'analyst@grazioso.org',
                    'created_at': datetime.datetime.utcnow(),
                    'active': True
                }
            ]
            
            for user in default_users:
                if not self.users_collection.find_one({'username': user['username']}):
                    self.users_collection.insert_one(user)
                    self._log_audit_event('system', 'USER_CREATED', f"Default user {user['username']} created")
                    print(f"Created default user: {user['username']}")
                else:
                    print(f"User {user['username']} already exists")
                    
        except Exception as e:
            print(f"Warning: Could not initialize users: {e}")

    # Authentication methods
    
    def create_user(self, current_user, username, password, role='viewer', email=''):
        """ Create new user with hashed password - requires admin privileges """
        if not self.connection_successful:
            return False, "Database not available - running in demo mode"
            
        try:
            # Verify current user has admin privileges
            current_user_data = self.users_collection.find_one({'username': current_user})
            if not current_user_data or current_user_data.get('role') != 'admin':
                return False, "Insufficient privileges: Admin role required"
                
            if self.users_collection.find_one({'username': username}):
                return False, "User already exists"
            
            if role not in ['admin', 'viewer', 'analyst']:
                return False, "Invalid role. Must be: admin, viewer, or analyst"
                
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            user_data = {
                'username': username,
                'password': hashed_password,
                'role': role,
                'email': email,
                'created_at': datetime.datetime.utcnow(),
                'active': True,
                'created_by': current_user
            }
            
            self.users_collection.insert_one(user_data)
            self._log_audit_event(current_user, 'USER_CREATED', f"Created user {username} with role {role}")
            return True, f"User {username} created successfully with role {role}"
            
        except Exception as e:
            return False, f"Error creating user: {str(e)}"

    def authenticate_user(self, username, password):
        """ Authenticate user and return JWT token """
        # Demo mode authentication - always works with default credentials
        if not self.connection_successful:
            default_credentials = {
                'admin': ('admin234', 'admin'),
                'user': ('user123', 'viewer'),
                'analyst': ('analyst456', 'analyst')
            }
            
            if username in default_credentials:
                expected_password, role = default_credentials[username]
                if password == expected_password:
                    token = jwt.encode({
                        'username': username,
                        'role': role,
                        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                    }, self.secret_key, algorithm='HS256')
                    print(f"Demo authentication successful for {username}")
                    return True, token
            
            return False, "Invalid credentials in demo mode"
        
        # Real database authentication
        try:
            user = self.users_collection.find_one({'username': username, 'active': True})
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
                token = jwt.encode({
                    'username': username,
                    'role': user['role'],
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
                }, self.secret_key, algorithm='HS256')
                
                self._log_audit_event(username, 'LOGIN_SUCCESS', "User logged in successfully")
                return True, token
            else:
                self._log_audit_event(username, 'LOGIN_FAILED', "Failed login attempt")
                return False, "Invalid credentials"
        except Exception as e:
            return False, f"Authentication error: {str(e)}"

    def verify_token(self, token):
        """ Verify JWT token and return user data """
        try:
            if isinstance(token, bytes):
                token = token.decode('utf-8')
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            
            # If database is available, verify user still exists and is active
            if self.connection_successful and self.users_collection is not None:
                user = self.users_collection.find_one({'username': payload['username'], 'active': True})
                if not user:
                    return False, "User no longer active"
                
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, "Token expired"
        except jwt.InvalidTokenError:
            return False, "Invalid token"

    def list_users(self, current_user):
        """ List all users - admin only """
        if not self.connection_successful:
            return False, "Database not available - running in demo mode"
            
        try:
            current_user_data = self.users_collection.find_one({'username': current_user})
            if not current_user_data or current_user_data.get('role') != 'admin':
                return False, "Insufficient privileges: Admin role required"
                
            users = list(self.users_collection.find({}, {'password': 0}))  # Exclude passwords
            return True, users
        except Exception as e:
            return False, f"Error listing users: {str(e)}"

    def deactivate_user(self, current_user, username):
        """ Deactivate a user - admin only """
        if not self.connection_successful:
            return False, "Database not available - running in demo mode"
            
        try:
            current_user_data = self.users_collection.find_one({'username': current_user})
            if not current_user_data or current_user_data.get('role') != 'admin':
                return False, "Insufficient privileges: Admin role required"
                
            if username == current_user:
                return False, "Cannot deactivate your own account"
                
            result = self.users_collection.update_one(
                {'username': username}, 
                {'$set': {'active': False, 'deactivated_at': datetime.datetime.utcnow(), 'deactivated_by': current_user}}
            )
            
            if result.modified_count > 0:
                self._log_audit_event(current_user, 'USER_DEACTIVATED', f"Deactivated user {username}")
                return True, f"User {username} deactivated successfully"
            else:
                return False, "User not found or already deactivated"
        except Exception as e:
            return False, f"Error deactivating user: {str(e)}"

    # CRUD operations
    
    def read_without_auth(self, query):
        """ Read animal records without authentication for initial dashboard load """
        if not self.connection_successful:
            # Return comprehensive mock data if database not available
            mock_data = [
                {
                    'animal_id': 'A001', 'animal_type': 'Dog', 'breed': 'Labrador Retriever Mix',
                    'age_upon_outcome_in_weeks': 52, 'outcome_type': 'Adoption',
                    'sex_upon_outcome': 'Intact Female', 'name': 'Buddy', 'location_lat': 30.75, 'location_long': -97.48
                },
                {
                    'animal_id': 'A002', 'animal_type': 'Dog', 'breed': 'Chesapeake Bay Retriever',
                    'age_upon_outcome_in_weeks': 60, 'outcome_type': 'Adoption',
                    'sex_upon_outcome': 'Intact Female', 'name': 'Sadie', 'location_lat': 30.76, 'location_long': -97.49
                },
                {
                    'animal_id': 'A003', 'animal_type': 'Dog', 'breed': 'Newfoundland',
                    'age_upon_outcome_in_weeks': 80, 'outcome_type': 'Transfer',
                    'sex_upon_outcome': 'Intact Female', 'name': 'Molly', 'location_lat': 30.74, 'location_long': -97.47
                },
                {
                    'animal_id': 'A004', 'animal_type': 'Dog', 'breed': 'German Shepherd',
                    'age_upon_outcome_in_weeks': 48, 'outcome_type': 'Adoption',
                    'sex_upon_outcome': 'Intact Male', 'name': 'Max', 'location_lat': 30.77, 'location_long': -97.50
                },
                {
                    'animal_id': 'A005', 'animal_type': 'Dog', 'breed': 'Alaskan Malamute',
                    'age_upon_outcome_in_weeks': 55, 'outcome_type': 'Adoption',
                    'sex_upon_outcome': 'Intact Male', 'name': 'Duke', 'location_lat': 30.73, 'location_long': -97.46
                },
                {
                    'animal_id': 'A006', 'animal_type': 'Cat', 'breed': 'Siamese',
                    'age_upon_outcome_in_weeks': 26, 'outcome_type': 'Transfer',
                    'sex_upon_outcome': 'Spayed Female', 'name': 'Whiskers', 'location_lat': 30.78, 'location_long': -97.51
                },
                {
                    'animal_id': 'A007', 'animal_type': 'Dog', 'breed': 'Golden Retriever',
                    'age_upon_outcome_in_weeks': 45, 'outcome_type': 'Return to Owner',
                    'sex_upon_outcome': 'Neutered Male', 'name': 'Charlie', 'location_lat': 30.72, 'location_long': -97.45
                }
            ]
            return mock_data
            
        try:
            if query is not None:
                data = self.collection.find(query, {"_id": False})
                return list(data)
            else:
                raise Exception("Nothing to read, because query parameter is empty")
        except Exception as e:
            print(f"Error reading data: {e}")
            return []

    def create(self, data, username):
        """ Create new animal record with audit logging """
        if not self.connection_successful:
            return False
            
        try:
            if data is not None:
                result = self.collection.insert_one(data)
                success = result.inserted_id is not None
                if success:
                    self._log_audit_event(username, 'CREATE_RECORD', f"Created animal record {result.inserted_id}")
                return success
            else:
                raise Exception("Nothing to save, because data parameter is empty")
        except Exception as e:
            print(f"Error creating record: {e}")
            return False

    def read(self, query, username):
        """ Read animal records with query and audit logging """
        if not self.connection_successful:
            return self.read_without_auth(query)
            
        try:
            if query is not None:
                self._log_audit_event(username, 'READ_RECORDS', f"Query: {json.dumps(query, default=str)}")
                data = self.collection.find(query, {"_id": False})
                return list(data)
            else:
                raise Exception("Nothing to read, because query parameter is empty")
        except Exception as e:
            print(f"Error reading records: {e}")
            return []

    def update(self, query, update_data, username, multiple=False):
        """ Update animal records with audit logging """
        if not self.connection_successful:
            return 0
            
        try:
            if query is not None and update_data is not None:
                if multiple:
                    result = self.collection.update_many(query, {"$set": update_data})
                    self._log_audit_event(username, 'UPDATE_RECORDS', f"Updated {result.modified_count} records")
                    return result.modified_count
                else:
                    result = self.collection.update_one(query, {"$set": update_data})
                    if result.modified_count > 0:
                        self._log_audit_event(username, 'UPDATE_RECORD', f"Updated record matching {json.dumps(query, default=str)}")
                    return result.modified_count
            else:
                raise Exception("Nothing to update, because parameters are empty")
        except Exception as e:
            print(f"Error updating records: {e}")
            return 0

    def delete(self, query, username, multiple=False):
        """ Delete animal records with audit logging """
        if not self.connection_successful:
            return 0
            
        try:
            if query is not None:
                if multiple:
                    result = self.collection.delete_many(query)
                    self._log_audit_event(username, 'DELETE_RECORDS', f"Deleted {result.deleted_count} records")
                    return result.deleted_count
                else:
                    result = self.collection.delete_one(query)
                    if result.deleted_count > 0:
                        self._log_audit_event(username, 'DELETE_RECORD', f"Deleted record matching {json.dumps(query, default=str)}")
                    return result.deleted_count
            else:
                raise Exception("Nothing to delete, because query parameter is empty")
        except Exception as e:
            print(f"Error deleting records: {e}")
            return 0

    #Advances analytics    
    def get_breed_performance_metrics(self):
        """ Advanced analytics using MongoDB aggregation pipeline """
        if not self.connection_successful:
            return self._get_mock_breed_performance()
            
        try:
            pipeline = [
                {
                    "$match": {
                        "animal_type": "Dog",
                        "outcome_type": {"$in": ["Adoption", "Return to Owner", "Transfer"]}
                    }
                },
                {
                    "$group": {
                        "_id": "$breed",
                        "total_animals": {"$sum": 1},
                        "adoption_count": {
                            "$sum": {"$cond": [{"$eq": ["$outcome_type", "Adoption"]}, 1, 0]}
                        },
                        "return_to_owner_count": {
                            "$sum": {"$cond": [{"$eq": ["$outcome_type", "Return to Owner"]}, 1, 0]}
                        },
                        "transfer_count": {
                            "$sum": {"$cond": [{"$eq": ["$outcome_type", "Transfer"]}, 1, 0]}
                        }
                    }
                },
                {
                    "$project": {
                        "breed": "$_id",
                        "total_animals": 1,
                        "adoption_count": 1,
                        "adoption_rate": {
                            "$multiply": [{"$divide": ["$adoption_count", "$total_animals"]}, 100]
                        },
                        "success_rate": {
                            "$multiply": [
                                {"$divide": [
                                    {"$add": ["$adoption_count", "$return_to_owner_count", "$transfer_count"]},
                                    "$total_animals"
                                ]},
                                100
                            ]
                        }
                    }
                },
                {
                    "$match": {"total_animals": {"$gte": 5}}
                },
                {
                    "$sort": {"success_rate": -1, "total_animals": -1}
                },
                {
                    "$limit": 15
                }
            ]
            
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            print(f"Error in breed performance analytics: {e}")
            return self._get_mock_breed_performance()

    def _get_mock_breed_performance(self):
        """ Return mock breed performance data """
        return [
            {'breed': 'Labrador Retriever Mix', 'total_animals': 45, 'adoption_count': 38, 'adoption_rate': 84.4, 'success_rate': 91.1},
            {'breed': 'German Shepherd', 'total_animals': 32, 'adoption_count': 25, 'adoption_rate': 78.1, 'success_rate': 87.5},
            {'breed': 'Golden Retriever', 'total_animals': 28, 'adoption_count': 24, 'adoption_rate': 85.7, 'success_rate': 92.8},
            {'breed': 'Bulldog', 'total_animals': 22, 'adoption_count': 16, 'adoption_rate': 72.7, 'success_rate': 81.8},
            {'breed': 'Beagle', 'total_animals': 35, 'adoption_count': 28, 'adoption_rate': 80.0, 'success_rate': 88.6}
        ]

    def get_rescue_type_analytics(self):
        """ Enhanced rescue analytics with detailed breakdown """
        if not self.connection_successful:
            return self._get_mock_rescue_analytics()
            
        try:
            water_rescue_pipeline = [
                {
                    "$match": {
                        "animal_type": "Dog",
                        "breed": {"$in": ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"]},
                        "sex_upon_outcome": "Intact Female"
                    }
                },
                {
                    "$group": {
                        "_id": "$breed",
                        "count": {"$sum": 1},
                        "avg_age_weeks": {"$avg": "$age_upon_outcome_in_weeks"}
                    }
                }
            ]
            
            wilderness_rescue_pipeline = [
                {
                    "$match": {
                        "animal_type": "Dog",
                        "breed": {"$in": ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog", "Siberian Husky", "Rottweiler"]},
                        "sex_upon_outcome": "Intact Male"
                    }
                },
                {
                    "$group": {
                        "_id": "$breed",
                        "count": {"$sum": 1},
                        "avg_age_weeks": {"$avg": "$age_upon_outcome_in_weeks"}
                    }
                }
            ]
            
            disaster_rescue_pipeline = [
                {
                    "$match": {
                        "animal_type": "Dog",
                        "breed": {"$in": ["Doberman Pinscher", "German Shepherd", "Golden Retriever", "Bloodhound", "Rottweiler"]},
                        "sex_upon_outcome": "Intact Male"
                    }
                },
                {
                    "$group": {
                        "_id": "$breed",
                        "count": {"$sum": 1},
                        "avg_age_weeks": {"$avg": "$age_upon_outcome_in_weeks"}
                    }
                }
            ]
            
            water_breakdown = list(self.collection.aggregate(water_rescue_pipeline))
            wilderness_breakdown = list(self.collection.aggregate(wilderness_rescue_pipeline))
            disaster_breakdown = list(self.collection.aggregate(disaster_rescue_pipeline))
            
            return {
                'water_rescue': {
                    'total': sum(item['count'] for item in water_breakdown),
                    'breakdown': water_breakdown
                },
                'wilderness_rescue': {
                    'total': sum(item['count'] for item in wilderness_breakdown),
                    'breakdown': wilderness_breakdown
                },
                'disaster_rescue': {
                    'total': sum(item['count'] for item in disaster_breakdown),
                    'breakdown': disaster_breakdown
                }
            }
        except Exception as e:
            print(f"Error in rescue analytics: {e}")
            return self._get_mock_rescue_analytics()

    def _get_mock_rescue_analytics(self):
        """ Return mock rescue analytics data """
        return {
            'water_rescue': {
                'total': 25,
                'breakdown': [
                    {'_id': 'Labrador Retriever Mix', 'count': 12, 'avg_age_weeks': 45.2},
                    {'_id': 'Chesapeake Bay Retriever', 'count': 8, 'avg_age_weeks': 52.7},
                    {'_id': 'Newfoundland', 'count': 5, 'avg_age_weeks': 61.3}
                ]
            },
            'wilderness_rescue': {
                'total': 18,
                'breakdown': [
                    {'_id': 'German Shepherd', 'count': 6, 'avg_age_weeks': 48.5},
                    {'_id': 'Alaskan Malamute', 'count': 5, 'avg_age_weeks': 55.2},
                    {'_id': 'Siberian Husky', 'count': 4, 'avg_age_weeks': 42.8},
                    {'_id': 'Rottweiler', 'count': 3, 'avg_age_weeks': 50.1}
                ]
            },
            'disaster_rescue': {
                'total': 32,
                'breakdown': [
                    {'_id': 'Doberman Pinscher', 'count': 8, 'avg_age_weeks': 47.3},
                    {'_id': 'German Shepherd', 'count': 7, 'avg_age_weeks': 49.2},
                    {'_id': 'Golden Retriever', 'count': 9, 'avg_age_weeks': 43.7},
                    {'_id': 'Bloodhound', 'count': 5, 'avg_age_weeks': 58.4},
                    {'_id': 'Rottweiler', 'count': 3, 'avg_age_weeks': 51.6}
                ]
            }
        }

    def get_monthly_adoption_trends(self, months=12):
        """ Enhanced adoption trends with multiple metrics """
        if not self.connection_successful:
            return self._get_mock_adoption_trends()
            
        try:
            pipeline = [
                {
                    "$match": {
                        "outcome_type": "Adoption",
                        "datetime": {"$exists": True, "$ne": None}
                    }
                },
                {
                    "$addFields": {
                        "parsed_date": {"$toDate": "$datetime"}
                    }
                },
                {
                    "$group": {
                        "_id": {
                            "year": {"$year": "$parsed_date"},
                            "month": {"$month": "$parsed_date"}
                        },
                        "adoption_count": {"$sum": 1},
                        "dog_adoptions": {"$sum": {"$cond": [{"$eq": ["$animal_type", "Dog"]}, 1, 0]}},
                        "cat_adoptions": {"$sum": {"$cond": [{"$eq": ["$animal_type", "Cat"]}, 1, 0]}}
                    }
                },
                {
                    "$project": {
                        "year": "$_id.year",
                        "month": "$_id.month",
                        "adoption_count": 1,
                        "dog_adoptions": 1,
                        "cat_adoptions": 1
                    }
                },
                {
                    "$sort": {"_id.year": -1, "_id.month": -1}
                },
                {
                    "$limit": months
                }
            ]
            
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            print(f"Error in adoption trends: {e}")
            return self._get_mock_adoption_trends()

    def _get_mock_adoption_trends(self):
        """ Return mock adoption trends data """
        return [
            {'year': 2024, 'month': 10, 'adoption_count': 62, 'dog_adoptions': 38, 'cat_adoptions': 22},
            {'year': 2024, 'month': 9, 'adoption_count': 58, 'dog_adoptions': 36, 'cat_adoptions': 20},
            {'year': 2024, 'month': 8, 'adoption_count': 65, 'dog_adoptions': 40, 'cat_adoptions': 23},
            {'year': 2024, 'month': 7, 'adoption_count': 60, 'dog_adoptions': 38, 'cat_adoptions': 20},
            {'year': 2024, 'month': 6, 'adoption_count': 58, 'dog_adoptions': 36, 'cat_adoptions': 20},
            {'year': 2024, 'month': 5, 'adoption_count': 60, 'dog_adoptions': 38, 'cat_adoptions': 20}
        ]

    def get_animal_demographics(self):
        """ Comprehensive animal demographics analytics """
        if not self.connection_successful:
            return self._get_mock_demographics()
            
        try:
            pipeline = [
                {
                    "$group": {
                        "_id": "$animal_type",
                        "total_count": {"$sum": 1},
                        "avg_age_weeks": {"$avg": "$age_upon_outcome_in_weeks"}
                    }
                },
                {
                    "$project": {
                        "animal_type": "$_id",
                        "total_count": 1,
                        "avg_age_weeks": 1
                    }
                },
                {
                    "$sort": {"total_count": -1}
                }
            ]
            
            return list(self.collection.aggregate(pipeline))
        except Exception as e:
            print(f"Error in demographics analytics: {e}")
            return self._get_mock_demographics()

    def _get_mock_demographics(self):
        """ Return mock demographics data """
        return [
            {'animal_type': 'Dog', 'total_count': 65, 'avg_age_weeks': 45.2},
            {'animal_type': 'Cat', 'total_count': 35, 'avg_age_weeks': 32.7},
            {'animal_type': 'Bird', 'total_count': 12, 'avg_age_weeks': 28.3},
            {'animal_type': 'Other', 'total_count': 8, 'avg_age_weeks': 36.5}
        ] 

        