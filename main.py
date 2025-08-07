from PolicyClassifierAgent import PolicyClassifierAgent
import logging
from datetime import datetime
import json
from DocumentTermAgent import DocumentTermAgent
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

open_ai_key = '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'
# Path to the PDF form
pdf_path = "resources/Term-CTP.pdf" #fileid = 'file-VWsgoAhsmzuz4hMXmBye1x'
pdf_id = 'file-VWsgoAhsmzuz4hMXmBye1x'


# logging.info("Classifing document...")
# classifier_agent = PolicyClassifierAgent(open_ai_key)
# policy_type = classifier_agent.classify(file_id=pdf_id)
# logging.info(str(policy_type))

# logging.info("Extracting term document data...")
term_agent = DocumentTermAgent(open_ai_key)
doc = term_agent.extract(file_id=pdf_id)


# Term agent


