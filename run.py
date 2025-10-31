import os
from dotenv import load_dotenv

from app import create_app

load_dotenv()


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=os.getenv('APP_PORT', 5005), debug=True)
