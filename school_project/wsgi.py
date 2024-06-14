import os
from dotenv import load_dotenv
from school_project.run import application

load_dotenv()


application = application

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    application.run(host='0.0.0.0', port=port)