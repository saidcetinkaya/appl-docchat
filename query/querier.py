from typing import Dict, Tuple, List, Any
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain
from langchain.schema import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from loguru import logger
# local imports
import settings
from ingest.embeddings_creator import EmbeddingsCreator
from ingest.vectorstore_creator import VectorStoreCreator
from query.llm_creator import LLMCreator
from query.retriever_creator import RetrieverCreator
import prompts.prompt_templates as pr


class Querier:
    """
    When parameters are read from settings.py, object is initiated without parameter settings
    When parameters are read from GUI, object is initiated with parameter settings listed
    """
    def __init__(self, llm_type=None, llm_model_type=None, embeddings_provider=None, embeddings_model=None,
                 vecdb_type=None, chain_name=None, chain_type=None, chain_verbosity=None, search_type=None,
                 score_threshold=None, chunk_k=None, local_api_url=None, azureopenai_api_version=None):
        load_dotenv()
        self.llm_type = settings.LLM_TYPE if llm_type is None else llm_type
        self.llm_model_type = settings.LLM_MODEL_TYPE if llm_model_type is None else llm_model_type
        self.embeddings_provider = settings.EMBEDDINGS_PROVIDER if embeddings_provider is None else embeddings_provider
        self.embeddings_model = settings.EMBEDDINGS_MODEL if embeddings_model is None else embeddings_model
        self.vecdb_type = settings.VECDB_TYPE if vecdb_type is None else vecdb_type
        self.chain_name = settings.CHAIN_NAME if chain_name is None else chain_name
        self.chain_type = settings.CHAIN_TYPE if chain_type is None else chain_type
        self.chain_verbosity = settings.CHAIN_VERBOSITY if chain_verbosity is None else chain_verbosity
        self.search_type = settings.SEARCH_TYPE if search_type is None else search_type
        self.score_threshold = settings.SCORE_THRESHOLD if score_threshold is None else score_threshold
        self.chunk_k = settings.CHUNK_K if chunk_k is None else chunk_k
        self.local_api_url = settings.API_URL \
            if local_api_url is None and settings.API_URL is not None else local_api_url
        self.chat_history = []
        self.vector_store = None
        self.azureopenai_api_version = settings.AZUREOPENAI_API_VERSION \
            if azureopenai_api_version is None and settings.AZUREOPENAI_API_VERSION is not None \
            else azureopenai_api_version
        self.chain = None

        # define llm
        self.llm = LLMCreator(self.llm_type,
                              self.llm_model_type,
                              self.local_api_url,
                              self.azureopenai_api_version).get_llm()

        # define embeddings
        self.embeddings = EmbeddingsCreator(self.embeddings_provider,
                                            self.embeddings_model,
                                            self.local_api_url,
                                            self.azureopenai_api_version).get_embeddings()

    def make_chain(self, content_folder: str, vecdb_folder: str, search_filter=None) -> None:
        """
        Creates the chain that is used for question answering

        Parameters
        ----------
        content_folder : str
            the content folder
        vecdb_folder : str
            the folder of the vector databse that is associated with the content folder
        search_filter : _type_, optional
            _description_, by default None
        """
        # get vector store
        self.vector_store = VectorStoreCreator(self.vecdb_type).get_vectorstore(self.embeddings,
                                                                                content_folder,
                                                                                vecdb_folder)
        logger.info(f"Loaded vector store from folder {vecdb_folder}")

        # get retriever with some search arguments
        # # maximum number of chunks to retrieve
        # search_kwargs = {"k": self.chunk_k}
        # # filter, if set
        # if search_filter is not None:
        #     logger.info(f"querying vector store with filter {search_filter}")
        #     search_kwargs["filter"] = search_filter
        # if self.search_type == "similarity_score_threshold":
        #     search_kwargs["score_threshold"] = self.score_threshold

        # retriever = RetrieverCreator(vectorstore=self.vector_store, search_kwargs=search_kwargs).get_retriever()
        retriever = RetrieverCreator(vectorstore=self.vector_store).get_retriever(search_filter)

        # get appropriate RAG prompt for querying
        if settings.RETRIEVER_PROMPT_TEMPLATE == "openai_rag":
            current_template = pr.OPENAI_RAG_TEMPLATE
        elif settings.RETRIEVER_PROMPT_TEMPLATE == "openai_rag_concise":
            current_template = pr.OPENAI_RAG_CONCISE_TEMPLATE
        elif settings.RETRIEVER_PROMPT_TEMPLATE == "openai_rag_language":
            current_template = pr.OPENAI_RAG_LANGUAGE_TEMPLATE
        prompt = PromptTemplate.from_template(template=current_template)

        # get chain
        if self.chain_name == "conversationalretrievalchain":
            self.chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                chain_type=self.chain_type,
                verbose=self.chain_verbosity,
                combine_docs_chain_kwargs={'prompt': prompt},
                return_source_documents=True
            )
        logger.info("Executed Querier.make_chain")

    def ask_question(self, question: str) -> Tuple[Dict[str, Any], List[float]]:
        """
        Finds most similar docs to prompt in the vectorstore and determines the response
        If the closest doc found is not similar enough to the prompt, any answer from the LLM is overruled by a message
        """
        logger.info(f"current question: {question}")
        logger.info(f"current chat history: {self.chat_history}")

        response = self.chain.invoke({"question": question, "chat_history": self.chat_history})
        # if no chunk qualifies, overrule any answer generated by the LLM
        if len(response["source_documents"]) == 0:
            response["answer"] = "I don't know because there is no relevant context containing the answer"
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(AIMessage(content=response["answer"]))

        return response

    def clear_history(self) -> None:
        """
        Clears the chat history
        Used by "Clear Conversation" button in streamlit_app.py
        """
        self.chat_history = []

    def get_meta_data_by_file_name(self, filename: str) -> dict[str: str]:
        """
        Returns the meta data of a specific file
        Need to run make_chain first
        """
        # sources keys: ['ids', 'embeddings', 'metadatas', 'documents', 'uris', 'data']
        sources = self.vector_store.get()
        metadata = [metadata for metadata in sources['metadatas'] if metadata['filename'] == filename]

        # return only the first chunk, as filename metadata is the same for all chunks
        return metadata[0]
