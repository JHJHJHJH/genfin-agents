from PolicyClassifierAgent import PolicyClassifierAgent
import logging
from datetime import datetime
import os
from DocumentTermAgent import DocumentTermAgent

from dotenv import load_dotenv
load_dotenv()  # take environment variables

now = str(datetime.now().strftime("%Y%b%d-%HH%MM%SS"))


logging.basicConfig(         # Log file name            # Append mode (use 'w' to overwrite)
    level=logging.INFO,          # Minimum level to log
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler('logs/'+ now+'.log'),          # Log to file
        logging.StreamHandler()                 # Log to console (terminal)
    ]
)

open_ai_key = os.environ['OPENAI_API_KEY']
# Path to the PDF form
pdf_path = "resources/Term/Term-3-Singlife.pdf" 
# pdf_id = 'file-VWsgoAhsmzuz4hMXmBye1x' #Term-1-CTP
pdf_id = 'file-EddV8AV4q9dmStBwaK4Tcn' #Term-2-Singlife


# logging.info("Classifing document...")
classifier_agent = PolicyClassifierAgent(open_ai_key)
policy_type = classifier_agent.classify(file_path=pdf_path)
logging.info(str(policy_type))


# Term agent
logging.info("Extracting term document data...")
term_agent = DocumentTermAgent(open_ai_key)
doc = term_agent.extract(file_path=pdf_path)

