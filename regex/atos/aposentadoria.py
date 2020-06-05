from atos.base import Regex

class Retirements(Regex):
    
    def __init__(self, text):
        super().__init__(text)
        self._columns = ["Tipo do Ato", "SEI", "Nome", "Matrícula", "Tipo de Aposentadoria", "Cargo", "Classe",
               "Padrao", "Quadro", "Fundamento Legal", "Orgao", "Vigencia", "Matricula SIAPE"]
        
        self.rules = {"nome": "\s([^,]*?),\smatricula",
                      "matricula":"matricula\s?n?o?\s([\s\S]*?)[,|\s]",
                      "tipo_ret": "",
                      "cargo": "Cargo\s[d|D]?[e|E]?\s([\s\S]*?),",
                      "classe": "[C|c]lasse\s([\s\S]*?),",
                      "padrao": "[p|P]adr[a|ã]o\s([\s\S]*?),",
                      "quadro": "d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                      "fundamento": "nos\stermos\sdo\s([\s\S]*?),\sa?\s",
                      "orgao": "Lotacao: ([\s\S]*?)[.]",
                      "vigencia": "",
                      "siape": "[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]"}
        
        self._raw_acts = self._extract_instances(text)   
        self._acts = self._acts_props()
        data_frame = self._build_dataframe()

    def _act_props(self, sei):
        act = {}
        act["tipo_ato"] = "Aposentadoria"
        act["sei"] = sei
        for key in self.rules:
            try:
                act[key], = self.find_in_act(self.rules[key], self._raw_acts)
            except:
                act[key] = "nan"

        return act
    
    def _acts_props(self, raw_acts):
        acts = []
        for sei, raw in raw_acts.items():
            act = self._act_props(sei, raw)
            acts.append(act)
        return acts        
        
    def _extract_instances(self, text):
        start = "(APOSENTAR|CONCEDER\sAPOSENTADORIA),?\s?"
        body = "([\s\S]*?)"
        end = "[P|p]rocesso:?\s[s|S]?[e|E]?[i|I]?\s?[n|N]?[o|O]?\s?([\s\S]*?)[.]\s"
        rule = start + body + end
        found = self.find_all(rule, text)
        results = {}
        for instance in found:
            start, body, sei = instance
            results[sei] = body
            
        return results