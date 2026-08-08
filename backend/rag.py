import os
from typing import Tuple
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import RetrievalQA
import uuid

from dotenv import load_dotenv
load_dotenv()

store = {}  

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


LLM_MODEL = "gemini-3-flash-preview"
EMBED_MODEL = "gemini-embedding-2"   

llm = ChatGoogleGenerativeAI(model=LLM_MODEL)

embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBED_MODEL   
)


def split_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )
    return splitter.create_documents([text])


def create_vectorstore(text):
    docs = split_text(text)
    vectorstore = FAISS.from_documents(docs, embeddings)
    return vectorstore


def create_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        return_source_documents=True
    )

    return qa_chain


def ask_question(text, question):
    vectorstore = create_vectorstore(text)
    qa_chain = create_qa_chain(vectorstore)

    result = qa_chain.invoke({"query": question})

    answer = result["result"]
    sources = result["source_documents"]

    return answer, sources



if __name__ == "__main__":
    text = "Your document content goes here..."

    answer, sources = ask_question(text, "What is this document about?")

    print("Answer:", answer)
    print("\nSources:")
    for s in sources:
        print(s.page_content[:100])



def get_model_info() -> Tuple[str, str]:
    return LLM_MODEL, EMBED_MODEL


def index_document(filename: str, text: str):
    docs = split_text(text)

    vectorstore = FAISS.from_documents(docs, embeddings)

    doc_id = str(uuid.uuid4())

    store[doc_id] = {
        "filename": filename,
        "vectorstore": vectorstore
    }

    return doc_id, len(docs)



def answer_question(document_id: str, question: str):
    if document_id not in store:
        raise KeyError("Document not found")

    vectorstore = store[document_id]["vectorstore"]

    qa_chain = create_qa_chain(vectorstore)

    result = qa_chain.invoke({"query": question})

    answer = result["result"]

    sources = [
        {"content": doc.page_content}
        for doc in result["source_documents"]
    ]

    return answer, sources