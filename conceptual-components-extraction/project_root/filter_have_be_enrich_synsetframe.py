import json
import pandas as pd
import csv
import sys

def remove_have_be_synsetframe(input_synset_frame_csv, top_level_anchestors_synsets, output_synset_frame_csv):
	#synsetframe_df = pd.read_csv("/Users/vale/Documents/PhD/experiments/text_clustering/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered/all_communities_synset_frame_withDOREMUS.csv")
	synsetframe_df = pd.read_csv(input_synset_frame_csv)
	#toplevelframe_df = pd.read_csv("/Users/vale/Documents/PhD/experiments/text_clustering/wordnet-disambiguation/topLevelAnchestors-prefix.csv")
	toplevelframe_df = pd.read_csv(top_level_anchestors_synsets)

#print(toplevelframe_df.loc[toplevelframe_df['f'].str.contains("frame:Revenge")]['topLevelAnchestor'].values[0] + "\n")

	#with open("/Users/vale/Documents/PhD/experiments/text_clustering/clustering-nocomments-100-alsocommswithoutsynsetframe-filtered/all_communities_filtered_enriched_synset_frame_withDOREMUS1.csv", "w") as csv_output:
	with open(output_synset_frame_csv, "w") as csv_output:
		csvwriter = csv.writer(csv_output)
		csvwriter.writerow(['community', 'text', 'annotated text', 'synset frame', 'filtered synset frame', 'synset frame triplet', 'noun/verb w/o frame', 'adj/adv w/o frame', 'annotated synset frame'])
		for index, row in synsetframe_df.iterrows():
			#filtered_synsetframe_string = ""
			filtered_synsetframe_list = list()
			synsetframe_triplet = ""
			synset_withoutframe = ""
			adv_adj_withoutframe = ""
			#we use try except because some of the communities don't have disambiguation, thus can't be read as a dictionary
			try:
				synsetframe = row["annotated synset frame"]
				synsetframe_dict = json.loads(synsetframe)
				#print(synsetframe_dict)
				for sentence in synsetframe_dict['sentences']:
					for multiword in sentence['multiWords']:
						if multiword['lemma'] == 'be' or multiword['lemma'] == 'have':
							sentence['multiWords'].remove(multiword)
				for sentence in synsetframe_dict['sentences']:
					#synset_withoutframe = ""
					for multiword in sentence['multiWords']:
						# check if key "FN17" in dictionary (if not, the multiWord has no frames)
						if 'WN30_FRAMESTER' in multiword['scoredAnnotations']:
							synset_scores = list()
							for synset in multiword['scoredAnnotations']['WN30_FRAMESTER']:
								if not synset['annotation'] == 'Oregon':
									synset_scores.append(synset['score'])
							max_score = max(synset_scores)
							for synset in multiword['scoredAnnotations']['WN30_FRAMESTER']:
								if synset['score'] == max_score:
									filtered_synsetframe_list.append(synset['annotation'])
									max_synset = synset['annotation']
							if 'FN17' in multiword['annotations']:
								for frame in multiword['annotations']['FN17']:
									#print(frame)
									synsetframe_triplet += max_synset + " - "
									synsetframe_triplet += frame
									# check if the frame has some toplevel anchestor
									if toplevelframe_df['f'].str.contains(frame).any():
										synsetframe_triplet += " - " + toplevelframe_df.loc[toplevelframe_df['f'].str.contains(frame)]['topLevelAnchestor'].values[0] + "\n"
									else:
										synsetframe_triplet += "\n"
									filtered_synsetframe_list.append(frame)
							# if there is no frame, I concatenate in synset_withoutframe all synsets without frame
							else:
								if "adjective" in max_synset or "adverb" in max_synset:
									adv_adj_withoutframe += max_synset + "\n"
								else:
									synset_withoutframe += max_synset + "\n"
				if not len(filtered_synsetframe_list) == 0:
					filtered_synsetframe_string = ",".join(filtered_synsetframe_list)
				#print(filtered_synsetframe_string)
			except:
				filtered_synsetframe_string = row["text"]
			csvwriter.writerow([row["community"], row["text"], row["annotated text"], row["synset frame"], filtered_synsetframe_string, synsetframe_triplet, synset_withoutframe, adv_adj_withoutframe, row["annotated synset frame"]])

if __name__ == '__main__':
	remove_have_be_synsetframe(sys.argv[1], sys.argv[2], sys.argv[3])

