# Results

In this folder you can find the results of the experiments that we describe in the paper https://arxiv.org/abs/2106.12831.

### CH: results from the Cultural Heritage corpus
### Conf: results from the Conference corpus

Each of the previous folders have the following subfolders:

- communities: txt files with all nodes of the communities from the intensional graph

- communities_images: images of the communities (one folder per ontology)

- communities_intensional: intensional representation of the communities (one folder per ontology)

- communities_original_uris: txt files with the original URIs of the ontology entities in the communities

- communities_texts: one folder per ontology with the initial version of the texts of the communities, and files: 
  - "all_communities_text.csv" with the initial texts of all communities, 
  - "all_communities_text_annotated.csv" includes also the annotation of the text wrt its provenance (class or property), 
  - "all_communities_synsetframe.csv" adds two columns with synsets and frames of the texts and the text annotated with this synsets and frames, 
  - "all_communities_synsetsframe_filtered_enriched" provides the synsets and frames filtered (we remove those coming from lemmas "have" and "be") and enriched with more general frames in the hierarchy, 
  - "all_communities81clusters.csv" (Conf) /"all_communities_communities100clusters.csv" (CH) is the output of the clustering of communities based on the texts in "all_communities_synsetsframe_filtered_enriched".

- Subfolder statistics_communities: txt files with some statistics of the communities (one file for each ontology)

- Subfolder labeled_clusters: it contains the files:
  - "clustering-framesynset-analysis.csv" contains the output of the method, that is used for producing the catalogue, with clusters, their labels, a description (the docs of the communities, # communities per cluster, #ontologies per cluster, and all synsets and frames of the cluster with their frequency) 
  - "clustering-framesynset-mostfrequent.csv" is the same as (i) but contains only frames and synsets with a frequency equal or above the average frequency of synset/frames in the cluster, 
  - "clustering-framesynset.csv" is an intermediate file used to generate (i) and (ii).

