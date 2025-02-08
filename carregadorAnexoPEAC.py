import os
from typing import List, override
import re
import typing
import pdfplumber

from carregadorDocumento import CarregadorDocumento




class CarregadorAnexoPeac(CarregadorDocumento):
    __LINHAS_IGNORADAS = (
        'Classificação: Documento Ostensivo', 
        'Unidade Gestora: ADIG'
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
    def __getLinhasIgnoradas(self):
        return self.__LINHAS_IGNORADAS
    
    @override
    def __getPathArquivoDocumento(self) -> str:
        return 'pdf/anexo-procedimentos-peac.pdf'

    @override
    def __verificaLinhaDeveSerIgnorada(self, linha: str) -> bool:
            if linha.startswith(self.__getLinhasIgnoradas()):
                return True
            
            return False

    @override
    def carregarArquivo(self) -> tuple[str,str]:
        linhasExtraidas = []
        dicionarioOn: bool = False

        print("==> Carregando Anexo")

        ignorarInicioDocumento = True
        with pdfplumber.open(self.__getPathArquivoDocumento()) as pdf:
            for pagina in pdf.pages:
                linhas = pagina.extract_text(x_tolerance=2, y_tolerance=2).split("\n"); 
                if linhas[-1].strip().isdigit():  # Verifica se a última linha é um número (número da página)
                    linhas.pop()  # Remove a última linha
                for li in linhas:
                    if ignorarInicioDocumento:
                        if "14. DEMAIS ORIENTAÇÕES" in li:
                            ignorarInicioDocumento = False
                        continue
                    if self.__verificaLinhaDeveSerIgnorada(li):
                        continue 

                    linhasExtraidas.append(li) 
        textoFinal = "\n".join(linhasExtraidas)

        if self.geraLogArquivo:
            print("====> gerando arquivos log do anexo-peac ")
            with open("logs/anexo-peac.log", "w", encoding="utf-8") as arquivo:
                for linha in linhasExtraidas:
                    arquivo.write(linha + "\n")             

        return textoFinal, ""




