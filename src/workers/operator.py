import logging

from ollama import Client, chat

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

endpoint = "http://localhost:11434"

class Operator:
    def __init__(self):
        self.model = "gemma2:latest"
        self.client = Client(host=endpoint)

    def ask(self, question):
        try:
            messages = [
                {
                    'role': 'user',
                    'content': question,
                },
            ]
            response = chat(model=self.model, messages=messages)
            logging.info(response)
            return response
        except Exception as e:
            logging.error(f"Error asking question: {e}, {endpoint}")
            return None