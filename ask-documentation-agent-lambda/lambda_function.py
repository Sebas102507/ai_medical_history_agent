import os
import sys
import boto3
import json
from typing import Dict, List

from langchain_community.embeddings import SagemakerEndpointEmbeddings
from langchain_community.embeddings.sagemaker_endpoint import EmbeddingsContentHandler

from langchain_community.llms.sagemaker_endpoint import LLMContentHandler
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain_community.llms import SagemakerEndpoint
from langchain.vectorstores import OpenSearchVectorSearch
from langchain.prompts import PromptTemplate

import asyncio
from typing import AsyncIterable

import logging
logging.getLogger().setLevel(logging.DEBUG)


sagemaker_client = boto3.client("sagemaker-runtime",region_name="us-east-1")
apigw_client = boto3.client('apigatewaymanagementapi', endpoint_url=os.environ.get("GATEWAY_ENDPOINT_URL"))
opensearch_auth = (os.environ.get("OPEN_SEARCH_USERNAME"), os.environ.get("OPEN_SEARCH_PASSWORD"))
open_search_domain= os.environ.get("OPEN_SEARDCH_DOMAIN")
MODEL_ENDPOINT = os.environ.get("MODEL_ENDPOINT")
EMBEDDING_ENDPOINT= os.environ.get("EMBEDDING_MODEL_ENDPOINT")



def handler(event, context):
    logging.debug(f"ℹ️🤖Chating with documentation agent...")
    logging.debug(f'ℹ️🔔' +  sys.version + '!' )
    connection_id = event["requestContext"]["connectionId"]
    _askAgent(connection_id,json.loads(event["body"])["content"])
    return {'statusCode': 200}
 
 
def _askAgent(connection_id,payload):
    logging.debug(f"ℹ️🔔Payload data for chat : {payload}")
    documentationAgent=DocumentationAgent(index=payload['index'])
    documentationAgent.ask(question=payload['question'],connection_id=connection_id)
 
 

class ContentHandler(LLMContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, prompt: str, model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"inputs": prompt, "parameters": model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> str:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json[0]["generated_text"]

class EmbeddingContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, inputs: list[str], model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"text_inputs": inputs, **model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> List[List[float]]:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["embedding"]
       
class DocumentationAgent():
      def __init__(self,index,is_streaming=False):
        self.is_streaming=is_streaming
        self.index=index
        self.llm=self._initLLM()
        self.embedding_model=self._initEmbeddingModel()
        self.docsearch= self._initVectorStore()

      def _initLLM(self):
        if self.is_streaming:
          callback = AsyncIteratorCallbackHandler()
          return SagemakerEndpoint(
            endpoint_name=MODEL_ENDPOINT,
            client=sagemaker_client,
            model_kwargs={"temperature": 0.1},
            content_handler=ContentHandler(),
            streaming=True,
            callbacks=[callback]
          )
        else:
          return SagemakerEndpoint(
            endpoint_name=MODEL_ENDPOINT,
            client=sagemaker_client,
            model_kwargs={"temperature": 0.1},
            content_handler=ContentHandler()
          )

      def _initEmbeddingModel(self):
        return SagemakerEndpointEmbeddings(
          endpoint_name=EMBEDDING_ENDPOINT,
          region_name="us-east-1",
          content_handler=EmbeddingContentHandler(),
          client=sagemaker_client)
      
      def _initVectorStore(self):
          return OpenSearchVectorSearch(
            index_name=self.index,
            embedding_function=self.embedding_model,
            opensearch_url=open_search_domain,
            http_auth=opensearch_auth)
    
      def ask(self,connection_id,question,k=3):
        documents = self.docsearch.similarity_search(query=question,k=k)
        join_content_chunks = "".join(f"{{{document.page_content } | Source: {document.metadata['source']} }}" for document in documents)
        logging.debug(f"🔔Join content chunks: {join_content_chunks}")
        prompt_template = """Use the following pieces of context to answer the question at the end.
        {context}
        Question: {question}
        Answer:"""
        prompt = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
        )
        formatted_prompt=prompt.format(context=join_content_chunks, question=question)
        logging.debug(f"✅OK FORMATTED PROMPT")
        if (self.is_streaming==False):
          output= self.llm.invoke(formatted_prompt)
          logging.debug(f"✅OK OUPUT NOT STREAMIG")
          
          if (not connection_id==None):
            self._sendDataToClientAPIGateway(connection_id,output)
            return output
          else:    
            return output

      def _sendDataToClientAPIGateway(self,connection_id,data):
        response = apigw_client.post_to_connection(
            ConnectionId=connection_id,
            Data=json.dumps(data, ensure_ascii=False)
        )
        logging.debug(f"ℹ️🔔Response: {response}")        