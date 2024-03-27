from abc import ABC, abstractmethod

class SecretsManager(ABC):

    @abstractmethod
    def get_secret(self, secret_name: str) -> str:
        pass

    @abstractmethod
    def set_secret(self, secret_name: str, secret_value: str):
        pass


class BasicSecretsManager(SecretsManager):

    def __init__(self, secrets: dict = {}):
        self.secrets = secrets

    def get_secret(self, secret_name: str) -> str:
        return self.secrets.get(secret_name, None)
    
    def set_secret(self, secret_name: str, secret_value: str):
        self.secrets[secret_name] = secret_value