class Personne:
    def __init__(self, nom: str, prenom: str, dateNaissance: str, qualite: str = None):
        self.nom = nom
        self.prenom = prenom
        self.dateNaissance = dateNaissance
        self.qualite = qualite

    def to_dict(self, visited=None):
        return {
            "nom": self.nom,
            "prenom": self.prenom,
            # "dateNaissance": self.dateNaissance,
            "qualite": self.qualite
        }

    def __repr__(self):
        return f"{self.nom} {self.prenom}"


class Organisation:
    def __init__(
            self,
            siren: str,
            raisonSociale: str,
            dateCreation: str,
            dateFermeture: str,
            adresse: str,
            activite: str,
            qualite: str = None,
            dirigeants: list = None
    ):
        self.siren = siren
        self.raisonSociale = raisonSociale
        self.dateCreation = dateCreation
        self.dateFermeture = dateFermeture
        self.adresse = adresse
        self.activite = activite
        self.qualite = qualite
        self.dirigeants = list(dirigeants) if dirigeants else []
    
    def dirigeants_to_dict(self, visited):
        dirigeants_dicts = []
        for dirigeant in self.dirigeants:
            if isinstance(dirigeant, (Personne, Organisation)):
                dirigeants_dicts.append(dirigeant.to_dict(visited))
            else:
                print("Dirigeant non sérialisable, ajout en tant que string : ", dirigeant)
                dirigeants_dicts.append(str(dirigeant))
        return dirigeants_dicts

    def to_dict(self, visited=None):

        if visited is None:
            visited = set()

        if self.siren in visited:
            return {"siren": self.siren}
        
        visited.add(self.siren)
        return {
            "siren": self.siren,
            "raisonSociale": self.raisonSociale,
            "dateCreation": self.dateCreation,
            "dateFermeture": self.dateFermeture,
            "adresse": self.adresse,
            "activite": self.activite,
            "qualite": self.qualite,
            "dirigeants": self.dirigeants_to_dict(visited)
        }

    def __repr__(self):
        return (
            f"{self.raisonSociale} :\n"
            f"{self.siren}\n"
            f"{self.adresse}\n"
            f"Activité: {self.activite}\n"
            f"Création: {self.dateCreation}\n"
            f"Fermeture: {self.dateFermeture}"
        )