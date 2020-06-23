import pandas as pd
import re


DODF = r"(DODF|[Dd]i.rio\s+[Oo]ficial\s+[Dd]o\s+[Dd]istrito\s+[Ff]ederal)"
_EDICAO_DODF = r"(\b(?i:suplement(o|ar)|extra|.ntegra))\b."
TIPO_EDICAO = r"\b(?P<tipo>(?i:extra(\sespecial)?|suplement(ar|o)))\b"
DODF_TIPO_EDICAO = DODF + r"(?P<tipo_edicao>.{0,50}?)" + _EDICAO_DODF

MONTHS = (
    r'(?i:janeiro|fevereiro|mar.o|abril|maio|junho|' \
    r'julho|agosto|setembro|outubro|novembro|dezembro)'
)

FLEX_DATE = r"(?P<date>\d+\s+(?:de\s*)?" + MONTHS + "\s*(?:de\s*)?\d+|\d+[.]\d+[.]\d+|\d+[/]\d+[/]\d+)"

DODF_NUM = r"(?i:DODF|[Dd]i.rio [Oo]ficial [Dd]o [Dd]istrito [Ff]ederal)\s*[\w\W]{0,3}?(?i:n?(.mero|[.roº]{1,4})?[^\d]+?)(?P<num>\d+)"

DODF_DATE = DODF + r"[^\n\n]{0,50}?(de\s?)?" + FLEX_DATE

SIAPE = r"(?i:siape)\s*(?i:n?.?)\s*[-\d.Xx/\s]"

MATRICULA = r"(?i:matr.cul.|matr?[.]?\B)[^\d]+(?P<matricula>[-\d.XxZzYz/\s]+)"

MATRICULA_GENERICO = r"(?<![^\s])(?P<matricula>([-\d.XxZzYz/\s]{1,})[.-][\dXxYy][^\d])"

MATRICULA_ENTRE_VIRGULAS = r"(?<=[A-ZÀ-Ž]{3})\s*,\s+([-\d.XxZzYz/\s]{3,}?),"

PAGE = r"((?i:p\.|p.ginas?|p.?gs?\.?\b)(?P<page_nums>.{0,}?)(?=[,;:]|\n|\s[A-Z]|$))"

SERVIDOR_NOME_COMPLETO = r"(?i:servidora?\b.{0,40}?)(?P<name>[A-ZÀ-Ž][.'A-ZÀ-Ž\s]{7,})"

NOME_COMPLETO = r"(?P<name>[.'A-ZÀ-Ž\s]{8,})"


LOWER_LETTER = r"[áàâäéèẽëíìîïóòôöúùûüça-z]"
UPPER_LETTER = r"[ÁÀÂÄÉÈẼËÍÌÎÏÓÒÔÖÚÙÛÜÇA-Z]"

PROCESSO_MATCH = r"(?i:processo):?[^\d]{0,50}?(?P<processo>\d[-0-9./\s]*\d(?!\d))"
TIPO_DOCUMENTO = r"(?i:portaria|ordem de servi.o|instru..o)"

class SemEfeitoAposentadoria:
    _name = "Atos Tornados sem Efeito (aposentadoria)"

    _raw_pattern = (
        r"TORNAR SEM EFEITO" + \
        r"([^\n]+\n){0,10}?[^\n]*?(tempo\sde\sservi.o|aposentadoria|aposentou|([Dd][Ee][Ss])?[Aa][Vv][Ee][Rr][Bb][Aa]..[Oo]|(des)?averb(ar?|ou))[\d\D]{0,500}?[.]\s" \
        r"(?=[A-Z]{4})"
    )

    _BAD_MATCH_WORDS = [
        "AVERBAR",
        "NOMEAR",
        "CONCEDER",
        "EXONERAR",
        "DESAVERBAR",
        "APOSTILAR",
        "RETIFICAR",
    ]

    def __init__(self,file_name, text=False, nlp=None, debug=False):
        self._debug = debug
        self.nlp = nlp
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


    def _extract_raw_matches(self):
        """Returns list of re.Match objects found on `self._text`.

        Return:
            a list with all re.Match objects resulted from searching for
        """
        l = list(re.finditer(self._raw_pattern, self._text))
        if self._debug:
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
        tipo_lis = []
        processo_lis = []
        dodf_dates = []
        dodf_num = []
        tornado_sem_dates = []
        pages = []
        servidor_nome = []
        servidor_matricula = []
        cargo_efetivo_lis = []
        edicoes = []
        for tex in self._processed_text:
            tipo = re.search(TIPO_DOCUMENTO, tex)
            processo = re.search(PROCESSO_MATCH, tex)
            dodf_date = re.search(DODF_DATE, tex)
            num = dodf_date and re.search(DODF_NUM, dodf_date.group())         
            published_date = dodf_date and \
                re.search(FLEX_DATE, tex[:dodf_date.start()] + tex[dodf_date.end():])
            page = dodf_date and re.search(PAGE, tex[dodf_date.end():][:50])
            servidor = re.search(SERVIDOR_NOME_COMPLETO, tex)

            if not servidor:
                #  If it fails then a more generic regex is searched for
                dodf_mt = re.search(DODF, tex)
                dodf_end = 0 if not dodf_mt else dodf_mt.end()
                servidor = re.search(NOME_COMPLETO, tex[dodf_end:])
                del dodf_mt, dodf_end
                if not servidor:
                    # Appeal to spacy
                    all_cands = re.findall(NOME_COMPLETO, tex)
                    cand_text = 'SEM-SERVIDOR'
                    for cand in self.nlp(', '.join([c.strip().title() for c in all_cands])).ents:
                        cand_text = cand.text                
                        if cand.label_ == 'PER':
                            break
                    servidor =  re.search(cand_text.upper(), tex)
                    del all_cands, cand_text, cand
            end_employee = servidor.end() if servidor else 0
            matricula = re.search(MATRICULA, tex[end_employee:]) or \
                        re.search(MATRICULA_GENERICO, tex[end_employee:]) or \
                        re.search(MATRICULA_ENTRE_VIRGULAS, tex[end_employee:] ) 
            del end_employee

            if not matricula or not servidor:
                cargo = None
            else:
                servidor_start = tex[servidor.start():].find(servidor.group()) + servidor.start()
                matricula_start = tex[matricula.start():].find(matricula.group()) + matricula.start()

                # NOTE: -1 is important in case `matricula` end with `,`
                if 0 <= (matricula_start - (servidor_start + len(servidor.group()))) <= 5:
                    # cargo does not fit between 'servidor' e 'matricula'
                    cargo = re.search(r",(?P<cargo>[^,]+)", tex[ matricula_start + len(matricula.group())-1: ])        
                else:
                    # cargo right after employee's name                    
                    cargo = re.search(r",(?P<cargo>[^,]+)", tex[servidor_start + len(servidor.group())-1:])
                del matricula_start, servidor_start
            edicao = re.search(DODF_TIPO_EDICAO, tex)
            edicao = re.search(TIPO_EDICAO, tex[edicao.start()-1:edicao.end()+1]) if edicao \
                        else re.search("normal", "normal")

            tipo_lis.append(tipo)
            processo_lis.append(processo)
            dodf_dates.append(dodf_date)            
            dodf_num.append(num)
            tornado_sem_dates.append(published_date)
            pages.append(page)
            servidor_nome.append(servidor)
            servidor_matricula.append(matricula)
            cargo_efetivo_lis.append(cargo)
            edicoes.append(edicao)

        l = list(zip(
            tipo_lis,
            processo_lis,
            dodf_dates,
            dodf_num,
            tornado_sem_dates,
            pages,
            servidor_nome,
            servidor_matricula,
            cargo_efetivo_lis,
            edicoes
        ))
        if len(l) != len(self._processed_text):
            raise Exception("Processed matches and list of attributes differ! {} vs {}".format(
                len(self._processed_text), len(l)
            ))
        return l


    def _build_dataframe(self):
        def by_group_name(match):
            if match:
                keys = list(match.groupdict().keys())
                if len(keys) == 0:
                    return match.group()
                elif len(keys) > 1:
                    raise ValueError("Named regex must have AT MOST ONE NAMED GROUP.")
                if self._debug:
                    print('key: ', keys[0])
                return match.group(keys[0])
            else:
                return "nan"
        return pd.DataFrame(
            data=map(lambda lis: [by_group_name(i) for i in lis],self._final_matches),
            columns=[
                'tipo',
                'processo',
                'dodf_data',
                'dodf_num',
                'tse_data',
                'pag',
                'nome',
                'matricula',
                'cargo_efetivo',
                'tipo_edicao'
            ]
        )
    

