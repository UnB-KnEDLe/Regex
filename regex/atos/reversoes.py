class Revertions(Regex):

    def __init__(self, text):
        super().__init__(text)
        self._columns = ["Tipo do Ato", "SEI", "Nome", "Matrícula", "Cargo", "Classe",
               "Padrao", "Quadro", "Fundamento Legal", "Orgao", "Vigencia", "Matricula SIAPE"]
        
        self.rules = {"nome": "\s([^,]*?),\smatricula",
                      "matricula":"matricula\s?n?o?\s([\s\S]*?)[,| ]",
                      "cargo": "[C|c]argo\s[d|D]?[e|E]?\s([\s\S]*?),",
                      "classe": "[C|c]lasse\s([\s\S]*?),",
                      "padrao": "[p|P]adr[a|ã]o\s([\s\S]*?),",
                      "quadro": "d?[e|a|o]?(Quadro[\s\S]*?)[,|;|.]",
                      "fundamento": "nos\stermos\sdo\s([\s\S]*?),\sa?\s",
                      "orgao": "Lotacao: ([\s\S]*?)[.]",
                      "vigencia": "",
                      "siape": ""}
                      
        self._raw_acts = self._extract_instances()   
        self._acts = self._acts_props()
        self.data_frame = self._build_dataframe()
        
        
    
    def _act_props(self, sei, act_raw):
        act = {}
        act["tipo_ato"] = "Reversão"
        act["sei"] = sei
        for key in self.rules:
            try:
                act[key], = self.find_in_act(self.rules[key], act_raw)
            except:
                act[key] = "nan"
        return act
    
    def _acts_props(self):
        acts = []
        for sei, raw in self._raw_acts.items():
            act = self._act_props(sei, raw)
            acts.append(act)
        return acts        
        
    
    def _extract_instances(self):
        start = "(reverter\sa\satividade),?\s?"
        body = "([\s\S]*?)"
        end = "[P|p]rocesso:?\s[s|S]?[e|E]?[i|I]?\s?[n|N]?[o|O]?\s?([\s\S]*?)[.]\s"
        end2 = "Processo\sde\sReversao:?\sn?\s?([\s\S]*?)[.]\s"
        end3 = "Processo\sde\sReversao\sSigiloso:?\s([\s\S]*?)[.]\s"
        end4 = "Processo\sde\sReversao\sPGDF\sSEI:?\s([\s\S]*?)[.]\s"
        rule = start + body + end
        found = self.find_all(rule, re.IGNORECASE)
        results = {}
        for instance in found:
            start, body, sei = instance
            results[sei] = body
        return results
