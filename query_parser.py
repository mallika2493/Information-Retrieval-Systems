
import xml.etree.ElementTree as ET
from collections import OrderedDict
import re
import os
from bs4 import BeautifulSoup

queries=OrderedDict()
query_file="cacm.query"
query_xml="cacm_query.xml"
folder="cacm/"
parsed_path="parsed_corpus/"

def clean(string):
    str=re.sub(r'(\[.+?\])', '', string) #removes citation
    str=re.sub(r'\,(?=[^0-9])',' ',str).rstrip(",") # remove comma except within digits
    str=re.sub(r'\.(?=[^0-9])', ' ', str).rstrip(".") # remove dot except within digits
    str=re.sub(r"[^\w\s,.-]|_", ' ', str)  #remvoes all the punctuations except for - , comma and dot
    return str.lower()

def get_parsed_queries():
    with open(query_file, 'rb') as f, open(query_xml, 'wb') as g:
        g.write('<ROOT>{}</ROOT>'.format(f.read()))
    read_xml_into_dict()
    return queries

def read_xml_into_dict():
    tree = ET.parse(query_xml)
    root = tree.getroot()
    root.findall('DOC')[0][0].tail
    docs=root.findall('DOC')
    for doc in docs:
        query=doc[0].tail
        queries[doc[0].text.strip()]=clean(query.replace("\n",' '))

        #print doc[0].text+"|"+queries[doc[0].text]

def get_filenames():
    if not os.path.exists(parsed_path):
        os.makedirs(parsed_path)
    filenames= os.listdir(folder)
    return filenames

def parse_corpus():
    filenames = get_filenames()
    i = 0

    for filename in filenames:
        if filename==".DS_Store":
            continue
        with open(folder + filename, "r") as fd:
            fileCon = fd.read()
            soup = BeautifulSoup(fileCon, "html.parser")
            file_path = parsed_path + filename
            fil = open(file_path.split(".")[0] + ".txt", "w")

            body = soup.pre
            fil.write(clean(body.text).encode('utf8') + '\n')
            fil.close()
            fd.close()

get_parsed_queries()
parse_corpus()