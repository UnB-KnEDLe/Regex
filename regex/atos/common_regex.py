from atos.utils import case_insensitive

_DODF = r"(DODF|[Dd]i.rio\s+[Oo]ficial\s+[Dd]o\s+[Dd]istrito\s+[Ff]ederal)"

MONTHS_LOWER = (
    r'(janeiro|fevereiro|março|abril|maio|junho|' \
    r'julho|agosto|setembro|outubro|novembro|dezembro)'
)

FLEX_DATE = r"(?P<date>\d+\s+(?:de\s*)?{}\s*(?:de\s*)?\d+|\d+[.]\d+[.]\d+|\d+[/]\d+[/]\d+)".format(case_insensitive(MONTHS_LOWER))

DODF_DATE = r"{}[^\n\n]{{0,50}}?(de\s?)?{}".format(_DODF, FLEX_DATE)

SIAPE = r"{}\s*(?:n?.?)\s*[-\d.Xx/\s]".format(case_insensitive("siape"))

MATRICULA = r"{}[^\d]+([-\d.XxZzYz/\s]+)".format(case_insensitive('(?:matr.cul.|mat[.]\B)'))

MATRICULA_GENERICO = r"(?<![^\s])(?P<matricula>([-\d.XxZzYz/\s]{1,})[.-][\dXxYy][^\d])"

# WARNING: "page_nums" may match not only nums.
# TODO: deal with edge cases like "p 33". There are only a few ones.
PAGE = r"(?P<page>(?:p\.|p.ginas?|p.?gs?\.?\b)(?P<page_nums>.{0,}?)(?=[,;:]|\n|\s[A-Z]|$))"

