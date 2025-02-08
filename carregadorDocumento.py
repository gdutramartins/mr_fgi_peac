from abc import abstractmethod
import os
from typing import List
import re
import pdfplumber




class CarregadorDocumento:

    
    def __init__(self):
        self.geraLogArquivo = True

    @abstractmethod
    def __getLinhasIgnoradas() -> List[str]:
        pass
    
    @abstractmethod
    def __getPathArquivoDocumento() -> str:
        pass
    
    

    @abstractmethod
    def __verificaLinhaDeveSerIgnorada(self, linha: str) -> bool:
        pass

    """
        Carrega o arquivo PDF, transformando em texto. Separando regras de dicionário (quando pertinente)

        Args:
            a (int ou float): só para exemplo, não tem parâmetro.            

        Returns:
            Tupla com dois campos, o primeiro são as regras e o segundo é o dicionário (quando ouver necessidade)

        Raises:
            TypeError: Se `a` ou `b` não forem números.
        """
    @abstractmethod
    def carregarArquivo(self) -> tuple[str,str]:
        pass




