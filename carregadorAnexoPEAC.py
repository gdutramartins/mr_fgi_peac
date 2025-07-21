import os
from typing import List, override
import re
import typing
import pdfplumber

from carregadorDocumento import CarregadorDocumento




class CarregadorAnexoPeac(CarregadorDocumento):
    _LINHAS_IGNORADAS = (
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
    def _getLinhasIgnoradas(self):
        return self._LINHAS_IGNORADAS
    
    @override
    def _getPathArquivoDocumento(self) -> str:
        return 'pdf/anexo-2-peac.pdf'
    
    @override
    def _getNomeArquivoLogRegulamento(self):
        return "logs/anexo-peac.log"
    
    @override
    def _getNomeArquivoLogDicionario(self):
        return ""

    @override
    def _verificaLinhaDeveSerIgnorada(self, linha: str) -> bool:
            if linha.startswith(self._getLinhasIgnoradas()):
                return True
            
            return False

    @override
    def carregarArquivo(self) -> tuple[str,str]:
        linhasExtraidas = []
        dicionarioOn: bool = False

        print(f"==> Carregando Anexo - {self._getPathArquivoDocumento()}")

        ignorarInicioDocumento = True
        with pdfplumber.open(self._getPathArquivoDocumento()) as pdf:
            for pagina in pdf.pages:
                linhas = pagina.extract_text(x_tolerance=2, y_tolerance=2).split("\n"); 
                if linhas[-1].strip().isdigit():  # Verifica se a última linha é um número (número da página)
                    linhas.pop()  # Remove a última linha
                for li in linhas:
                    if ignorarInicioDocumento:
                        if "14. DEMAIS ORIENTAÇÕES" in li:
                            ignorarInicioDocumento = False
                        continue
                    if self._verificaLinhaDeveSerIgnorada(li):
                        continue 

                    linhasExtraidas.append(li) 
        textoFinal = "\n".join(linhasExtraidas)

        self._gerarLogCarga(linhasExtraidas, [])
        
        return textoFinal, ""




