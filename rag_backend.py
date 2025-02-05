#1. Import OS, Document Loader, Text Splitter, Bedrock Embeddings, Vector DB, VectorStoreIndex, Bedrock-LLM
import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_aws import BedrockEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.indexes import VectorstoreIndexCreator
from langchain_aws import BedrockLLM
import re
import pdfplumber
import pickle







def criarChuncksRegulamento(texto: str) -> List[str]:
   


#5c. Wrap within a function
def hr_index():
    # textSplitter = RecursiveCharacterTextSplitter(separators=["\nArt.", "\n§", " ", ""], chunk_size=2000,chunk_overlap=200)
    #2. Define the data source and load data with PDFLoader(https://www.upl-ltd.com/images/people/downloads/Leave-Policy-India.pdf)
    
    

    chuncksRegulamento = criarChuncksRegulamento(textoRegulamentoPreparado)

    with open("regulamento-peac.txt", "w", encoding="utf-8") as arquivo:
        for linha in linhasRegulamentoFiltrado:
            arquivo.write(linha + "\n") 
    with open("regulamento-peac-dicionario.txt", "w", encoding="utf-8") as arquivoDicionario:
        for linha in linhasDicionario:
            arquivoDicionario.write(linha + "\n") 
    with open("chuncks-regulamento.txt", "w", encoding="utf-8") as arquivoChunckRegulamento:
        for c in chuncksRegulamento:
            arquivoChunckRegulamento.write(c + "\n==================================\n")
   
 
    #3. Split the Text based on Character, Tokens etc. - Recursively split by character - ["\n\n", "\n", " ", ""]
    # Todos os arquivos precisam ser pré-processados
    # regulamento-peac 
    #   - retirar termos em maisculos que são repetidos
    #   - explicações que podem poluir
    #   - remover títulos em caixa alta (testar). 
    #   - Definições pode ser um texto que sempre é adicionado como contexto, já que é um dicionário.
    #   - ver como ficará a tabela
    # anexo-procedimentos-peac
    #   - retirar sumário
    #   - tópicos podem ter o prefixo Art. e subtópicos o §
    #   - ver como ficará a tabela
    # antecipação limite
    #   - remover os avisos históricos, podem poluir as respostas (testar)
    #   - remover caixas alta como título (testar)

    # Fazer o RecursiveCharacterTextSplitter duas vezes, uma separa os artigos sem overlap, depois separa os parágrafos com overlap, dessa forma não misturamos artigos, o que pode gerar confusão
    

    docsRegulamento = [Document(page_content=text) for text in chuncksRegulamento]
    #4. Create Embeddings -- Client connection
    bedrockEmbedding=BedrockEmbeddings(
        credentials_profile_name= 'default',
        model_id='amazon.titan-embed-text-v2:0')
        #5à Create Vector DB, Store Embeddings and Index for Search - VectorstoreIndexCreator
    #data_index=VectorstoreIndexCreator(
    #    embedding=data_embeddings,
    #    vectorstore_cls=FAISS)
    dbIndex = FAISS.from_documents(docsRegulamento, bedrockEmbedding)
    dbIndex.save_local(INDEX_NORMAS_PATH)

    # Salvar metadados dos chuncks
    with open(f"{INDEX_NORMAS_PATH}/metadata.pkl", "wb") as f:
        pickle.dump(docsRegulamento, f)

    return dbIndex












    
#6a. Write a function to connect to Bedrock Foundation Model 
def hr_llm():
    llm=BedrockLLM(
        credentials_profile_name='default',
        #model_id='meta.llama3-3-70b-instruct-v1:0',
        provider='meta',
        model_id='arn:aws:bedrock:us-east-1:021958399306:inference-profile/us.meta.llama3-3-70b-instruct-v1:0',
        model_kwargs={
        "max_gen_len":512,
        "temperature": 0.5,
        "top_p": 0.9})
    return llm
#6b. Write a function which searches the user prompt, searches the best match from Vector DB and sends both to LLM.
def hr_rag_response(index,question):
    rag_llm=hr_llm()
    hr_rag_query=index.query(question=question,llm=rag_llm)
    return hr_rag_query
# Index creation --> https://api.python.langchain.com/en/latest/indexes/langchain.indexes.vectorstore.VectorstoreIndexCreator.html