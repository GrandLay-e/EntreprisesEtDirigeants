"""Graph construction and visualization functions for organisations and leaders."""

from pyvis.network import Network
from classes import Personne, Organisation


def build_graph_from_research(organisations: list, visited_ids=None) -> dict:
    """
    Convert deep_research results (list of Organisation objects) into a graph structure.
    
    Args:
        organisations: List of Organisation objects from deep_research()
        visited_ids: Set to track already processed nodes (prevents duplicates)
    
    Returns:
        Dictionary with nodes and edges for graph visualization
    """
    if visited_ids is None:
        visited_ids = set()
    
    graph = {
        "nodes": {},
        "edges": []
    }
    
    for org in organisations:
        _add_organisation_to_graph(org, graph, visited_ids)
    
    return graph


def _add_organisation_to_graph(org: Organisation, graph: dict, visited_ids: set) -> None:
    """
    Recursively add an organisation and its leaders to the graph.
    
    Args:
        org: Organisation object to add
        graph: Graph dictionary to update
        visited_ids: Set of already processed node IDs
    """
    org_id = org.siren
    
    # Avoid duplicate nodes
    if org_id in visited_ids:
        return
    
    visited_ids.add(org_id)
    
    # Add organisation node
    graph["nodes"][org_id] = {
        "id": org_id,
        "label": org.raisonSociale,
        "type": "organisation",
        "data": {
            "siren": org.siren,
            "raison_sociale": org.raisonSociale,
            "date_creation": org.dateCreation,
            "date_fermeture": org.dateFermeture,
            "adresse": org.adresse,
            "activite": org.activite
        }
    }
    
    # Process leaders (dirigeants)
    for dirigeant in org.dirigeants:
        if isinstance(dirigeant, Personne):
            _add_personne_to_graph(dirigeant, graph, visited_ids)
            # Create edge: organisation -> person
            personne_id = _get_personne_id(dirigeant)
            graph["edges"].append({
                "source": org_id,
                "target": personne_id,
                "type": "manages",
                "label": dirigeant.qualite or "Dirigeant"
            })
        
        elif isinstance(dirigeant, Organisation):
            _add_organisation_to_graph(dirigeant, graph, visited_ids)
            # Create edge: organisation -> organisation
            graph["edges"].append({
                "source": org_id,
                "target": dirigeant.siren,
                "type": "manages",
                "label": dirigeant.qualite or "Dirigeant"
            })


def _add_personne_to_graph(personne: Personne, graph: dict, visited_ids: set) -> None:
    """
    Add a person node to the graph.
    
    Args:
        personne: Personne object to add
        graph: Graph dictionary to update
        visited_ids: Set of already processed node IDs
    """
    personne_id = _get_personne_id(personne)
    
    if personne_id in visited_ids:
        return
    
    visited_ids.add(personne_id)
    
    graph["nodes"][personne_id] = {
        "id": personne_id,
        "label": f"{personne.prenom} {personne.nom}",
        "type": "personne",
        "data": {
            "nom": personne.nom,
            "prenom": personne.prenom,
            "date_naissance": personne.datNaissance,
            "qualite": personne.qualite
        }
    }


def _get_personne_id(personne: Personne) -> str:
    """Generate unique ID for a person based on their attributes."""
    return f"personne_{personne.nom}_{personne.prenom}_{personne.datNaissance or 'unknown'}".replace(" ", "_")


def graph_to_vis_format(graph: dict) -> dict:
    """
    Convert internal graph structure to vis.js compatible format.
    
    Args:
        graph: Graph dictionary from build_graph_from_research()
    
    Returns:
        Dictionary with 'nodes' (list) and 'edges' (list) for vis.js Network
    """
    vis_nodes = []
    vis_edges = []
    
    # Convert nodes
    for node_id, node_data in graph["nodes"].items():
        color = "#FF9999" if node_data["type"] == "personne" else "#99CCFF"
        shape = "dot" if node_data["type"] == "personne" else "box"
        
        vis_nodes.append({
            "id": node_id,
            "label": node_data["label"],
            "title": node_data["label"],
            "color": color,
            "shape": shape,
            "data": node_data["data"]
        })
    
    # Convert edges
    for edge in graph["edges"]:
        vis_edges.append({
            "from": edge["source"],
            "to": edge["target"],
            "label": edge["label"],
            "arrows": "to",
            "color": {"color": "#333333", "opacity": 0.5}
        })
    
    return {
        "nodes": vis_nodes,
        "edges": vis_edges
    }


def add_nodes_and_edges_to_network(graph: dict, net: Network) -> None:
    """
    Add nodes and edges from internal graph structure to a vis.js Network.
    
    Args:
        graph: Graph dictionary from build_graph_from_research()
        net: pyvis.network.Network instance
    """
    # Add nodes
    for node_id, node_data in graph["nodes"].items():
        is_personne = node_data["type"] == "personne"
        color = "#FF9999" if is_personne else "#99CCFF"
        shape = "dot" if is_personne else "box"
        size = 25 if is_personne else 30
        
        if node_data["type"] == "personne":
            title = f"{node_data['label']}\nDate de naissance: {node_data['data']['date_naissance']}\nQualité: {node_data['data']['qualite']}"
        else:
            title = f"{node_data['label']}\nAdresse: {node_data['data']['adresse']}\nActivité: {node_data['data']['activite']}"
        net.add_node(
            node_id,
            label=node_data["label"],
            title=title,
            color=color,
            shape=shape,
            size=size,
            font={"size": 16, "color": "white"},
            borderWidth=2
        )
    
    # Add edges
    for edge in graph["edges"]:
        net.add_edge(
            edge["source"],
            edge["target"],
            label=edge["label"],
            arrows="to",
            font={"size": 14, "color": "white"},
            width=2
        )


def graph_to_json_structure(organisations: list) -> dict:
    """
    Convert organisations to JSON-serializable structure with hierarchy.
    
    Args:
        organisations: List of Organisation objects
    
    Returns:
        Dictionary with hierarchical structure for export
    """
    result = {}
    
    for org in organisations:
        org_data = {
            "siren": org.siren,
            "raison_sociale": org.raisonSociale,
            "date_creation": org.dateCreation,
            "date_fermeture": org.dateFermeture,
            "adresse": org.adresse,
            "activite": org.activite,
            "dirigeants": []
        }
        
        for dirigeant in org.dirigeants:
            if isinstance(dirigeant, Personne):
                org_data["dirigeants"].append({
                    "type": "personne",
                    "nom": dirigeant.nom,
                    "prenom": dirigeant.prenom,
                    "date_naissance": dirigeant.datNaissance,
                    "qualite": dirigeant.qualite
                })
            elif isinstance(dirigeant, Organisation):
                org_data["dirigeants"].append({
                    "type": "organisation",
                    "siren": dirigeant.siren,
                    "raison_sociale": dirigeant.raisonSociale,
                    "qualite": dirigeant.qualite
                })
        
        result[org.siren] = org_data
    
    return result


def get_graph_statistics(graph: dict) -> dict:
    """
    Generate statistics about the graph.
    
    Args:
        graph: Graph dictionary from build_graph_from_research()
    
    Returns:
        Dictionary with graph statistics
    """
    organisations = [n for n in graph["nodes"].values() if n["type"] == "organisation"]
    personnes = [n for n in graph["nodes"].values() if n["type"] == "personne"]
    
    return {
        "total_nodes": len(graph["nodes"]),
        "total_organisations": len(organisations),
        "total_personnes": len(personnes),
        "total_edges": len(graph["edges"]),
        "graph_density": len(graph["edges"]) / (len(graph["nodes"]) * (len(graph["nodes"]) - 1) / 2) if len(graph["nodes"]) > 1 else 0
    }