# Entreprises Et Dirigeants

Outil pour explorer, sérialiser et visualiser la structure hiérarchique des entreprises françaises et de leurs dirigeants à partir des données publiques INSEE et de l'API Recherche d'entreprises.

## Présentation

Le projet récupère une entreprise à partir d'un SIREN ou d'une recherche textuelle, puis explore récursivement ses dirigeants et les organisations liées. Les résultats sont exportés en JSON et en graphe Graphviz au format SVG, PNG ou PDF.

## Fonctionnalités

- Recherche par SIREN ou par texte
- Exploration récursive des organisations et des dirigeants
- Génération d'un graphe orienté des relations hiérarchiques
- Export en SVG, PNG ou PDF
- Sérialisation JSON des données récupérées
- Gestion des cycles dans les relations entre organisations
- Cache des codes d'activité pour réduire le nombre de requêtes

## Prérequis

- Python 3.8 ou plus récent
- Le module Python `requests`
- Le module Python `beautifulsoup4`
- Le module Python `graphviz`
- Le binaire système Graphviz (`dot`), indispensable pour générer le rendu

## Installation

### Linux Debian / Ubuntu

```bash
git clone https://github.com/GrandLay-e/EntreprisesEtDirigeants.git
cd EntreprisesEtDirigeants
sudo apt update
sudo apt install -y graphviz
python3 -m pip install -r requirements.txt
```
#### _NB_ : si vous avez un autre gestionnaire de paquets, adaptez la commande d'installation de Graphviz.

### Windows

Avec Winget :

```powershell
git clone https://github.com/GrandLay-e/EntreprisesEtDirigeants.git
cd EntreprisesEtDirigeants
winget install Graphviz.Graphviz
python -m pip install -r requirements.txt
```

Avec Chocolatey :

```powershell
git clone https://github.com/GrandLay-e/EntreprisesEtDirigeants.git
cd EntreprisesEtDirigeants
choco install graphviz
python -m pip install -r requirements.txt
```

Si le chemin vers `dot.exe` n'est pas dans le `PATH`, le rendu du graphe échouera même si le paquet Python est installé.

## Utilisation

### Recherche par SIREN

```bash
python main.py -s 985180215 -o svg
```

### Recherche textuelle

```bash
python main.py -r "github france" -o svg
```

### Formats de sortie (optionnels)

- `-o svg` : sortie SVG, format par défaut
- `-o png` : sortie PNG
- `-o pdf` : sortie PDF

### Aide

```bash
python main.py -h
python main.py --help
```

## Sorties générées

Chaque exécution crée un dossier dans `outputs/<requete>/` contenant :

- `graph.svg`, `graph.png` ou `graph.pdf` : le graphe des relations
- `response.json` : les données sérialisées complètes
- `not_completed.json` : les données partielles en cas d'erreur ou d'arrêt

### Graphe

- Les organisations sont affichées en rectangles
- Les personnes sont affichées en ellipses
- Les arêtes portent la qualité du dirigeant
- Le graphe est orienté de gauche à droite

Exemple de rendu :

![Exemple Github France](exemple/github%20france/graph.svg)

### JSON

Exemple de structure (GITHUB FRANCE) :

```json
[
    {
        "siren": "985180215",
        "raisonSociale": "GITHUB FRANCE",
        "dateCreation": "2024-02-27",
        "dateFermeture": null,
        "adresse": "37 QUAI DU PRESIDENT ROOSEVELT 92130 ISSY-LES-MOULINEAUX",
        "activite": "Programmation informatique",
        "qualite": null,
        "dirigeants": [
            {
                "nom": "DOLLIVER",
                "prenom": "KEITH RANGER",
                "qualite": "Directeur Général"
            },
            {
                "nom": "GAUTHIER",
                "prenom": "FABIEN LAURENT",
                "qualite": "Président de SAS"
            },
            {
                "nom": "ORNDORFF",
                "prenom": "BENJAMIN OWEN",
                "qualite": "Directeur Général"
            }
        ]
    }
]
```

## Structure du projet

```text
classes.py          Modèles de données Personne et Organisation
functions.py        Récupération des données, sérialisation et parsing CLI
graph_functions.py  Construction et mise en forme des graphes
main.py             Point d'entrée de l'application
CONSTS.py           Constantes de configuration
requirements.txt    Dépendances Python
outputs/            Dossiers de sortie générés
exemple/            Exemples de résultats
```

## Optimisations

- Cache LRU sur les codes d'activité pour éviter les requêtes répétées
- Réutilisation d'une session HTTP sur les appels récursifs
- Déduplication des nœuds du graphe via un identifiant sémantique
- Détection des cycles dans les organisations liées

## Exemples

- `exemple/github france/` : exemple complet d'exécution et de rendu
- `outputs/` : dossiers créés par les exécutions locales

## Licence
Projet open source sous licence MIT.

# Auteur : Grand Laye
