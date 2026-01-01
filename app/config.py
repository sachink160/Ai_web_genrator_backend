import os
import dspy  # type: ignore
from dotenv import load_dotenv # type: ignore


load_dotenv()

# Direct Third Party api key servies use 

# API_KEY = os.getenv("API_KEY")
# print(API_KEY)
# LLM_MODEL = os.getenv("LLM_MODEL")
# print(LLM_MODEL)

# llm = dspy.LM(
#     model=f"{LLM_MODEL}",
#     api_key=API_KEY,
#     temperature=1.0,
#     max_tokens=16000,
#     cache=True,
# )

# Use Auzuer model 

API_KEY = os.getenv("AZURE_AI_TOKEN")
print(API_KEY)
API_BASE = os.getenv("AZURE_AI_ENDPOINT_URL")
print(API_BASE)
LLM_MODEL = os.getenv("AZURE_AI_DEPLOYMENT_NAME")
print(LLM_MODEL)

API_VERSION = os.getenv("AZURE_AI_APP_VERSION")
print(API_VERSION)

llm = dspy.LM(
    f'azure/{LLM_MODEL}',
    api_key=API_KEY,
    api_base=API_BASE,
    api_version=API_VERSION,
    temperature=1.0,
    max_tokens=16000,
    cache=True
)



dspy.settings.configure(lm=llm)
