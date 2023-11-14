# logo in user interface
APP_LOGO = "./images/nmdc_logo.png"
# content for application explanation in user interface
APP_INFO="./info/explanation.txt"
# header in user interface
APP_HEADER = "ChatNMDC: chat with your documents"
# folder location of where input documents
DOC_DIR = "./docs"
# folder location of vector database
VECDB_DIR = "./vector_stores"
# folder location of evaluation result
EVAL_DIR = "./evaluate"
# header in evaluation user interface
EVAL_APP_HEADER = "ChatNMDC: evaluation"
# content for evaluation explanation in evaluation user interface
EVAL_APP_INFO="./info/evaluation_explanation.txt"
# filename of json file with question and answer lists
EVAL_FILE_NAME = "eval_paper.json"
# CHAIN_VERBOSITY must be boolean. True shows standalone question that is conveyed to LLM
CHAIN_VERBOSITY = False

#### the settings below can be used for testing ####
# LLM_TYPE must be one of: "chatopenai", "huggingface", "local_llm"
LLM_TYPE = "chatopenai"
# if LLM_TYPE is "chatopenai" then LLM_MODEL_TYPE must be one of: "gpt35", "gpt35_16", "gpt4"
# if LLM_TYPE is "huggingface" then LLM_MODEL_TYPE must be one of "llama2", "GoogleFlan"
# if LLM_TYPE is "local_llm" then LLM_MODEL_TYPE must be one of the local models, e.g. "llama2"
# "llama2" requires Huggingface Pro Account and access to the llama2 model https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
# note: llama2 is not fully tested, the last step was not undertaken, because no HF Pro account was available for the developer
# Context window sizes are currently:
# "gpt35": 4097 tokens which is equivalent to ~3000 words
# "gpt35_16": 16385 tokens
# "gpt4": 8192 tokens
# "GoogleFlan": ? tokens
# "llama2": ? tokens
LLM_MODEL_TYPE = "gpt35"
# API_URL must be the URL to your (local) API
# If LLM_TYPE is "local_llm" and model is run on your local machine, API_URL should be "localhost:11434" by default
# API_URL = "localhost:11434"
# EMBEDDINGS_PROVIDER must be one of: "openai", "huggingface", "local_embeddings"
EMBEDDINGS_PROVIDER = "openai"
# EMBEDDINGS_MODEL must be one of: "text-embedding-ada-002", "all-mpnet-base-v2"
# If EMBEDDINGS_MODEL is "all-mpnet-base-v2" then EMBEDDINGS_PROVIDER must be "huggingface"
# If EMBEDDINGS_MODEL is "local_embeddings" then EMBEDDINGS_PROVIDER must be one of the local models, e.g. "llama2"
EMBEDDINGS_MODEL = "text-embedding-ada-002"
# TEXT_SPLITTER_METHOD, one of: 
# "RecursiveCharacterTextSplitter" (cut words/sentences to achieve chunk size) or 
# "NLTKTextSplitter" (keep full sentences even if chunk size is exceeded)
TEXT_SPLITTER_METHOD = "NLTKTextSplitter"
# CHAIN_NAME must be one of: "conversationalretrievalchain", 
CHAIN_NAME = "conversationalretrievalchain"
# CHAIN_TYPE must be one of: "stuff", 
CHAIN_TYPE = "stuff"
# SEARCH_TYPE must be one of: "similarity", 
SEARCH_TYPE = "similarity"
# VECDB_TYPE must be one of: "chromadb", 
VECDB_TYPE = "chromadb"
# CHUNK_SIZE must be integer
CHUNK_SIZE = 1000
# CHUNK_OVERLAP must be integer
CHUNK_OVERLAP = 200
# CHUNK_K must be integer (>=1)
CHUNK_K = 4
