import pandas as pd 
import numpy as np
import csv
import sys
import re
import os

def clusters_frames_frequency_analysis_and_labeling(input_clusters_csv, output_clusters_frames_analysis_folder):
	#df1 = pd.read_csv("/Users/vale/Documents/PhD/experiments/text_clustering/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered/clusters_run2_belowaverage_nocomments_filtered_enriched_synsetframe_tfidf_max0.90_min1_unigram_1641features_100clusters_randomstate42_withDOREMUS1.csv")
	df1 = pd.read_csv(input_clusters_csv)
	df1.fillna('', inplace=True)
	### 
	frame_list = list()
	synset_list = list()
	#with open("/Users/vale/Documents/PhD/experiments/text_clustering/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered-frame-synset.csv", "w") as csv_output:
	os.makedirs(os.path.dirname(output_clusters_frames_analysis_folder + "clustering-framesynset.csv"), exist_ok=True)
	with open(output_clusters_frames_analysis_folder + "clustering-framesynset.csv", "w") as csv_output:
		csvwriter = csv.writer(csv_output)
		csvwriter.writerow(['community', 'cluster', 'doc', 'annotateddoc', 'frame', 'synset', 'synsetframe triplet', 'noun/verb w/o frame', 'adj/adv w/o frame'])
		for i, row in df1.iterrows():
			frame_text = ""
			synset_text = ""
			synsetframe = row["synsetframe"].split(",")
			#FRAMES
			if "frame:" in row["synsetframe"]:
				for item in synsetframe:
					if "frame:" in item:
						frame_text += item + ","
			else:
				frame_text = "none" + ","
			frame_list.append(frame_text)
			#synsetframe_dict[row["synsetframe"]] = synsetframe_text
			#SYNSETS
			if "wn30:" in row["synsetframe"]:
				for item in synsetframe:
					if "wn30:" in item:
						synset_text += item + ","
			else:
				synset_text = "none" + ","
			synset_list.append(synset_text)
			csvwriter.writerow([row["community"], row["cluster"], row["doc"], row["annotateddoc"], frame_text, synset_text, row["synsetframe triplet"], row["noun/verb w/o frame"], row["adj/adv w/o frame"]])


	#df = pd.read_csv("/Users/vale/Documents/PhD/experiments/text_clustering/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered-frame-synset.csv")
	df = pd.read_csv(output_clusters_frames_analysis_folder + "clustering-framesynset.csv")
	df.fillna('', inplace=True)
	###

	number_clusters = range(df['cluster'].max()+1)
	#
	frame_quantity_list = list()
	synset_quantity_list = list()
	framesynset_triplet_quantity_list = list()
	nounverb_quantity_list = list()
	adjadv_quantity_list = list()
	#
	frame_quantity_aboveaverage_list = list()
	synset_quantity_aboveaverage_list = list()
	framesynset_triplet_quantity_aboveaverage_list = list()
	nounverb_quantity_aboveaverage_list = list()
	adjadv_quantity_aboveaverage_list = list()
	#
	community_list = list()
	number_communities_list = list()
	community_text_list = list()
	#
	cluster_labels = list()
	cluster_number_onto = list()
	# iteration over clusters
	for i in number_clusters:
		df_i = df.loc[df['cluster'] == i]

		# string joining all frames in each cluster
		frame_string = ''.join(df_i['frame'])
		# set of unique frames in each cluster
		frames = set(frame_string[:-1].split(","))
		if "none" in frames:
			frames.remove("none")

		# string joining all synsets in each cluster
		synset_string = ''.join(df_i['synset'])
		# set of unique synsets in each cluster
		synsets = set(synset_string[:-1].split(","))
		if "wn30:synset-Oregon-noun-1" in synsets:
			synsets.remove("wn30:synset-Oregon-noun-1")
		if "none" in synsets:
			synsets.remove("none")

		# string joining all framesynset triplets in each cluster
		framesynset_triplet_string = ''.join(df_i['synsetframe triplet'])
		# set of unique framesynset triplets in each cluster
		if not len(framesynset_triplet_string) == 0:
			framesynset_triplets = set(framesynset_triplet_string[:-1].split("\n"))
		else:
			framesynset_triplets = set()

		# string joining all nouns and verb synsets without frame in each cluster
		nounverb_string = ''.join(df_i['noun/verb w/o frame'])
		# set of unique framesynset triplets in each cluster
		if not len(nounverb_string) == 0:
			nounverbs = set(nounverb_string[:-1].split("\n"))
			if "wn30:synset-Oregon-noun-1" in nounverbs:
				nounverbs.remove("wn30:synset-Oregon-noun-1")
		else:
			nounverbs = set()

		# string joining all all adjective and adverb synsets without frame in each cluster
		adjadv_string = ''.join(df_i['adj/adv w/o frame'])
		# set of unique framesynset triplets in each cluster
		if not len(adjadv_string) == 0:
			adjadvs = set(adjadv_string[:-1].split("\n"))
		else:
			adjadvs = set()

		# string joining all communities ids in each cluster
		community_string = '\n'.join(df_i['community'])
		community_string += "\n"
		community_list.append(community_string)

		# number of communities per cluster
		number_of_communities = df_i['community'].size
		number_communities_list.append(number_of_communities)

		# number of different ontologies per cluster
		cluster_comms_list = df_i['community'].astype(str).tolist()
		print(cluster_comms_list)
		cluster_onto = set()
		for comm in cluster_comms_list:
			res = re.findall('[0-9]+', comm)
			cluster_onto.add(comm.split(res[0])[0])
		print(cluster_onto)
		cluster_number_onto.append(len(cluster_onto))


		# string joining all communities texts in each cluster
		community_text = '\n'.join(df_i['doc'])
		community_text_list.append(community_text)

		#dictionary for counting the occurrences of each frame in a cluster
		frame_quantity_dict = {}
		frame_quantity = ""
		frame_quantity_aboveaverage = ""
		if len(frames) > 0:
			for frame in frames:
				frame_quantity_dict[frame] = frame_string.count(frame)
			sorted_frame_quantity_dict = {k: v for k, v in sorted(frame_quantity_dict.items(), key=lambda item: item[1], reverse=True)}
			for key in sorted_frame_quantity_dict.keys():
				frame_quantity += key + ": " + str(sorted_frame_quantity_dict[key]) + "\n"
			frame_quantity_list.append(frame_quantity)
			average_frame_quantity = sum(sorted_frame_quantity_dict.values())/len(sorted_frame_quantity_dict)
			for key in sorted_frame_quantity_dict.keys():
				if sorted_frame_quantity_dict[key] >= average_frame_quantity:
					frame_quantity_aboveaverage += key + ": " + str(sorted_frame_quantity_dict[key]) + "\n"
			frame_quantity_aboveaverage_list.append(frame_quantity_aboveaverage)
		else:
			frame_quantity_list.append("no frames")
			frame_quantity_aboveaverage_list.append("no frames")

		#dictionary for counting the occurrences of each synset in a cluster
		synset_quantity_dict = {}
		synset_quantity = ""
		synset_quantity_aboveaverage = ""
		if len(synsets) > 0:
			for synset in synsets:
				synset_quantity_dict[synset] = synset_string.count(synset)
			sorted_synset_quantity_dict = {k: v for k, v in sorted(synset_quantity_dict.items(), key=lambda item: item[1], reverse=True)}
			for key in sorted_synset_quantity_dict.keys():
				synset_quantity += key + ": " + str(sorted_synset_quantity_dict[key]) + "\n"
			synset_quantity_list.append(synset_quantity)
			average_synset_quantity = sum(sorted_synset_quantity_dict.values())/len(sorted_synset_quantity_dict)
			for key in sorted_synset_quantity_dict.keys():
				if sorted_synset_quantity_dict[key] >= average_synset_quantity:
					synset_quantity_aboveaverage += key + ": " + str(sorted_synset_quantity_dict[key]) + "\n"
			synset_quantity_aboveaverage_list.append(synset_quantity_aboveaverage)
		else:
			synset_quantity_list.append("no synsets")
			synset_quantity_aboveaverage_list.append("no synsets")

		# generate labels for clusters taking the most frequent(s) between frame(s) and synset(s)
		if len(synsets) > 0 and len(frames) > 0:
			max_occurrences_frame = max(sorted_frame_quantity_dict.values())
			max_occurrences_synset = max(sorted_synset_quantity_dict.values())
			cluster_frames = list()
			cluster_synsets = list()
			if max_occurrences_frame >= max_occurrences_synset:
				for key in sorted_frame_quantity_dict.keys():
					if sorted_frame_quantity_dict[key] == max_occurrences_frame:
						cluster_frames.append(key.split(':')[1])
				cluster_labels.append(" - ".join(cluster_frames))
			else:
				for key in sorted_synset_quantity_dict.keys():
					if sorted_synset_quantity_dict[key] == max_occurrences_synset:
						cluster_synsets.append(key.split(':')[1])
				cluster_labels.append(" - ".join(cluster_synsets))
		elif len(synsets) > 0:
			max_occurrences_synset = max(sorted_synset_quantity_dict.values())
			for key in sorted_synset_quantity_dict.keys():
				if sorted_synset_quantity_dict[key] == max_occurrences_synset:
					cluster_synsets.append(key.split(':')[1])
			cluster_labels.append(" - ".join(cluster_synsets))
		else:
			cluster_labels.append("no label")



		#dictionary for counting the occurrences of each framesynset triplet in a cluster
		framesynset_triplet_quantity_dict = {}
		framesynset_triplet_quantity = ""
		framesynset_triplet_quantity_aboveaverage = ""
		if len(framesynset_triplets) > 0:
			for framesynset in framesynset_triplets:
				framesynset_triplet_quantity_dict[framesynset] = framesynset_triplet_string.count(framesynset)
			sorted_framesynset_triplet_quantity_dict = {k: v for k, v in sorted(framesynset_triplet_quantity_dict.items(), key=lambda item: item[1], reverse=True)}
			for key in sorted_framesynset_triplet_quantity_dict.keys():
				framesynset_triplet_quantity += key + ": " + str(sorted_framesynset_triplet_quantity_dict[key]) + "\n"
			framesynset_triplet_quantity_list.append(framesynset_triplet_quantity)
			average_framesynset_triplet_quantity = sum(sorted_framesynset_triplet_quantity_dict.values())/len(sorted_framesynset_triplet_quantity_dict)
			for key in sorted_framesynset_triplet_quantity_dict.keys():
				if sorted_framesynset_triplet_quantity_dict[key] >= average_framesynset_triplet_quantity:
					framesynset_triplet_quantity_aboveaverage += key + ": " + str(sorted_framesynset_triplet_quantity_dict[key]) + "\n"
			framesynset_triplet_quantity_aboveaverage_list.append(framesynset_triplet_quantity_aboveaverage)
		else:
			framesynset_triplet_quantity_list.append("no triplets")
			framesynset_triplet_quantity_aboveaverage_list.append("no triplets")


		#dictionary for counting the occurrences of each nounverb synset in a cluster
		nounverb_quantity_dict = {}
		nounverb_quantity = ""
		nounverb_quantity_aboveaverage = ""
		if len(nounverbs) > 0:
			for nounverb in nounverbs:
				nounverb_quantity_dict[nounverb] = nounverb_string.count(nounverb)
			sorted_nounverb_quantity_dict = {k: v for k, v in sorted(nounverb_quantity_dict.items(), key=lambda item: item[1], reverse=True)}
			for key in sorted_nounverb_quantity_dict.keys():
				nounverb_quantity += key + ": " + str(sorted_nounverb_quantity_dict[key]) + "\n"
			nounverb_quantity_list.append(nounverb_quantity)
			average_nounverb_quantity = sum(sorted_nounverb_quantity_dict.values())/len(sorted_nounverb_quantity_dict)
			for key in sorted_nounverb_quantity_dict.keys():
				if sorted_nounverb_quantity_dict[key] >= average_nounverb_quantity:
					nounverb_quantity_aboveaverage += key + ": " + str(sorted_nounverb_quantity_dict[key]) + "\n"
			nounverb_quantity_aboveaverage_list.append(nounverb_quantity_aboveaverage)
		else:
			nounverb_quantity_list.append("" + "\n")
			nounverb_quantity_aboveaverage_list.append("" + "\n")

		#dictionary for counting the occurrences of each adjadv synset in a cluster
		adjadv_quantity_dict = {}
		adjadv_quantity = ""
		adjadv_quantity_aboveaverage = ""
		if len(adjadvs) > 0:
			if not (len(adjadvs) == 1 and "" in adjadvs):
				for adjadv in adjadvs:
					adjadv_quantity_dict[adjadv] = adjadv_string.count(adjadv)
				sorted_adjadv_quantity_dict = {k: v for k, v in sorted(adjadv_quantity_dict.items(), key=lambda item: item[1], reverse=True)}
				for key in sorted_adjadv_quantity_dict.keys():
					adjadv_quantity += key + ": " + str(sorted_adjadv_quantity_dict[key]) + "\n"
				adjadv_quantity_list.append(adjadv_quantity)
				average_adjadv_quantity = sum(sorted_adjadv_quantity_dict.values())/len(sorted_adjadv_quantity_dict)
				for key in sorted_adjadv_quantity_dict.keys():
					if sorted_adjadv_quantity_dict[key] >= average_adjadv_quantity:
						adjadv_quantity_aboveaverage += key + ": " + str(sorted_adjadv_quantity_dict[key]) + "\n"
				adjadv_quantity_aboveaverage_list.append(adjadv_quantity_aboveaverage)
		else:
			adjadv_quantity_list.append("" + "\n")
			adjadv_quantity_aboveaverage_list.append("" + "\n")

	

	all_frames_synsets = pd.DataFrame(data={'cluster' : number_clusters, 'label' : cluster_labels, 'docs' : community_text_list, '# communities' : number_communities_list, '# onto' : cluster_number_onto, 'frames' : frame_quantity_list, 'synsets' : synset_quantity_list, 'framesynset triplets' : framesynset_triplet_quantity_list, 'adj/adv w/o frame' : adjadv_quantity_list, 'noun/verb w/o frame' : nounverb_quantity_list, 'communities' : community_list, 'docss' : community_text_list})
	#all_frames_synsets.to_csv("/Users/vale/Documents/PhD/experiments/text_clustering/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered-framesynset-analysis-withoutnone.csv")
	os.makedirs(os.path.dirname(output_clusters_frames_analysis_folder + "clustering-framesynset-analysis.csv"), exist_ok=True)
	all_frames_synsets.to_csv(output_clusters_frames_analysis_folder + "clustering-framesynset-analysis.csv")

	frames_synsets_aboveaverage = pd.DataFrame(data={'cluster' : number_clusters, 'label' : cluster_labels, 'docs' : community_text_list, '# communities' : number_communities_list, '# onto' : cluster_number_onto, 'frequent frames' : frame_quantity_aboveaverage_list, 'frequent synsets' : synset_quantity_aboveaverage_list, 'frequent framesynset triplets' : framesynset_triplet_quantity_aboveaverage_list, 'frequent adj/adv w/o frame' : adjadv_quantity_aboveaverage_list, 'frequent noun/verb w/o frame' : nounverb_quantity_aboveaverage_list, 'communities' : community_list, 'docss' : community_text_list})
	#frames_synsets_aboveaverage.to_csv("/Users/vale/Documents/PhD/experiments/text_clustering/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered-framesynset-mostfrequent-withoutnone.csv")
	os.makedirs(os.path.dirname(output_clusters_frames_analysis_folder + "clustering-framesynset-mostfrequent.csv"), exist_ok=True)
	frames_synsets_aboveaverage.to_csv(output_clusters_frames_analysis_folder + "clustering-framesynset-mostfrequent.csv")

if __name__ == '__main__':
	clusters_frames_frequency_analysis_and_labeling(sys.argv[1], sys.argv[2])
