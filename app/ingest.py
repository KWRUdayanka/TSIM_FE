import os
import glob
from langchain_text_splitters import RecursiveCharacterTextSplitter, Language
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

DB_CONNECTION = os.getenv("DB_CONNECTION", "postgresql+psycopg://postgres:password@localhost:5432/postgres")
# PATH TO YOUR JAVA PROJECT
SOURCE_DIRECTORY = os.getenv("JAVA_CORE_PATH", "./java-source")


def ingest_java_files():
    print("--- Starting Knowledge Base Ingestion ---")

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = PGVector(
        embeddings=embeddings,
        collection_name="esb_core_logic",
        connection=DB_CONNECTION,
        use_jsonb=True,
    )

    # Clear existing data (Optional: depends if you want full refresh or append)
    # vector_store.delete_collection() # Uncomment to wipe DB before load

    # Find Files
    files = glob.glob(f"{SOURCE_DIRECTORY}/**/*.java", recursive=True)
    documents = []

    for file_path in files:
        filename = os.path.basename(file_path)
        # Filter for relevant ESB definitions only
        if any(x in filename for x in ["Config", "Endpoint", "Mapping", "Route", "Processor"]):
            with open(file_path, "r", encoding="utf-8") as f:
                documents.append(Document(
                    page_content=f.read(),
                    metadata={"source": filename, "type": "java_core"}
                ))

    # Split
    splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.JAVA,
        chunk_size=2000,
        chunk_overlap=200
    )
    splits = splitter.split_documents(documents)

    # Add to DB
    if splits:
        vector_store.add_documents(splits)
        print(f"--- Ingestion Complete. Added {len(splits)} chunks. ---")
    else:
        print("--- No relevant Java files found to ingest. ---")