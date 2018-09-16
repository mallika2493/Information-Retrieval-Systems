from math import pow, log, sqrt
import re, csv
import os
from collections import OrderedDict, Counter
from query_parser import get_parsed_queries,clean,read_xml_into_dict
invertedIndex = {}
avdl = 0
dest_folder = "bm25_results/"

# creates the directory if not already present
def create_path(path):
     if not os.path.exists(path):
       os.makedirs(path)

def create_table(qid, bm25):
	create_path(dest_folder)
	with open(dest_folder + "bm25"+ ".csv", 'a') as csvfile:
		writer = csv.writer(csvfile)
		x = 0
		for docId, rank in bm25[:100]:
			x += 1
			writer.writerow([str(qid), "Q0", str(docId), str(x), str(rank), "SYS_BM25"])

def append_zeros(numstr):
	finalstr = numstr
	for i in range(0,4 - len(numstr)):
		finalstr = "0" + finalstr
	return finalstr 

def get_relevance_data():
	relDetails = OrderedDict()
	with open ("cacm.rel", 'r') as relFile:
		for line in relFile:
			fields = line.strip('\n').split(" ")
			filename = "CACM-" + append_zeros(fields[2][5:])
			if fields[0] not in relDetails:
				relDetails[fields[0]] = []
			relDetails[fields[0]].append(filename)
	return relDetails

def create_query_counters(queryList):
	queryTfs = OrderedDict()
	for qID, qtext in queryList.items():
		bm25Rank = OrderedDict()
		qID = qID.strip()
		qtext = qtext.split(" ")
		qtext = [x for x in qtext if x != '']
		queryTfs[qID] = Counter(qtext)
	return queryTfs


def compute_bm25(docTfs, N, queryTfs, relDetails):
	k1 = 1.2
	k2 = 100
	b = 0.75
	for qID in queryTfs:
		bm25Rank = OrderedDict()
		R = len(relDetails[qID]) if qID in relDetails else 0
		for docID, counters in docTfs.items():
			bm25Rank[docID] = 0 
			dl =  len(counters)
			for term, cntrs in queryTfs[qID].items():
				ni = invertedIndex[term] if term in invertedIndex else 0
				ri = len(filter(lambda x: term in docTfs[x], relDetails[qID])) if R != 0 else 0
				K = k1 * ((1 - b) + (b * (dl / avdl)))
				qfi = cntrs
				fi = counters[term]
				part1 = log(((ri + 0.5) /(R - ri + 0.5)) / ((ni - ri + 0.5) / (N - ni - R + ri + 0.5)))
				part2 = ((k1 + 1) * fi) / (K + fi)
				part3 = ((k2 + 1) * qfi) / (k2 + qfi)
				bm25Rank[docID] += part1 * part2 * part3
		create_table(qID, sorted(bm25Rank.items(), key=lambda x: x[1], reverse = True))

def create_counters():
	global invertedIndex
	global avdl	
	path="parsed_corpus/"
	fileNames = os.listdir(path)
	counters = OrderedDict()
	docID = 0
	for fname in fileNames:
		readFile = open("parsed_corpus/" + fname, 'r')
		content = readFile.read()
		readFile.close()
		unigrams = re.findall("([\w,.-]+)", content)
		avdl +=  len(unigrams)
		for word in set(unigrams):
			if word in invertedIndex:
				invertedIndex[word] += 1
			else:
				invertedIndex[word] = 1
		counters[fname[:-4]] = Counter(unigrams)
	avdl = avdl / len(counters)
	return counters

def main():
	queryList=get_parsed_queries()
	docsCounters = create_counters()
	N = len(docsCounters)
	compute_bm25(docsCounters, N, create_query_counters(queryList), get_relevance_data())

if __name__ == '__main__':
	main()