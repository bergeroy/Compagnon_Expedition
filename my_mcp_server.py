import os
from mcp.server.fastmcp import FastMCP

# 1. Initialisation du serveur
# FastMCP est une couche simplifiée pour créer des serveurs rapidement
mcp = FastMCP("MonServeurLocal")

# 2. Définition d'un outil (Tool)
# La docstring (les commentaires) est CRUCIALRE : c'est ce que Gemini lira.
@mcp.tool()
def read_local_file(path: str) -> str:
    """
    Lit le contenu d'un fichier texte sur le disque local de l'utilisateur.
    Le chemin doit être complet ou relatif au dossier de travail.
    """
    try:
        # Mesure de sécurité : limiter l'accès à certains dossiers si nécessaire
        if not os.path.exists(path):
            return f"Erreur : Le fichier {path} n'existe pas."
            
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Erreur lors de la lecture : {str(e)}"

@mcp.tool()
def list_directory(path: str = ".") -> list[str]:
    """Liste les fichiers et dossiers dans un répertoire spécifique."""
    try:
        return os.listdir(path)
    except Exception as e:
        return [f"Erreur : {str(e)}"]

@mcp.tool()
def get_mock_weather_api(city: str):
    """
    Récupère la météo en temps réel pour une ville donnée.
    """
    print(f"\n[ACTION] L'agent appelle l'API pour : {city}")
    # Simulation d'une base de données ou API
    db = {
        "Québec": {"temp": 15.0, "cond": "nuageux"},
        "Athènes": {"temp": 28.0, "cond": "soleil"},
        "Trois-Pistoles": {"temp": 12.0, "cond": "pluie"}
    }
    data = db.get(city, {"temp": 20.0, "cond": "inconnu"})
    return f"Il fait {data['temp']}°C à {city} avec un ciel {data['cond']}."

# 3. Lancement du serveur
if __name__ == "__main__":
    # Le mode "stdio" est le standard pour les serveurs locaux
    mcp.run(transport="stdio")

    