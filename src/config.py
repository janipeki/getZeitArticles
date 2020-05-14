import os
import json

# Read json file
def python_json_file_to_dict(file_path):
    try:
        # Get json file 
        file_object = open(file_path, 'r')
        # Load JSON file data to a python dict object.
        dict_object = json.load(file_object)

        return dict_object
    except FileNotFoundError:
        print(file_path + " not found. ")
        return None




# Read my own configuration
class Config: 
    config_file = ""
    def __init__(self, config_file = config_file): 
        self._config = {}
        config = python_json_file_to_dict(config_file)
#         print (str(config))
        self._config['url'] = config.get('url')
        self._config['target'] = config.get('target')
        self._config['revalid'] = config.get('revalid')
        self._config['reinvalid'] = config.get('reinvalid')
        self._config['storagetype'] = config.get('storagetype')
        self._config['storage'] = config.get('storage') + '/'

       
    # using property decorator 
    # a getter function 
    @property
    def config(self): 
        return self._config 
      
    @property
    def url(self): 
        return self._config['url']
      
    @property
    def target(self): 
        return self._config['target']
      
    @property
    def revalid(self): 
        return self._config['revalid']
      
    @property
    def reinvalid(self): 
        return self._config['reinvalid']
      
    @property
    def storagetype(self): 
        return self._config['storagetype']
      
    @property
    def storage(self): 
        return self._config['storage']
      
    # a setter function 
#     @config.setter 
#     def url(self, url): 
#         if(url == ""): 
#            raise ValueError("URL may not be empty") 
#         self._config.append(url)
      
