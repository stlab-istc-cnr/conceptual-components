from rdflib_to_networkx_graph import *
from networkx.algorithms.community import greedy_modularity_communities
import sys
import logging
from utils import getID
from graphviz import Digraph

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO, filename='odp_detector.log')
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger = logging.getLogger(__name__)


# this function takes as input a networkx graph and a list of nodes
# and returns the subgraph of the original graph containing the nodes in the list, 
# linked with the original edges
def rebuild_networkxgraph_from_nodelist(original_networkx_graph, node_list):
	community_nx_graph = nx.Graph()
	for node1 in node_list:
		for node2 in node_list:
			if original_networkx_graph.has_edge(node1, node2):
				community_nx_graph.add_edge(node1, node2)

	return community_nx_graph


# this recursive function takes as input a networkx graph
# and an empty list
# and returns the list with all the communities that have been found
# by rerunning the greedy modularity communities algorithm
# since it is not able to split any community in subcommunities
def find_all_communities(networkx_graph, communities_list):
	comm_frozenset_list = list(greedy_modularity_communities(networkx_graph))
	comm_int_list = [list(x) for x in comm_frozenset_list]
	if len(comm_int_list) > 1:
		for comm in comm_int_list:
			comm_nxgraph = rebuild_networkxgraph_from_nodelist(networkx_graph, comm)
			find_all_communities(comm_nxgraph, communities_list)
	else:
		communities_list.extend(comm_int_list)

	return communities_list


# this recursive function takes as input a networkx graph
# and an empty list
# and returns the list with all the communities that have been found
# by rerunning the greedy modularity communities algorithm
# only on communities with a density < the average density of the communities
# since it is not able to split any community in subcommunities
def find_all_communities_densitybelowaverage(networkx_graph, communities_list):
	comm_frozenset_list = list(greedy_modularity_communities(networkx_graph))
	comm_int_list = [list(x) for x in comm_frozenset_list]
	##
	comm_nxgraph_density_dict = {}
	comm_nxgraph_int_nodes_dict = {}
	##
	for comm in comm_int_list:
		comm_nxgraph = rebuild_networkxgraph_from_nodelist(networkx_graph, comm)
		comm_nxgraph_density = nx.density(comm_nxgraph)
		comm_nxgraph_density_dict[comm_nxgraph] = comm_nxgraph_density
		comm_nxgraph_int_nodes_dict[comm_nxgraph] = comm
	average_density = sum(comm_nxgraph_density_dict.values())/len(comm_nxgraph_density_dict)
	for key in comm_nxgraph_density_dict.keys():
		if nx.density(key) < average_density:
			find_all_communities_densitybelowaverage(key, communities_list)
		else:
			communities_list.append(key)

	return communities_list



# IF RECURSIVE BELOW AVERAGE
# this function takes as input a networkx graph
# derived from an rdf graph
# where node labels have been converted to integers
# and the networkx graph stores old node labels in an attribute named "uri"
# and returns as list of lists of nodes, one for each community, 
# the communities found in graph using Clauset-Newman-Moore greedy modularity maximization
# rerunning the greedy modularity communities algorithm
# only on communities with a density < the average density of the communities
# since it is not able to split any community in subcommunities
# and save them in an external txt file (txt_file_path) only if a file path (without extension) is given as input
def print_recursive_greedy_modularity_communities(networkx_graph, txt_file_path="no-txt"):
	# create a dictionary with current integers labelling nodes as keys and old labels (uris) as values
	uri_dict = {}
	for key in nx.get_node_attributes(networkx_graph, "uri").keys():
		uri_dict[key] = networkx_graph.nodes[key]["uri"]
	count = 0
	communities_list = list()
	# here I extend the communities_list with all the (sub)communities that can be found
	find_all_communities_densitybelowaverage(networkx_graph, communities_list)
	if not txt_file_path == "no-txt":
		os.makedirs(os.path.dirname(txt_file_path + "_greedy_mod_communities.txt"), exist_ok=True)
		with open(txt_file_path + "_greedy_mod_communities.txt", "a") as txt:
			for i in communities_list:
				count += 1
				for n in i:
					txt.write("community " + str(count) + ": " + uri_dict.get(n, n) + "\n")
	comm_uri_list = list()
	for comm in communities_list:
		uri_list = list()
		for item in comm:
			rdflib_uri = str(uri_dict.get(item, item))
			uri_list.append(rdflib_uri)
		comm_uri_list.append(uri_list)

	return comm_uri_list


# IF RECURSIVE BELOW AVERAGE
# this function saves the communities as images 
def print_recursive_greedy_modularity_communities_as_images(networkx_graph, txt_file_path="no-txt", ontology_name="no_name"):
	# create a dictionary with current integers labelling nodes as keys and old labels (uris) as values
	uri_dict = {}
	for key in nx.get_node_attributes(networkx_graph, "uri").keys():
		uri_dict[key] = networkx_graph.nodes[key]["uri"]
	# counter for number of communities
	count = 0
	# list of communities (as sets)
	communities_list = list()
	# here I extend the communities_list with all the (sub)communities that can be found
	find_all_communities_densitybelowaverage(networkx_graph, communities_list)
	if not txt_file_path == "no-txt":
		#os.makedirs(os.path.dirname(txt_file_path+"/"+ontology_name + "_greedy_mod_communities.txt"), exist_ok=True)
		os.makedirs(txt_file_path+"/"+ontology_name, exist_ok=True)
		folder_out = txt_file_path+"/"+ontology_name
		with open(folder_out+"/"+ontology_name + "_greedy_mod_communities.txt", "w") as txt:
			for i in communities_list:
				count += 1
				try:
					txt.write("Community " + str(count) + " : \n")
					digraph = Digraph("Community " + str(count), filename=folder_out+'/Community'+str(count))
					for n in i:
						# we avoid to print also the properties subsumedUnder and extensionallyEquivalent
						if not ("subsumedUnder" in str(uri_dict[n])) and not ("extensionallyEquivalent" in str(uri_dict[n])):
							# TODO transform http://edge.example/ into constant
							if uri_dict.get(n).startswith("http://edge.example/"):
								edge= getID(uri_dict.get(n)).split("--")
								txt.write("\t" + edge[0] +" "+edge[1]+" "+ edge[2]+"\n")
								digraph.edge(edge[0], edge[2], label=edge[1])
							else:
								digraph.node(getID(uri_dict.get(n)))
								txt.write("\t" + getID(uri_dict.get(n)) + "\n")

						if "subsumedUnder" in str(uri_dict[n]):
							edge = getID(uri_dict.get(n)).split("--")
							digraph.edge(edge[0], edge[2], arrowhead="empty")
							txt.write("\t" + edge[0] +" "+edge[1]+" "+ edge[2]+"\n")
						if "extensionallyEquivalent" in str(uri_dict[n]):
							edge = getID(uri_dict.get(n)).split("--")
							digraph.edge(edge[0], edge[2], label="extensionallyEquivalent")
							txt.write("\t" + edge[0] +" "+edge[1]+" "+ edge[2]+"\n")
					digraph.render(filename=folder_out+'/Community'+str(count))
				except:
					with open(folder_out+"/"+ontology_name + "_image_error.txt", "w") as error_txt:
						txt.write("Error for image of community " + str(count) + "\n")
	comm_uri_list = list()
	for comm in communities_list:
		uri_list = list()
		for item in comm:
			rdflib_uri = str(uri_dict.get(item, item))
			uri_list.append(rdflib_uri)
		comm_uri_list.append(uri_list)

	return comm_uri_list

# IF NOT RECURSIVE
# this function takes as input a networkx graph
# derived from an rdf graph
# where node labels have been converted to integers
# and the networkx graph stores old node labels in an attribute named "uri"
# and returns as list of lists of nodes, one for each community, 
# the communities found in graph using Clauset-Newman-Moore greedy modularity maximization
# and save them in an external txt file (txt_file_path) only if a file path (without extension) is given as input
def print_norecursive_greedy_modularity_communities(networkx_graph, txt_file_path="no-txt"):
	# create a dictionary with current integers labelling nodes as keys and old labels (uris) as values
	uri_dict = {}
	for key in nx.get_node_attributes(networkx_graph, "uri").keys():
		uri_dict[key] = networkx_graph.nodes[key]["uri"]
	# counter for number of communities
	count = 0
	# list of communities (as sets)
	comm_frozenset_list = list(greedy_modularity_communities(networkx_graph))
	if not txt_file_path == "no-txt":
		os.makedirs(os.path.dirname(txt_file_path + "_greedy_mod_communities.txt"), exist_ok=True)
		with open(txt_file_path + "_greedy_mod_communities.txt", "a") as txt:
			for i in comm_frozenset_list:
				count += 1
				for n in i:
					# we avoid to print also the properties subsumedUnder and extensionallyEquivalent
					#if not ("subsumedUnder" in str(uri_dict[n])) and not ("extensionallyEquivalent" in str(uri_dict[n])):
					txt.write("community " + str(count) + ": " + uri_dict.get(n, n) + "\n")
	comm_int_list = [list(x) for x in comm_frozenset_list]
	comm_uri_list = list()
	for comm in comm_int_list:
		uri_list = list()
		for item in comm:
			rdflib_uri = str(uri_dict.get(item, item))
			uri_list.append(rdflib_uri)
		comm_uri_list.append(uri_list)

	return comm_uri_list

# IF NOT RECURSIVE
# this function saves the communities as images 
def print_norecursive_greedy_modularity_communities_as_images(networkx_graph, txt_file_path="no-txt", ontology_name="no_name"):
	# create a dictionary with current integers labelling nodes as keys and old labels (uris) as values
	uri_dict = {}
	for key in nx.get_node_attributes(networkx_graph, "uri").keys():
		uri_dict[key] = networkx_graph.nodes[key]["uri"]
	# counter for number of communities
	count = 0
	# list of communities (as sets)
	comm_frozenset_list = list(greedy_modularity_communities(networkx_graph))
	if not txt_file_path == "no-txt":
		#os.makedirs(os.path.dirname(txt_file_path+"/"+ontology_name + "_greedy_mod_communities.txt"), exist_ok=True)
		os.makedirs(txt_file_path+"/"+ontology_name, exist_ok=True)
		folder_out = txt_file_path+"/"+ontology_name
		with open(folder_out+"/"+ontology_name + "_greedy_mod_communities.txt", "w") as txt:
			for i in comm_frozenset_list:
				count += 1
				try:
					txt.write("Community " + str(count) + " : \n")
					digraph = Digraph("Community " + str(count), filename=folder_out+'/Community'+str(count))
					for n in i:
						# we avoid to print also the properties subsumedUnder and extensionallyEquivalent
						if not ("subsumedUnder" in str(uri_dict[n])) and not ("extensionallyEquivalent" in str(uri_dict[n])):
							# TODO transform http://edge.example/ into constant
							if uri_dict.get(n).startswith("http://edge.example/"):
								edge= getID(uri_dict.get(n)).split("--")
								txt.write("\t" + edge[0] +" "+edge[1]+" "+ edge[2]+"\n")
								digraph.edge(edge[0], edge[2], label=edge[1])
							else:
								digraph.node(getID(uri_dict.get(n)))
								txt.write("\t" + getID(uri_dict.get(n)) + "\n")

						if "subsumedUnder" in str(uri_dict[n]):
							edge = getID(uri_dict.get(n)).split("--")
							digraph.edge(edge[0], edge[2], arrowhead="empty")
							txt.write("\t" + edge[0] +" "+edge[1]+" "+ edge[2]+"\n")
						if "extensionallyEquivalent" in str(uri_dict[n]):
							edge = getID(uri_dict.get(n)).split("--")
							digraph.edge(edge[0], edge[2], label="extensionallyEquivalent")
							txt.write("\t" + edge[0] +" "+edge[1]+" "+ edge[2]+"\n")
					digraph.render(filename=folder_out+'/Community'+str(count))
				except:
					with open(folder_out+"/"+ontology_name + "_image_error.txt", "w") as error_txt:
						txt.write("Error for image of community " + str(count) + "\n")
	comm_int_list = [list(x) for x in comm_frozenset_list]
	comm_uri_list = list()
	for comm in comm_int_list:
		uri_list = list()
		for item in comm:
			rdflib_uri = str(uri_dict.get(item, item))
			uri_list.append(rdflib_uri)
		comm_uri_list.append(uri_list)

	return comm_uri_list


# this function takes as input a list of communities
# and returns the list of intensional subgraphs that correspond to these communities
# and save each of them in a ttl file (ttl_file_path) only if a file path (without extension) is given as input
def rebuild_intensional_graphs_from_greedy_modularity_communities(communities_list, original_ontology, ttl_file_path="no-ttl"):
	count = 0
	communities_graphs = list()
	for community in communities_list:
		count += 1
		comm_graph = Graph()
		for uri1 in community:
			uriref1 = URIRef(uri1)
			for uri2 in community:
				uriref2 = URIRef(uri2)
				for s, p, o in original_ontology.triples((uriref1, None, uriref2)):
					comm_graph.add((s, p, o))
				for s, p, o in original_ontology.triples((uriref2, None, uriref1)):
					comm_graph.add((s, p, o))
		communities_graphs.append(comm_graph)
		if not ttl_file_path == "no-ttl":
			rdf_filename = ttl_file_path + str(count) + '.ttl'
			os.makedirs(os.path.dirname(rdf_filename), exist_ok=True)
			comm_graph.serialize(destination=rdf_filename, format='turtle')

	return communities_graphs


def print_original_uris_from_communities(communities_list, original_pred_uris_dict, txt_file_path="no-txt"):
	communities_original_uris_list = list()
	count = 0
	for community in communities_list:
		count += 1
		community_original_uris_list = list()
		for uri in community:
			if not "--" in uri:
				community_original_uris_list.append(uri)
			else:
				for value in original_pred_uris_dict[uri]:
					community_original_uris_list.append(value)
		communities_original_uris_list.append(community_original_uris_list)
		if not txt_file_path == "no-txt":
			originaluris_filename = txt_file_path + str(count) + "_original_uris.txt"
			os.makedirs(os.path.dirname(originaluris_filename), exist_ok=True)
			with open(originaluris_filename, "a") as txt:
				for uri in set(community_original_uris_list):
					if not uri == "https://w3id.org/framester/schema/subsumedUnder" and not uri == "https://w3id.org/framester/schema/extensionallyEquivalent":
						txt.write(uri + "\n")

	return communities_original_uris_list



def print_original_uris_from_rdfgraphs(rdf_communities_list, txt_file_path="no-txt"):
	communities_original_uris_list = list()
	count = 0
	for rdf_graph in rdf_communities_list:
		count += 1
		community_original_uris_set = set()
		for s, p, o in rdf_graph:
			community_original_uris_set.add(str(s))
			community_original_uris_set.add(str(o))
			if not str(p) == "https://w3id.org/framester/schema/subsumedUnder" and not str(p) == "https://w3id.org/framester/schema/extensionallyEquivalent":
				community_original_uris_set.add(str(p))
		communities_original_uris_list.append(community_original_uris_set)
		if not txt_file_path == "no-txt":
			originaluris_filename = txt_file_path + str(count) + "_rdf_original_uris.txt"
			os.makedirs(os.path.dirname(originaluris_filename), exist_ok=True)
			with open(originaluris_filename, "a") as txt:
				for uri in community_original_uris_set:
						txt.write(uri + "\n")

	return communities_original_uris_list




# this function takes as input a directory containing files serializing rdf graphs (including the final slash)
# a directory where to store the results (including the final slash) --> subfolders will be created
# and "True" if the community detection algorithm will be recursively run on communities that have a density < average, "False" otherwise
# and returns the communities 
def rdf_greedy_modularity_communities_with_rdf_from_folder(input_directory, output_directory, recursive="False"):
	# list for storing uris for each community of each ontology
	# e.g.
	# [[[uri1-ofcomm1-ofonto1, uri2-ofcomm1-ofonto1], [uri1-ofcomm2-ofonto1, uri2-ofcomm2-ofonto1]], 
	# [[uri1-ofcomm1-ofonto2, uri2-ofcomm1-ofonto2], [uri1-ofcomm2-ofonto2, uri2-ofcomm2-ofonto2]]]
	comm_uri_lists = list()
	ontology_rdf_graphs = list()
	comm_graph_lists = list()
	enriched_comm_graph_lists = list()
	for file in os.listdir(input_directory):
		logger.info("Processing "+file)
		print(file)
		rdf_graph = create_rdf_graph(input_directory + file)
		#for s, p, o in rdf_graph:
		# check if there is at least one triple in the Graph
			#if (s, p, o ) in rdf_graph:
		if rdf_graph:
			predicates_originaluris_dict = create_owlthing_nodisjoint_class_distinctproperty_nosubsumed(rdf_graph)[0][1]
			owlthing_nodisjoint_class_distinctproperty = create_owlthing_nodisjoint_class_distinctproperty_nosubsumed(rdf_graph)[0][0]
			ontology_rdf_graphs.append(owlthing_nodisjoint_class_distinctproperty)
			networkx_graph = from_rdflib_to_networkx_graph(owlthing_nodisjoint_class_distinctproperty)
			if recursive == "False":
				communities = print_norecursive_greedy_modularity_communities(networkx_graph, output_directory + "communities/" +  file.split(".")[0])
				print_norecursive_greedy_modularity_communities_as_images(networkx_graph,
																		output_directory + "communities_images",
																		file.split(".")[0])
			#networkx_graph = from_rdflib_to_networkx_owlthing_nodisjoint_class_distinctproperty(rdf_graph, "graph")
			elif recursive == "True":
				communities = print_recursive_greedy_modularity_communities(networkx_graph, output_directory + "communities/" +  file.split(".")[0])
				print_recursive_greedy_modularity_communities_as_images(networkx_graph,
																			output_directory + "communities_images",
																			file.split(".")[0])
			print_original_uris_from_communities(communities, predicates_originaluris_dict, output_directory + "communities_original_uris/" +  file.split(".")[0] + "/" + file.split(".")[0])
			comm_uri_lists.append(communities)
			communities_graphs = rebuild_intensional_graphs_from_greedy_modularity_communities(communities, owlthing_nodisjoint_class_distinctproperty, output_directory + "intensional_communities/" + file.split(".")[0] + "/" + file.split(".")[0])
			comm_graph_lists.append(communities_graphs)

			n_comm = 0
			statistics_filename = output_directory + "statistics_communities/" + file.split(".")[0] + "_greedy_mod_communities_rdfs_statistics.txt"
			os.makedirs(os.path.dirname(statistics_filename), exist_ok=True)
			with open(statistics_filename, "a") as txt:
				n_uri_per_comm_list = list()
				for community in communities:
					n_uri_per_comm = 0
					n_comm += 1
					for uri in community:
						n_uri_per_comm += 1
					n_uri_per_comm_list.append(n_uri_per_comm)

				txt.write("number of communities: " + str(n_comm) + "\n")
				txt.write("number of nodes per community: " + str(n_uri_per_comm_list) + "\n")
				txt.write("max number of nodes per community: " + str(max(n_uri_per_comm_list)) + "\n")
				txt.write("min number of nodes per community: " + str(min(n_uri_per_comm_list)) + "\n")
				txt.write("average number of nodes per community: " + str(sum(n_uri_per_comm_list)/len(n_uri_per_comm_list)) + "\n")

				graph_density_list = list()
				digraph_density_list = list()
				for rdf_graph in communities_graphs:
					networkx_graph = from_rdflib_to_networkx_graph(rdf_graph)
					networkx_graph_density = nx.density(networkx_graph)
					graph_density_list.append(networkx_graph_density)

					networkx_digraph = from_rdflib_to_networkx_digraph(rdf_graph)
					networkx_digraph_density = nx.density(networkx_digraph)
					digraph_density_list.append(networkx_digraph_density)
					
				txt.write("densities per graph: " + str(graph_density_list) + "\n")
				txt.write("max density per graph: " + str(max(graph_density_list)) + "\n")
				txt.write("min density per graph: " + str(min(graph_density_list)) + "\n")
				txt.write("average density per graph: " + str(sum(graph_density_list)/len(graph_density_list)) + "\n")
				txt.write("densities per digraph: " + str(digraph_density_list) + "\n")
				txt.write("max density per digraph: " + str(max(digraph_density_list)) + "\n")
				txt.write("min density per digraph: " + str(min(digraph_density_list)) + "\n")
				txt.write("average density per digraph: " + str(sum(digraph_density_list)/len(digraph_density_list)) + "\n")

				count = 1
				for community in communities:
					txt.write("community " + str(count) + " : number of nodes " + str(n_uri_per_comm_list[count - 1]) + "; density of graph " + str(graph_density_list[count - 1]) + "; density of digraph "  + str(digraph_density_list[count - 1]) + "\n")

					count += 1

	return comm_uri_lists, comm_graph_lists, enriched_comm_graph_lists, ontology_rdf_graphs



if __name__ == '__main__':
	logger.info("ODP detector")
	logger.info("Input directory " + sys.argv[1])
	logger.info("Output Directory " + sys.argv[2])
	logger.info("Recursion " + sys.argv[3])
	rdf_greedy_modularity_communities_with_rdf_from_folder(sys.argv[1], sys.argv[2], sys.argv[3])


