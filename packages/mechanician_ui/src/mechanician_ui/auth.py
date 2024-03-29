import bcrypt
bcrypt.__about__ = type("", (), {"__version__": bcrypt.__version__})

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from mechanician_ui.secrets import SecretsManager, BasicSecretsManager
from zoneinfo import ZoneInfo
import json
from jose import JWTError, jwt
import logging
import secrets
import os

logger = logging.getLogger(__name__)

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

    @abstractmethod
    def decode_access_token(self, token):
        """
        Decode the access token and return the user's data.
        """
        pass

    @abstractmethod
    def update_user_attributes(self, username, password, attributes):
        """
        Update the user's attributes after verifying the password.
        """
        pass

    @abstractmethod
    def generate_secret_key(self):
        """
        Generate a secret key for use in token signing.
        """
        pass


class BasicCredentialsManager(CredentialsManager):
        
        ALGORITHM = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES = "1440" # 24 hours
    
        def __init__(self, credentials_filename: str, secrets_manager: SecretsManager=None):
            self.secrets_manager = secrets_manager or BasicSecretsManager(secrets={})
            self.credentials_filename = credentials_filename
            self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            self.credentials_data = {}
            self.load_credentials()
            self.tokens = {}

            secret_key = self.secrets_manager.get_secret("SECRET_KEY")
            if not secret_key:
                self.secrets_manager.set_secret("SECRET_KEY", 
                                                os.getenv("SECRET_KEY", self.generate_secret_key()))
            
            algorithm = self.secrets_manager.get_secret("ALGORITHM")
            if not algorithm:
                self.secrets_manager.set_secret("ALGORITHM", 
                                                os.getenv("ALGORITHM", self.ALGORITHM))
            
            access_token_expire_minutes = self.secrets_manager.get_secret("ACCESS_TOKEN_EXPIRE_MINUTES")
            if not access_token_expire_minutes:
                self.secrets_manager.set_secret("ACCESS_TOKEN_EXPIRE_MINUTES", 
                                                os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", self.ACCESS_TOKEN_EXPIRE_MINUTES))



        def generate_secret_key(self):
            # to get a string like this run:
            # openssl rand -hex 32
            # Generate a 32-byte (256-bit) hex-encoded secret key
            secret_key = secrets.token_hex(32)
            return secret_key



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
                logger.info(f"Error loading credentials: {e}")
                

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
        

        def update_user_attributes(self, username, password, attributes):
            if not self.verify_password(username, password):
                return False
            
            user = self.get_user(username)
            # merge user and attributes
            user.update(attributes)
            normalized_username = username.lower().strip()
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
                return True
            except (JWTError, json.JSONDecodeError) as e:
                    return False
            

        def decode_access_token(self, token):
            try:
                SECRET_KEY = self.secrets_manager.get_secret("SECRET_KEY")
                ALGORITHM = self.secrets_manager.get_secret("ALGORITHM")
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
                return payload
            except JWTError:
                return None