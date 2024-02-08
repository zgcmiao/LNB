import argparse
import json
from collections import defaultdict

from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans


def clustering_label(label_path, num_clusters, output_path):
    """
    Read the label list from label_path, cluster it into num_clusters categories,
     and finally save the results to output_path

    :param label_path: path to the label_list
    :param num_clusters: number of clusters
    :param output_path: path to save
    """
    with open(label_path, encoding='utf-8') as f:
        label_list = json.load(f)

    sbert = SentenceTransformer('all-MiniLM-L6-v2')
    label_embeddings = sbert.encode(label_list)
    km_cluster = KMeans(n_clusters=num_clusters, max_iter=300, n_init=40, init='k-means++')
    result = km_cluster.fit_predict(label_embeddings)

    label_dict = defaultdict(list)
    for label_str, label_result in zip(label_list, result):
        label_dict[f'{label_result}'].append(label_str)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(label_dict, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('label_path')
    parser.add_argument('num_clusters')
    parser.add_argument('output_path')

    args = parser.parse_args()
    label_path = args.label_path
    num_clusters = args.num_clusters
    output_path = args.output_path

    clustering_label(label_path, num_clusters, output_path)
