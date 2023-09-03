import requests
import yaml

def check_session():
    with open('config.yaml', 'r') as yaml_file:
        data = yaml.safe_load(yaml_file)
    
    SESSION_ID = data['user_data']['session_id']
    if SESSION_ID == '': # or the id is not valid!
        SESSION_ID = input("Please provide the SESSION_ID: ")
        data['user_data']['session_id'] = SESSION_ID
        with open('config.yaml', 'w') as yaml_file:
            yaml.dump(data, yaml_file, default_flow_style=False)
    return True

""" The main configuration class for the connection to GraphQL API.
    Contains the cookies and headers for the connection.
    
    session_id can be found in the web browser cookies of https://leetcode.com/
    
    The default session_id is taken from the configuration file. 
    """
    

class Configuration():
    def __init__(self, session_id: str = ''):
        self.host = 'https://leetcode.com/'
        if session_id:
            self.session_id = session_id
        else:
            self.load_config()
        
        self._csrf_cookie: str = self.csrf_cookie
        
        self._headers: dict = {'x-csrftoken': self._csrf_cookie,
                               'Referer': self.host}
        self._cookies: dict = {'csrftoken': self._csrf_cookie,
                               'LEETCODE_SESSION': self.session_id}       
    
    @property
    def csrf_cookie(self) -> str:
        response = requests.get(url=self.host,
                                cookies={"LEETCODE_SESSION": self.session_id})
        return response.cookies["csrftoken"]
    
    @csrf_cookie.setter
    def csrf_cookie(self, value: str):
        self._csrf_cookie = value
        
    @property
    def headers(self) -> dict:
        return self._headers
    
    @property
    def cookies(self) -> dict:
        return self._cookies
    
    def load_config(self):
        with open('config.yaml', 'r') as yaml_file:
            data = yaml.safe_load(yaml_file)
        
        self.session_id = data['user_data']['session_id']
        