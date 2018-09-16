from query_parser import get_parsed_queries

queries=get_parsed_queries()
with open("queries.txt", 'wb') as f:
    for query_id,query_text in queries.items():
        f.write(query_id.strip()+" "+query_text.lstrip()+"\n")
f.close()
