# Loka Challenge

This repository was created for the Loka Challenge, whose main idea was to create an AWS architecture to communicate with an LLM about a bunch of .md files containing SageMaker documentation.

For this project, two alternatives were proposed, but only one was implemented in AWS.

Below is the implemented architecture:

![1](https://github.com/Sebas102507/loka_challenge/assets/52805660/30bb7f6a-ac0c-4f68-80be-c3caa3a2e79b)



**Inference Generator:** This component generates inferences by utilizing the LLM Mixtral 8x7b to process and interpret queries or documents, thus producing outputs based on the analyzed data.

**Vector Database:** A database specifically designed to store vectors, which are typically produced by embedding models and are utilized within OpenSearch.

**Embedding Model (GPT-6B Embedding):** This component transforms input data into vector embeddings. These embeddings are then leveraged by the vector database to carry out similarity searches.

**Query:** This section processes queries. It includes a WebSocket API, which facilitates streaming communication between the LLM and the client.

**AskDocumentation Agent:** A Lambda function that employs the SageMaker model endpoint to respond to questions or retrieve information from the documentation.

**Client:** The user interface where clients can pose their questions and obtain answers. It interfaces with both the WebSocket API and the REST API.

**Files Encoder:** This component encodes files into a format that is suitable for processing by the LLM.

**UploadFiles:** A Lambda function that manages the uploading of files from the client.

**Bulk Arrow from Vector Database to Embedding:** This denotes that chunks of files will be uploaded to the vector database.

Non-Implemented Solution:

![2](https://github.com/Sebas102507/loka_challenge/assets/52805660/92a1d7e3-db58-489c-b777-6fc9e7b5224e)


This architecture provides Vectara as an integrated service for the Embedding Model and Vector Database (Corpus), which could be beneficial in scenarios where there is no desire to manage and deploy separate embedding models and a vector database. It offers a cost-effective solution, charging only USD 1.25 for 1,000 queries and an additional 50MB of storage, making it suitable for small to medium-sized projects. For larger projects, the use of OpenSearch and SageMaker endpoints is recommended.

**Inference Generator:** This component is tasked with generating inferences and utilizes the LLM Mixtral 8x7b to process and interpret queries or documents, thereby producing outputs informed by the data it analyzes.

**Embedding Model and Vector Database:** This component is accountable for transforming input data into vector embeddings. These embeddings are then employed by the vector database to conduct similarity searches.

**AskDocumentation Agent:** A Lambda function that uses the SageMaker model endpoint to answer questions or retrieve information from the documentation.

**Client:** The user interface where clients can submit their queries and receive responses. It interfaces with both the WebSocket API and REST API.

**Files Encoder:** This component is charged with encoding files into a format that is amenable for processing by the LLM.

**UploadFiles:** A Lambda function that manages the uploading of files from the client.


## DEMO (VIDEO):
https://youtu.be/PbWBFHeGiIM
