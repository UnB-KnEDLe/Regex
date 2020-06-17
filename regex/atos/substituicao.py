import re
from atos.base import Atos

class Substituicao(Atos):
    
    def __init__(self, text):
        super().__init__(text)

    def _regex_flags(self):
        return re.IGNORECASE

    def _act_name(self):
        return "Substituição de Funções"

    def _props_names(self):
        return ["Tipo do Ato", "Nome do Servidor Substituto", "Matrícula do Servidor Substituto", 
                "Nome do Servidor a ser Substituido", "Matrícula do Servidor a ser Substituido"
                "Cargo", "Símbolo do cargo do servidor substituto",
                "Cargo comissionado objeto da substituição",
                "Símbolo do cargo comissionado objeto da substituição",
                "Hierarquia da Lotação", "Órgão", "Data Inicial da Vigência", 
                "Data Final de Vigência", "Matrícula SIAPE", "Motivo"]
        
        
    def _rule_for_inst(self):
        start = r"(DESIGNAR)"
        body = r"([\s\S]*?)"
        end = r"\.\s"
        return start + body + end
    
    def _prop_rules(self):
        rules = {"Nome Serv Substituto": r"(^[A-ZÀ-Ž\s]+[A-ZÀ-Ž])",
                 "Matricula Serv Substituto": "",
                 "Nome do Servidor a ser Substituido": "",
                 "Matrícula do Servidor a ser Substituido": "",
                 "cargo": "Cargo\s[d|D]?[e|E]?\s([\s\S]*?),",
                 "Símbolo do cargo do servidor substituto": "",
                 "Cargo comissionado objeto da substituição": "",
                 "Hierarquia da Lotação": "",
                 "orgao": "Lotacao: ([\s\S]*?)[.]",
                 "Data Inicial da Vigência": "",
                 "Data Final de Vigência": "",
                 "siape": "[S|s][I|i][A|a][P|p][E|e]\s[N|n]?[o|O]?\s([\s\S]*?)[,| | .]",
                 "Motivo": "" }
        return rules