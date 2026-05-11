from functions import *
import graphviz


def define_node_id(object):
    """Define a unique node ID based on the object's type and attributes."""
    if isinstance(object, Organisation):
        return f"org_{object.siren}"
    elif isinstance(object, Personne):
        person_id = f"person_{object.nom}_{object.prenom}"
        if object.dateNaissance:
            person_id += f"_{object.dateNaissance.replace('-', '')}"
        return person_id
    else:
        return f"node_{id(object)}"

def define_node_color(object):
    """Define a color for the node based on the object's type."""
    if isinstance(object, Organisation):
        return ["#1E3A5F", "#F8FAFC"]
    elif isinstance(object, Personne):
        return ["#5B2156", "#F8FAFC"]
    else:
        return ["lightgray", "white"]

def define_node_shape(object):
    """Define a shape for the node based on the object's type."""
    if isinstance(object, Organisation):
        return "box"
    elif isinstance(object, Personne):
        return "ellipse"
    else:
        return "oval"

def define_edge_label(dirigeant):
    """Define a label for the edge based on the dirigeant's quality."""
    return dirigeant.qualite if dirigeant.qualite else "Dirigeant"

def add_nodes_and_edges(dot, organisations, visited=None):
    """Add nodes and edges to the graphviz Digraph based on the organisations."""

    # Use a set to track visited nodes to avoid duplicates
    if visited is None:
        visited = set()

    for obj in organisations:
        obj_id = define_node_id(obj)
        if obj_id in visited: 
            continue

        visited.add(obj_id)
        
        label = str(obj)
        colors = define_node_color(obj)
        shape = define_node_shape(obj)

        dot.node(obj_id, label=label, style="filled", fillcolor=colors[0], shape=shape, fontcolor=colors[1])
        if isinstance(obj, Organisation):

            for dirigeant in obj.dirigeants:
                dirigeant_id = define_node_id(dirigeant)
                dot.edge(obj_id, dirigeant_id, label=define_edge_label(dirigeant), fillcolor="#94A3B8", fontcolor="#CBD5E1")
                #recusion
                add_nodes_and_edges(dot, [dirigeant], visited=visited)
                
def define_dot():
    dot = graphviz.Digraph("G")

    # Structure générale
    dot.attr(
        rankdir="LR",
        splines="spline",
        bgcolor="#0F172A",
        nodesep="0.6",
        ranksep="1",
        overlap="false",
        concentrate="true",
        width="100%",
        height="100%"
    )

    # Style des nodes
    dot.attr(
        "node",
        style="filled,rounded",
        shape="box",
        fontname="Helvetica",
        fontsize="11",
        color="#D0D7DE",
        penwidth="1.2"
    )

    # Style des edges
    dot.attr(
        "edge",
        color="#7F8C8D",
        penwidth="1.3",
        fontname="Helvetica",
        fontsize="9"
    )
    return dot
