from rdflib import *
from rdflib.extras.external_graph_libs import *
import rdfextras
import networkx as nx
from rdf_graph_transformations import *


# this function takes as input an rdflib graph and convert it to a networkx
# multidigraph 
# where node labels are converted to integers
# the networkx graph stores old node labels in an attribute named "uri"
def from_rdflib_to_networkx_multidigraph(rdf_graph):
    networkx_graph = rdflib_to_networkx_multidigraph(rdf_graph)
    networkx_graph_int = nx.convert_node_labels_to_integers(networkx_graph, first_label=0, ordering='sorted',
                                                            label_attribute='uri')
    return networkx_graph_int


# this function takes as input an rdflib graph and convert it to a networkx
# digraph 
# where node labels are converted to integers
# the networkx graph stores old node labels in an attribute named "uri"
def from_rdflib_to_networkx_digraph(rdf_graph):
    networkx_graph = rdflib_to_networkx_digraph(rdf_graph)
    networkx_graph_int = nx.convert_node_labels_to_integers(networkx_graph, first_label=0, ordering='sorted',
                                                            label_attribute='uri')
    return networkx_graph_int


# this function takes as input an rdflib graph and convert it to a networkx
# graph 
# where node labels are converted to integers
# the networkx graph stores old node labels in an attribute named "uri"
def from_rdflib_to_networkx_graph(rdf_graph):
    networkx_graph = rdflib_to_networkx_graph(rdf_graph)
    networkx_graph_int = nx.convert_node_labels_to_integers(networkx_graph, first_label=0, ordering='sorted',
                                                            label_attribute='uri')
    return networkx_graph_int


# this function takes as input an rdflib graph
# and returns a networkx multidigraph (if g_type = "multidigraph") / digraph (if g_type = "digraph") / graph (if g_type = "graph")
# from the intensional graph 
# ignoring disjoint axioms
# with both classes and properties as nodes
# with additional
#rdfs:domain and rdfs:range restrictions with owl:Thing as object
# when a property has no domain and/or range
def from_rdflib_to_networkx_owlthing_nodisjoint_class_distinctproperty(rdf_graph, g_type):
    owl_thing_graph = rdf_graph + create_graph_w_owlthing(rdf_graph)
    nodisjoint_intensional_graph = create_intensional_graph_nodisjoint_subequalproperty_without_annotations(owl_thing_graph)
    class_distinctproperty_intensional_graph = create_class_distinctproperty_graph(nodisjoint_intensional_graph)
    if g_type == "multidigraph":
        networkx_graph_int = from_rdflib_to_networkx_multidigraph(class_distinctproperty_intensional_graph)
    if g_type == "digraph":
        networkx_graph_int = from_rdflib_to_networkx_digraph(class_distinctproperty_intensional_graph)
    else:
        networkx_graph_int = from_rdflib_to_networkx_graph(class_distinctproperty_intensional_graph)
    
    return networkx_graph_int









    


