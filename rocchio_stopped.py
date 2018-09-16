from query_parser import get_parsed_queries
from collections import defaultdict,OrderedDict,Counter
import csv
from cosine_similarity_model import counters_all_docs,build_inverted_indexer,store_tfidfs,compute_cosine_similarity
import numpy as np
from stopping import query_stopping

# get the vocabulary for the whole corpus

#get the relevant docs
#get non relevant docs
#loop through each word from vocabulary and loop relevant docs inside it to create a dictionary(matrix) for each doc
#also loop through relevant docs
#loop to calculate matrix for query also
#finally apply the formula
kdocs=10
alpha=1
beta=0.75
gamma=0.15
top_kwords=20

top_kreldocs_query=OrderedDict()
#relevant_docs=list()
#nonrelevant_docs=list()
sorted_scores_query=OrderedDict()
vocabulary=OrderedDict()
doc_vectors=OrderedDict()

#relevant_vectors=list()
#nonrelevant_vectors=list()
query_vector=OrderedDict()

folder="cosine_stopped_results/"
filename="cosine_similiarity.csv"

queries=get_parsed_queries()
all_counters = counters_all_docs()
all_docs=all_counters.keys()
def read_cosine_similarity_results():
    with open(folder + filename, "r") as fd:
        reader=csv.reader(fd)
        scores_query=OrderedDict()
        for rows in reader:
            scores_query.setdefault(rows[0],[]).append([rows[2],rows[3]])
        sorted_scores_query=sorted(scores_query.items())
        for key,value in sorted_scores_query:
            top_kreldocs_query.setdefault(key,[]).append(value[:kdocs])

def get_relevant_docs(query_id):
    rel_docs=list()
    reldoc_list=top_kreldocs_query[query_id]
    for each_doc_tuple in reldoc_list:
        for each_doc in each_doc_tuple:
            rel_docs.append(each_doc[0])
    return rel_docs


def get_nonrelvant_docs(relevant_docs):
    # alldocs-relevant docs=non-relevant
    all_docs=all_counters.keys()
    #relevant_docs=get_relevant_docs(query_id)
    nonrel_docs=[item for item in all_docs if item not in relevant_docs]
    return nonrel_docs

#nonrelevant_docs=get_nonrelvant_docs()

vocabulary=build_inverted_indexer()

def initialize_vectors_for_all_docs():
    for doc_id in all_docs:
        doc_vectors[doc_id]=(np.zeros((1, len(vocabulary)),dtype=np.int))

def initialize_vector_for_queries():
    for query_id in queries:
        query_vector[query_id]= (np.zeros((1, len(vocabulary)), dtype=np.int))
    return query_vector

def create_doc_query_vectors():
    #key:docId #value:vector
    iter=0
    initialize_vectors_for_all_docs()
    query_vector = initialize_vector_for_queries()
    for each_term in vocabulary:
        for doc_id in all_docs:
            counter_doc=all_counters[doc_id]
            if each_term in counter_doc:
                doc_vectors[doc_id][0][iter]=counter_doc[each_term]
        #for queries
        for query_id,query_text in queries.items():
            query_text_counter = Counter(query_text.split())
            if each_term in query_text_counter:
                query_vector[query_id][0][iter]=query_text_counter[each_term]

        iter=iter+1
    x=0

def create_relevant_vectors(relevant_docs):
    relevant_vectors=list()
    for doc_id in relevant_docs:
            relevant_vectors.append(doc_vectors[doc_id])
    return relevant_vectors

def create_nonrelevant_vectors(nonrelevant_docs):
    nonrelevant_vectors = list()
    for doc_id in nonrelevant_docs:
        nonrelevant_vectors.append(doc_vectors[doc_id])
    return nonrelevant_vectors

def roccio_feedback():
    file = "cosine_similarity_rocchio_stopped"
    system_name = "ROCCHIO_STOP_COSINE_SIM"
    dict_idf = store_tfidfs(vocabulary)
    create_doc_query_vectors()
    read_cosine_similarity_results()
    for query_id,query_text in queries.items():
        expanded_query=query_stopping(query_text+expand_query(query_id))
        print query_id+":"+expanded_query+"\n"
        compute_main(query_id, expanded_query,dict_idf,file,system_name)

def compute_main(id,query,dict_idf,file,system_name):
    compute_cosine_similarity(id,query,dict_idf,file,system_name)

def expand_query(query_id):
        relevant_docs=get_relevant_docs(query_id)
        nonrelevant_docs=get_nonrelvant_docs(relevant_docs)
        relevant_vectors =create_relevant_vectors(relevant_docs)
        nonrelevant_vectors=create_nonrelevant_vectors(nonrelevant_docs)
        final_vector=alpha*query_vector[query_id]+beta*sum(relevant_vectors)/len(relevant_docs)-(gamma*sum(nonrelevant_vectors))/len(nonrelevant_docs)
        iteration=0
        final_dict=OrderedDict()
        for each_term in vocabulary:
            final_dict[each_term]=final_vector[0][iteration]
            iteration+=1
        ordered_final_dict = sorted(final_dict.items(), key=lambda t: t[1], reverse=True)
        ordered_topk_words = ordered_final_dict[:top_kwords]
        # print ordered_topk_words
        expansion_words = ''
        for each_word in ordered_topk_words:
            expansion_words += ' ' + each_word[0]
        return expansion_words

def main():
    roccio_feedback()

if __name__ == "__main__":main()








