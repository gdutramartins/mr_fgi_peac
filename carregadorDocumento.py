import os
from typing import List
import re
import pdfplumber




class CarregadorDocumento:
    LINHAS_IGNORADAS = (
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
        self.geraLogArquivo = True


    def __linhaRegulamentoDeveSerIgnorada(self, linha: str) -> bool:
            if not linha.startswith(self.SIGLAS) and re.fullmatch(r"(?=.*[A-ZÀ-ÖØ-Ý])[A-ZÀ-ÖØ-Ý\s\d\W]+", linha):  # Verifica se a linha é toda maiúscula 
                return True

            if linha.startswith(self.LINHAS_IGNORADAS):
                return True
            # Somente se a linha for exatamente um número romano (geralmente lixo)
            if linha.upper() in self.NUMEROS_ROMANOS:
                return True

            return False

    # Retorna o texto de normas tratado e
    def carregarArquivoNormas(self) -> tuple[str,str]:
        linhasRegulamento = []
        linhasDicionario = []
        dicionarioOn: bool = False

        print("==> Carregando regulamento")

        with pdfplumber.open('pdf/regulamento-peac.pdf') as pdf:
            for pagina in pdf.pages:
                linhas = pagina.extract_text(x_tolerance=2, y_tolerance=2).split("\n"); # divide em linhas
                if linhas[-1].strip().isdigit():  # Verifica se a última linha é um número (número da página)
                    linhas.pop()  # Remove a última linha
                for li in linhas:
                    if li.startswith("Parágrafo único. Para os efeitos deste Regulamento, serão adotadas as seguintes"):  # a linha será descartada
                        dicionarioOn = True              
                    elif li.startswith("CAPÍTULO II – DA HABILITAÇÃO DO AGENTE FINANCEIRO"): 
                        dicionarioOn = False
                    elif self.__linhaRegulamentoDeveSerIgnorada(li):
                        continue
                    elif dicionarioOn:
                        linhasDicionario.append(li)
                    else:
                        linhasRegulamento.append(li) 
        textoRegulamento = "\n".join(linhasRegulamento)
        textoDicionario = "\n".join(linhasDicionario)

        if self.geraLogArquivo:
            print("====> gerando arquivos log ")
            with open("logs/regulamento-peac.log", "w", encoding="utf-8") as arquivo:
                for linha in linhasRegulamento:
                    arquivo.write(linha + "\n") 
            with open("logs/regulamento-peac-dicionario.log", "w", encoding="utf-8") as arquivoDicionario:
                for linha in linhasDicionario:
                    arquivoDicionario.write(linha + "\n") 

        return textoRegulamento, textoDicionario


