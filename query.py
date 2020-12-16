# RANDOM COMMENT dadsfdsakf;
import sys
import math
import json
import re
import webbrowser
from flask import Flask ,request, render_template
from collections import defaultdict
from datetime import datetime
from nltk.stem import PorterStemmer

seek_index = dict()
docid_to_url = dict()
seek_doc_index = dict()
N_corpus = 0


def create_seek_index():
    global seek_index, N_corpus, seek_doc_index
    curr_offset = 0
    with open("Index.txt", "r") as index:
        for line in index:
            token_entry = line.split(',')[0].split(':')
            token = token_entry[0]
            if token_entry[1] == "num_docs":
                N_corpus = int(token)
                break
            seek_index[token] = curr_offset
            if sys.platform.startswith('darwin'):
                curr_offset += (len(line))
            else:
                curr_offset += (len(line)) + 1

    with open("doc_vector_length.txt", "r") as doc_db:
        curr_offset = 0
        for line in doc_db:
            N_corpus += 1  # MIGHT NEED TO SUBTRACT 1 FOR EXTRA LINE AT THE END OF DOC VECTOR LENGTH TXT
            doc, sum_of_sq = line.split(':')
            seek_doc_index[doc] = float(sum_of_sq)
    '''
    with open("doc_vector_length.txt", "r") as doc_db:
        curr_offset = 0
        for line in doc_db:
            N_corpus += 1  # MIGHT NEED TO SUBTRACT 1 FOR EXTRA LINE AT THE END OF DOC VECTOR LENGTH TXT
            doc_entry = line.split(':')
            doc = doc_entry[0]
            seek_doc_index[doc] = curr_offset
            if sys.platform.startswith('darwin'):
                curr_offset += (len(line))
            else:
                curr_offset += (len(line)) + 1
    '''
    #print("Num Docs:", N_corpus)



# query vector: {token1:tf_idf, token2:tf_idf}  doc_vector: {token1:wt1, token3:wt2}
def cosine_similarity(query_vector, document_vector):
    dot_product = 0
    for token, norm_tf_idf in query_vector.items():
        if token in document_vector:
            dot_product += document_vector[token]*norm_tf_idf
    return dot_product


def search(query, index, doc_db):  # we are using lnc.ltc (ddd.qqq)
    ps = PorterStemmer()
    tokens = [ps.stem(token.lower()) for token in re.findall("[a-zA-Z0-9]+", query)] # removes everything except alpha numeric from query
   
    df_dict = defaultdict(int)  # used for query_vector only to get the df values in computing idf, gets the doc frequency for each token
    line_cache = dict() # {token:line} caching the line from index.txt.
    for token in set(tokens):# building tf-wt for doc_vector and df_dict for idf score in query vector 
        if token.lower() not in seek_index:
            continue

        #if it a bad idf continue else we can seek

        offset = seek_index[token.lower()]
        index.seek(offset)
        line = index.readline().rstrip().split(",") # [term:num_doc, doc_id:term_freq, doc_id2:term_freq, ...]
        line_cache[token] = line #caching the seek of line 
        df_dict[token] = line[0].split(':')[1]  # "line[0] -> term:num_docs  .split(':')[1] -> num_docs "

    query_vector = vector_query(tokens, df_dict) # {token1:tf_idf_normalized, token2:tf_idf_normalized}
    
    initial_doc_vectors = defaultdict(dict)  # {doc1:{token1:wt1, token2:wt2}, doc2:{token1:wt1, token2:wt2}} 
    dict_of_doc_scores = defaultdict(int) # {doc_id:score}
    
    for token in query_vector: #query vector removed tokens with low idf scores and now we create out document vectors based on remaining tokens
        line = line_cache[token] # no need to seek line because cached
        for docFreq in line[1:]:

            doc, tf_raw = docFreq.split(':')  # doc_id:tf -> split(':') -> doc_id, tf
            
            sum_of_sq = seek_doc_index[doc]
            tf_wt = 1 + math.log10(int(tf_raw)) # building the doc vector 
            dict_of_doc_scores[doc]+=tf_wt/sum_of_sq * query_vector[token]
            initial_doc_vectors[doc][token] = tf_wt/sum_of_sq

    doc_vectors = defaultdict(dict)  # {doc1:{token1:wt1, token2:wt2}, doc2:{token1:wt1, token2:wt2}} 
    k_threshold = 50 #take a score and cut off at k_threshold documents so we dont have to take the cosine similarity of every single doc
    count = 0
    for doc, score in sorted(dict_of_doc_scores.items(), key = lambda x: x[1], reverse=True):
        doc_vectors[doc] = initial_doc_vectors[doc]
        count+=1
        if count>=k_threshold:
            break


    if len(df_dict) == 0: #all tokens in query were not in the seek_index so return empty seach result
        return []

    '''
    for doc in doc_vectors:
        offset = seek_doc_index[doc]
        doc_db.seek(offset)
        line = doc_db.readline().rstrip().split(":")# docid:sumofSquare\n -> [docid, sumofSquare]
        doc_sum_of_sq = line[1]
        for token in doc_vectors[doc]: # doc_vectors[doc] = {token1:wt1, token2:wt2}
            doc_vectors[doc][token] = float(
                doc_vectors[doc][token])/float(doc_sum_of_sq)  # wt1/sumofSquare
    '''
    

    return_list = []
    for docs, doc_vector in doc_vectors.items(): #OPTIMIZE WITH THRESHOLD K
        sim = cosine_similarity(query_vector, doc_vector)
        return_list.append(f"{docs}:{sim}") # [doc_id1:similarity, doc_id2:similarity]
    return_list.sort(key=lambda x: float(x.split(':')[1]), reverse=True) # sorts by similarity by splitting doc_id1:similarity -> similarity
    return return_list



def vector_query(tokens, df_dict):
    global N_corpus
    '''returns the normalized query vector'''
    token_vector = defaultdict(int)  # {token1: normalized tf.idf, token2: normalized tf.idf}

    for token in tokens:
        token_vector[token] += 1
    for token, frequency in token_vector.items():  # Calculate weight = 1 + log(tf)
        if frequency == 0:
            continue
        token_vector[token] = 1 + math.log10(frequency)
    sum_of_sq = 0
    total_idf = 0
    idf_vector = list()
    for token, df in df_dict.items():
        idf = math.log10(N_corpus/float(df))
        total_idf+=idf
        idf_vector.append((token, idf))
        token_vector[token] = token_vector[token]*idf  # Calculate the weight vector which is tf * idf
        sum_of_sq += token_vector[token]**2 # gets the sum of squares for normalization of vector

    final_token_vector = dict()
    idf_sum = 0

    threshold_percentage = 0.9 
    for token, idf in sorted(idf_vector, key=lambda x: x[1], reverse = True): #heuristic to remove tokens with low idf scores
        idf_sum+=idf
        percentage = idf_sum/total_idf
        final_token_vector[token] = token_vector[token]
        if percentage>threshold_percentage:
            break
    

    
    for token, tf_idf in final_token_vector.items(): # calculating the normalized vector for cosine.
        final_token_vector[token] = tf_idf/math.sqrt(sum_of_sq)

    return final_token_vector


app = Flask(__name__)
@app.route('/')
def main():
    global docid_to_url, index, doc_db
    create_seek_index()
    with open("docidToUrl.json", 'r') as docidToUrl:
        docid_to_url = json.load(docidToUrl)
    index = open("Index.txt", "r")
    doc_db = open("doc_vector_length.txt", "r")
    return render_template('index.html')
     

@app.route('/', methods=['POST'])
def what():
    user_query = request.form['search']
    start = datetime.now()

    top_url_list = search(user_query, index, doc_db)
    fixed_list = []
    for link in top_url_list:
        docid = link.split(":")[0]
        fixed_list.append(docid_to_url[docid])

    return render_template('index.html', urls = fixed_list , time = datetime.now() - start)

if __name__ == '__main__':
    webbrowser.open("http://localhost:5000/") 
    app.run()
    

index.close()
doc_db.close()


