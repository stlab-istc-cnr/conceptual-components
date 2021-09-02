from rdflib import *
import os
from utils import getID


# Create an rdf graph from a string containing one uri (or local path)
# or more space separated uris (or local paths), without specifying their format
def create_rdf_graph(url):
    graph = Graph()
    for i in url.split():
        try:
            graph.parse(i, format="application/rdf+xml")
        except:
            try:
                graph.parse(i, format="turtle")
            except:
                print("error with ontology:", i)
                pass
    return graph


# Create an rdf graph from a txt containing one uri (or the local path of a file)
# or more uris, each per line, without specifying their format
def create_rdf_graph_from_txt(url_txt):
    graph = Graph()
    with open(url_txt) as txt:
        for count, line in enumerate(txt):
            url = line.split("\n")[0]
            try:
                graph.parse(url, format="application/rdf+xml")
            except:
                try:
                    graph.parse(url, format="turtle")
                except:
                    print("error with ontology:", url)
                    pass
    return graph


# Create an rdf graph from a directory containing one or more ontology files
def create_rdf_graph_from_directory(directory):
    graph = Graph()
    for file in os.listdir(directory):
        try:
            graph.parse(directory + file, format="application/rdf+xml")
        except:
            try:
                graph.parse(directory + file, format="turtle")
            except:
                print("error with ontology:", file)
                pass
    return graph

# serialize graph
def serialize_graph(graph, file_path, file_format):
    graph.serialize(destination=file_path, format=file_format)

# this function takes an rdf graph as input and returns an intensional graph, by performing sparql queries
# it ignores class constructions
def create_intensional_graph_without_annotations(graph):
    intensional_results_no_class_construction = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    ?class1 fschema:subsumedUnder ?class2 .
    ?equal1 fschema:extensionallyEquivalent ?equal2  .
    ?disjoint1 fschema:incompatibleWith ?disjoint2 .
    ?domain1 ?domain2 ?domain3 .
    ?universal1 ?universal2 ?universal3 .
    ?existential1 ?existential2 ?existential3 .
    ?card1 ?card2 ?card3 .
    }

    WHERE {
    {
    ?class1 rdfs:subClassOf ?class2 . 
    FILTER NOT EXISTS {?class2 a owl:Restriction} 
    FILTER NOT EXISTS {?class2 owl:unionOf ?u}
    FILTER NOT EXISTS {?class2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?class2 owl:oneOf ?o}
    FILTER NOT EXISTS {?class2 owl:complementOf ?c}
    }
    UNION
    {
    ?equal1 owl:equivalentClass ?equal2 .
    FILTER NOT EXISTS {?equal2 a owl:Restriction}  
    FILTER NOT EXISTS {?equal2 owl:unionOf ?u}
    FILTER NOT EXISTS {?equal2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?equal2 owl:oneOf ?o}
    FILTER NOT EXISTS {?equal2 owl:complementOf ?c}
    FILTER(!isBlank(?equal2))
    FILTER(!isBlank(?equal1))
    }
    UNION
    {
    ?allequivalent a owl:AllEquivalentClasses ; 
    owl:members/rdf:rest*/rdf:first ?equal1 ; owl:members/rdf:rest*/rdf:first ?equal2 .
    FILTER(?equal1 != ?equal2)
    }
    UNION
    {
    ?disjoint1 owl:disjointWith ?disjoint2 .
    FILTER NOT EXISTS {?disjoint2 a owl:Restriction} . 
    FILTER NOT EXISTS {?disjoint2 owl:unionOf ?u}
    FILTER NOT EXISTS {?disjoint2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?disjoint2 owl:oneOf ?o}
    FILTER NOT EXISTS {?disjoint2 owl:complementOf ?c}
    }
    UNION
    {
    ?alldisjoint a owl:AllDisjointClasses ; 
    owl:members/rdf:rest*/rdf:first ?disjoint1 ; owl:members/rdf:rest*/rdf:first ?disjoint2 .
    FILTER(?disjoint1 != ?disjoint2)
    }
    UNION
    {
    ?domain2 rdfs:domain ?domain1 . ?domain2 rdfs:range ?domain3 .
    FILTER NOT EXISTS {?domain1 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER NOT EXISTS {?domain3 owl:unionOf|owl:intersectionOf ?z}
    }
    UNION
    {
    ?universal1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?universal2 ; owl:allValuesFrom ?universal3 .
    FILTER NOT EXISTS {?universal3 a owl:Restriction} 
    FILTER NOT EXISTS {?universal3 owl:unionOf ?u}
    FILTER NOT EXISTS {?universal3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?universal3 owl:complementOf ?c}
    FILTER(!isBlank(?universal2))
    FILTER(!isBlank(?universal3))
    }
    UNION
    {
    ?existential1 rdfs:subClassOf|owl:equivalentClass ?z . 
    ?z owl:onProperty ?existential2 ; owl:someValuesFrom ?existential3 .
    FILTER NOT EXISTS {?existential3 a owl:Restriction} . 
    FILTER NOT EXISTS {?existential3 owl:unionOf ?u}
    FILTER NOT EXISTS {?existential3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?existential3 owl:complementOf ?c}
    FILTER(!isBlank(?existential2))
    FILTER(!isBlank(?existential3))
    } 
    UNION
    {
    ?card1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:minCardinality|owl:maxCardinality|owl:cardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    }
    }
    """)

    intensional_graph = Graph()
    for triple in intensional_results_no_class_construction:
        intensional_graph.add(triple)

    return intensional_graph


# this function takes an rdf graph as input and returns an intensional graph
# ignoring subclassof, equivalentclass and disjoint axioms,
# by performing sparql queries
def create_relation_intensional_graph_without_annotations(graph):
    relation_intensional_results_no_class_construction = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    ?domain1 ?domain2 ?domain3 .
    ?universal1 ?universal2 ?universal3 .
    ?existential1 ?existential2 ?existential3 .
    ?card1 ?card2 ?card3 .
    }

    WHERE {
    {
    ?domain2 rdfs:domain ?domain1 . ?domain2 rdfs:range ?domain3 .
    FILTER NOT EXISTS {?domain1 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER NOT EXISTS {?domain3 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER(!isBlank(?domain1))
    FILTER(!isBlank(?domain2))
    FILTER(!isBlank(?domain3))
    }
    UNION
    {
    ?universal1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?universal2 ; owl:allValuesFrom ?universal3 .
    FILTER NOT EXISTS {?universal2 a owl:Restriction}
    FILTER NOT EXISTS {?universal3 a owl:Restriction}  
    FILTER NOT EXISTS {?universal3 owl:unionOf ?u}
    FILTER NOT EXISTS {?universal3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?universal3 owl:complementOf ?c}
    FILTER(!isBlank(?universal2))
    FILTER(!isBlank(?universal3))
    }
    UNION
    {
    ?existential1 rdfs:subClassOf|owl:equivalentClass ?z . 
    ?z owl:onProperty ?existential2 ; owl:someValuesFrom ?existential3 .
    FILTER NOT EXISTS {?existential2 a owl:Restriction} .
    FILTER NOT EXISTS {?existential3 a owl:Restriction} . 
    FILTER NOT EXISTS {?existential3 owl:unionOf ?u}
    FILTER NOT EXISTS {?existential3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?existential3 owl:complementOf ?c}
    FILTER(!isBlank(?existential2))
    FILTER(!isBlank(?existential3))
    } 
    UNION
    {
    ?card1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:minCardinality|owl:maxCardinality|owl:cardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    FILTER(!isBlank(?card2))
    FILTER(!isBlank(?card3))
    }
    }
    """)

    relation_intensional_graph = Graph()
    for triple in relation_intensional_results_no_class_construction:
        relation_intensional_graph.add(triple)

    return relation_intensional_graph


# this function takes an rdf graph as input and returns an intensional graph
# ignoring subclassof, equivalentclass and disjoint axioms,
# by performing sparql queries
def create_relation_and_subsumed_intensional_graph_without_annotations(graph):
    relation_intensional_results_no_class_construction = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    ?class1 fschema:subsumedUnder ?class2 .
    ?equal1 fschema:extensionallyEquivalent ?equal2  .
    ?domain1 ?domain2 ?domain3 .
    ?universal1 ?universal2 ?universal3 .
    ?existential1 ?existential2 ?existential3 .
    ?card1 ?card2 ?card3 .
    }

    WHERE {
    {
    ?class1 rdfs:subClassOf ?class2 . 
    FILTER NOT EXISTS {?class2 a owl:Restriction} 
    FILTER NOT EXISTS {?class2 owl:unionOf ?u}
    FILTER NOT EXISTS {?class2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?class2 owl:oneOf ?o}
    FILTER NOT EXISTS {?class2 owl:complementOf ?c}
    }
    UNION
    {
    ?equal1 owl:equivalentClass ?equal2 .
    FILTER NOT EXISTS {?equal2 a owl:Restriction}  
    FILTER NOT EXISTS {?equal2 owl:unionOf ?u}
    FILTER NOT EXISTS {?equal2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?equal2 owl:oneOf ?o}
    FILTER NOT EXISTS {?equal2 owl:complementOf ?c}
    FILTER(!isBlank(?equal2))
    FILTER(!isBlank(?equal1))
    }
    UNION
    {
    ?allequivalent a owl:AllEquivalentClasses ; 
    owl:members/rdf:rest*/rdf:first ?equal1 ; owl:members/rdf:rest*/rdf:first ?equal2 .
    FILTER(?equal1 != ?equal2)
    }
    UNION
    {
    ?domain2 rdfs:domain ?domain1 . ?domain2 rdfs:range ?domain3 .
    FILTER NOT EXISTS {?domain1 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER NOT EXISTS {?domain3 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER(!isBlank(?domain1))
    FILTER(!isBlank(?domain2))
    FILTER(!isBlank(?domain3))
    }
    UNION
    {
    ?universal1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?universal2 ; owl:allValuesFrom ?universal3 .
    FILTER NOT EXISTS {?universal2 a owl:Restriction}
    FILTER NOT EXISTS {?universal3 a owl:Restriction}  
    FILTER NOT EXISTS {?universal3 owl:unionOf ?u}
    FILTER NOT EXISTS {?universal3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?universal3 owl:complementOf ?c}
    FILTER(!isBlank(?universal2))
    FILTER(!isBlank(?universal3))
    }
    UNION
    {
    ?existential1 rdfs:subClassOf|owl:equivalentClass ?z . 
    ?z owl:onProperty ?existential2 ; owl:someValuesFrom ?existential3 .
    FILTER NOT EXISTS {?existential2 a owl:Restriction} .
    FILTER NOT EXISTS {?existential3 a owl:Restriction} . 
    FILTER NOT EXISTS {?existential3 owl:unionOf ?u}
    FILTER NOT EXISTS {?existential3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?existential3 owl:complementOf ?c}
    FILTER(!isBlank(?existential2))
    FILTER(!isBlank(?existential3))
    } 
    UNION
    {
    ?card1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:minCardinality|owl:maxCardinality|owl:cardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    FILTER(!isBlank(?card2))
    FILTER(!isBlank(?card3))
    }
    }
    """)

    subsumed_intensional_graph = Graph()
    for triple in relation_intensional_results_no_class_construction:
        subsumed_intensional_graph.add(triple)

    relation_intensional_graph = Graph()
    for s, p, o in subsumed_intensional_graph:
        if not p == URIRef("https://w3id.org/framester/schema/extensionallyEquivalent") and not p == URIRef("https://w3id.org/framester/schema/subsumedUnder"):
            relation_intensional_graph.add((s, p, o))


    return relation_intensional_graph, subsumed_intensional_graph


# this function takes an rdf graph as input and returns an intensional graph
# ignoring disjoint axioms,
# by performing sparql queries
def create_intensional_graph_nodisjoint_without_annotations(graph):
    nodisjoint_intensional_results_no_class_construction = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    ?class1 fschema:subsumedUnder ?class2 .
    ?equal1 fschema:extensionallyEquivalent ?equal2  .
    ?domain1 ?domain2 ?domain3 .
    ?universal1 ?universal2 ?universal3 .
    ?existential1 ?existential2 ?existential3 .
    ?card1 ?card2 ?card3 .
    }

    WHERE {
    {
    ?class1 rdfs:subClassOf ?class2 . 
    FILTER NOT EXISTS {?class2 a owl:Restriction} 
    FILTER NOT EXISTS {?class2 owl:unionOf ?u}
    FILTER NOT EXISTS {?class2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?class2 owl:oneOf ?o}
    FILTER NOT EXISTS {?class2 owl:complementOf ?c}
    }
    UNION
    {
    ?equal1 owl:equivalentClass ?equal2 .
    FILTER NOT EXISTS {?equal2 a owl:Restriction}  
    FILTER NOT EXISTS {?equal2 owl:unionOf ?u}
    FILTER NOT EXISTS {?equal2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?equal2 owl:oneOf ?o}
    FILTER NOT EXISTS {?equal2 owl:complementOf ?c}
    FILTER(!isBlank(?equal2))
    FILTER(!isBlank(?equal1))
    }
    UNION
    {
    ?allequivalent a owl:AllEquivalentClasses ; 
    owl:members/rdf:rest*/rdf:first ?equal1 ; owl:members/rdf:rest*/rdf:first ?equal2 .
    FILTER(?equal1 != ?equal2)
    }
    UNION
    {
    ?domain2 rdfs:domain ?domain1 . ?domain2 rdfs:range ?domain3 .
    FILTER NOT EXISTS {?domain1 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER NOT EXISTS {?domain3 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER(!isBlank(?domain1))
    FILTER(!isBlank(?domain2))
    FILTER(!isBlank(?domain3))
    }
    UNION
    {
    ?universal1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?universal2 ; owl:allValuesFrom ?universal3 .
    FILTER NOT EXISTS {?universal2 a owl:Restriction}
    FILTER NOT EXISTS {?universal3 a owl:Restriction}  
    FILTER NOT EXISTS {?universal3 owl:unionOf ?u}
    FILTER NOT EXISTS {?universal3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?universal3 owl:complementOf ?c}
    FILTER(!isBlank(?universal2))
    FILTER(!isBlank(?universal3))
    }
    UNION
    {
    ?existential1 rdfs:subClassOf|owl:equivalentClass ?z . 
    ?z owl:onProperty ?existential2 ; owl:someValuesFrom ?existential3 .
    FILTER NOT EXISTS {?existential2 a owl:Restriction} .
    FILTER NOT EXISTS {?existential3 a owl:Restriction} . 
    FILTER NOT EXISTS {?existential3 owl:unionOf ?u}
    FILTER NOT EXISTS {?existential3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?existential3 owl:complementOf ?c}
    FILTER(!isBlank(?existential2))
    FILTER(!isBlank(?existential3))
    } 
    UNION
    {
    ?card1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:minCardinality|owl:maxCardinality|owl:cardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    FILTER(!isBlank(?card2))
    FILTER(!isBlank(?card3))
    }
    }
    """)

    nodisjoint_intensional_graph = Graph()
    for triple in nodisjoint_intensional_results_no_class_construction:
        nodisjoint_intensional_graph.add(triple)

    return nodisjoint_intensional_graph


# this function takes an rdf graph as input and returns an intensional graph
# ignoring disjoint axioms,
# and considering also axioms inherited by superclasses
# by performing sparql queries
def create_intensional_graph_nodisjoint_inheritedsuperclassaxioms_without_annotations(graph):
    nodisjoint_intensional_results_no_class_construction = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    ?class1 fschema:subsumedUnder ?class2 .
    ?equal1 fschema:extensionallyEquivalent ?equal2  .
    ?domain1 ?domain2 ?domain3 .
    ?universal1 ?universal2 ?universal3 .
    ?existential1 ?existential2 ?existential3 .
    ?card1 ?card2 ?card3 .
    }

    WHERE {
    {
    ?class1 rdfs:subClassOf ?class2 . 
    FILTER NOT EXISTS {?class2 a owl:Restriction} 
    FILTER NOT EXISTS {?class2 owl:unionOf ?u}
    FILTER NOT EXISTS {?class2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?class2 owl:oneOf ?o}
    FILTER NOT EXISTS {?class2 owl:complementOf ?c}
    }
    UNION
    {
    ?equal1 owl:equivalentClass ?equal2 .
    FILTER NOT EXISTS {?equal2 a owl:Restriction}  
    FILTER NOT EXISTS {?equal2 owl:unionOf ?u}
    FILTER NOT EXISTS {?equal2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?equal2 owl:oneOf ?o}
    FILTER NOT EXISTS {?equal2 owl:complementOf ?c}
    FILTER(!isBlank(?equal2))
    FILTER(!isBlank(?equal1))
    }
    UNION
    {
    ?allequivalent a owl:AllEquivalentClasses ; 
    owl:members/rdf:rest*/rdf:first ?equal1 ; owl:members/rdf:rest*/rdf:first ?equal2 .
    FILTER(?equal1 != ?equal2)
    }
    UNION
    {
    ?domain2 rdfs:domain ?domain1 . ?domain2 rdfs:range ?domain3 .
    FILTER NOT EXISTS {?domain1 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER NOT EXISTS {?domain3 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER(!isBlank(?domain1))
    FILTER(!isBlank(?domain2))
    FILTER(!isBlank(?domain3))
    }
    UNION
    {
    ?universal1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?universal2 ; owl:allValuesFrom ?universal3 .
    FILTER NOT EXISTS {?universal2 a owl:Restriction}
    FILTER NOT EXISTS {?universal3 a owl:Restriction}  
    FILTER NOT EXISTS {?universal3 owl:unionOf ?u}
    FILTER NOT EXISTS {?universal3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?universal3 owl:complementOf ?c}
    FILTER(!isBlank(?universal2))
    FILTER(!isBlank(?universal3))
    }
    UNION
    {
    ?universal1 rdfs:subClassOf ?superclass1 .
    ?superclass1 rdfs:subClassOf|owl:equivalentClass ?z . 
    ?z owl:onProperty ?universal2 ; owl:allValuesFrom ?universal3 .
    FILTER NOT EXISTS {?universal2 a owl:Restriction}
    FILTER NOT EXISTS {?universal3 a owl:Restriction}  
    FILTER NOT EXISTS {?universal3 owl:unionOf ?u}
    FILTER NOT EXISTS {?universal3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?universal3 owl:complementOf ?c}
    FILTER(!isBlank(?universal2))
    FILTER(!isBlank(?universal3))
    }
    UNION
    {
    ?existential1 rdfs:subClassOf|owl:equivalentClass ?z . 
    ?z owl:onProperty ?existential2 ; owl:someValuesFrom ?existential3 .
    FILTER NOT EXISTS {?existential2 a owl:Restriction} .
    FILTER NOT EXISTS {?existential3 a owl:Restriction} . 
    FILTER NOT EXISTS {?existential3 owl:unionOf ?u}
    FILTER NOT EXISTS {?existential3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?existential3 owl:complementOf ?c}
    FILTER(!isBlank(?existential2))
    FILTER(!isBlank(?existential3))
    } 
    UNION
    {
    ?existential1 rdfs:subClassOf ?superclass1 .
    ?superclass1 rdfs:subClassOf|owl:equivalentClass ?z . 
    ?z owl:onProperty ?existential2 ; owl:someValuesFrom ?existential3 .
    FILTER NOT EXISTS {?existential2 a owl:Restriction} .
    FILTER NOT EXISTS {?existential3 a owl:Restriction} . 
    FILTER NOT EXISTS {?existential3 owl:unionOf ?u}
    FILTER NOT EXISTS {?existential3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?existential3 owl:complementOf ?c}
    FILTER(!isBlank(?existential2))
    FILTER(!isBlank(?existential3))
    }
    UNION
    {
    ?card1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:minCardinality|owl:maxCardinality|owl:cardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    FILTER(!isBlank(?card2))
    FILTER(!isBlank(?card3))
    }
    UNION
    {
    ?card1 rdfs:subClassOf ?superclass1 .
    ?superclass1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:minCardinality|owl:maxCardinality|owl:cardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    FILTER(!isBlank(?card2))
    FILTER(!isBlank(?card3))
    }
    }
    """)

    nodisjoint_intensional_graph = Graph()
    for triple in nodisjoint_intensional_results_no_class_construction:
        nodisjoint_intensional_graph.add(triple)

    return nodisjoint_intensional_graph


# this function takes an rdf graph as input and returns an intensional graph
# ignoring disjoint axioms,
# including equivalent class and property axioms, subclass and subproperty axioms
# by performing sparql queries
def create_intensional_graph_nodisjoint_subequalproperty_without_annotations(graph):
    nodisjoint_intensional_results_no_class_construction = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    ?class1 fschema:subsumedUnder ?class2 .
    ?equal1 fschema:extensionallyEquivalent ?equal2  .
    ?domain1 ?domain2 ?domain3 .
    ?universal1 ?universal2 ?universal3 .
    ?existential1 ?existential2 ?existential3 .
    ?card1 ?card2 ?card3 .
    ?subproperty1 fschema:subsumedUnder ?subproperty2 .
    ?equalproperty1 fschema:extensionallyEquivalent ?equalproperty2 .
    }

    WHERE {
    {
    ?class1 rdfs:subClassOf ?class2 . 
    FILTER NOT EXISTS {?class2 a owl:Restriction} 
    FILTER NOT EXISTS {?class2 owl:unionOf ?u}
    FILTER NOT EXISTS {?class2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?class2 owl:oneOf ?o}
    FILTER NOT EXISTS {?class2 owl:complementOf ?c}
    }
    UNION
    {
    ?subproperty1 rdfs:subPropertyOf ?subproperty2 . 
    FILTER(!isBlank(?subproperty2))
    FILTER(!isBlank(?subproperty1))
    }
    UNION
    {
    ?equal1 owl:equivalentClass ?equal2 .
    FILTER NOT EXISTS {?equal2 a owl:Restriction}  
    FILTER NOT EXISTS {?equal2 owl:unionOf ?u}
    FILTER NOT EXISTS {?equal2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?equal2 owl:oneOf ?o}
    FILTER NOT EXISTS {?equal2 owl:complementOf ?c}
    FILTER(!isBlank(?equal2))
    FILTER(!isBlank(?equal1))
    }
    UNION
    {
    ?equalproperty1 owl:equivalentProperty ?equalproperty2 . 
    FILTER(!isBlank(?equalproperty2))
    FILTER(!isBlank(?equalproperty1))
    }
    UNION
    {
    ?allequivalent a owl:AllEquivalentClasses ; 
    owl:members/rdf:rest*/rdf:first ?equal1 ; owl:members/rdf:rest*/rdf:first ?equal2 .
    FILTER(?equal1 != ?equal2)
    }
    UNION
    {
    ?domain2 rdfs:domain ?domain1 . ?domain2 rdfs:range ?domain3 .
    FILTER NOT EXISTS {?domain1 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER NOT EXISTS {?domain3 owl:unionOf|owl:intersectionOf|owl:complementOf ?z}
    FILTER(!isBlank(?domain1))
    FILTER(!isBlank(?domain2))
    FILTER(!isBlank(?domain3))
    }
    UNION
    {
    ?universal1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?universal2 ; owl:allValuesFrom ?universal3 .
    FILTER NOT EXISTS {?universal2 a owl:Restriction}
    FILTER NOT EXISTS {?universal3 a owl:Restriction}  
    FILTER NOT EXISTS {?universal3 owl:unionOf ?u}
    FILTER NOT EXISTS {?universal3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?universal3 owl:complementOf ?c}
    FILTER(!isBlank(?universal2))
    FILTER(!isBlank(?universal3))
    }
    UNION
    {
    ?existential1 rdfs:subClassOf|owl:equivalentClass ?z . 
    ?z owl:onProperty ?existential2 ; owl:someValuesFrom ?existential3 .
    FILTER NOT EXISTS {?existential2 a owl:Restriction} .
    FILTER NOT EXISTS {?existential3 a owl:Restriction} . 
    FILTER NOT EXISTS {?existential3 owl:unionOf ?u}
    FILTER NOT EXISTS {?existential3 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?existential3 owl:complementOf ?c}
    FILTER(!isBlank(?existential2))
    FILTER(!isBlank(?existential3))
    } 
    UNION
    {
    ?card1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:minCardinality|owl:maxCardinality|owl:cardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    FILTER(!isBlank(?card2))
    FILTER(!isBlank(?card3))
    }
    }
    """)

    nodisjoint_intensional_graph = Graph()
    for triple in nodisjoint_intensional_results_no_class_construction:
        nodisjoint_intensional_graph.add(triple)

    return nodisjoint_intensional_graph


# this function takes an rdf graph as input and returns a graph where also rdf properties become nodes
# along with classes
# e.g. C1 -p1-> C2
# becomes
# C1 -edge-> p1
# p1 -edge-> C2
def create_class_property_graph(graph):
    property_graph_results = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    ?class1 fschema:edge ?property .
    ?property fschema:edge ?class2 .
    }

    WHERE 
    {
    ?class1 ?property ?class2 . 
    }
    """)

    property_graph = Graph()
    for triple in property_graph_results:
        property_graph.add(triple)

    return property_graph


# this function takes an rdf graph as input and returns a property graph
# i.e. all rdf properties in input graph become nodes, along with classes
# e.g. C1 -p1-> C2
# becomes
# C1 -edge-> p1
# p1 -edge-> C2
# but properties are made distinct by concatenating the original triple they were property of
def create_class_distinctproperty_graph(graph):
    # property_graph_results = graph.query("""
    # PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    # PREFIX owl: <http://www.w3.org/2002/07/owl#>
    # PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    # PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    # PREFIX fschema: <https://w3id.org/framester/schema/>
    #
    # CONSTRUCT {
    #
    # ?class1 fschema:edge ?edge .
    # ?edge fschema:edge ?class2 .
    #
    # }
    #
    # WHERE
    # {
    # ?class1 ?property ?class2 .
    # BIND(IRI(CONCAT(STR(?class1),strafter(STR(?property),"http"), strafter(STR(?class2),"http"))) AS ?edge)
    # }
    # """)
    #for triple in property_graph_results:
    #    property_graph.add(triple)

    pred_dict = {}

    edge = URIRef("https://w3id.org/framester/schema/edge")
    # TODO transform http://edge.example/ into constant
    prefix = "http://edge.example/"
    property_graph = Graph()
    for s, p, o in graph.triples((None, None, None)):
        pred = URIRef(prefix+getID(s)+"--"+getID(p)+"--"+getID(o))
        property_graph.add((s, edge, pred))
        property_graph.add((pred, edge, o))
        pred_dict[str(pred)] = [str(s), str(p), str(o)]
    return property_graph, pred_dict, graph
    

# this function takes an rdf graph as input and returns a line graph (or edge graph)
# i.e. nodes represent only properties, while classes, as domain and range, are used for creating the edges betw nodes
# e.g.
# C1 -p1-> C2
# C2-p2->C3
# becomes
# p1 -C2-> p2
# it is similar to what networkX does with the function nx.line_graph(G)
def create_onlyproperty_graph(graph):
    onlyproperty_graph_results = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    ?property1 ?class2 ?property2 .
    }

    WHERE 
    {
    ?class1 ?property1 ?class2 .
    ?class2 ?property2 ?class3 .  
    }
    """)

    onlyproperty_graph = Graph()
    for triple in onlyproperty_graph_results:
        onlyproperty_graph.add(triple)

    return onlyproperty_graph


# this function takes an rdf graph as input and returns a graph with additional
# rdfs:domain and rdfs:range restrictions
# with owl:Thing as object
# when a property has no domain and/or range
def create_graph_w_owlthing(graph):
    owlthing_graph_results = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    ?property1 rdfs:domain owl:Thing .
    ?property2 rdfs:range owl:Thing .
    }

    WHERE {
    {
    ?property1 a owl:ObjectProperty
    FILTER NOT EXISTS {?property1 rdfs:domain ?domain}
    }
    UNION
    {
    ?property2 a owl:ObjectProperty
    FILTER NOT EXISTS {?property2 rdfs:range ?range}
    }
    }
    """)

    owlthing_graph = Graph()
    for triple in owlthing_graph_results:
        owlthing_graph.add(triple)

    return owlthing_graph


# this function takes an rdf graph as input and returns a line graph (or edge graph)
# i.e. nodes represent only properties, while classes, as domain and range, are used for creating the edges betw nodes
# after transforming it in an intensional graph ignoring disjointness axioms
# with additional rdfs:domain and rdfs:range restrictions
# with owl:Thing as object
# when a property has no domain and/or range
def create_intensional_nodisjoint_owlthing_onlyproperty_graph(graph):
    owl_thing_graph = graph + create_graph_w_owlthing(graph)
    nodisjoint_intensional_graph = create_intensional_graph_nodisjoint_without_annotations(owl_thing_graph)
    onlyproperty_intensional_graph = create_onlyproperty_graph(nodisjoint_intensional_graph)

    return onlyproperty_intensional_graph


# this function takes an rdf graph as input and returns a graph where also rdf properties become nodes
# along with classes
# after transforming it in an intensional graph ignoring disjointness axioms
def create_intensional_nodisjoint_class_property_graph(graph):
    nodisjoint_intensional_graph = create_intensional_graph_nodisjoint_without_annotations(graph)
    class_property_intensional_graph = create_class_property_graph(nodisjoint_intensional_graph)

    return class_property_intensional_graph

# this query takes an rdf graph as input and returns a graph with the annotations that help explaining a respective
# intensional graph created with the function create_intensional_graph_without_annotations
def create_intensional_graph_annotations(graph):
    annotation1 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x1 a owl:Axiom ; fschema:axiomType fschema:SubclassAxiom ; owl:annotatedProperty rdfs:subClassOf ; 
    owl:annotatedSource ?class1 ; owl:annotatedTarget ?class2 .
    }

    WHERE
    {
    ?class1 rdfs:subClassOf ?class2 . 
    FILTER NOT EXISTS {?class2 a owl:Restriction} 
    FILTER NOT EXISTS {?class2 owl:unionOf ?u}
    FILTER NOT EXISTS {?class2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?class2 owl:oneOf ?o}
    }
    """)

    annotation2 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x1 a owl:Axiom ; fschema:axiomType fschema:EquivalenceAxiom ; owl:annotatedProperty owl:equivalentClass ; 
    owl:annotatedSource ?equal1 ; owl:annotatedTarget ?equal2 .
    }

    WHERE
    {
    ?equal1 owl:equivalentClass ?equal2 .
    FILTER NOT EXISTS {?equal2 a owl:Restriction}  
    FILTER NOT EXISTS {?equal2 owl:unionOf ?u}
    FILTER NOT EXISTS {?equal2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?equal2 owl:oneOf ?o}
    }
    """)

    annotation3 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x3 a owl:Axiom ; fschema:axiomType fschema:DisjointnessAxiom ; 
    owl:annotatedProperty owl:disjointWith ; owl:annotatedSource ?disjoint1 ; owl:annotatedTarget ?disjoint2 .
    }

    WHERE
    {
    ?disjoint1 owl:disjointWith ?disjoint2 .
    FILTER NOT EXISTS {?disjoint2 a owl:Restriction} . 
    FILTER NOT EXISTS {?disjoint2 owl:unionOf ?u}
    FILTER NOT EXISTS {?disjoint2 owl:intersectionOf ?i}
    FILTER NOT EXISTS {?disjoint2 owl:oneOf ?o}
    }
    """)

    annotation4 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x4 a owl:Axiom ; fschema:axiomType fschema:DomainAxiom ; owl:annotatedProperty rdfs:domain ; 
    owl:annotatedSource ?domain2 ; owl:annotatedTarget ?domain1 .

    }

    WHERE
    {
    ?domain2 rdfs:domain ?domain1 . ?domain2 rdfs:range ?domain3 .
    FILTER NOT EXISTS {?domain1 owl:unionOf|owl:intersectionOf ?z}
    FILTER NOT EXISTS {?domain3 owl:unionOf|owl:intersectionOf ?z}
    }
    """)

    annotation5 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x5 a owl:Axiom ; fschema:axiomType fschema:RangeAxiom ; owl:annotatedProperty rdfs:range ; 
    owl:annotatedSource ?domain2 ; owl:annotatedTarget ?domain3 .

    }

    WHERE
    {
    ?domain2 rdfs:domain ?domain1 . ?domain2 rdfs:range ?domain3 .
    FILTER NOT EXISTS {?domain1 owl:unionOf|owl:intersectionOf ?z}
    FILTER NOT EXISTS {?domain3 owl:unionOf|owl:intersectionOf ?z}
    }
    """)

    annotation6 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x6 a owl:Axiom ; fschema:axiomType fschema:UniversalAxiom ; owl:annotatedProperty ?universal2 ; 
    owl:annotatedSource ?universal1 ; owl:annotatedTarget ?universal3 .

    }

    WHERE
    {
   ?universal1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?universal2 ; owl:allValuesFrom ?universal3 .
    FILTER NOT EXISTS {?universal3 a owl:Restriction} 
    FILTER NOT EXISTS {?universal3 owl:unionOf ?u}
    FILTER NOT EXISTS {?universal3 owl:intersectionOf ?i}
    }
    """)

    annotation7 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x7 a owl:Axiom ; fschema:axiomType fschema:ExistentialAxiom ; 
    owl:annotatedProperty ?existential2 ; owl:annotatedSource ?existential1 ; 
    owl:annotatedTarget ?existential3 .

    }

    WHERE
    {
   ?existential1 rdfs:subClassOf|owl:equivalentClass ?z . 
    ?z owl:onProperty ?existential2 ; owl:someValuesFrom ?existential3 .
    FILTER NOT EXISTS {?existential3 a owl:Restriction} . 
    FILTER NOT EXISTS {?existential3 owl:unionOf ?u}
    FILTER NOT EXISTS {?existential3 owl:intersectionOf ?i}
    }
    """)

    annotation8 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x8 a owl:Axiom ; fschema:axiomType fschema:MinimumCardinalityAxiom ; 
    owl:annotatedProperty ?card2 ; owl:annotatedSource ?card1 ; 
    owl:annotatedTarget ?card3 ; owl:mincardinality ?q .

    }

    WHERE
    {
    ?card1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:minCardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    }
    """)

    annotation9 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x8 a owl:Axiom ; fschema:axiomType fschema:MaximumCardinalityAxiom ; 
    owl:annotatedProperty ?card2 ; owl:annotatedSource ?card1 ; 
    owl:annotatedTarget ?card3 ; owl:maxCardinality ?q .

    }

    WHERE
    {
    ?card1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:maxCardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    }
    """)

    annotation10 = graph.query("""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX fschema: <https://w3id.org/framester/schema/>

    CONSTRUCT { 
    _:x8 a owl:Axiom ; fschema:axiomType fschema:ExactCardinalityAxiom ; 
    owl:annotatedProperty ?card2 ; owl:annotatedSource ?card1 ; 
    owl:annotatedTarget ?card3 ; owl:cardinality ?q .

    }

    WHERE
    {
    ?card1 rdfs:subClassOf|owl:equivalentClass ?z .
    ?z owl:onProperty ?card2 ; owl:cardinality ?q . 
    ?card2 rdfs:range ?card3 .
    FILTER (?q != 0) 
    }
    """)

    annotations_graph = Graph()
    annotations_graph += annotation1
    annotations_graph += annotation2
    annotations_graph += annotation3
    annotations_graph += annotation4
    annotations_graph += annotation5
    annotations_graph += annotation6
    annotations_graph += annotation7
    annotations_graph += annotation8
    annotations_graph += annotation9
    annotations_graph += annotation10

    return annotations_graph


### combinations of queries
def create_owlthing_nodisjoint_class_distinctproperty(graph):
    owl_thing_graph = graph + create_graph_w_owlthing(graph)
    nodisjoint_intensional_graph = create_intensional_graph_nodisjoint_without_annotations(owl_thing_graph)
    class_distinctproperty_intensional_graph = create_class_distinctproperty_graph(nodisjoint_intensional_graph)

    return class_distinctproperty_intensional_graph


def create_owlthing_nodisjoint_class_distinctproperty_nosubsumed(graph):
    owl_thing_graph = graph + create_graph_w_owlthing(graph)
    nosubsumed_intensional_graph = create_relation_and_subsumed_intensional_graph_without_annotations(owl_thing_graph)[0]
    class_distinctproperty_nosubsumed_intensional_graph = create_class_distinctproperty_graph(nosubsumed_intensional_graph)
    subsumed_intensional_graph = create_relation_and_subsumed_intensional_graph_without_annotations(owl_thing_graph)[1]

    return class_distinctproperty_nosubsumed_intensional_graph, subsumed_intensional_graph

