# Project root

Here you can find the instructions for reproducing our experiments.
The already produced results (described in the paper https://arxiv.org/abs/2106.12831) are in the folder ``results``, and the results are explained there in a ``readme`` file.

The subfolder ``data`` contains a csv with top level ancestors of frames, which is used in one step of the experiment.

All the requirements for running the experiment are in the file environment.yml

The first part of all paths (``/Users/goofy/conceptual-components-extraction/``) is an example, replace it with the local path of a folder where you downloaded the main folder ``conceptual-components-extraction`` and where you will store the results of your experiment.

### 1 ``compute_greedy_modularity_communities.py``
Input:
- folder with the dataset of ontologies (one file per ontology)
- folder for storing the output
- "True": in this way, the community detection algorithm will be run recursively on communities with a density higher that the average

From the folder "/Users/goofy/conceptual-components-extraction/project_root/", run this line of code from the terminal:

    python compute_greedy_modularity_communities.py "/Users/goofy/conceptual-components-extraction/corpora/CH/CH_dataset_inferred/" "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/" "True"

(Replace "CH/CH_dataset_inferred/" with "Conf/Conf_dataset_inferred/" if you want to run the experiment on the Conf dataset)

Output: it produces all the results of the community detection algorithm applied to the corpus.

### 2 ``ontology_entities_to_annotatedtext_from_txt.py``
Input:
- folder with the dataset of ontologies (one file per ontology) 
- folder with the original uris of the entities within the detected communities: it is generated in step 1
- folder for storing the output
- "False": in this way, rdfs:comments will not be considered for generating the documents of the ontology entities
- "True": in this way, you will remove duplicates from the text of the communities
- "http://www.w3.org/2001/XMLSchema http://www.w3.org/2002/07/owl http://www.w3.org/2000/01/rdf-schema http://www.w3.org/1999/02/22-rdf-syntax-ns": these prefixes will not be considered for generating the documents of the ontology entities

From the folder "/Users/goofy/conceptual-components-extraction/project_root/", run this line of code from the terminal:

    python ontology_entities_to_annotatedtext_from_txt.py "/Users/goofy/conceptual-components-extraction/corpora/CH/CH_dataset_inferred/" "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_original_uris/" "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_texts/" "False" "True" "http://www.w3.org/2001/XMLSchema http://www.w3.org/2002/07/owl http://www.w3.org/2000/01/rdf-schema http://www.w3.org/1999/02/22-rdf-syntax-ns"

Output: it produces all the results of the initial step for creating the virtual documents of the communities.

### 3 ``ukb``
Build ukb (https://github.com/asoroa/ukb) and replace the executable in /Users/goofy/conceptual-components-extraction/project_root/disambiguation_framedetection/ukb/bin/ukb_wsd with your version.
Then,
From the folder "/Users/goofy/conceptual-components-extraction/project_root/disambiguation_framedetection/", run this line of code from the terminal:

    java -jar xxx.jar

Output: you will run an instance of the server that you will need in step 4

### 4 ``disambiguation_from_csv.py``
Input:
- csv with annotated texts of ontology entities: it is generated in step 2
- csv for storing the output

From the folder "/Users/goofy/conceptual-components-extraction/project_root/", run this line of code from the terminal:

    python disambiguation_from_csv.py  "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_texts/all_communities_text_annotated.csv" "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_texts/all_communities_synsetframe.csv"

Output: it produces the disambiguated and with related frames version of the virtual documents of the communities.

### 5 ``filter_have_be_enrich_synsetframe.py``
Input:
- csv with the disambiguated texts: it is generated in step 4
- csv with prefixed toplevel anchestors of frames (it is provided within the package)
- csv for storing the output

From the folder "/Users/goofy/conceptual-components-extraction/project_root/", run this line of code from the terminal:

    python filter_have_be_enrich_synsetframe.py  "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_texts/all_communities_synsetframe.csv" "/Users/goofy/conceptual-components-extraction/project_root/data/topLevelAnchestors-prefix.csv" "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_texts/all_communities_synsetframe_filtered_enriched.csv"

Output: it produces a filtered (no have and be lemmas) and enriched (top level ancestors frames) version of the disambiguated virtual documents of the communities.

### 6 ``clustering_synsetframe_communities.py``
Input:
- csv with the filtered and enriched with ancestors synset and frames: it is generated in step 5
- csv for storing the output
- number of clusters

From the folder "/Users/goofy/conceptual-components-extraction/project_root/", run this line of code from the terminal:

    python clustering_synsetframe_communities.py  "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_texts/all_communities_synsetframe_filtered_enriched.csv" "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_texts/all_communities_clusters.csv" "100"

(Replace "100" with "81" if you want to run the experiment on the Conf dataset)

Output: it runs the clustering algorithm on the virtual documents of the communities

### 7 ``clusters_frame_analysis.py``
Input:
- csv with clusters: it is generated in step 6
- folder for storing the results, i.e. 3 csvs

From the folder "/Users/goofy/conceptual-components-extraction/project_root/", run this line of code from the terminal:

    python clusters_frame_analysis.py  "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_texts/all_communities_clusters.csv" "/Users/goofy/conceptual-components-extraction/CH-community-clustering-output/communities_texts/labeled_clusters/"

Output: it produces all the final results.







