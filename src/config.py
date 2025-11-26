from logger import logger
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    MODEL_NAME = "gemini-2.0-flash"
    OUTPUT_DIR = "outputs"

    @staticmethod
    def ensure_dirs():
        if not os.path.exists(Config.OUTPUT_DIR):
            os.makedirs(Config.OUTPUT_DIR)

if not Config.GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY missing.")

if __name__ == "__main__":
    if Config.GOOGLE_API_KEY:
        logger.info("Successfully connected to Gemini API!")
