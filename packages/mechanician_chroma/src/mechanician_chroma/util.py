import re

def get_collection_name(username, ai_name):
    return f"{username}_{sanitize_for_filename(ai_name)}_collection"


def sanitize_for_filename(text: str, max_length: int = 255) -> str:
        """
        Converts a given string into a sanitized version suitable for filenames.
        
        :param text: The input string to sanitize.
        :param max_length: Maximum length of the filename. Defaults to 255, which is the typical maximum for most filesystems.
        :return: A sanitized string suitable for use as a filename.
        """
        # Lowercase the string
        sanitized = text.lower()
        
        # Replace spaces and unwanted characters
        sanitized = re.sub(r'\s+', '_', sanitized)  # Replace one or more spaces with underscore
        sanitized = re.sub(r'[\/\\:*?"<>|]', '', sanitized)  # Remove problematic characters
        
        # Truncate to max_length to avoid issues with long filenames
        return sanitized[:max_length]