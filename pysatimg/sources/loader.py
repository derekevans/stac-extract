
import os
import yaml


class SourceLoader:
    
    def __init__(self, source_name):
        self.source_name = source_name

    def load(self):
      config_path = f'{os.path.dirname(__file__)}/configs/{self.source_name}.yml'
      with open(config_path, 'r') as f:
          return yaml.safe_load(f)