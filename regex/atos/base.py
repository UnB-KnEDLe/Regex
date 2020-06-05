import re
import pandas as pd
import utils

class Regex:
    
    def __init__(self, files_path):
        # self._text = text
        self._files = utils.get_txts(files_path)
        self._raw_acts = {}
        self._acts = []
        self._columns = []
        self.data_frame = pd.DataFrame()

#     dodfs_space_dir = "../data/dodfs_txt_espaco"
# dodfs_space_files = get_txts(dodfs_space_dir)

# dodfs_n_dir = "../data/dodfs_txt_barra_n"
# dodfs_n_files = get_txts(dodfs_n_dir)

# output = "./results"

    def files():
        for txt in files_path:
            txt_str = open(txt, "r").read()

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
            df.columns = self._columns
            return df
        return pd.DataFrame()

