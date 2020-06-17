import pandas as pd
import re

def case_insensitive(s: str):
    """Returns regular expression similar to `s` but case careless.

    Note: strings containing characters set, as `[ab]` will be transformed to `[[Aa][Bb]]`.
        `s` is espected to NOT contain situations like that.
    Args:
        s: the stringregular expression string to be transformed into case careless
    Returns:
        the new case-insensitive string 
    """

    return ''.join([c if not c.isalpha() else '[{}{}]'.format(c.upper(), c.lower()) for c in s])


def remove_crossed_words(s: str):
    """Any hífen followed by 1+ spaces are removed.
    """
    return re.sub(r'-\s+', '', s)


DODF = r"(DODF|[Dd]i.rio\s+[Oo]ficial\s+[Dd]o\s+[Dd]istrito\s+[Ff]ederal)"

MONTHS_LOWER = (
    r'(janeiro|fevereiro|mar.o|abril|maio|junho|' \
    r'julho|agosto|setembro|outubro|novembro|dezembro)'
)

FLEX_DATE = r"(?P<date>\d+\s+(?:de\s*)?{}\s*(?:de\s*)?\d+|\d+[.]\d+[.]\d+|\d+[/]\d+[/]\d+)".format(case_insensitive(MONTHS_LOWER))

DODF_NUM = r"(DODF|[Dd]i.rio [Oo]ficial [Dd]o [Dd]istrito [Ff]ederal)\s*(n?r?o?[^\d]?)(?P<num>\d+)"
DODF_DATE = r"{}[^\n\n]{{0,50}}?(de\s?)?{}".format(DODF, FLEX_DATE)

SIAPE = r"{}\s*(?:n?.?)\s*[-\d.Xx/\s]+".format(case_insensitive("siape"))

MATRICULA = r"(?:matr.cul.|matr?[.]?\B)[^\d]+([-\d.XxZzYz/\s]+)"

MATRICULA_GENERICO = r"(?<![^\s])(?P<matricula>([-\d.XxZzYz/\s]{1,})[.-][\dXxYy][^\d])"

MATRICULA_ENTRE_VIRGULAS = r"(?<=[A-Z]{3})\s*,\s+([-\d.XxZzYz/\s]{3,}?),"

# WARNING: "page_nums" may match not only nums.
# TODO: deal with edge cases like "p 33". There are only a few ones.
PAGE = r"((?:p\.|p.ginas?|p.?gs?\.?\b)(?P<page_nums>.{0,}?)(?=[,;:]|\n|\s[A-Z]|$))"

SERVIDOR_NOME_COMPLETO = r"servidora?\b.{0,40}?(?P<name>[A-ZÀ-Ž][.'A-ZÀ-Ž\s]{7,})"

NOME_COMPLETO = r"(?P<name>['A-ZÀ-Ž][.'A-ZÀ-Ž\s]{6,}[,.:;])"

EDICAO_DODF = r"(?P<edition>[Ss]uplement(o|ar)|[Ee]xtra|.ntegra)"

PROCESSO = r"(?P<processo>[-0-9/.]+)"

LOWER_LETTER = r"[áàâäéèẽëíìîïóòôöúùûüça-z]"
UPPER_LETTER = r"[ÁÀÂÄÉÈẼËÍÌÎÏÓÒÔÖÚÙÛÜÇA-Z]"

class Cessoes:
    _name = "Cessoes"

    _raw_pattern = (
        # r"([Pp][Rr][Oo][Cc][Ee][Ss][Ss][Oo][^0-9]{0, 12})([^\n]+\n){0,2}[^\n]*[Aa]\s*[Ss]\s*[Ss]\s*[Uu]\s*[Nn]\s*[Tt]\s*[Oo]\s*:?\s?\bCESS.O\b([^\n]*\n){0,}?[^\n]*?(?=(?P<look_ahead>PROCESSO|Processo:|PUBLICAR|pertinentes[.]|autoridade cedente))"
        # r"([Pp][Rr][Oo][Cc][Ee][Ss][Ss][Oo][^0-9]{0, 12})([^\n]+\n){0,2}[^\n]*[Aa]\s*[Ss]\s*[Ss]\s*[Uu]\s*[Nn]\s*[Tt]\s*[Oo]\s*:?\s?\bCESS.O\b([^\n]*\n){0,}?[^\n]*?(?=(?P<look_ahead>PROCESSO|Processo:|PUBLICAR|pertinentes[.]|autoridade cedente))"
        r"([Pp][Rr][Oo][Cc][Ee][Ss][Ss][Oo][^0-9]{0,12})([^\n]+?\n){0,2}?[^\n]*?[Aa]\s*[Ss]\s*[Ss]\s*[Uu]\s*[Nn]\s*[Tt]\s*[Oo]\s*:?\s?\bCESS.O\b([^\n]*\n){0,}?[^\n]*?(?=(?P<look_ahead>PROCESSO|Processo:|PUBLICAR|pertinentes[.]|autoridade cedente))"
    )

    def __init__(self,file_name, text=False, debug=False):
        self._debug = debug
        if not text:
            fp = open(file_name, "r")
            self._file_name = file_name
            self._text = fp.read()
            self._no_crosswords = remove_crossed_words(self._text)
            fp.close()
        else:
            self._file_name = ''
            self._text = file_name
        
        self._raw_matches = self._extract_raw_matches()
        self._processed_text = self._post_process_raw()
        self._final_matches = self._run_property_extraction()
        
        self._data_frame = self._build_dataframe()


    @classmethod
    def _self_match(cls, s:str, group_name: str):
        return re.match(fr'(?P<{group_name}>{s})', s)


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
        l = list(re.finditer(self._raw_pattern, self._no_crosswords))
        print("DEBUG:", len(l), 'matches')
        return l


    def _post_process_raw(self):
        l = []
        for raw in self._raw_matches:
            s = raw.group()
            single_spaces = re.sub(r'\s+', r' ', s)            
            l.append(single_spaces)
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
        servidor_nome = []
        servidor_matricula = []
        processo_lis = []
        onus_lis = []
        siape_lis = []
        # orgao_cessionario = [] # HARD
        for idx, tex in enumerate(self._raw_matches):
            # First, get DODF date.
            print('IDX:', idx)
            processo = re.search(r"{}{}".format(
                    tex.group(1) , PROCESSO
                ), tex.group())
            nome = re.search(
                r"{}:\s*({})".format(
                    case_insensitive("interessad."),
                    NOME_COMPLETO
                ), tex.group())
            matricula = re.search(MATRICULA, tex.group())
            if not matricula:
                matricula = re.search(MATRICULA_GENERICO, tex)
                if not matricula:
                    matricula = re.search(MATRICULA_ENTRE_VIRGULAS, tex)
            onus = re.search(r"\b[oô]nus\b.+?[.]", tex.group(), re.DOTALL)
            siape = re.search(SIAPE, tex.group())

            processo_lis.append(processo)
            servidor_nome.append(nome)
            servidor_matricula.append(matricula)
            onus_lis.append(onus)
            siape_lis.append(siape)
        if self._debug:
            print(
                "servidor_nome:", len(servidor_nome), '\n',
                "servidor_matricula:", len(servidor_matricula), '\n',
                "processo_lis:", len(processo_lis), '\n',
                "onus_lis:", len(onus_lis), '\n',
            )
        l = list(zip(            
            servidor_nome,
            servidor_matricula,
            processo_lis,
            onus_lis,
            siape_lis,
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
                print('key: ', keys[0])
                return match.group(keys[0])
            else:
                return "nan"
        return pd.DataFrame(
            data=map(lambda lis: [by_group_name(i) for i in lis],self._final_matches),
            columns=[
                'nome',
                'matricula',
                'processo',
                'onus',
                'siape',
            ]
        )
    

