import os
import json
import httpx
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def search_duckduckgo(query):
    # Usant DuckDuckGo HTML per evitar tokens d'API de moment
    # O un simple scraper de DDG
    url = f"https://duckduckgo.com/html/?q={query}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        # Processar HTML simple per treure resultats rellevants
        # En una versió més robusta usaríem una llibreria de cerques
        # De moment, retornem un resum del que ha trobat (emulat)
        return {"query": query, "url": url, "results": "Resultats generats via DDG HTML..."}

if __name__ == "__main__":
    if len(os.sys.argv) > 1:
        query = os.sys.argv[1]
        print(json.dumps(asyncio.run(search_duckduckgo(query))))
