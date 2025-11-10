from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_core.tools import tool

load_dotenv()

# Embedding Model
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
)

# Paths to PDFs
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CV_PATH = os.path.join(BASE_DIR, "literature", "CV.pdf")
COVER_LETTER_GUIDE_PATH = os.path.join(BASE_DIR, "literature", "How to write an excellent Cover Letter.pdf")
PERSIST_DIRECTORY = os.path.join(BASE_DIR, "chroma_db")

def initialize_rag_system():
    """Initialize the RAG system with CV and Cover Letter guide."""
    
    print("Initializing RAG system...")
    
    # Check if PDFs exist
    if not os.path.exists(CV_PATH):
        raise FileNotFoundError(f"CV not found: {CV_PATH}")
    if not os.path.exists(COVER_LETTER_GUIDE_PATH):
        raise FileNotFoundError(f"Cover Letter guide not found: {COVER_LETTER_GUIDE_PATH}")
    
    # Load CV PDF
    print("Loading CV...")
    cv_loader = PyPDFLoader(CV_PATH)
    cv_pages = cv_loader.load()
    print(f"CV loaded: {len(cv_pages)} pages")
    
    # Load Cover Letter Guide PDF
    print("Loading Cover Letter Guide...")
    guide_loader = PyPDFLoader(COVER_LETTER_GUIDE_PATH)
    guide_pages = guide_loader.load()
    print(f"Cover Letter Guide loaded: {len(guide_pages)} pages")
    
    # Text splitting
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    cv_chunks = text_splitter.split_documents(cv_pages)
    guide_chunks = text_splitter.split_documents(guide_pages)
    
    # Add metadata to distinguish between CV and guide
    for chunk in cv_chunks:
        chunk.metadata["source_type"] = "cv"
    for chunk in guide_chunks:
        chunk.metadata["source_type"] = "cover_letter_guide"
    
    # Combine all chunks
    all_chunks = cv_chunks + guide_chunks
    
    # Create persist directory if it doesn't exist
    if not os.path.exists(PERSIST_DIRECTORY):
        os.makedirs(PERSIST_DIRECTORY)
    
    # Create or load ChromaDB vector store
    print("Creating ChromaDB vector store...")
    vectorstore = Chroma.from_documents(
        documents=all_chunks,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY,
        collection_name="resume_assistant"
    )
    print("ChromaDB vector store created successfully!")
    
    return vectorstore

def get_vectorstore():
    """Get existing vectorstore or create new one."""
    if os.path.exists(PERSIST_DIRECTORY) and os.listdir(PERSIST_DIRECTORY):
        print("Loading existing ChromaDB vector store...")
        vectorstore = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embeddings,
            collection_name="resume_assistant"
        )
    else:
        vectorstore = initialize_rag_system()
    
    return vectorstore

def get_retriever_tools():
    """Create retriever tools for CV and cover letter guide."""
    vectorstore = get_vectorstore()
    
    # Create retrievers with filters
    cv_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5,
            "filter": {"source_type": "cv"}
        }
    )
    
    guide_retriever = vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={
            "k": 5,
            "filter": {"source_type": "cover_letter_guide"}
        }
    )
    
    @tool
    def retrieve_cv_content(query: str) -> str:
        """
        Retrieves relevant information from the user's CV/resume.
        Use this to understand the user's background, experience, skills, and qualifications.
        """
        docs = cv_retriever.invoke(query)
        
        if not docs:
            return "No relevant CV information found."
        
        results = []
        for i, doc in enumerate(docs):
            results.append(f"CV Section {i+1}:\n{doc.page_content}")
        
        return "\n\n".join(results)
    
    @tool
    def retrieve_cover_letter_guide(query: str) -> str:
        """
        Retrieves guidance on writing excellent cover letters.
        Use this to understand best practices, structure, and tips for cover letter writing.
        """
        docs = guide_retriever.invoke(query)
        
        if not docs:
            return "No relevant cover letter guidance found."
        
        results = []
        for i, doc in enumerate(docs):
            results.append(f"Guide Section {i+1}:\n{doc.page_content}")
        
        return "\n\n".join(results)
    
    return [retrieve_cv_content, retrieve_cover_letter_guide]

