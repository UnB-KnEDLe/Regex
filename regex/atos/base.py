import re
import pandas as pd
import utils

class Regex:
    
    def __init__(self, text):
        self._text = text
        self._raw_acts = {}
        self._acts = []
        self._columns = []
        self.data_frame = pd.DataFrame()

    # ex find_all
    def _find_instances(self, rule, flag=0):
        return re.findall(rule, self._text, flags=flag)
    
    def _extract_instances(self, text):
        pass
    
    # ex find_in_act
    def find_props(self, rule, act):
        match = re.search(rule, act) 
        if match:
            return match.groups()
        return "nan"
    
    def _acts_props(self):
        pass

    def _act_props(self, sei, act_raw):
        pass


    def _build_dataframe(self):
        if len(self._acts) > 0:
            df = pd.DataFrame(self._acts, columns=self._columns)
            df.columns = self._columns
            return df
        return pd.DataFrame()




