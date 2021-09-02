from rdf_graph_transformations import *
import sys
import csv
import pandas as pd
import re

# check if a piece of "text" has the language "lang"
def detect_language(text, language_to_detect):
    # in language_to_detect you pass the "code" of the language, e.g. "en" for english
    from langdetect import detect
    try:
        detected_lang = detect(text)
        if detected_lang == language_to_detect:
            return True
        else:
            return False
    except:
        pass
    
    
# return the local name of an ontology entity, by passing its uri
# we assume that the local name is the string after the hash or the last slash
def get_onto_local_name(uri):
    if "#" in uri:
        local_name = str(uri).split("#")[1]
    else:
        local_name = str(uri).split("/")[-1]
    return local_name

# split at upper case and/or underscore but not when acronyms/abbreviations (e.g. URL)
def splitAtUpperCaseUnderscore(s):
    for i in range(len(s)-1)[::-1]:
        if s[i].isupper() and s[i+1].islower():
            s = s[:i]+' '+s[i:]
        if s[i].isupper() and s[i-1].islower():
            s = s[:i]+' '+s[i:]
    s_underscore = " ".join(s.split("_"))

    return " ".join(s_underscore.split())

# return the namespace of an ontology, by providing the uri of an ontology entity
# we assume that the local name is the string before the hash or the last slash
def get_onto_namespace(uri):
    if "#" in uri:
        namespace = str(uri).replace(str(uri).split("#")[-1], "")
    else:
        namespace = str(uri).replace(str(uri).split("/")[-1], "")
    return namespace


# get all labels of an ontology entity in a specific language, if any. e.g. language = "en"
# it returns a list of labels
# if there is no labels in that language, it returns an empty list
def get_language_labels(graph, entity, language):
    # initialise variable where to store all labels in a specific language
    labels = []
    # try with rdflib method
    label_list = graph.preferredLabel(URIRef(entity), lang=language)
    # check if there is at least one english label
    if not len(label_list) == 0:
        for i in range(len(label_list)):
            # get all english labels and put them in a list
            labels.append(str(label_list[i][1]))
            # in order to avoid multiple labels in the whole VD
    elif (URIRef(entity), RDFS.label, None) in graph:
        # if there is no english label by using the method preferredLabel from rdflib
        # (e.g. the label language is not annotated),
        # try to detect language from existing labels
        for a, b, c in graph.triples((URIRef(entity), RDFS.label, None)):
            if detect_language(c, language):
                labels.append(c)
    return labels


# get all comments of an ontology entity in a specific language, if any. e.g. language = "en"
# it returns a list of comments
# if there is no comment in that language, it returns an empty list
def get_language_comments(graph, entity, language):
	comments = []
	try:
		for a, b, c in graph.triples((URIRef(entity), RDFS.comment, None)):
			if c.language == language and c is not None:
				comments.append(c)
			elif detect_language(c, language):
				comments.append(c)
		if len(comments) == 0:
			for a, b, c in graph.triples((URIRef(entity), URIRef("http://www.w3.org/2004/02/skos/core#definition"), None)):
				if c.language == language and c is not None:
					comments.append(c)
				elif detect_language(c, language):
					comments.append(c)
	except:
		return comments

	return comments


# create a text for an entity of an ontology, by concatenating labels and comments in a certain language
# (e.g. "en" for english)
# it returns 3 values: first the local name, second the list of the URIs of all entities selected for the VD,
# third the VD as a string
def create_text_from_ontology_entity_noblanknodes(graph, entity, language):
		entity_text = ""
		annotated_entity_text = ""
		if not isinstance(URIRef(entity), BNode):
			entity_uri = str(entity)
			entity_local_name = get_onto_local_name(entity_uri)
			split_entity_local_name = splitAtUpperCaseUnderscore(entity_local_name)
			# get english labels, if any
			label_list = get_language_labels(graph, entity, language)
			#print(label_list)
			if not len(label_list) == 0:
				for label in label_list:
					if label not in entity_text:
						entity_text += label + " "
						for s, p, o in graph.triples((URIRef(entity), RDF.type, None)):
							if o == RDF.Property or o == OWL.ObjectProperty or o == OWL.DatatypeProperty or o == OWL.AnnotationProperty or o == OWL.FunctionalProperty or o == OWL.InverseFunctionalProperty or o == OWL.TransitiveProperty or o == OWL.SymmetricProperty or o == OWL.AsymmetricProperty or o == OWL.IrreflexiveProperty or o == OWL.ReflexiveProperty:
								annotated_entity_text = "[" + entity_text + "[P]]"
							elif o == RDFS.Class or o == OWL.Class:
								annotated_entity_text = "[" + entity_text + "[C]]"
								break
							else:
								annotated_entity_text = "[" + entity_text + "[OTHER]]"
			# else, concatenate the local name
			else:
				if entity_local_name not in entity_text:
					#split_entity_local_name = " ".join(re.findall('.[^A-Z]*', " ".join(entity_local_name.split("_"))))
					entity_text += split_entity_local_name + " "
					for s, p, o in graph.triples((URIRef(entity), RDF.type, None)):
						if o == RDF.Property or o == OWL.ObjectProperty or o == OWL.DatatypeProperty or o == OWL.AnnotationProperty or o == OWL.FunctionalProperty or o == OWL.InverseFunctionalProperty or o == OWL.TransitiveProperty or o == OWL.SymmetricProperty or o == OWL.AsymmetricProperty or o == OWL.IrreflexiveProperty or o == OWL.ReflexiveProperty:
							annotated_entity_text = "[" + entity_text + "[P]]"
						elif o == RDFS.Class or o == OWL.Class:
							annotated_entity_text = "[" + entity_text + "[C]]"
							break
						else:
							annotated_entity_text = "[" + entity_text + "[OTHER]]"
			# get english comments
			comment_list = get_language_comments(graph, entity, language)
			#print(comment_list)
			if not len(comment_list) == 0:
				for comment in comment_list:
					if comment not in entity_text:
						entity_text += comment + " "
						for s, p, o in graph.triples((URIRef(entity), RDF.type, None)):
							if o == RDF.Property or o == OWL.ObjectProperty or o == OWL.DatatypeProperty or o == OWL.AnnotationProperty or o == OWL.FunctionalProperty or o == OWL.InverseFunctionalProperty or o == OWL.TransitiveProperty or o == OWL.SymmetricProperty or o == OWL.AsymmetricProperty or o == OWL.IrreflexiveProperty or o == OWL.ReflexiveProperty:
								annotated_entity_text = "[" + entity_text + "[P]]"
							elif o == RDFS.Class or o == OWL.Class:
								annotated_entity_text = "[" + entity_text + "[C]]"
								break
							else:
								annotated_entity_text = "[" + entity_text + "[OTHER]]"


			return {"entity localname": split_entity_local_name, "entity uri": entity_uri, "entity text": entity_text, "annotated text": annotated_entity_text}


# create a text for an entity of an ontology, by concatenating labels in a certain language
# (e.g. "en" for english)
# it returns 3 values: first the local name, second the list of the URIs of all entities selected for the VD,
# third the VD as a string
def create_text_from_ontology_entity_noblanknodes_onlylabels(graph, entity, language):
		entity_text = ""
		annotated_entity_text = ""
		if not isinstance(URIRef(entity), BNode):
			entity_uri = str(entity)
			entity_local_name = get_onto_local_name(entity_uri)
			split_entity_local_name = splitAtUpperCaseUnderscore(entity_local_name)
			# get english labels, if any
			label_list = get_language_labels(graph, entity, language)
			#print(label_list)
			if not len(label_list) == 0:
				for label in label_list:
					if label not in entity_text:
						entity_text += label + " "
						for s, p, o in graph.triples((URIRef(entity), RDF.type, None)):
							if o == RDF.Property or o == OWL.ObjectProperty or o == OWL.DatatypeProperty or o == OWL.AnnotationProperty or o == OWL.FunctionalProperty or o == OWL.InverseFunctionalProperty or o == OWL.TransitiveProperty or o == OWL.SymmetricProperty or o == OWL.AsymmetricProperty or o == OWL.IrreflexiveProperty or o == OWL.ReflexiveProperty:
								annotated_entity_text = "[" + entity_text + "[P]]"
							elif o == RDFS.Class or o == OWL.Class:
								annotated_entity_text = "[" + entity_text + "[C]]"
								break
							else:
								annotated_entity_text = "[" + entity_text + "[OTHER]]"
	        # else, concatenate the local name
			else:
				if entity_local_name not in entity_text:
					#split_entity_local_name = " ".join(re.findall('.[^A-Z]*', " ".join(entity_local_name.split("_"))))
					entity_text += split_entity_local_name + " "
					for s, p, o in graph.triples((URIRef(entity), RDF.type, None)):
						if o == RDF.Property or o == OWL.ObjectProperty or o == OWL.DatatypeProperty or o == OWL.AnnotationProperty or o == OWL.FunctionalProperty or o == OWL.InverseFunctionalProperty or o == OWL.TransitiveProperty or o == OWL.SymmetricProperty or o == OWL.AsymmetricProperty or o == OWL.IrreflexiveProperty or o == OWL.ReflexiveProperty:
							annotated_entity_text = "[" + entity_text + "[P]]"
						elif o == RDFS.Class or o == OWL.Class:
							annotated_entity_text = "[" + entity_text + "[C]]"
							break
						else:
							annotated_entity_text = "[" + entity_text + "[OTHER]]"


			return {"entity localname": split_entity_local_name, "entity uri": entity_uri, "entity text": entity_text, "annotated text": annotated_entity_text}


# this function takes as input the path (with final slash) of a folder with one or more ontologies
# a folder (with subfolders, one for each ontology) with files txt 
# with the original uris (separated by \n) of the ontology entities of the community
# it is important that the sublfolders have the same name as the file name of the respective ontologies
# "True" if you want that also rdfs:comments are included, "False" if not
# and an optional string with the namespace(s) to be excluded, separated by white spaces
# and returns a folder with subfolders (one for each ontology) with files csv (one for each community)
# with the uri and the text (that concatenates english labels (and comments))
def communities_text_from_folder(ontologies_folder, original_uris_communities_folder, output_folder, also_comments, remove_duplicates, namespaces_tobe_excluded="no-namespaces"):
	if not namespaces_tobe_excluded == "no-namespaces":
		namespaces = list()
		for namespace in namespaces_tobe_excluded.split():
			namespaces.append(namespace)
	all_text_dict = {}
	all_annotated_text_list = list()
	for ontology_file in os.listdir(ontologies_folder):
		rdf_graph = create_rdf_graph(ontologies_folder + ontology_file)
		if rdf_graph:
			for uris_file in os.listdir(original_uris_communities_folder + ontology_file.split(".")[0]):
				text_list = list()
				annotated_text_list = list()
				text_concatenated = ""
				annotated_text_concatenated = ""
				with open(original_uris_communities_folder + ontology_file.split(".")[0] + "/" + uris_file) as file:
					#print(original_uris_communities_folder + ontology_file.split(".")[0] + "/" + uris_file)
					for count, line in enumerate(file):
						url = line.split("\n")[0]
						if not namespaces_tobe_excluded == "no-namespaces":
							if not any(x in str(url) for x in namespaces):
								if also_comments == "True":
									entity_dict = create_text_from_ontology_entity_noblanknodes(rdf_graph, url, "en")
								elif also_comments == "False":
									entity_dict = create_text_from_ontology_entity_noblanknodes_onlylabels(rdf_graph, url, "en")
								text_list.append([entity_dict["entity uri"], entity_dict["entity text"]])
								text_concatenated += entity_dict["entity text"] + " "
								text_lines = text_concatenated.splitlines()
								text_rejoined = ''.join(text_lines)
								annotated_text_list.append([entity_dict["entity uri"], entity_dict["annotated text"]])
								annotated_text_concatenated += entity_dict["annotated text"] + " "
								annotated_text_lines = annotated_text_concatenated.splitlines()
								annotated_text_rejoined = ''.join(annotated_text_lines)
						else:
							if also_comments == "True":
								entity_dict = create_text_from_ontology_entity_noblanknodes(rdf_graph, url, "en")
							elif also_comments == "False":
								entity_dict = create_text_from_ontology_entity_noblanknodes_onlylabels(rdf_graph, url, "en")
							text_list.append([entity_dict["entity uri"], entity_dict["entity text"]])
							text_concatenated += entity_dict["entity text"] + " "
							text_lines = text_concatenated.splitlines()
							text_rejoined = ''.join(text_lines)
							annotated_text_list.append([entity_dict["entity uri"], entity_dict["annotated text"]])
							annotated_text_concatenated += entity_dict["annotated text"] + " "
							annotated_text_lines = annotated_text_concatenated.splitlines()
							annotated_text_rejoined = ''.join(annotated_text_lines)
				if remove_duplicates == "True":
					text_words = text_rejoined.split()
					unique_text_words = " ".join(sorted(set(text_words), key=text_words.index))
					all_text_dict[uris_file.split("_original_uris")[0]] = unique_text_words
					all_annotated_text_list.append(annotated_text_rejoined)
				elif remove_duplicates == "False":
					all_text_dict[uris_file.split("_original_uris")[0]] = text_rejoined
					all_annotated_text_list.append(annotated_text_rejoined)
				# csv with one row per ontology entity of the community, with its text
				csv_entities_filename = output_folder + ontology_file.split(".")[0] + "/entities_csv/" + uris_file.split("_original_uris")[0] + "_entities" + ".csv"
				# csv with only one row, with the concatenated text of all the entities of the community
				csv_community_filename = output_folder + ontology_file.split(".")[0] + "/community_csv/" + uris_file.split("_original_uris")[0] + ".csv"
				os.makedirs(os.path.dirname(csv_entities_filename), exist_ok=True)
				os.makedirs(os.path.dirname(csv_community_filename), exist_ok=True)
				with open(csv_entities_filename, "w") as e:
					csvwriter = csv.writer(e)
					csvwriter.writerow(['uri', 'text'])
					for i in text_list:
						csvwriter.writerow([i[0], i[1]])
				df = pd.read_csv(csv_entities_filename)
				df['annotated text'] = annotated_text_list
				with open(csv_community_filename, "w") as c:
					csvwriter = csv.writer(c)
					csvwriter.writerow(['community', 'text', 'annotated text'])
					if remove_duplicates == "True":
						csvwriter.writerow([uris_file.split("_original_uris")[0], unique_text_words, annotated_text_rejoined])
					elif remove_duplicates  == "False":
						csvwriter.writerow([uris_file.split("_original_uris")[0], text_rejoined, annotated_text_rejoined])
	# merge all community texts in one csv
	with open(output_folder + "all_communities_text.csv", 'w') as csv_file:  
		writer = csv.writer(csv_file)
		for key, value in all_text_dict.items():
			writer.writerow([key, value])
	# names=["comm_id", "text"]
	df = pd.read_csv(output_folder + "all_communities_text.csv", header=None)
	df['annotated text'] = all_annotated_text_list
	#df = df.append([all_annotated_text_list], ignore_index=True)
	df.to_csv(output_folder + "all_communities_text_annotated.csv", header=False)


if __name__ == '__main__':
	if len(sys.argv) == 7:
		communities_text_from_folder(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6])
	else:
		communities_text_from_folder(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])