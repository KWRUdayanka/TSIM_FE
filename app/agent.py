import os
from operator import itemgetter  # <--- IMPORT THIS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from app.models import PluginPackageResponse
from dotenv import load_dotenv

load_dotenv()

# Ensure we point to port 5433 (your docker container) and database "postgres"
DB_CONNECTION = os.getenv("DB_CONNECTION", "postgresql+psycopg://postgres:password@localhost:5433/postgres")


class EsbAgentService:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name="esb_core_logic",
            connection=DB_CONNECTION,
        )
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 4})

        self.llm = ChatOpenAI(model="gpt-4o", temperature=0)
        self.structured_llm = self.llm.with_structured_output(PluginPackageResponse)

        self.prompt = ChatPromptTemplate.from_template("""
            You are a Senior Integration Architect for DFN Iolos ESB.

            ### TASK
            Generate a complete Java ESB Plugin for: '{requirement}'
            Plugin Name: '{plugin_name}'

            ### CONTEXT (Use these patterns strictly):
            {context}

            ### RULES:
            1. Main Configuration Class MUST extend `PluginConfigBuilder`.
            2. Use the Fluent API (`restProducer()`, `addProcessor()`, `sqlProcedureConsumer()`) exactly as shown in Context.
            3. Do NOT use generic Camel `from(...)` routes; use the `PluginConfigBuilder` wiring methods.
            4. Include all necessary imports matching `com.dfn.iolos.esb...`.

            Return the result as a structured JSON package.
        """)

        # --- THE FIX IS HERE ---
        # We use itemgetter to pick specific fields from the input dictionary
        self.chain = (
                {
                    # Extract 'requirement' text -> Search DB -> Format Docs
                    "context": itemgetter("requirement") | self.retriever | self._format_docs,
                    # Pass 'requirement' text to the prompt variable {requirement}
                    "requirement": itemgetter("requirement"),
                    # Pass 'plugin_name' text to the prompt variable {plugin_name}
                    "plugin_name": itemgetter("plugin_name")
                }
                | self.prompt
                | self.structured_llm
        )

    def _format_docs(self, docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def generate(self, requirement: str, plugin_name: str) -> PluginPackageResponse:
        return self.chain.invoke({
            "requirement": requirement,
            "plugin_name": plugin_name
        })


agent_service = EsbAgentService()