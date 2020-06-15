import pandas as pd
import re
from atos.common_regex import DODF_DATE, FLEX_DATE, PAGE, SERVIDOR_NOME_COMPLETO, NOME_COMPLETO
from atos.utils import case_insensitive

class SemEfeitoAposentadoria:
    _name = "Atos Tornados sem Efeito (aposentadoria)"
    _prop_rules = {
            'dodf_num': r'',
            'dodf_data': r'',
            'dodf_pagina': r'',
            'nome': r'',
            'simbolo': r'',     # Could not find one.
            'cargo_comissao': r'',       # TODO. HARD
            'hierarquia': r'',  # ??
            'orgao': r'',        # ? Kind of hard..
            'cargo_efetivo': r'', # Have no ideia what is this
            'matricula': r'',
            'matricula_siape': r'',
            'tipo_documento': r'',
            'dodf_tipo_edicao': r'',
        }
    _raw_pattern = (
        r"TORNAR SEM EFEITO" + \
        # r"([^\n]+\n){0,10}?[^\n]*?(aposentadoria|aposentou|({})?{}|(des)?averb(ar?|ou))[\d\D]{0,500}?[.]\s" \
        r"([^\n]+\n){0,10}?[^\n]*?(tempo\sde\sservi.o|aposentadoria|aposentou|([Dd][Ee][Ss])?[Aa][Vv][Ee][Rr][Bb][Aa]..[Oo]|(des)?averb(ar?|ou))[\d\D]{0,500}?[.]\s" \
        # .format(
        #     case_insensitive("des"), case_insensitive("averbacao")
        # ) +\
        r"(?=[A-Z]{4})"
    )
    _BAD_MATCH_WORDS = [
        "AVERBAR",
        "NOMEAR",
        # "CONCEDER ABONO DE PERMANENCIA",
        "CONCEDER",
        "EXONERAR",
        "DESAVERBAR",
        "APOSTILAR",
        "RETIFICAR",
    ]

    def __init__(self,file_name, text=False):
        if not text:
            fp = open(file_name, "r")
            self._file_name = file_name
            self._text = fp.read()
            fp.close()
        else:
            self._file_name = ''
            self._text = file_name
        
        self._raw_matches = self._extract_raw_matches()
        self._processed_text = self._post_process_raw()
        self._final_matches = self._run_property_extraction()
        
        self._data_frame = self._build_dataframe()
        

    @property
    def data_frame(self):
        return self._data_frame

    @property
    def name(self):
        return self._name

    @property
    def acts_str(self):
        return self._processed_text    

    @property
    def props(self):
        return self._final_matches
    def _extract_raw_matches(self):
        """Returns list of re.Match objects found on `self._text`.

        Return:
            a list with all re.Match objects resulted from searching for
        """
        l = list(re.finditer(self._raw_pattern, self._text))
        print("DEBUG:", len(l), 'matches')
        return l


    def _post_process_raw(self):
        l = []
        for raw in self._raw_matches:
            s = raw.group()
            # Make sure words splitted accross lines are joined together
            no_split_word = s.replace('-\n', '-')
            
            # Makes easier to deal with the text.
            single_spaces = re.sub(r'\s+', r' ', no_split_word)
            
            # Sometimes more than one "TORNAR SEM EFEITO" is captured. Only the last
            # one hould matter.
            last_tornar_sem_efeito = single_spaces[single_spaces.rfind("TORNAR SEM EFEITO"):]
            l.append(last_tornar_sem_efeito)
        return l


    def _run_property_extraction(self):
        """Effectively extracts que information it was supposed to extract.
        For more details check "TCDF_requisitos" for KnEDLe project.

        Note:
            WARNING: this function tends to be very extense.
                Maybe a pipepilne-like approach would be better
                but haven't figured how to do so (yet).
        """
        # DODF date usually is easily extracted.
        dodf_dates = []
        tornado_sem_dates = []
        pages = []
        servidor_nome = []
        for tex in self._processed_text:
            # First, get DODF date.
            date_mt = re.search(DODF_DATE, tex)
            dodf_dates.append(date_mt)
            if date_mt:
                # THEN lets search for publication date (heuristic)
                span = date_mt.span()
                removed_dodf_date = '{}{}'.format(tex[:span[0]], tex[span[1]:])
                published_date = re.search(FLEX_DATE, removed_dodf_date)
                tornado_sem_dates.append(published_date)
                # ALSO, page numbers (if present) come right after DODF date
                window = tex[span[1]:][:50]
                page = re.search(PAGE, window)
                
                pages.append(page)
            else:
                tornado_sem_dates.append(None)
                pages.append(None)
            servidor = re.search(SERVIDOR_NOME_COMPLETO, tex)
            if not servidor:
                servidor = re.search(NOME_COMPLETO, tex[tex.rfind('DODF')+len('DODF'):])
            servidor_nome.append(servidor)
        return list(zip(dodf_dates, tornado_sem_dates, pages, servidor_nome))


    def _build_dataframe(self):
        return pd.DataFrame()
    
