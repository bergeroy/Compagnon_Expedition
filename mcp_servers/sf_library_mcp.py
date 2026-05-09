import lxml.etree as ET
from typing import List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

load_dotenv()

# --- 1. Modèles de données ---

class Story(BaseModel):
    title: str
    author: str

class SFBook(BaseModel):
    id: str
    title: str
    publisher: Optional[str]
    year: Optional[str]
    plot: Optional[str]
    series: Optional[str]
    stories: List[Story] = []
    main_authors: List[str] = []

# --- 2. Initialisation du Serveur et du Cache ---

# Création du serveur MCP
mcp = FastMCP("SF-Library-Manager")

# Cache global en mémoire pour éviter de relire le XML à chaque fois
BIBLIOTHEQUE_CACHE: List[SFBook] = []

def charger_donnees_xml():
    """Charge le XML une seule fois en mémoire au démarrage."""
    global BIBLIOTHEQUE_CACHE
    path = os.getenv("PATH_COLLECTION_SF") 
    
    try:
        tree = ET.parse(path)
        root = tree.getroot()
        temp_list = []

        for book_node in root.xpath("//book"):
            main = book_node.find("mainsection")
            
            # Extraction auteurs
            main_authors = [a.text for a in main.xpath("authors/author/person/displayname") if a.text]
            
            # Extraction nouvelles
            stories = []
            for section in book_node.xpath("sections/section"):
                s_title = section.findtext("title")
                s_author = section.xpath("authors/author/person/displayname/text()")
                stories.append(Story(title=s_title, author=s_author[0] if s_author else "Inconnu"))

            temp_list.append(SFBook(
                id=book_node.findtext("id"),
                title=main.findtext("title") if main is not None else "Sans titre",
                publisher=book_node.xpath("string(publisher/displayname)"),
                year=book_node.xpath("string(publicationdate/year/displayname)"),
                plot=main.findtext("plot") if main is not None else "",
                series=main.xpath("string(series/displayname)"),
                stories=stories,
                main_authors=main_authors
            ))
        BIBLIOTHEQUE_CACHE = temp_list
        print(f"Indexation terminée : {len(BIBLIOTHEQUE_CACHE)} livres chargés.")
    except Exception as e:
        print(f"Erreur de chargement XML : {e}")

# --- 3. Définition des Outils pour l'IA ---

@mcp.tool()
async def rechercher_livre(critere: str) -> List[SFBook]:
    """
    Recherche un livre ou une nouvelle dans la bibliothèque par titre, auteur ou résumé.
    L'IA utilisera cet outil pour répondre aux questions sur la collection.
    """
    critere = critere.lower()
    resultats = []

    for livre in BIBLIOTHEQUE_CACHE:
        # Cherche dans le titre du livre
        in_title = critere in livre.title.lower()
        # Cherche dans les auteurs
        in_authors = any(critere in a.lower() for a in livre.main_authors)
        # Cherche dans les titres de nouvelles
        in_stories = any(critere in s.title.lower() or critere in s.author.lower() for s in livre.stories)
        # Cherche dans le résumé
        in_plot = critere in (livre.plot or "").lower()

        if in_title or in_authors or in_stories or in_plot:
            resultats.append(livre)

    return resultats[:10] # On limite à 10 pour ne pas saturer le contexte de l'IA

# --- 4. Lancement ---

if __name__ == "__main__":
    # On charge les données avant de lancer le serveur
    charger_donnees_xml()
    # Lancement du serveur (par défaut en mode STDIO pour être utilisé par les agents)
    mcp.run()