from PolicyClassifierAgent import PolicyClassifierAgent

open_ai_key = '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'
# Path to the PDF form
pdf_path = "resources/Term-CTP.pdf" #fileid = 'file-VWsgoAhsmzuz4hMXmBye1x'
pdf_id = 'file-VWsgoAhsmzuz4hMXmBye1x'

classifier_agent = PolicyClassifierAgent(open_ai_key)

policy_type = classifier_agent.classify(file_id=pdf_id)

