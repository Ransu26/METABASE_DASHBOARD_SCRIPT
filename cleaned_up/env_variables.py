import os
from dotenv import load_dotenv

load_dotenv()

def getEnvVar(varName: str) -> str:
    return os.getenv(varName)