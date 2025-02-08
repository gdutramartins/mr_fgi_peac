
import json
import re
from typing import Dict, List, Tuple
from langchain.docstore.document import Document
import pickle
from langchain_community.vectorstores import FAISS
from langchain.indexes import VectorstoreIndexCreator
from langchain_aws import BedrockEmbeddings

class IndexadorAnexoPeac:
    __INDEX_ANEXO_PATH = "faiss_anexo_index"
    

    MODEL_EMBEDDING = 'amazon.titan-embed-text-v2:0'

    def __init__(self):
        self.geraLogArquivo = True

    def __corrigeTitulos(self, texto: str) -> str:
        """
        Corrige os titulos do documento, o inicio do documento tem o formato X.X.X.X e depois do item 9.2 foi retirado esse ponto após a numeração

        Args:
            texto (str): texto a ser ajustado

        Returns:
            str: texto ajustado

        Raises:
            Não lança exceção
        """
        textoAjustado = texto.replace("ver a seção\n4.6.", "ver a seção 4.6.")
        textoAjustado = textoAjustado.replace("9.2.1 Encaminhamento do Informe de Amortização Antecipada", "9.2.1. Encaminhamento do Informe de Amortização Antecipada")
        textoAjustado = textoAjustado.replace("9.2.2 Validação do Informe de Amortização Antecipada", "9.2.2. Validação do Informe de Amortização Antecipada")
        textoAjustado = textoAjustado.replace("9.2.2.1 Validação de Formato", "9.2.2.1. Validação de Formato")
        textoAjustado = textoAjustado.replace("9.2.2.2 Validação de Conteúdo", "9.2.2.2. Validação de Conteúdo")
        textoAjustado = textoAjustado.replace("9.2.3 Processamento dos Informes de Amortização Antecipada", "9.2.3. Processamento dos Informes de Amortização Antecipada")
        textoAjustado = textoAjustado.replace("9.2.4 Retorno da Crítica", "9.2.4. Retorno da Crítica")
        textoAjustado = textoAjustado.replace("10 SOLICITAÇÃO DE HONRA DE GARANTIA", "10. SOLICITAÇÃO DE HONRA DE GARANTIA")
        textoAjustado = textoAjustado.replace("10.1 Encaminhamento do Lote Mensal de Solicitações de Honra", "10.1. Encaminhamento do Lote Mensal de Solicitações de Honra")
        textoAjustado = textoAjustado.replace("10.2 Validação da Solicitação de Honra", "10.2. Validação da Solicitação de Honra")
        textoAjustado = textoAjustado.replace("10.2.1 Validação de Formato", "10.2.1. Validação de Formato")
        textoAjustado = textoAjustado.replace("10.2.2 Validação de Conteúdo", "10.2.2. Validação de Conteúdo")
        textoAjustado = textoAjustado.replace("10.2.3 Validação da Cobertura de Inadimplência", "10.2.3. Validação da Cobertura de Inadimplência")
        textoAjustado = textoAjustado.replace("10.2.4 Processamento das Solicitações de Honra", "10.2.4. Processamento das Solicitações de Honra")
        textoAjustado = textoAjustado.replace("10.2.5 Retorno da Crítica", "10.2.5. Retorno da Crítica")
        textoAjustado = textoAjustado.replace("10.3 Substituição de Lote Mensal", "10.3. Substituição de Lote Mensal")
        textoAjustado = textoAjustado.replace("10.4 Cancelamento de Lote Mensal", "10.4. Cancelamento de Lote Mensal")
        textoAjustado = textoAjustado.replace("10.5 Processamento da Solicitação de Honra", "10.5. Processamento da Solicitação de Honra")
        textoAjustado = textoAjustado.replace("11 RECUPERAÇÃO DE CRÉDITO", "11. RECUPERAÇÃO DE CRÉDITO")
        textoAjustado = textoAjustado.replace("11.1 Aplicabilidade", "11.1. Aplicabilidade")
        textoAjustado = textoAjustado.replace("11.2 Encaminhamento do Informe de Recuperação de Crédito", "11.2. Encaminhamento do Informe de Recuperação de Crédito")
        textoAjustado = textoAjustado.replace("11.3 Validação do Informe de Recuperação de Crédito", "11.3. Validação do Informe de Recuperação de Crédito")
        textoAjustado = textoAjustado.replace("11.3.1 Validação de Formato", "11.3.1. Validação de Formato")
        textoAjustado = textoAjustado.replace("11.3.2 Validação de Conteúdo", "11.3.2. Validação de Conteúdo")
        textoAjustado = textoAjustado.replace("11.3.3 Processamento dos Informes de Recuperação de Crédito", "11.3.3. Processamento dos Informes de Recuperação de Crédito")
        textoAjustado = textoAjustado.replace("11.4 Retorno da Crítica", "11.4. Retorno da Crítica")
        textoAjustado = textoAjustado.replace("11.5 Retificação e Cancelamento de Informes Enviados", "11.5. Retificação e Cancelamento de Informes Enviados")
        textoAjustado = textoAjustado.replace("12 DEVOLUÇÃO DO VALOR HONRADO A RECUPERAR PELO AGENTE", "12. DEVOLUÇÃO DO VALOR HONRADO A RECUPERAR PELO AGENTE")
        textoAjustado = textoAjustado.replace("13 PRESTAÇÃO DE INFORMAÇÕES PELO AGENTE FINANCEIRO", "13. PRESTAÇÃO DE INFORMAÇÕES PELO AGENTE FINANCEIRO")
        textoAjustado = textoAjustado.replace("13.1 Posição de Carteira em Recuperação de Crédito", "13.1. Posição de Carteira em Recuperação de Crédito")
        textoAjustado = textoAjustado.replace("13.2 Informe de Classificação de Risco Atualizada", "13.2. Informe de Classificação de Risco Atualizada")
        textoAjustado = textoAjustado.replace("13.3 Informe da Inclusão, Troca de IPOC, Alteração de Dados Retroativos ou", "13.3. Informe da Inclusão, Troca de IPOC, Alteração de Dados Retroativos ou")
        textoAjustado = textoAjustado.replace("14 RENÚNCIA DE PARTE DO VALOR DA COBERTURA MÁXIMA DE", "14. RENÚNCIA DE PARTE DO VALOR DA COBERTURA MÁXIMA DE")
        textoAjustado = textoAjustado.replace("15 DEMAIS ORIENTAÇÕES", "15. DEMAIS ORIENTAÇÕES")
        textoAjustado = textoAjustado.replace("16 OBSERVAÇÕES", "16. OBSERVAÇÕES")

        return textoAjustado

    def __montarchunks(self, texto: str) -> List[Tuple[str,str]]:
        """
        Separa os chunks da regras do regulamento, utilização específica para o regulamento.

        Args:
            a (int ou float): O primeiro número.
            b (int ou float): O segundo número.

        Returns:
            int ou float: O resultado da soma.

        Raises:
            TypeError: Se `a` ou `b` não forem números.
        """
        print("====> Montando chunks anexo ")

        textoAjustado = self.__corrigeTitulos(texto)            

        pattern = re.compile(r'(?m)^(\d{1,2}(?:\.\d+){0,3})\.(?=\s)', re.MULTILINE)
    
        matches = list(pattern.finditer(textoAjustado))
        result = []
    
        if matches:
            # Captura o texto inicial antes da primeira seção
            first_section_start = matches[0].start()
            if first_section_start > 0:
                result.append(("Intro", textoAjustado[:first_section_start].strip()))
            
            for i in range(len(matches)):
                section_number = matches[i].group(1)
                start = matches[i].end()
                end = matches[i+1].start() if i + 1 < len(matches) else len(textoAjustado)
                content = textoAjustado[start:end].strip()
                result.append((section_number, content))
        else:
            result.append(("1. ", textoAjustado.strip()))    
        
        # Remove chunks com uma só linha (titulo perdido)
        chunks = []
        for tupla in result:
            if tupla[1].count('\n') >= 2:  # Verifica se a descrição tem pelo menos 3 linhas
                chunks.append(tupla)
            else:
                print("Chunk anexo removido "+ tupla[0] + ' ' + tupla[1])
                print("=====================")
        
        return chunks
    
    
    def indexarAnexo(self, texto: str):
        print("==> Indexando Anexo")
        chunks: List[str] = self.__montarchunks(texto)
    #    docsRegulamento = [Document(page_content=text) for text in chunks]

    #    print("====> gerando embeddings")
    #    #4. Create Embeddings -- Client connection
    #    bedrockEmbedding=BedrockEmbeddings(
    #       credentials_profile_name= 'default',
    #            model_id=self.MODEL_EMBEDDING)
        
    #    print("====> Gerando índice multidimensional")
    #    dbIndex = FAISS.from_documents(docsRegulamento, bedrockEmbedding)
    #    dbIndex.save_local(self.__INDEX_NORMAS_PATH)

        # Salvar metadados dos chunks
    #    with open(f"{self.__INDEX_NORMAS_PATH}/metadata.pkl", "wb") as f:
    #        pickle.dump(docsRegulamento, f)
    
        if self.geraLogArquivo:
            with open("logs/chunks-anexo.log", "w", encoding="utf-8") as arquivoChunkAnexo:
                for c in chunks:
                    arquivoChunkAnexo.write(c[0] + ' ' + c[1] + "\n==================================\n")
        
    def buscarRegulamentosPorSimliaridade(self, textoConsulta: str, qtdMax: int = 3) -> List[str]:
        itensRegulamento: List[str] = []
        db_index = FAISS.load_local(self.__INDEX_NORMAS_PATH, BedrockEmbeddings(
                        credentials_profile_name='default',
                        model_id=self.MODEL_EMBEDDING,
                        ), 
                    allow_dangerous_deserialization=True)

        # Definir o número de chunks e o limite de similaridade
        TOP_K = 3
        SIMILARITY_THRESHOLD = 0.70  # Ajuste conforme necessário

        # Realizar busca com pontuações
        results = db_index.similarity_search_with_score(textoConsulta, k=TOP_K)

        for doc, score in results:
            print(doc, score)
            print("+++++++++++++++++++++++++")

        # Filtrar por similaridade mínima
        filtered_results = [(doc, score) for doc, score in results if score >= SIMILARITY_THRESHOLD]
        if not filtered_results:
        # Encontrar o item com o maior score em results
            item_maior_score = [max(results, key=lambda x: x[1])]  # x[1] é o campo score


        # Exibir os resultados
        for idx, (doc, score) in enumerate(filtered_results):
            itensRegulamento.append(doc.page_content)
            print(f"Resultado {idx+1}:")
            print(f"Similaridade: {score:.2f}")
            print(f"Texto: {doc.page_content}\n{'-'*50}")
        
        return itensRegulamento
    

