import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re

# Fonction pour nettoyer les requêtes de recherche
def sanitize_query(query):
    return re.sub(r'[^\w\s%&]', '', query)

# Fonction générique pour récupérer les résultats d'un moteur de recherche
def fetch_search_results(search_url, headers, retries=3):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.get(search_url, headers=headers)
            if response.status_code == 200:
                return response.text
            elif response.status_code == 403:
                print(f"Erreur 403. Tentative {attempt + 1}. Attente avant nouvelle tentative.")
            else:
                print(f"Erreur {response.status_code}. Tentative {attempt + 1}.")
            attempt += 1
            wait_time = 2 ** attempt
            time.sleep(wait_time)
        except Exception as e:
            print(f"Erreur lors de la requête : {e}")
            attempt += 1
            time.sleep(2 ** attempt)
    print(f"Échec après {retries} tentatives.")
    return None

# Fonction pour extraire les résultats
def parse_search_results(html_content, result_selector, title_selector, link_selector, snippet_selector):
    soup = BeautifulSoup(html_content, 'html.parser')
    search_results = []
    for g in soup.select(result_selector):
        title = g.select_one(title_selector).text if g.select_one(title_selector) else 'No title'
        link = g.select_one(link_selector)['href'] if g.select_one(link_selector) else 'No link'
        snippet_tag = g.select_one(snippet_selector)
        snippet = snippet_tag.text if snippet_tag else 'Snippet non disponible'
        search_results.append({
            "title": title,
            "snippet": snippet,
            "link": link
        })
    return search_results

# Fonction pour sauvegarder les résultats dans un fichier tout en évitant les doublons
def save_results_to_file(results, filename="result.txt"):
    if not results:
        print("Aucun résultat à sauvegarder.")
        return

    existing_links = set()
    try:
        with open(filename, "r", encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line.strip())
                    existing_links.add(data["link"])
                except json.JSONDecodeError:
                    print("Erreur lors du parsing JSON dans le fichier existant. Ignorer les lignes mal formatées.")
    except FileNotFoundError:
        pass  # Le fichier n'existe pas, pas besoin de faire quoi que ce soit
    except UnicodeDecodeError:
        with open(filename, "r", encoding='latin-1') as file:
            for line in file:
                try:
                    data = json.loads(line.strip())
                    existing_links.add(data["link"])
                except json.JSONDecodeError:
                    print("Erreur lors du parsing JSON dans le fichier existant. Ignorer les lignes mal formatées.")

    try:
        with open(filename, "a", encoding='utf-8') as file:
            for result in results:
                if result["link"] not in existing_links:
                    file.write(json.dumps(result, ensure_ascii=False) + "\n")
                    existing_links.add(result["link"])
    except IOError as e:
        print(f"Erreur lors de l'écriture dans le fichier {filename}: {e}")

# Fonction pour extraire les mots-clés des titres et snippets dans result.txt
def extract_keywords_from_file(filename="result.txt"):
    keywords = set()
    try:
        with open(filename, "r", encoding='utf-8') as file:
            for line in file:
                try:
                    data = json.loads(line.strip())
                    title_words = data.get("title", "").split()
                    snippet_words = data.get("snippet", "").split()
                    keywords.update(title_words)
                    keywords.update(snippet_words)
                except json.JSONDecodeError:
                    print("Erreur lors du parsing JSON : ligne ignorée.")
    except FileNotFoundError:
        print(f"{filename} n'existe pas encore.")
    except UnicodeDecodeError:
        with open(filename, "r", encoding='latin-1') as file:
            for line in file:
                try:
                    data = json.loads(line.strip())
                    title_words = data.get("title", "").split()
                    snippet_words = data.get("snippet", "").split()
                    keywords.update(title_words)
                    keywords.update(snippet_words)
                except json.JSONDecodeError:
                    print("Erreur lors du parsing JSON : ligne ignorée.")
    return list(keywords)

# Fonction de recherche Google
def search_google(query, num_results=5, retries=3):
    search_url = f"https://www.google.com/search?q={query}&num={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    html_content = fetch_search_results(search_url, headers, retries)
    if html_content:
        return parse_search_results(html_content, 'div.tF2Cxc', 'h3', 'a', 'span.aCOpRe, div.VwiC3b')
    return []

# Boucle de recherche automatique
search_interval = 8  # Intervalle de 8 secondes entre chaque recherche

while True:
    search_queries = extract_keywords_from_file()

    if search_queries:
        for _ in range(3):  # Limiter le nombre de requêtes par itération
            query = random.choice(search_queries)
            sanitized_query = sanitize_query(query)

            if sanitized_query:
                print(f"Recherche avec la requête: '{sanitized_query}'")

                google_results = search_google(sanitized_query, num_results=5)

                if google_results:
                    save_results_to_file(google_results)
                    print(f"Résultats pour '{sanitized_query}' enregistrés dans 'result.txt'.")
                else:
                    print(f"Aucun résultat trouvé pour '{sanitized_query}'.")

                time.sleep(search_interval)
            else:
                print("La requête après nettoyage est vide.")
                time.sleep(search_interval)
    else:
        print("Aucun mot-clé trouvé pour lancer une nouvelle recherche.")
        time.sleep(search_interval)
