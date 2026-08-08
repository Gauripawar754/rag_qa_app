from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.chains import Retrieval_QA
from langchain_text_splitters import RecursiveCharacterTextSplitter
import 





LLM_MODEL = "gemini-3-flash-preview"
EMBED_MODEL = "gemini-embedding-2"   


llm = ChatGoogleGenerativeAI(model = LLM_MODEL)
embed  = GoogleGenerativeAIEmbeddings(EMBED_MODEL)


def create_text (text):
    splitter = RecursiveCharacterTextSplitter(chunk_size = 200, chunk_overlap = 50)
    return  splitter.create_documents([text])


def create_vectorstore(text):
    doc = create_text(text)
    vectorstore = FAISS.from_documents(doc, embedding= embed)
    return vectorstore

def create_qachain(vectorstore):
    retriever = vectorstore.as_retriever(search_kwargs = {'k':3})
    qa_chain = Retrieval_QA.from_chain_type(
        llm = llm,
        retriever=  retriever,
        return_source_documents = True
    )
    return qa_chain



def ask_question(text, question):
    vectorstore = create_vectorstore(text)
    qa_chain = create_qachain(vectorstore)
    
    result = qa_chain.invoke({'query': question})

    answer = result['answer']
    source_doc = result['source_document']