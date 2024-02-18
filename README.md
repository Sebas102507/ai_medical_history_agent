# Loka Challenge

This Repository was created for the Loka Challenge, which is main idea was to create a AWS architecture to talk with a LLM about a bouch of .md files containing SageMaker documentation.

For this project is was purposed, but just one was implemented in AWS. 

Below is the implemented architecture:


![1](https://github.com/Sebas102507/loka_challenge/assets/52805660/df0a455f-f935-4a67-806b-be9cef45833d)

**Inference Generator:** This component is responsible for generating inferences, which  uses the LLM Mixtral 8x7b to process and interpret queries or documents to produce outputs based on the data it analyzes.

**Vector Database:** A database designed to store vectors, which are typically the output of embedding models using Open Search.

**Embedding Model:** gpt 6b embedding: This component is responsible for transforming input data into vector embeddings.These embeddings are then used by the vector database to perform similarity searches.

**Query:** This is the section where queries are processed. It includes a WebSocket API, indicating a streaming communication between LLM and the client.

**AskDocumentation Agent:** Lambda that uses the sagemkaer-model-enpoint to answer questions or retrieve information from documentation.

**Client:** The user interface where clients can submit their questions and receive answers. It interacts with the WebSocket API and Rest API.

**Files Encoder:** This component is responsible for encoding files into a format suitable for processing by the LLM.

**UploadFiles:** Lambda that handles the uploading of files from the client.

**Bulk Arrow from Vector Database to Embedding:** This indicates that there files chunks will be uploaded to the vector database.
