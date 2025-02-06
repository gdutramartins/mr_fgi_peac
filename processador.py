
from typing import Dict, List
from langchain_aws import BedrockLLM
from indexador import Indexador


class Processador:
    __MODEL_ID = 'arn:aws:bedrock:us-east-1:021958399306:inference-profile/us.meta.llama3-3-70b-instruct-v1:0'
    __PROMPT_INICIAL = """Você é um assistente especializado em normativos do Fundo Garantidor. 
                          Responda de forma clara e objetiva, utilizando as informações abaixo:
    """

    def __init__(self):
        self.__llm = BedrockLLM(
            credentials_profile_name='default',
            #model_id='meta.llama3-3-70b-instruct-v1:0',
            provider='meta',
            model_id='arn:aws:bedrock:us-east-1:021958399306:inference-profile/us.meta.llama3-3-70b-instruct-v1:0',
            model_kwargs={
            "max_gen_len":512,
            "temperature": 0.5,
            "top_p": 0.9}
        )

        self.__indexador = Indexador()


    
    def responderPergunta(self, pergunta: str) -> str:
        contextoNormas: List[str] = self.__indexador.buscarRegulamentosPorSimliaridade(pergunta)
        dicionarioTermos: Dict[str,str] = self.__indexador.buscarTermosDicionario(pergunta)
        contexto = ""

        if dicionarioTermos:
            contexto += "**Termos técnicos relevantes:**\n"
            for termo, definicao in dicionarioTermos.items():
                contexto += f"- **{termo}:** {definicao}\n"
            contexto += "\n"

        # Adicionar os trechos normativos encontrados anteriormente (filtered_results)
        contexto += "**Trechos da norma:**\n"
        for doc in contextoNormas:
            contexto += f"- {doc}\n"

        prompt = f"""{self.__PROMPT_INICIAL}

        {contexto} 

        Agora, responda à seguinte pergunta com base no contexto fornecido:  
        **Pergunta:** {pergunta}
        """
        print("Pergunta para LLM:")
        print(prompt)
        print("-----------------------------------------")

        resposta = self.__llm(prompt)
        
        print("Resposta da LLM:\n", resposta)
        print("==========================================")
        
        return resposta




