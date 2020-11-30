
#RANDOM COMMENT dadsfdsakf;
import sys
import math
import json
from collections import defaultdict
from datetime import datetime
seek_index = dict()
docid_to_url = dict()
N_corpus = None

def create_seek_index():
    global seek_index, N_corpus
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

         
'''
def merge_lists(list1, list2):
    return_list = []
    list1_dict = dict()
    for docs1 in list1:
        list1_dict[docs1.split(':')[0]] = docs1.split(':')[1]
    for docs2 in list2:
        if(docs2.split(':')[0] in list1_dict):
            new_str = docs2.split(':')[0] +":"+ str(int(list1_dict[docs2.split(':')[0]]) + int(docs2.split(':')[1]))
            return_list.append(new_str)
    return return_list
'''
    
def cosine_similarity(query_vector, document_vector): #query vector: {token1:tf_idf, token2:tf_idf}  doc_vector: {token1:wt1, token3:wt2}
    dot_product = 0
    for token, norm_tf_idf in query_vector.items():
        if token in document_vector:
            dot_product += document_vector[token]*norm_tf_idf
    return dot_product
                         
             
def search(query): # we are using lnc.ltc (ddd.qqq)
    tokens = query.split(' ')
    doc_vectors = defaultdict(dict)    # {doc1:{token1:wt1, token2:wt2}, doc2:{token1:wt1, token2:wt2}} used for keeping order for dot prodcut
    doc_vectors_sum_of_sqrts = defaultdict(int) # {doc1: sum_of_sqrts1, doc2: sum_of_sqrts2}
    with open("Index.txt", "r") as index:
        df_dict = defaultdict(int) # used for query_vector only to get the df values in computing idf
        for token in set(tokens):
            if token.lower() not in seek_index:
                return []
            offset = seek_index[token.lower()]
            index.seek(offset)
            line = index.readline().rstrip().split(",") # [term:num_doc, doc_id:term_freq, doc_id2:term_freq, ...]
            for docFreq in line[1:]:
                doc, freq = docFreq.split(':')  #term:num_doc -> split(':') -> term, num_doc
                wt = 1 + math.log10(int(freq))
                doc_vectors[doc][token] = wt
                doc_vectors_sum_of_sqrts[doc] += wt**2
            #get tokens doc freq
            df_dict[token] = line[0].split(':')[1] # "line[0] -> term:num_docs  .split(':')[1] -> num_docs "
            
            
    for doc, sum_of_sq in doc_vectors_sum_of_sqrts.items():
        for token in doc_vectors[doc]:
            doc_vectors[doc][token] = float(doc_vectors[doc][token])/math.sqrt(sum_of_sq)

    query_vector  = vector_query(tokens, df_dict)   #{token1:tf_idf_normalized, token2:tf_idf_normalized}
    
    return_list = []
    for docs, doc_vector in doc_vectors.items():
        sim = cosine_similarity(query_vector, doc_vector)
        return_list.append(f"{docs}:{sim}")  # [doc_id1:similarity, doc_id2:similarity]

    return_list.sort(key=lambda x: float(x.split(':')[1]), reverse=True) #sorts by similarity by splitting doc_id1:similarity -> similarity
    return return_list



    '''
    line_list.sort(key=lambda x: x[0].split(':')[1])
    if(len(line_list) == 1):
        current_line = line_list[0][1:]
        current_line.sort(key=lambda x: int(x.split(':')[1]), reverse=True)
        return current_line

    indx = 2
    current_line = merge_lists(line_list[0][1:], line_list[1][1:])
    while indx<len(tokens):
        current_line = merge_lists(current_line, line_list[indx][1:])
        indx +=1
    current_line.sort(key=lambda x: int(x.split(':')[1]), reverse=True)
    return current_line
    '''

def vector_query(tokens, df_dict):
    global N_corpus
    '''returns the normalized query vector'''
    token_vector = defaultdict(int) #{token1: normalized tf.idf, token2: normalized tf.idf}
   
    for token in tokens:
        token_vector[token] += 1
    for token, frequency in token_vector.items(): # Calculate weight = 1 + log(tf)
        if frequency == 0:
            continue
        token_vector[token] = 1 + math.log10(frequency)
    sum_of_sq = 0
    for token, df in df_dict.items():
        idf = math.log10(N_corpus/float(df))  
        token_vector[token] =  token_vector[token]*idf # Calculate the weight vector which is tf * idf 
        sum_of_sq += token_vector[token]**2 #gets the sum of squares for normalization of vector
        
    for token, tf_idf in token_vector.items(): #calculating the normalized vector for cosine.
        token_vector[token] = tf_idf/math.sqrt(sum_of_sq)
    
    return token_vector


    


def main():
    global docid_to_url
    create_seek_index()  
    with open("docidToUrl.json", 'r') as docidToUrl:
        docid_to_url = json.load(docidToUrl)
    user_query = input("enter query: ")
    start = datetime.now()
    while(user_query != "quit()"):
        top_url_list = search(user_query)
        print(datetime.now() - start)
        #print(top_url_list)
        i = 0
        show_more=True
        while show_more:
            if(i>=len(top_url_list)):
                break
            docid = top_url_list[i]

            print(docid_to_url[docid.split(':')[0]])
            #print(docid.split(':')[1])
            i+=1
            if(i%10==0):
                show = input("Show More? (yes/no)")
                if(show=='no'):
                    show_more=False
        user_query = input("enter query: ")

main() 