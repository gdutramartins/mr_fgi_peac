from carregadorDocumento import CarregadorDocumento
from indexadorNormasPeac import IndexadorNormasPeac
from indexadorAnexoPeac import IndexadorAnexoPeac
from processador import Processador
from carregadorNormasPeac import CarregadorNormasPeac
from carregadorAnexoPEAC import CarregadorAnexoPeac


def main():
    carregadorNormas = CarregadorNormasPeac();
    carregadorAnexo = CarregadorAnexoPeac()
    #indexadorNormas = IndexadorNormasPeac()
    #indexadorAnexo = IndexadorAnexoPeac()
    
    textoRegulamento, textoDicionario = carregadorNormas.carregarArquivo()
    textoAnexo,_ = carregadorAnexo.carregarArquivo()
    #indexadorAnexo.indexarAnexo(textoAnexo)
    #indexador.indexarRegulamento(textoRegulamento);
    #indexador.indexarDicionario(textoDicionario)
    #regs = indexador.buscarRegulamentosPorSimliaridade("Limite de contratação de operações por agente financeiro")
    #for idx, r in enumerate(regs):
     #       print(f"Texto: {r}\n{'-'*50}")
    #x = indexador.buscarTermosDicionario("Qual o administrador o FGI com informe de liberação posterior e limite por agente financeiro")
    
    #processador = Processador()
    #x = processador.responderPergunta("Pode me explicar como funcionam as garantias no FGI PEAC?")


if __name__ == "__main__":
    main()