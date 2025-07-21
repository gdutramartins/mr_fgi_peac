import os
from typing import List, override
import re
import typing
import pdfplumber

from carregadorDocumento import CarregadorDocumento




class CarregadorNormasPeac(CarregadorDocumento):
    _LINHAS_IGNORADAS = (
        'Classificação: Documento Ostensivo', 
        'Unidade Gestora: ADIG',
        'definições, utilizadas no singular ou plural:'
    )

    SIGLAS = (
        'BNDES',
        'PEAC',
        'SCR',
        '- SCR',
        'CNAE',
        '(CNAE'
    )

    NUMEROS_ROMANOS = [
        'I',
        'II',
        'III',
        'IV',
        'V',
        'VI',
        'VII',
        'VIII',
    ]

    def __init__(self):
        super().__init__()

    @override
    def _getLinhasIgnoradas(self):
        return self._LINHAS_IGNORADAS
  
    @override
    def _getPathArquivoDocumento(self) -> str:
        return 'pdf/regulamento-peac.pdf'

    @override
    def _getNomeArquivoLogRegulamento(self):
        return "logs/regulamento-peac.log"
    
    @override
    def _getNomeArquivoLogDicionario(self):
        return "logs/regulamento-peac-dicionario.log"
    
    @override
    def _verificaLinhaDeveSerIgnorada(self, linha: str) -> bool:
            if not linha.startswith(self.SIGLAS) and re.fullmatch(r"(?=.*[A-ZÀ-ÖØ-Ý])[A-ZÀ-ÖØ-Ý\s\d\W]+", linha):  # Verifica se a linha é toda maiúscula 
                return True

            if linha.startswith(self._getLinhasIgnoradas()):
                return True
            # Somente se a linha for exatamente um número romano (geralmente lixo)
            if linha.upper() in self.NUMEROS_ROMANOS:
                return True

            return False

    @override
    def carregarArquivo(self) -> tuple[str,str]:
        linhasRegulamento = []
        linhasDicionario = []
        dicionarioOn: bool = False

        print(f"==> Carregando regulamento ({self._getPathArquivoDocumento()})")

        with pdfplumber.open(self._getPathArquivoDocumento()) as pdf:
            for pagina in pdf.pages:
                linhas = pagina.extract_text(x_tolerance=2, y_tolerance=2).split("\n"); # divide em linhas
                if linhas[-1].strip().isdigit():  # Verifica se a última linha é um número (número da página)
                    linhas.pop()  # Remove a última linha
                for li in linhas:
                    if li.startswith("Parágrafo único. Para os efeitos deste Regulamento, serão adotadas as seguintes"):  # a linha será descartada
                        dicionarioOn = True              
                    elif li.startswith("CAPÍTULO II – DA HABILITAÇÃO DO AGENTE FINANCEIRO"): 
                        dicionarioOn = False
                    elif self._verificaLinhaDeveSerIgnorada(li):
                        continue
                    elif dicionarioOn:
                        linhasDicionario.append(li)
                    else:
                        linhasRegulamento.append(li) 
        textoRegulamento = "\n".join(linhasRegulamento)
        textoDicionario = "\n".join(linhasDicionario)

        self._gerarLogCarga(linhasRegulamento, linhasDicionario)

        return textoRegulamento, textoDicionario




