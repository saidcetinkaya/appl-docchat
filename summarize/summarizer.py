import os
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import PyPDFLoader
from dotenv import load_dotenv
# local imports
from query.llm_creator import LLMCreator
from ingest.splitter_creator import SplitterCreator
import settings
import utils as ut


class Summarizer:
    """
    When the summarizer class parameters are read from settings.py, object is initiated without parameter settings
    When parameters are read from GUI, object is initiated with parameter settings listed
    """
    def __init__(self, content_folder_path: str, summarization_method: str, text_splitter_method=None,
                 chunk_size=None, chunk_overlap=None, llm_provider=None, llm_model=None) -> None:
        """
        When parameters are read from settings.py, object is initiated without parameter settings
        When parameters are read from GUI, object is initiated with parameter settings listed
        """
        self.content_folder_path = content_folder_path
        self.chain_type = summarization_method
        self.text_splitter_method = settings.TEXT_SPLITTER_METHOD \
            if text_splitter_method is None else text_splitter_method
        self.chunk_size = settings.CHUNK_SIZE if chunk_size is None else chunk_size
        self.chunk_overlap = settings.CHUNK_OVERLAP if chunk_overlap is None else chunk_overlap
        self.llm_provider = settings.LLM_PROVIDER if llm_provider is None else llm_provider
        self.llm_model = settings.LLM_MODEL if llm_model is None else llm_model

        # create splitter object
        self.text_splitter = SplitterCreator(text_splitter_method=self.text_splitter_method,
                                             chunk_size=self.chunk_size,
                                             chunk_overlap=self.chunk_overlap).get_splitter()()

        # create llm object
        load_dotenv()
        self.llm = LLMCreator(llm_provider=self.llm_provider,
                              llm_model=self.llm_model).get_llm()

        # create summarization chain
        self.chain = load_summarize_chain(llm=self.llm, chain_type=self.chain_type)

    def summarize_folder(self) -> None:
        """
        creates summaries of all files in the folder, using the chosen summarization method. One summary per file.
        """
        # create subfolder "summaries" if not existing
        if 'summaries' not in os.listdir(self.content_folder_path):
            os.mkdir(os.path.join(self.content_folder_path, "summaries"))

        # list of relevant files to summarize
        files_in_folder = ut.get_relevant_files_in_folder(self.content_folder_path)

        # loop over all files in the folder
        for file in files_in_folder:
            self.summarize_file(file=file)

    def summarize_file(self, file: str) -> None:
        """
        creates summary for one specific file
        """
        loader = PyPDFLoader(os.path.join(self.content_folder_path, file))
        docs = loader.load_and_split(text_splitter=self.text_splitter)
        summary = self.chain.invoke(docs)["output_text"]
        # store summary on disk
        file_name, _ = os.path.splitext(file)
        result = os.path.join(self.content_folder_path, "summaries", str(file_name) + "_" +
                              str.lower(self.chain_type) + ".txt")
        with open(file=result, mode="w", encoding="utf8") as f:
            f.write(summary)
