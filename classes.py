import json
from pyvis.network import Network

class Personne:
    def __init__(self, nom: str, prenom: str, datNaissance: str, qualite: str = None):
        self.nom = nom
        self.prenom = prenom
        self.datNaissance = datNaissance
        self.qualite = qualite

    def to_dict(self):
        return {
            "nom": self.nom,
            "prenom": self.prenom,
            "datNaissance": self.datNaissance,
            "qualite": self.qualite
        }

    def to_html(self):
        return f"""
        <div style='width:200px'>
            <h3>👤 Personne</h3>
            <b>{self.prenom} {self.nom}</b><br>
            Né(e) : {self.datNaissance}
            <b>Qualité :</b> {self.qualite}<br>
        </div>
        """

    def __repr__(self):
        return f"{self.nom} {self.prenom} né(e) {self.datNaissance} ({self.qualite})"


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
    
    def dirigeants_to_dict(self):
        dirigeants_dicts = []
        for dirigeant in self.dirigeants:
            if isinstance(dirigeant, Personne) or isinstance(dirigeant, Organisation):
                dirigeants_dicts.append(dirigeant.to_dict())
            else:
                print("Dirigeant non sérialisable, ajout en tant que string : ", dirigeant)
                dirigeants_dicts.append(str(dirigeant))
        return dirigeants_dicts

    def to_dict(self):
        return {
            "siren": self.siren,
            "raisonSociale": self.raisonSociale,
            "dateCreation": self.dateCreation,
            "dateFermeture": self.dateFermeture,
            "adresse": self.adresse,
            "activite": self.activite,
            "qualite": self.qualite,
            "dirigeants": self.dirigeants_to_dict()
        }

    def to_html(self):
        return f"""
          <div style='width:300px'>
              <h2>🏢 {self.raisonSociale}</h2>
              <b>SIREN :</b> {self.siren}<br>
              <b>Activité :</b> {self.activite}<br>
              <b>Adresse :</b> {self.adresse}<br>
              <b>Qualité :</b> {self.qualite}<br>
          </div>
          """

    def __repr__(self):
        return (
            f"  siren: {self.siren!r},\n"
            f"  raisonSociale: {self.raisonSociale!r},\n"
            f"  dateCreation: {self.dateCreation!r},\n"
            f"  dateFermeture: {self.dateFermeture!r},\n"
            f"  adresse: {self.adresse!r},\n"
            f"  activite: {self.activite!r}\n"
            f"  qualite: {self.qualite!r}\n"
            f"  dirigeants: {self.dirigeants!r}\n\n"
        )