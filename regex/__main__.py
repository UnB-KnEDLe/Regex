import helper
from atos.aposentadoria import Retirements
from atos.reversoes import Revertions
from atos.nomeacao import NomeacaoComissionados
from atos.exoneracao import Exoneracao


if __name__ == "__main__":
    txts = helper.get_txts("./data/test/")
    ret = Retirements(txts[0])
    rev = Revertions(txts[4])
    nom = NomeacaoComissionados(txts[0])
    exo = Exoneracao(txts[0])

    print(ret.data_frame)
    helper._build_act_txt(nom.acts_str, nom.name)
    helper._build_act_txt(rev.acts_str, rev.name)
    helper._build_act_txt(ret.acts_str, ret.name)
    helper._build_act_txt(exo.acts_str, exo.name)