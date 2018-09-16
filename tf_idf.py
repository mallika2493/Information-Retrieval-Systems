from collections import OrderedDict,Counter
from math import log
from query_parser import get_parsed_queries
import os
import csv

dict_df = OrderedDict()

dest_folder="TFIDF_results/"
file="TFIDF"
tfidf_values=OrderedDict()
path="parsed_corpus/"
def get_filenames():
    return os.listdir(path)
filenames=get_filenames()
N=len(filenames)
system_name="TF_IDF"

#IndexInfo Class stores Doc ID and count
class IndexInfo(object):
    docId = ""
    tf = 0
    def __init__(self,doc_id,count):
        self.docId=doc_id
        self.tf=count

def make_IndexInfo(doc_id,count):
    index_info = IndexInfo(doc_id,count)
    return index_info


def counters_all_docs():
    counter_docs=OrderedDict()
    for filename in filenames:
        fd = open(path + filename, "r")
        fileCon = fd.read()
        fd.close()
        counter_docs[filename] = Counter(fileCon.strip().split())
    return counter_docs

all_counters=counters_all_docs()

def store_tfidfs(unigram):
    tf_idf=OrderedDict()
    for key in unigram:
            val=unigram[key]
            len_val=len(val)
            if len_val == 0:
                print len_val
                tf_idf[key] = 0
            else:
                tf_idf[key] = 1+log(float(N)/len_val)
    return tf_idf

def build_inverted_indexer():
    filenames = get_filenames()
    unigram = OrderedDict()
    file_map=OrderedDict()
    doc_num=0
    for filename in filenames:
        doc_num+=1
        fd=open(path+filename,"r")
        fileCon = fd.read()
        fd.close()
        counters = Counter(fileCon.strip().split())
        file_map[doc_num]=filename
        for each_word in counters:
            unigram.setdefault(each_word,[]).append(make_IndexInfo(doc_num, counters[each_word]))
    return unigram

# creates the directory if not already present
def create_path(path):
     if not os.path.exists(path):
       os.makedirs(path)

#query_id Q0 doc_id rank TFIDF_score system_name
def write_TFIDF_matrix(query_id,sorted_TFIDF):
    create_path(dest_folder)
    with open(dest_folder+file+".csv", 'a') as csv_file:
        writer_tf = csv.writer(csv_file)
        limit=0
        for tuple in sorted_TFIDF:
            if limit >= 100:
                break
            limit+=1
            print "DOCID:"+str(tuple[0])+"|"+str(tuple[1])
            writer_tf.writerow([query_id,"Q0",tuple[0][:-4],limit, tuple[1],system_name])

def compute_tfidf(query_id,query,dict_tfidf):
    for filename in filenames:
        counters = all_counters[filename]
        tfidf_values[filename]=0
        query_terms=query.split(" ")
        for term in query_terms:
            if term in counters:
                doc_tfidf = dict_tfidf[term]
                tfidf_values[filename]+=counters[term]*doc_tfidf
    write_TFIDF_matrix(query_id,sorted(tfidf_values.items(),key=lambda t:t[1],reverse=True))

def main():
    unigram=build_inverted_indexer()
    dict_idf = store_tfidfs(unigram)
    if os.path.exists(dest_folder+file+".csv"):
        os.remove(dest_folder+file+".csv")
    queries = get_parsed_queries()
    for key in queries:
        query_id = key
        compute_tfidf(query_id.strip(),queries[key],dict_idf)

if __name__ == "__main__":main()
