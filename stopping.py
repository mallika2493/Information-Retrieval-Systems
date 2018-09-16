import os
def get_filenames():
    parsed_path="parsed_corpus"
    if not os.path.exists(parsed_path):
        os.makedirs(parsed_path)
    filenames= os.listdir(parsed_path)
    return filenames

def parse_corpus():
    filenames = get_filenames()
    i = 0
    swfile = open('common_words', 'r')
    stopwords = [word.strip('\n') for word in swfile]
    swfile.close()
    for filename in filenames:
        if filename==".DS_Store":
            continue
        fd = open("parsed_corpus/" + filename, "r")
        fileCon = fd.read()
        fd.close()
        wordList = [x for x in fileCon.split(" ") if x != '']
        contAftrStop = [word for word in wordList if word not in stopwords]
        stopFile = open("stopped_corpus/" + filename, "w")
        stopFile.write(' '.join(contAftrStop).encode('utf8') + '\n')
        stopFile.close()

def query_stopping(qtext):
    swfile = open('common_words', 'r')
    stopwords = [word.strip('\n') for word in swfile]
    swfile.close()
    wordList = [x for x in qtext.split(" ") if x != '']
    stoppedQuery = [word for word in wordList if word not in stopwords]
    return " ".join(stoppedQuery)