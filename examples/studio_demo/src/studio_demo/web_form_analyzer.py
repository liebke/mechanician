from mechanician.resources import ResourceConnector, ResourceConnectorProvisioner
from mechanician.tools import AITools, MechanicianToolsProvisioner
import requests
from bs4 import BeautifulSoup
from pprint import pprint

###############################################################################
## WebFormAnalyzerConnectorProvisioner
###############################################################################
    
class WebFormAnalyzerConnectorProvisioner(ResourceConnectorProvisioner):

        def create_connector(self, context: dict={}):
            # Use the context to control access to resources provided by the connector.
            # ...
            return WebFormAnalyzerConnector()


###############################################################################
## WebFormAnalyzerConnector
###############################################################################

class WebFormAnalyzerConnector(ResourceConnector):

    def extract_communication_elements(self, html_content):
        # Initialize BeautifulSoup to parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract all forms
        forms = soup.find_all('form')
        forms_html = ''.join(str(form) for form in forms)
        
        # Extract all JavaScript
        scripts = soup.find_all('script')
        scripts_html = ''.join(str(script) for script in scripts)
        
        # Combine the extracted forms and scripts
        extracted_html = forms_html + scripts_html
        
        return extracted_html

    

    def analyze_web_form(self, params={}):
        # Check if 'url' key exists in params
        if 'url' not in params:
            print("The 'url' key is missing from the parameters.")
            raise ValueError("The 'url' key is missing from the parameters.")
        
        url = params['url']
        
        # # Ensure the URL starts with 'https://'
        # if not url.startswith('https://'):
        #     raise ValueError("The URL must be HTTPS.")
        
        # Fetch the web page content
        response = requests.get(url)
        
        # Check for successful request
        if response.status_code != 200:
            print(f"Failed to load the URL. Status code: {response.status_code}")
            raise Exception(f"Failed to load the URL. Status code: {response.status_code}")
        
        extracted_html = self.extract_communication_elements(response.text)
        print(f"Loaded the URL: {url}")
        pprint(extracted_html)

        max_length = 100000 # leave room for prompt and other data
        content = extracted_html[:max_length]

        return [{"name": "url", "data": url},
                {"name": "content", "data": content}]



    def get_github_commit_diff(self, repo, commit_hash, token=None):
        """
        Fetches the diff for a specific commit in a GitHub repository.

        :param repo: Repository name in the format "owner/repo".
        :param commit_hash: The commit hash to get the diff for.
        :param token: Optional GitHub personal access token for authentication.
        :return: The diff as a string.
        """
        base_url = f"https://api.github.com/repos/{repo}/commits/{commit_hash}"
        headers = {}
        
        if token:
            headers["Authorization"] = f"token {token}"

        response = requests.get(base_url, headers=headers)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching commit data: {response.status_code}, {response.text}")
        
        commit_data = response.json()
        files = commit_data.get("files", [])
        
        diffs = []
        for file in files:
            filename = file.get("filename", "unknown")
            patch = file.get("patch", "")
            diffs.append(f"--- {filename}\n{patch}")
        
        return "\n\n".join(diffs)

    # Example usage:
    # repo = "octocat/Hello-World"
    # commit_hash = "commit-hash"
    # token = "your-github-token" # Optional, but helpful for increased rate limits
    # diff = get_github_commit_diff(repo, commit_hash, token)
    # print(diff)


    def analyze_commit_diff(self, params={}):
        try:
            # Check if 'repo' key exists in params
            if 'repo' not in params:
                print("The 'repo' key is missing from the parameters.")
                raise ValueError("The 'repo' key is missing from the parameters.")
            
            # Check if 'commit_hash' key exists in params
            if 'commit_hash' not in params:
                print("The 'commit_hash' key is missing from the parameters.")
                raise ValueError("The 'commit_hash' key is missing from the parameters.")
            
            repo = params['repo']
            commit_hash = params['commit_hash']
            token = params.get('token', None)
            
            diff = self.get_github_commit_diff(repo, commit_hash, token)
            print(f"Loaded the commit diff for {commit_hash} in {repo}")
            print(diff)

            return [{"name": "repo", "data": repo},
                    {"name": "commit_hash", "data": commit_hash},
                    {"name": "diff", "data": diff}]
        except Exception as e:
            print(f"Error: {e}")
            raise e