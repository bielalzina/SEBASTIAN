import dotenv
import os
import json

def load_config():
    dotenv.load_dotenv()
    with open('sebastian.json', 'r') as f:
        return json.load(f)

config = load_config()

# Aqui aniran les definicions de les skills/eines
# Totes les skills es registraran en un diccionari central.
