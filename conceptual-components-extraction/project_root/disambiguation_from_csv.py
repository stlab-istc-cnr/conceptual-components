import requests
import os
import pandas as pd
import csv
import sys


def replace_all(text, dic):
    for i, j in dic.items():
        text = text.replace(i, j)
    return text

#os.chdir("/Users/vale/Documents/PhD/experiments/text_clustering/wordnet-disambiguation/test_2")
#os.system("java -jar lgu.commons.server-0.0.8.jar")

def from_communities_text_to_synsetframe(input_text_csv, output_synsetframe_csv):
	d = { "https://w3id.org/framester/wn/wn30/instances/": "wn30:", "https://w3id.org/framester/framenet/abox/frame/": "frame:"}

	comm_csv_df = pd.read_csv(input_text_csv, names=["community", "text", "annotated text"])
#	comm_csv_df = pd.read_csv("/Users/vale/Documents/PhD/experiments/greedy_modularity_communities/dataset_documentation/CH_communities/latest_test/nosubsumed_recursion_belowaverage_run2/communities_texts_nocomments_filtered_annotated_NODOREMUS1/all_communities_text_annotated.csv", names=["community", "text", "annotated text"])


	# both synsets and frame, and annotates sentences with synsets and frames
	#with open("/Users/vale/Documents/PhD/experiments/greedy_modularity_communities/dataset_documentation/CH_communities/latest_test/nosubsumed_recursion_belowaverage_run2/communities_texts_nocomments_filtered_annotated_NODOREMUS1/all_communities_synset_frame.csv", "w") as csv_output:
	with open(output_synsetframe_csv, "w") as csv_output:
		csvwriter = csv.writer(csv_output)
		csvwriter.writerow(['community', 'text', 'annotated text', 'synset frame', 'annotated synset frame'])
		for i, row in comm_csv_df.iterrows():
			resp = requests.get('http://localhost:8080/cd?text=' + row["text"] + '&senseInventory=fn17')
			# check if any synset and/or frame has been found
			if not resp.text == "[]":
				start = resp.text.find("[") + 1
				end = resp.text.find("]")
				processed_resp = resp.text[start:end]
				processed_resp2 = processed_resp.replace("\"", "")
				annotated_resp = requests.get('http://localhost:8080/wfd?text=' + row["text"] + '&serialization=json')
				csvwriter.writerow([row["community"], row["text"], row["annotated text"], replace_all(processed_resp2, d), replace_all(annotated_resp.text, d)])
			# if no synset / frame is found, use the original text for columns "synset frame" and "annotated synset frame"
			else:
				csvwriter.writerow([row["community"], row["text"], row["annotated text"], row["text"], row["text"]])

if __name__ == '__main__':
	from_communities_text_to_synsetframe(sys.argv[1], sys.argv[2])

