import json

def clean_json_file(input_file, output_file):
    cleaned_data = []
    
    # Ouverture du fichier avec une gestion d'encodage flexible
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()  # Supprime les espaces ou les nouvelles lignes
                if line:  # Vérifie que la ligne n'est pas vide
                    try:
                        # Tente de charger chaque ligne comme un objet JSON
                        json_data = json.loads(line)
                        cleaned_data.append(json_data)  # Ajoute à la liste si c'est valide
                    except json.JSONDecodeError:
                        print(f"Ligne mal formée ignorée : {line}")  # Affiche l'erreur pour les lignes mal formées

    except UnicodeDecodeError:
        # Si 'utf-8' échoue, réessaie avec 'latin-1' ou 'windows-1252'
        with open(input_file, 'r', encoding='latin-1') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        json_data = json.loads(line)
                        cleaned_data.append(json_data)
                    except json.JSONDecodeError:
                        print(f"Ligne mal formée ignorée : {line}")

    # Enregistrement des données nettoyées dans un nouveau fichier
    with open(output_file, 'w', encoding='utf-8') as f_out:
        json.dump(cleaned_data, f_out, ensure_ascii=False, indent=4)
    
    print(f"Fichier nettoyé sauvegardé dans {output_file}")

# Utilisation du script
input_file = 'result.txt'  # Nom du fichier d'entrée
output_file = 'result_cleaned.json'  # Nom du fichier de sortie
clean_json_file(input_file, output_file)
