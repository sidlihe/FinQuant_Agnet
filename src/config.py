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

    @staticmethod
    def require_api_key():
        if not Config.GOOGLE_API_KEY:
            raise EnvironmentError(
                "GOOGLE_API_KEY missing. Set it in your environment or .env file."
            )

if __name__ == "__main__":
    try:
        Config.require_api_key()
        logger.info("Successfully connected to Gemini API!")
    except EnvironmentError as exc:
        logger.error(str(exc))
