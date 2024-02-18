import base64
import json
import os
import sys
import uuid
import boto3
from io import BytesIO
from typing import Dict, List
from langchain_community.document_loaders import S3FileLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import SagemakerEndpointEmbeddings
from langchain_community.embeddings.sagemaker_endpoint import EmbeddingsContentHandler
from langchain.vectorstores import OpenSearchVectorSearch
import nltk
import logging

nltk.download('punkt', download_dir='/tmp/nltk_data')
logging.getLogger().setLevel(logging.DEBUG)

sagemaker_client = boto3.client("sagemaker-runtime",region_name="us-east-1")
s3 = boto3.client('s3')
bucket_name = 'boostfs'
index='sagemaker_docs'
EMBEDDING_ENDPOINT= os.environ.get("EMBEDDING_MODEL_ENDPOINT")
opensearch_auth = (os.environ.get("OPEN_SEARCH_USERNAME"), os.environ.get("OPEN_SEARCH_PASSWORD"))
open_search_domain= os.environ.get("OPEN_SEARDCH_DOMAIN")

def handler(event, context):
    logging.debug('Handle files ' + sys.version + '!' )
    base64_data=event['body']
    logging.debug(f"✅ Ready Econded base64_data")
    decoded_data = base64.b64decode(base64_data)
    logging.debug(f"✅ Ready Decoded")
    content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
    if content_type: boundary = content_type.split('boundary=')[-1]
    logging.debug(f"✅ Ready before checking boundary: {boundary} | Len: {len(boundary)}")
    boundary= f"{'--'}{boundary}"
    logging.debug(f"✅ Ready after checking boundary: {boundary} | Len: {len(boundary)}")
    
    try:
        data = _parseMultipartData(decoded_data, boundary)    
        _vectorizeDocumentation(data)    
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({
            'status': "OK",
            'filesNames':data['filesNames']
        })
        }
        
    except Exception as e:
        logging.error(f"🔴 Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 
 
 
def _parseMultipartData(raw_data, boundary):
    parts = raw_data.split(boundary.encode())
    filesNames = []
    filesBytes = []
    for part in parts:
        if b"Content-Disposition: form-data;" in part:
            headers, body = part.split(b"\r\n\r\n", 1)
            body = body.strip()                
            if b'name="files"' in headers:
                logging.debug(f"🧩FILE ")
                filename = headers.split(b'filename="')[1].split(b'"')[0].decode('utf-8')
                file_content = body 
                filesNames.append(filename)
                filesBytes.append(file_content)
        
    return {
        'filesNames': filesNames,
        'filesBytes': filesBytes
    }




def _vectorizeDocumentation(data):
    logging.debug(f"🟢 Data: {data}")
    logging.debug(f"🟢 Files to upload: {data['filesNames']}")
    logging.debug(f"🟢 Files Bytes to upload: {data['filesBytes']}")
    
    
    for file_name, file_content in zip(data['filesNames'], data['filesBytes']):
        delete_from_s3(file_name)
        upload_to_s3(file_name, file_content)
                
        loader = S3FileLoader(bucket_name, file_name)
        logging.debug(f"✅OK Loader")
        logging.debug(f"🔔 NLTK data paths: {nltk.data.path}")
        
        data = loader.load()
        logging.debug(f"🟢 Markdown Data: {data}")
        delete_from_s3(file_name)
        text_splitter = CharacterTextSplitter(chunk_size=1024, chunk_overlap=64)
        documents = text_splitter.split_documents(data)
        
        
        embedding_model=SagemakerEndpointEmbeddings(
            endpoint_name=EMBEDDING_ENDPOINT,
            region_name="us-east-1",
            content_handler=EmbeddingContentHandler(),
            client=sagemaker_client)
        
        ##HERE WE SAVE THE EMBEDDINGS TO OPENSEARCH
        OpenSearchVectorSearch.from_documents(
            index_name = index,
            documents=documents,
            embedding=embedding_model,
            opensearch_url=open_search_domain,
            http_auth=opensearch_auth
        )
        

def delete_from_s3(file_name):
    try:
        s3.delete_object(Bucket=bucket_name, Key=file_name)
        logging.debug(f"✅ File {file_name} deleted from S3.")
    except Exception as e:
        logging.error(f"🚨 Error deleting file from S3: {e}")
        

def upload_to_s3(file_name, file_content):
    try:
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=file_content)
        logging.debug(f"✅ File {file_name} uploaded to S3.")
    except Exception as e:
        logging.error(f"🚨 Error uploading file to S3: {e}")   
        
        
        

class EmbeddingContentHandler(EmbeddingsContentHandler):
    content_type = "application/json"
    accepts = "application/json"

    def transform_input(self, inputs: list[str], model_kwargs: Dict) -> bytes:
        input_str = json.dumps({"text_inputs": inputs, **model_kwargs})
        return input_str.encode("utf-8")

    def transform_output(self, output: bytes) -> List[List[float]]:
        response_json = json.loads(output.read().decode("utf-8"))
        return response_json["embedding"]        