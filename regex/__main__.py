import helper
from atos.aposentadoria import Retirements
from atos.reversoes import Revertions
from atos.nomeacao import NomeacaoComissionados
from atos.exoneracao import Exoneracao

from core import Regex

if __name__ == "__main__":
    txts = helper.get_txts("./data/test/")

    apo = Regex.get_act_obj("aposentadoria", txts[0])

    all = Regex.get_all_df(txts[0])
    print(all)