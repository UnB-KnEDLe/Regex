import re
from typing import List, Match
import pandas as pd
from atos.base import Atos

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

SIAPE = r"{}\s*(?:n?.?)\s*(?P<siape>[-\d.Xx/\s]+)".format(case_insensitive("siape"))

MATRICULA = r"(?:matr.cul.|matr?[.]?\B)[^\d]+(?P<matricula>[-\d.XxZzYz/\s]+)"
MATRICULA_GENERICO = r"(?<![^\s])(?P<matricula>([-\d.XxZzYz/\s]{1,})[.-][\dXxYy][^\d])"
MATRICULA_ENTRE_VIRGULAS = r"(?<=[A-Z]{3})\s*,\s+(?P<matricula>[-\d.XxZzYz/\s]{3,}?),"

# WARNING: "page_nums" may match not only nums.
# TODO: deal with edge cases like "p 33". There are only a few ones.
PAGE = r"((?:p\.|p.ginas?|p.?gs?\.?\b)(?P<page_nums>.{0,}?)(?=[,;:]|\n|\s[A-Z]|$))"

SERVIDOR_NOME_COMPLETO = r"(servidor.?|empregad.)[^A-ZÀ-Ž]{0,40}(?P<name>[A-ZÀ-Ž][.'A-ZÀ-Ž\s]{6,}(?=[,]))"

NOME_COMPLETO = r"(?P<name>['A-ZÀ-Ž][.'A-ZÀ-Ž\s]{6,}(?=[,.:;]))"

EDICAO_DODF = r"(?P<edition>[Ss]uplement(o|ar)|[Ee]xtra|.ntegra)"

PROCESSO_NUM = r"(?P<processo>[-0-9/.]+)"
INTERESSADO = r"{}:\s*{}".format(case_insensitive("interessad."), NOME_COMPLETO)
ONUS = r"(?P<onus>\b[oôOÔ]{}\b[^.]+[.])".format(case_insensitive("nus"))

LOWER_LETTER = r"[áàâäéèẽëíìîïóòôöúùûüça-z]"
UPPER_LETTER = r"[ÁÀÂÄÉÈẼËÍÌÎÏÓÒÔÖÚÙÛÜÇA-Z]"

class Cessoes(Atos):
    _special_acts = ['matricula', 'cargo']
    def __init__(self, file, debug=False, extra_search = True):
        self._debug = debug
        self._extra_search = True
        self._processed_text = remove_crossed_words(open(file).read())
        self._raw_matches = []
        super().__init__(file)


    @classmethod
    def _self_match(cls, s:str, group_name: str):
        return re.match(fr'(?P<{group_name}>{s})', s)

    def _act_name(self):
        return "Cessoes"


    def _props_names(self):
        return list(self._prop_rules())

    def _rule_for_inst(self):
        return (
            r"([Pp][Rr][Oo][Cc][Ee][Ss][Ss][Oo][^0-9/]{0,12})([^\n]+?\n){0,2}?"\
            + r"[^\n]*?[Aa]\s*[Ss]\s*[Ss]\s*[Uu]\s*[Nn]\s*[Tt]\s*[Oo]\s*:?\s*\bCESS.O\b"\
            + r"([^\n]*\n){0,}?[^\n]*?(?=(?P<look_ahead>PROCESSO|Processo:|PUBLICAR|pertinentes[.]|autoridade cedente|"\
            + case_insensitive('publique-se') + "))"
        )


    def _prop_rules(self):
        return {
            'interessado': INTERESSADO,
            'nome': SERVIDOR_NOME_COMPLETO,
            'matricula': MATRICULA,
            'processo': r"[^0-9]+?{}".format(PROCESSO_NUM),
            'onus': ONUS,
            'siape': SIAPE,
            'cargo': r",(?P<cargo>[^,]+)",
        }


    @property
    def data_frame(self):
        return self._data_frame

    @property
    def name(self):
        return self._name


    @property
    def acts_str(self):
        return self._acts_str


    def _find_instances(self) -> List[Match]:
        """Returns list of re.Match objects found on `self._text_no_crosswords`.

        Return:
            a list with all re.Match objects resulted from searching for
        """
        text = remove_crossed_words( self._text )
        self._raw_matches = list(
            re.finditer(self._inst_rule, text, flags=self._flags)
        )
        l = [i.group() for i in self._raw_matches]
        if self._debug:
            print("DEBUG:", len(l), 'matches')
        return l


    def _get_special_acts(self, lis_matches):
        for i, match in enumerate(self._raw_matches):
            act = match.group()
            matricula = re.search(MATRICULA, act) or \
                    re.search(MATRICULA_GENERICO, act) or \
                    re.search(MATRICULA_ENTRE_VIRGULAS, act)
            
            nome = re.search(self._rules['nome'], act)
            if matricula and nome:
                offset = matricula.end()-1 if 0 <= (matricula.start() - nome.end()) <= 5 \
                            else nome.end() - 1
                cargo, = self._find_props(r",(?P<cargo>[^,]+)", act[offset:])
            else:
                cargo = "nan"
            
            lis_matches[i]['matricula'] = matricula.group('matricula') if matricula \
                                        else "nan"
            lis_matches[i]['cargo'] = cargo


    def _find_props(self, rule, act):
        """Returns named group, or the whole match if no named groups
                are present on the match.
        Args:
            match: a re.Match object
        Returns: content of the unique named group found at match,
            the whole match if there are no groups at all or raise
            an exception if there are more than two groups.
        """
        match = re.search(rule, act, flags=self._flags)
        
        if match:
            keys = list(match.groupdict().keys())
            if len(keys) == 0:
                return match.group()
            elif len(keys) > 1:
                raise ValueError("Named regex must have AT MOST ONE NAMED GROUP.")
            if self._debug:
                print('key: ', keys[0])
            return match.group(keys[0]),
        else:
            return "nan"


    def _acts_props(self):
        acts = []
        for raw in self._raw_acts:
            act = self._act_props(raw)
            acts.append(act)
        if self._extra_search:
            self._get_special_acts(acts)
        return acts      


    def _extract_instances(self) -> List[Match]:
        found = self._find_instances()
        self._acts_str = found.copy()
        return found


    def _run_property_extraction(self):
        """Effectively extracts que information it was supposed to extract.
        For more details check "TCDF_requisitos" for KnEDLe project.

        Note:
            WARNING: this function tends to be very extense.
                Maybe a pipepilne-like approach would be better
                but haven't figured how to do so (yet).
        """
        # DODF date usually is easily extracted.
        interessado_nome = []
        servidor_nome = []
        servidor_matricula = []
        cargo_efetivo_lis = []
        processo_lis = []
        onus_lis = []
        siape_lis = []
        # orgao_cessionario = [] # HARD
        for idx, tex in enumerate(self._raw_acts):
            interessado = re.search(INTERESSADO, tex.group())
            nome = re.search(SERVIDOR_NOME_COMPLETO, tex.group())
            matricula = re.search(MATRICULA, tex.group()) or \
                        re.search(MATRICULA_GENERICO, tex.group()) or \
                        re.search(MATRICULA_ENTRE_VIRGULAS, tex.group())
            processo = re.search(r"[^0-9]+?{}".format(PROCESSO_NUM), tex.group())
            onus = re.search(ONUS, tex.group())
            siape = re.search(SIAPE, tex.group())
        
            if not matricula or not nome:
                cargo = None
            else:
                # TODO: improve robustness: cargo_efetivo is assumed to be either right after 
                # employee name or its matricula
                if 0 <= (matricula.start() - nome.end()) <= 5:
                    # cargo NAO CABE entre 'servidor' e 'matricula'
                    print("CARGO DEPOIS DE MATRICULA em",
                            str(self._file_name).split('/')[-1])
                    cargo = re.search(r",(?P<cargo>[^,]+)", tex.group()[ matricula.end()-1: ])        
                else:
                    # cargo apohs nome do servidor
                    print("CARGO ANTES DE MATRICULA em",
                            str(self._file_name).split('/')[-1])
                    cargo = re.search(r",(?P<cargo>[^,]+)", tex.group()[nome.end()-1:])

            interessado_nome.append(interessado)
            servidor_nome.append(nome)
            servidor_matricula.append(matricula)
            cargo_efetivo_lis.append(cargo)
            processo_lis.append(processo)
            onus_lis.append(onus)
            siape_lis.append(siape)
        if self._debug:
            print(
                "interessado_nome:", len(interessado_nome), '\n',
                "servidor_nome:", len(servidor_nome), '\n',
                "servidor_matricula:", len(servidor_matricula), '\n',
                "cargo_efetivo_lis:", len(cargo_efetivo_lis), '\n',
                "processo_lis:", len(processo_lis), '\n',
                "onus_lis:", len(onus_lis), '\n',
                "siape_lis:", len(siape_lis), '\n',
            )
        l = list(zip(
            interessado_nome,
            servidor_nome,
            servidor_matricula,
            cargo_efetivo_lis,
            processo_lis,
            onus_lis,
            siape_lis,
        ))
        if len(l) != len(self._raw_matches):
            raise Exception("Processed matches and list of attributes differ! {} vs {}".format(
                len(self._raw_matches), len(l)
            ))
        return l

    def _build_dataframe(self):
        return pd.DataFrame(self._acts)

