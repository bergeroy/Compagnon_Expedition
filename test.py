import asyncio
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
# Importez la classe de configuration du fournisseur
from pydantic_ai.providers.openai import OpenAIProvider

# 1. On initialise le Provider (sans client, il utilise ses propres arguments)
# Dans les dernières versions, on passe directement les paramètres réseau ici
my_provider = OpenAIProvider(
    base_url='http://localhost:1234/v1',
    api_key='lm-studio'
)

# 2. On l'injecte dans le modèle
local_model = OpenAIChatModel(
    model_name='meta-llama-3.1-8b-instruct',
    provider=my_provider
)

# 3. L'agent
agent = Agent(model=local_model)

# --- Test rapide ---
async def test():
    result = await agent.run("Bonjour !")
    print(result.response.text)

if __name__ == "__main__":
    asyncio.run(test())