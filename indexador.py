
import json
import re
from typing import Dict, List, Tuple
from langchain.docstore.document import Document
import pickle
from langchain_community.vectorstores import FAISS
from langchain.indexes import VectorstoreIndexCreator
from langchain_aws import BedrockEmbeddings

class Indexador:
    __INDEX_NORMAS_PATH = "faiss_normas_index"
    __INDEX_DICIONARIO = "faiss_dicionario_index"
    __ARQUIVO_DICIONARIO = "resources/dicionario-regulamento.json"
    __ARQUIVO_SINONIMOS = "resources/sinonimos.json"

    MODEL_EMBEDDING = 'amazon.titan-embed-text-v2:0'

    def __init__(self):
        self.geraLogArquivo = True

    def __montarchunksRegulamento(self, textoRegulamento: str) -> List[str]:
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
        artigos = textoRegulamento.split("\nArt.")
        chunks: List[str] = []
        patternNumeroArtigo = re.compile(r"\d+[.\--º°]")

        print("====> Montando chunks regulamento ")

        for i, art in enumerate(artigos):
            artigo = art.strip()
            #Ignora artigos revogados, mas se tiver parágrafo então deixa a decisão para o parágrafo
            if  "\n§" not in artigo and '(Revogado)' in artigo:
                continue
            if i > 0 :
                artigo = 'Art. ' + artigo
            numeroArtigo = ""
            match = re.search(patternNumeroArtigo, artigo)
            if (match):
                estensaoMatch = 0
                if artigo[match.end()].isalpha() or artigo[match.end()] in ['-', '-']:
                    estensaoMatch += 1
                    if artigo[match.end()-1] in ['º','°']:
                        estensaoMatch += 1                
                numeroArtigo = artigo[:(match.end() + estensaoMatch)]
                
            if "\n§" in artigo:
                #busca pelo número do artigo            
                paragrafos = artigo.split("\n§")
                for j, pa in enumerate(paragrafos):
                    prefixoParagrafo = f"{numeroArtigo} § " if j>0 else ""
                    paragrafo = pa.strip()
                    if (paragrafo) and '(Revogado)' not in paragrafo:
                        chunks.append(prefixoParagrafo + paragrafo)
            else:
                chunks.append(artigo)
        
        return chunks
    
    def __montarchunksDicionario(self, texto: str) -> Dict[str, str]:
        items: Dict[str, str] = dict()

        # Tratar casos onde a organização do texto quebra o algoritma de quebrar pares de chave e descrição
        textoAjustado = texto
        textoAjustado = textoAjustado.replace("(Peac-\nFGI):", "(Peac-FGI):")
        textoAjustado = textoAjustado.replace("Crédito Solidário\nRS):", "Crédito Solidário RS):")
        textoAjustado = textoAjustado.replace("Programas de Garantia do\nPEAC: Programa Emergencial de Acesso", "Programas de Garantia do PEAC- Programa Emergencial de Acesso")
        textoAjustado = textoAjustado.replace("Outorga de Garantia, que será: igual ao Valor", "Outorga de Garantia, que será igual ao Valor")

        lines = textoAjustado.split('\n')
        current_key = None
    
        for line in lines:
            match = re.match(r'([^:]+):\s*(.*)', line)
            if match:
                if current_key:
                    items[current_key] = current_value.strip()
                current_key = match.group(1).strip()
                current_value = match.group(2).strip()
            elif current_key:
                current_value += ' ' + line.strip()
        
        if current_key:
            items[current_key] = current_value.strip()

        return items  
        

    
    def indexarRegulamento(self, texto: str):
        print("==> Indexando Regulamentos")
        chunks: List[str] = self.__montarchunksRegulamento(texto)
        docsRegulamento = [Document(page_content=text) for text in chunks]

        print("====> gerando embeddings")
        #4. Create Embeddings -- Client connection
        bedrockEmbedding=BedrockEmbeddings(
            credentials_profile_name= 'default',
                model_id=self.MODEL_EMBEDDING)
        
        print("====> Gerando índice multidimensional")
        dbIndex = FAISS.from_documents(docsRegulamento, bedrockEmbedding)
        dbIndex.save_local(self.__INDEX_NORMAS_PATH)

        # Salvar metadados dos chunks
        with open(f"{self.__INDEX_NORMAS_PATH}/metadata.pkl", "wb") as f:
            pickle.dump(docsRegulamento, f)
    
        if self.geraLogArquivo:
            with open("logs/chunks-regulamento.log", "w", encoding="utf-8") as arquivochunkRegulamento:
                for c in chunks:
                    arquivochunkRegulamento.write(c + "\n==================================\n")
        
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
    

    def indexarDicionario(self, texto: str):
        print("==> Indexando Dicionário")
        itensDicionario: Dict[str, str] = self.__montarchunksDicionario(texto)
        # docsDicionario = []
        #for item in itensDicionario:
        #    docsDicionario.append(Document(page_content=item['termo'], metadata={"descricao": item['descricao']}))

        with open(self.__ARQUIVO_DICIONARIO, "w", encoding="utf-8") as file:
            json.dump(itensDicionario, file, ensure_ascii=False, indent=4)
        
        #print("====> gerando embeddings dicionário")
        #4. Create Embeddings -- Client connection
        #bedrockEmbedding=BedrockEmbeddings(
        #    credentials_profile_name= 'default',
        #        model_id=self.MODEL_EMBEDDING)
        
        #print("====> Gerando índice multidimensional do dicionário ")
        #dbIndex = FAISS.from_documents(docsDicionario, bedrockEmbedding)
        #dbIndex.save_local(self.__INDEX_DICIONARIO)

        # Salvar metadados dos chunks
        #with open(f"{self.__INDEX_DICIONARIO}/metadata.pkl", "wb") as f:
        #    pickle.dump(docsDicionario, f)
    
        
    def buscarTermosDicionario(self, pergunta: str) -> Dict[str, str]:                
        termosRelevantes = dict()
        with open(self.__ARQUIVO_DICIONARIO, "r", encoding="utf-8") as file:
            itensDicionario = json.load(file)
        
        with open(self.__ARQUIVO_SINONIMOS, "r", encoding="utf-8") as file:
            termosComSinonimos: Dict[str,str] = json.load(file)


        perguntaTratada = pergunta.lower()
        
        for termo, definicao in itensDicionario.items():
            if termo.lower() in perguntaTratada:
                termosRelevantes[termo] = definicao
            else:  
                sinonimos = [s.strip() for s in termosComSinonimos[termo].split(",")]
                for sin in sinonimos:
                    if sin.lower() in perguntaTratada:
                        termosRelevantes[termo] = definicao
                        break

        return termosRelevantes






