from abc import abstractmethod
import os
from typing import List
import re
import pdfplumber




class CarregadorDocumento:

    
    def __init__(self):
        self.geraLogArquivo = True

    @abstractmethod
    def _getLinhasIgnoradas(self) -> List[str]:
        pass
    
    @abstractmethod
    def _getPathArquivoDocumento(self) -> str:
        pass
    
    @abstractmethod
    def _isLogOn(self) -> bool:
        pass
    
    @abstractmethod
    def _getNomeArquivoLogRegulamento(self) -> str:
        pass
    
    @abstractmethod
    def _getNomeArquivoLogDicionario(self) -> str:
        pass
        

    @abstractmethod
    def _verificaLinhaDeveSerIgnorada(self, linha: str) -> bool:
        pass

    """
        Carrega o arquivo PDF, transformando em texto. Separando regras de dicionário (quando pertinente)

        Args:
            não informado, o nome do arquivo vem por método            

        Returns:
            Tupla com dois campos, o primeiro são as regras e o segundo é o dicionário (quando ouver necessidade)

        Raises:
            sem exceção até o momento
        """
    @abstractmethod
    def carregarArquivo(self) -> tuple[str,str]:
        pass

    
    def _gerarLogCarga(self, linhasRegulamento: List[str], linhasDicionario:List[str]) -> None: 
        if not self._isLogOn():
            print("====> Log de carga desativado")
            return
                
        print("====> gerando arquivos log ")
        print(f"====> Log Regulamentos -> {self.__getNomeArquivoLogRegulamento}")        
        with open(self.__getNomeArquivoLogRegulamento(), "w", encoding="utf-8") as arquivo:
            for linha in linhasRegulamento:
                arquivo.write(linha + "\n")
        if (not linhasDicionario or len(linhasDicionario) == 0):
            print("Dicionário não gerado - sem linhas para processar")
            return 
        with open(self.__getNomeArquivoLogDicionario(), "w", encoding="utf-8") as arquivoDicionario:
            for linha in linhasDicionario:
                arquivoDicionario.write(linha + "\n")


