# Loka Challenge

This Repository was created for the Loka Challenge, which main idea was to create a AWS architecture to talk with a LLM about a bouch of .md files containing SageMaker documentation.

For this project it was proposed two alternatives, but just one was implemented in AWS. 

Below is the implemented architecture:

![1](https://github.com/Sebas102507/loka_challenge/assets/52805660/30bb7f6a-ac0c-4f68-80be-c3caa3a2e79b)



**Inference Generator:** This component is responsible for generating inferences, which  uses the LLM Mixtral 8x7b to process and interpret queries or documents to produce outputs based on the data it analyzes.

**Vector Database:** A database designed to store vectors, which are typically the output of embedding models using Open Search.

**Embedding Model:** gpt 6b embedding: This component is responsible for transforming input data into vector embeddings.These embeddings are then used by the vector database to perform similarity searches.

**Query:** This is the section where queries are processed. It includes a WebSocket API, indicating a streaming communication between LLM and the client.

**AskDocumentation Agent:** Lambda that uses the sagemkaer-model-enpoint to answer questions or retrieve information from documentation.

**Client:** The user interface where clients can submit their questions and receive answers. It interacts with the WebSocket API and Rest API.

**Files Encoder:** This component is responsible for encoding files into a format suitable for processing by the LLM.

**UploadFiles:** Lambda that handles the uploading of files from the client.

**Bulk Arrow from Vector Database to Embedding:** This indicates that there files chunks will be uploaded to the vector database.


Non implemented solution:

![2](https://github.com/Sebas102507/loka_challenge/assets/52805660/92a1d7e3-db58-489c-b777-6fc9e7b5224e)


This an architecture that provides Vectara as the Embedding Model and Vector Database (Corpus) services in once, this could be useful for those cases that we don't want to handle and deploy embedding models and a vector database, this is a cheaper option taking account that it just charges USD 1.25 for 1000 queries and 50MB extra storage (Recommended for small-medium projects) for large projects it's recommended using OpenSearch and SageMaker endpoints.

**Inference Generator:** This component is responsible for generating inferences, which  uses the LLM Mixtral 8x7b to process and interpret queries or documents to produce outputs based on the data it analyzes.

**Embedding Model and Vector Database** This component is responsible for transforming input data into vector embeddings.These embeddings are then used by the vector database to perform similarity searches.

**AskDocumentation Agent:** Lambda that uses the sagemkaer-model-enpoint to answer questions or retrieve information from documentation.

**Client:** The user interface where clients can submit their questions and receive answers. It interacts with the WebSocket API and Rest API.

**Files Encoder:** This component is responsible for encoding files into a format suitable for processing by the LLM.

**UploadFiles:** Lambda that handles the uploading of files from the client.


## DEMO (VIDEO):
https://youtu.be/PbWBFHeGiIM
