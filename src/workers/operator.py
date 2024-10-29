import logging

from ollama import Client

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

endpoint = "http://ollama:11434"


class Operator:
    def __init__(self):
        self.client = Client(host=endpoint)
        self.model = "gemma2:latest"

    def ask(self, question):
        try:
            messages = [{'role': 'user', 'content': question}]
            response = self.client.chat(
                model=self.model,
                messages=messages
            )
            return response["message"]["content"].replace("\n", " ").replace("  ", " ")
        except Exception as e:
            logging.error(f"Error asking question: {e}, {endpoint}")
            return None
