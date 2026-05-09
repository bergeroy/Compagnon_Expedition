import asyncio
import os
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 1. Configuration du modèle local (LM Studio)
my_provider = OpenAIProvider(
    base_url='http://localhost:1234/v1',
    api_key='lm-studio'
)

local_model = OpenAIChatModel(
    model_name='meta-llama-3.1-8b-instruct',
    provider=my_provider
)

# 2. Définition de l'Agent
agent = Agent(
    model=local_model,
    system_prompt=(
        "Tu es l'assistant personnel d'Yves. "
        "Tu as accès à sa collection de livres via l'outil 'rechercher_livre'. "
        "Utilise cet outil pour trouver des informations dans son fichier XML."
    )
)

async def main():
    # 3. Paramètres du serveur MCP (votre script XML)
    server_params = StdioServerParameters(
        command=r".venv\Scripts\python.exe",
        args=["mcp_servers/sf_library_mcp.py"], 
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialisation de la connexion avec le serveur MCP
            await session.initialize()
            
            # Note pour le développement : 
            # Pour que l'agent utilise l'outil du serveur, nous devons 
            # l'enregistrer. Dans Pydantic-AI, on peut définir un outil 
            # qui appelle la session MCP.
            
            @agent.tool
            async def rechercher_livre(ctx, critere: str | dict):
               """
               Outil permettant de rechercher dans la bibliothèque d'Yves.
               L'argument 'critere' peut être un nom d'auteur, un titre ou un mot-clé.
               """
               # 1. On normalise l'entrée pour gérer les erreurs de format de Llama
               if isinstance(critere, dict):
                   search_term = critere.get("critere", "")
               else:
                   search_term = critere

               # 2. On appelle la fonction REELLE qui se trouve sur votre serveur MCP
               # C'est ici que le pont se fait vers votre code de recherche XML
               result = await session.call_tool(
                   "rechercher_livre", 
                   arguments={"critere": search_term}
               )
    
               # 3. On renvoie les résultats (les 10 livres) à Llama
               return result.content

            # 4. Test réel sur votre collection
            query = "Quels livres de Vonda McIntyre ai-je dans ma collection ?"
            print(f"\nRequête d'Yves : {query}")
            
            result = await agent.run(query)
            
            # Utilisation de la structure validée par vos tests
            print(f"\nRéponse de l'IA :\n{result.response.text}")

if __name__ == "__main__":
    asyncio.run(main())