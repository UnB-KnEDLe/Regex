from base import Regex

class NomeacaoComissionados(Regex):
    
    def __init__(self,text):
        super().__init__(text)
        self._columns = ['nome','cargo_efetivo','matricula','siape','simbolo','cargo_comissao','lotacao','orgao']
        self.rules = {
            "nome": r"(^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
            "cargo_efetivo": r"",
            "matricula": r"matr[í|i]cula\s?n?o?\s([\s\S]*?)[,|\s]",
            "siape": r"[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]",
            "simbolo": r"[S|s][í|i]mbolo\s?n?o?\s([\s\S]*?)[,|\s]",
            "cargo_comissao": "",
            "lotacao": "",
            "orgao": ""
        }
        self._raw_acts = self._extract_instances()
        self._acts = self._acts_props()
        self.data_frame = self._build_dataframe()
        
        
    
    def _act_props(self, act_raw):
        act = {}
        for key in self.rules:
            try:
                act[key], = self.find_in_act(self.rules[key], act_raw)
            except:
                act[key] = "nan"
        return act
    
    def _acts_props(self):
        acts = []
        for raw in self._raw_acts:
            act = self._act_props(raw)
            acts.append(act)
        return acts        
        
    def _extract_instances(self):
        start = r"(NOMEAR)"
        body = r"([\s\S]*?)"
        end = "\."
        rule = start + body + end
        found = self.find_all(rule)
        results = []
        for instance in found:
            start, body = instance
            results.append(body)
            
        return results