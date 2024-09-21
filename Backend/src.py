import base64
import logging
from typing import List
from io import BytesIO
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.runnables.base import Runnable
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.prompt_values import StringPromptValue
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
import tempfile
import os
import cohere
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define template for prompts
TEMPLATE = """Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Be helpful in your answer and be sure to reference the following context when possible.

{context}

Question: {question}

Answer:"""

prompt = PromptTemplate.from_template(TEMPLATE)

# Initialize Cohere API client
load_dotenv()
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if not COHERE_API_KEY:
    raise ValueError("Cohere API key not found in environment variables.")

co = cohere.Client(COHERE_API_KEY)

def get_embedding_function():
    logger.info("Creating new embedding function")
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def get_embedding_retriever(splits: List[Document]) -> VectorStoreRetriever:
    logger.info("Embedding document chunks")
    embedding_function = get_embedding_function()
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embedding_function,
        persist_directory=None
    )
    return vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

def save_doc_locally(pdf_string: str) -> BytesIO:
    logger.info("Saving pdf document locally")
    try:
        decoded_bytes = base64.b64decode(pdf_string)
        if decoded_bytes[:4] != b"%PDF":
            raise ValueError("Invalid PDF file received.")
        return BytesIO(decoded_bytes)
    except Exception as e:
        logger.error(f"Error saving PDF: {e}")
        raise

def load_and_split_doc(pdf_file: BytesIO) -> List[Document]:
    logger.info("Splitting pdf document into chunks")
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(pdf_file.getvalue())
            temp_file_path = temp_file.name

        loader = PyPDFLoader(temp_file_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50, add_start_index=True)
        return loader.load_and_split(text_splitter=splitter)
    finally:
        os.remove(temp_file_path)

def get_chain(retriever: VectorStoreRetriever, prompt: PromptTemplate) -> Runnable:
    logger.info("Getting RAG chain")
    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | generate_answer_cohere
        | StrOutputParser()
    )

def format_docs(docs: List[Document]) -> str:
    return "\n\n".join(doc.page_content for doc in docs)

def generate_answer_cohere(prompt_output: StringPromptValue) -> str:
    logger.info("Generating answer with Cohere")
    try:
        response = co.generate(
            model="command-r-plus-04-2024",
            prompt=prompt_output.to_string(),
            max_tokens=300,
            temperature=0.7
        )
        return response.generations[0].text.strip()
    except Exception as e:
        logger.error(f"Error generating answer with Cohere: {e}")
        raise

def process_pdf(pdf_string: str, question: str = None) -> str:
    logger.info("Processing PDF")
    try:
        pdf_file = save_doc_locally(pdf_string)
        splits = load_and_split_doc(pdf_file)
        retriever = get_embedding_retriever(splits)
        chain = get_chain(retriever, prompt)

        if question:
            logger.info("Generating answer")
            return chain.invoke(question)
        else:
            logger.info("Generating summary")
            return chain.invoke("Summarize the document")
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return f"An error occurred: {str(e)}"