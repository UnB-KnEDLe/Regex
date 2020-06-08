import helper
from atos.aposentadoria import Retirements
from atos.reversoes import Revertions
from atos.nomeacao import NomeacaoComissionados
from atos.exoneracao import Exoneracao

from core import Regex

if __name__ == "__main__":
    txts = helper.get_txts("./data/test/")
    ret = Regex.get_act_obj("aposentadoria", txts[2])
    helper._build_act_txt(ret.acts_str, "aposentadoria")
    print(ret.data_frame)