import bcrypt
bcrypt.__about__ = type("", (), {"__version__": bcrypt.__version__})

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from mechanician_ui.secrets import SecretsManager
from zoneinfo import ZoneInfo
import json
from jose import JWTError, jwt


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# def verify_password(plain_password, hashed_password):
#     return pwd_context.verify(plain_password, hashed_password)


# def get_user(users_secrets: SecretsManager, username: str):
#     user = users_secrets.get_secret(username)
#     return user


# def authenticate_user(users_secrets: SecretsManager, username: str, password: str):
#     user = get_user(users_secrets, username)
#     if not user:
#         return False
#     if not verify_password(password, user['hashed_password']):
#         return False
#     return user


# def create_access_token(secrets_manager: SecretsManager, data: dict, expires_delta: Optional[timedelta] = None):
#     to_encode = data.copy()
#     # Get the current time in UTC
#     current_time_utc = datetime.now(ZoneInfo("UTC"))
#     # Calculate expiration time
#     ACCESS_TOKEN_EXPIRE_MINUTES = int(secrets_manager.get_secret("ACCESS_TOKEN_EXPIRE_MINUTES"))
#     expire = current_time_utc + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     to_encode.update({"exp": expire})
#     SECRET_KEY = secrets_manager.get_secret("SECRET_KEY")
#     ALGORITHM = secrets_manager.get_secret("ALGORITHM")
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt




class CredentialsManager(ABC):

    @abstractmethod
    def user_exists(self, username):
        """
        Check if a user with the given username exists.
        """
        pass

    def get_user(self, username):
        """
        Get the user with the given username.
        """
        pass

    def get_user_by_token(self, token):
        """
        Get the user associated with the given token.
        """
        pass
    
    @abstractmethod
    def add_credentials(self, username, password):
        """
        Create a new user account with a username and password.
        The password should be hashed and salted before storage.
        """
        pass

    @abstractmethod
    def verify_password(self, username, password):
        """
        Verify a user's password.
        Returns True if the password is correct, False otherwise.
        """
        pass

    @abstractmethod
    def update_password(self, username, old_password, new_password):
        """
        Update the user's password after verifying the old password.
        The new password should be hashed and salted before storage.
        """
        pass

    @abstractmethod
    def reset_password(self, username, new_password):
        """
        Reset the user's password (typically after verifying some out-of-band authentication factor).
        The new password should be hashed and salted before storage.
        """
        pass

    @abstractmethod
    def delete_user(self, username):
        """
        Delete the user with the given username.
        """
        pass

    @abstractmethod
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """
        Create an access token for the user with the given data.
        """
        pass

    @abstractmethod
    def verify_access_token(self, token):
        """
        Verify the access token and return the user's data.
        """
        pass


class BasicCredentialsManager(CredentialsManager):
    
        def __init__(self, secrets_manager: SecretsManager, credentials_filename: str):
            self.secrets_manager = secrets_manager
            self.credentials_filename = credentials_filename
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            self.credentials_data = {}
            self.load_credentials()
            self.tokens = {}


        def load_credentials(self):
            # Load JSON file containing dict with username and hashed password using json.load
            try:
                with open(self.credentials_filename, "r") as f:
                    self.credentials_data = json.load(f)
            except FileNotFoundError:
                # If the file doesn't exist, create it
                with open(self.credentials_filename, "w") as f:
                    pass
            except Exception as e:
                print(f"Error loading credentials: {e}")
                

        def write_credentials(self):
            # Write the credentials data to the JSON file
            with open(self.credentials_filename, "w") as f:
                json.dump(self.credentials_data, f)


        def user_exists(self, username):
            normalized_username = username.lower().strip()
            return normalized_username in self.credentials_data
        

        def get_user(self, username):
            normalized_username = username.lower().strip()
            return self.credentials_data.get(normalized_username, None)
        

        def get_user_by_token(self, token):
            username = self.tokens.get(token, None)
            if username:
                return self.get_user(username)
            return None
        
    
        def add_credentials(self, username, password, attributes={}):
            if self.user_exists(username):
                return False
            
            normalized_username = username.lower().strip()
            hashed_password = self.pwd_context.hash(password)
            user = {"username": normalized_username, "hashed_password": hashed_password}
            # merge user and attributes
            user.update(attributes)
            self.credentials_data[normalized_username] = user
            self.write_credentials()
            return True
    

        def verify_password(self, username, password):
            if not self.user_exists(username):
                return False
            
            user = self.get_user(username)
            hashed_password = user.get("hashed_password")
            if not hashed_password:
                return False
            
            return self.pwd_context.verify(password, hashed_password)
    

        def update_password(self, username, old_password, new_password):
            if not self.verify_password(username, old_password):
                return False
            
            user = self.get_user(username)
            normalized_username = username.lower().strip()
            hashed_password = self.pwd_context.hash(new_password)
            user["hashed_password"] = hashed_password
            self.credentials_data[normalized_username] = user
            self.write_credentials()
            return True
    

        def reset_password(self, username, new_password):
            if not self.user_exists(username):
                return False
            
            user = self.get_user(username)
            hashed_password = self.pwd_context.hash(new_password)
            user["hashed_password"] = hashed_password
            normalized_username = username.lower().strip()
            self.credentials_data[normalized_username] = user
            self.write_credentials()
            return True
    

        def delete_user(self, username):
            if self.user_exists(username):
                normalized_username = username.lower().strip()
                self.credentials_data.pop(normalized_username, None)
                self.write_credentials()
                return True
            return False
        

        def create_access_token(self, username, data: dict, expires_delta: Optional[timedelta] = None):
            to_encode = data.copy()
            # Get the current time in UTC
            current_time_utc = datetime.now(ZoneInfo("UTC"))
            # Calculate expiration time
            ACCESS_TOKEN_EXPIRE_MINUTES = int(self.secrets_manager.get_secret("ACCESS_TOKEN_EXPIRE_MINUTES"))
            expire = current_time_utc + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
            to_encode.update({"exp": expire})
            SECRET_KEY = self.secrets_manager.get_secret("SECRET_KEY")
            ALGORITHM = self.secrets_manager.get_secret("ALGORITHM")
            encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

            # Store username keyed by token in the tokens dictionary
            self.tokens[encoded_jwt] = username

            return encoded_jwt


        def verify_access_token(self, token):
            try:
                # Decode and validate the JWT token
                SECRET_KEY = self.secrets_manager.get_secret("SECRET_KEY")
                ALGORITHM = self.secrets_manager.get_secret("ALGORITHM")
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                # Additional validation can be done here
                print(f"Token payload: {payload}")
                return True
            except (JWTError, json.JSONDecodeError) as e:
                    return False