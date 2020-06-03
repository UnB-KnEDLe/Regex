import re
import pandas as pd
from os import listdir
from os.path import isfile, join

class Regex:
    
    def __init__(self, text):
        self._text = text
        self._raw_acts = {}
        self._acts = []
        self._columns = []
        self.data_frame = pd.DataFrame()
    
    def find_all(self, rule, flag=0):
        return re.findall(rule, self._text, flags=flag)
    
    def find_in_act(self, rule, act):
        match = re.search(rule, act) 
        if match:
            return match.groups()
        return "nan"
    
    def _build_dataframe(self):
        if len(self._acts) > 0:
            df = pd.DataFrame(self._acts, columns=self._columns)
            #df.columns = self._columns
            return df
        return pd.DataFrame()

