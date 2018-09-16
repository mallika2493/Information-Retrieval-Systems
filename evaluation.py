import csv
from collections import OrderedDict
filename = 'bm25_results.csv'
def create_dictionary(filename):
	tablerows = []
	with open(filename, 'r') as csvfile:
		reader = csv.reader(csvfile, delimiter = ' ')
		for r in reader:
			tablerows.append(r[0].split(',')) 
	return tablerows


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

def map(tablerows):
	numqueries = 64
	rangeval = 100
	relDetails = get_relevance_data()
	x = 0
	finalmap = 0
	for x in range(0,6400,100):
		qID = tablerows[x][0]
		avgp = 0
		numRelDocs = 0
		if qID not in relDetails:
			continue
		for qranks in tablerows[x:(x + rangeval)]:
			if qranks[2] in relDetails[qID]:
				numRelDocs += 1
				precision = float(numRelDocs) / int(qranks[3])
				avgp += precision
		avgp = avgp/ len(relDetails[qID])
		finalmap += avgp
	finalmap = finalmap / numqueries
	return finalmap

#rr is taken as 0 for those query results whoch have no relevant documents
def mrr(tablerows):
	numqueries = 64
	rangeval = 100
	relDetails = get_relevance_data()
	x = 0
	finalmrr = 0
	for x in range(0,6400,100):
		qID = tablerows[x][0]
		if qID not in relDetails:
			continue
		for qranks in tablerows[x:(x + rangeval)]:
			if qranks[2] in relDetails[qID]:
				rr = float(1) / int(qranks[3])
				finalmrr += rr
				break
	finalmrr = finalmrr / 64
	return finalmrr

def p_at_k(tablerows, k):
	relDetails = get_relevance_data()
	patk = OrderedDict()
	for x in range(0,6400,100):
		qID = tablerows[x][0]
		numRelDocs = 0
		if qID not in relDetails:
			patk[qID] = 0
			continue
		for qranks in tablerows[x:(x + k)]:
			if qranks[2] in relDetails[qID]:
				numRelDocs += 1
			if int(qranks[3]) == k:
				patk[qID] = float(numRelDocs) / int(qranks[3])
	return patk

def compute_pnr(tablerows):
	updatedTR = list(tablerows)
	rangeval = 100
	relDetails = get_relevance_data()
	for x in range(0,6400,100):
		qID = tablerows[x][0]
		numRelDocs = 0
		cntr = 0
		if qID not in relDetails:
			for qranks in tablerows[x:(x + rangeval)]:
				index = x + cntr
				updatedTR[index].append('NA')
				updatedTR[index].append('NA')
				cntr += 1
		else:
			for qranks in tablerows[x:(x + rangeval)]:
				if qranks[2] in relDetails[qID]:
					numRelDocs += 1
				precision = float(numRelDocs) / int(qranks[3])
				recall = float(numRelDocs) / len(relDetails[qID])
				index = x + cntr
				updatedTR[index].append(round(precision,2))
				updatedTR[index].append(round(recall,2))
				cntr += 1
	return updatedTR

def store_in_file(filename, results):
	with open(filename[:-4] + "_pnr"+ ".csv", 'w') as csvfile:
		writer = csv.writer(csvfile)
		writer.writerow(['qID', 'Q0', 'DocID', 'Rank', 'Sim_Val', 'Sys_Name', 'Precision', 'Recall'])
		for row in results:
			writer.writerow(row)

def main():
	filenames = ['bm25_results/bm25.csv','cosine_results/cosine_similiarity_task1.csv','TFIDF_results/TFIDF.csv','cosine_results/cosine_similarity_rocchio.csv','lucene_results.csv']
	for filename in filenames:
		tablerows = create_dictionary(filename)
		with open(filename[:-4] + "_evaluation.txt", "w") as f:
			f.write('MAP = ' + str(map(tablerows)) + "\n")
			f.write('MRR = ' + str(mrr(tablerows)) + "\n")
			for qid, pk in p_at_k(tablerows, 5).items():
				f.write('Query ID: ' + str(qid) + " " + 'P@5: ' + str(pk) + "\n")
			for qid, pk in p_at_k(tablerows, 20).items():
				f.write('Query ID: ' + str(qid) + " " + 'P@20: ' + str(pk) + "\n")
		store_in_file(filename,compute_pnr(tablerows))

if __name__ == '__main__':
	main()
