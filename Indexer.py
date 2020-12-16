from bs4 import BeautifulSoup
from urllib.parse import urlparse
from os import walk, rename, path
import re
from collections import defaultdict
import json
from math import sqrt
from nltk.stem import PorterStemmer
from hashlib import sha224 

fingerprint_list = set()

def computeWordFrequencies(token_list):
    local_pages_word_frequencies = dict()
    for token in token_list:
        if token in local_pages_word_frequencies:
            local_pages_word_frequencies[token] += 1
        else:
            local_pages_word_frequencies[token] = 1
    return local_pages_word_frequencies




def simhash(word_frequency_dict):
    '''takes in the word frequency dict and output a binary vector for the ID of the website'''
    bin_length = 256
    total_vector = [0] * bin_length
    for word in word_frequency_dict.keys():
        one_vector = list()
        hash_val = bin(
            int(sha224(word.encode("utf-8")).hexdigest(), 16))[2:(bin_length+2)]
        hash_len = len(hash_val)

        if (hash_len < bin_length):
            difference = bin_length - hash_len
            hash_val = ("0" * difference) + hash_val
        for binary in hash_val:
            if binary == "0":
                one_vector.append(-1*word_frequency_dict[word])
            else:
                one_vector.append(word_frequency_dict[word])

        for indx in range(len(total_vector)):
            total_vector[indx] += one_vector[indx]
    binary_str = ""
    for i in total_vector:
        if i > 0:
            binary_str += "1"
        else:
            binary_str += "0"

    return binary_str

def check_duplicate_page(word_frequency_dict):
    global fingerprint_list
    fingerprint = simhash(word_frequency_dict)
    threshold = 0.9
    for each_website in fingerprint_list:
        total = 0
        xorval = bin(int(fingerprint, 2) ^ int(each_website, 2))[2:]
        if (len(xorval) < len(fingerprint)):
            difference = len(fingerprint)-len(xorval)
            xorval = ("0" * difference) + xorval
        for i in xorval:
            # we are forced to use xor but not xnor in this case
            # counting 0 means two digits are the same in xor
            if i == "0":
                total += 1
        similarity = float(total)/len(fingerprint)
        if similarity > threshold:
            fingerprint_list.add(fingerprint)
            return True
    fingerprint_list.add(fingerprint)
    return False



def store_doc_vector_length(doc_id, tokens):
    # docid1:sqrt_sum_of_square_tf\n docid2:sqrt_sum_of_square_tf
    with open("doc_vector_length.txt", 'a') as doc_db:
        vector_length = 0
        tf_dict = defaultdict(int)  # gets the token frequency in tokens
        for token in tokens:
            tf_dict[token] += 1
        for token, tf in tf_dict.items():  # computes the length of our vector by doing the sum of squares of the token counts
            vector_length += tf**2
        vector_length = sqrt(vector_length)  # Pythagorean Theorem
        write_string = f"{doc_id}:{vector_length}\n"
        doc_db.write(write_string)


def get_tokens_in_page(content):
    # gets the list of tokens in the website content
    ps = PorterStemmer()

    soup = BeautifulSoup(content, "html.parser")
    scripts = soup.find_all('script')
    for _ in scripts:
        soup.script.extract()
    styles = soup.find_all('style')
    for _ in styles:
        soup.style.extract()
    tokens_found = soup.get_text()

    tagWords = list()
    semiImportantTags =  soup.find_all(["h1", "h2", "h3", "strong","b"])
    title = soup.find_all('title')
    for tag in semiImportantTags:
        tagWords.append(tag.get_text().replace('\n', '').replace('\xa0', ''))
    for tag in title:
        t = tag.get_text().replace('\n', '').replace('\xa0', '')
        tagWords.append(t)
        tagWords.append(t)
    #print("tagwords", tagWords)
    #print(tokens_found)
    
    tokens = [ps.stem(token.lower()) for token in re.findall("[a-zA-Z0-9]+", tokens_found)]

    for words in tagWords:
        for token in re.findall("[a-zA-Z0-9]+", words):
            tokens.append(ps.stem(token.lower()))
    return tokens


def initialize_database():
    try:
        with open("Index.txt", 'w') as index:
            index.write("")
        with open("cache.txt", "w") as cache:
            cache.write("")
        with open("docidToUrl.json", "w") as docidToUrl:
            json.dump({}, docidToUrl, indent=4)
        with open("doc_vector_length.txt", 'w') as doc_db:
            doc_db.write("")
    except:
        raise Exception("Initailized database ran into trouble")


def store_index(merge_index):
    with open("Index.txt", 'r') as old_index:
        with open("cache.txt", 'a') as cache:
            merge_index = sorted(merge_index.items(), key=lambda x: x[0])
            merge_index_iter = 0
            for line in old_index:
                line = line.rstrip()
                row = line.split(",")
                old_index_token, old_index_num_docs = row[0].split(":")
                done = False
                while not done and merge_index_iter < len(merge_index):
                    merge_token_info = merge_index[merge_index_iter]
                    if old_index_token == merge_token_info[0]:
                        new_num_docs = int(old_index_num_docs) + \
                            int(merge_token_info[1]["num_docs"])
                        merge_string = ""
                        for doc_ID, tf_idf in merge_token_info[1].items():
                            if doc_ID == "num_docs":
                                continue
                            count = tf_idf["tf_idf"]
                            merge_string += f",{doc_ID}:{count}"
                        old_index_doc_string = ""
                        for doc_info in row[1:]:
                            old_index_doc_string += doc_info + ","
                        old_index_doc_string = old_index_doc_string[:-1]
                        final_string = f"{old_index_token}:{new_num_docs},{old_index_doc_string}" + \
                            merge_string+"\n"
                        cache.write(final_string)
                        merge_index_iter += 1
                        done = True
                    elif old_index_token < merge_token_info[0]:
                        cache.write(line+"\n")
                        done = True
                    else:
                        merge_string = ""
                        for doc_ID, tf_idf in merge_token_info[1].items():
                            if doc_ID == "num_docs":
                                continue
                            count = tf_idf["tf_idf"]
                            merge_string += f",{doc_ID}:{count}"
                        final_num_docs = merge_token_info[1]["num_docs"]
                        final_string = f"{merge_token_info[0]}:{final_num_docs}" + \
                            merge_string + "\n"
                        cache.write(final_string)
                        merge_index_iter += 1

            while merge_index_iter < len(merge_index):
                merge_token_info = merge_index[merge_index_iter]
                merge_string = ""
                for doc_ID, tf_idf in merge_token_info[1].items():
                    if doc_ID == "num_docs":
                        continue
                    count = tf_idf["tf_idf"]
                    merge_string += f",{doc_ID}:{count}"
                final_num_docs = merge_token_info[1]["num_docs"]
                final_string = f"{merge_token_info[0]}:{final_num_docs}" + \
                    merge_string+"\n"
                cache.write(final_string)
                merge_index_iter += 1

    rename("Index.txt", "temp.txt")
    rename("cache.txt", "Index.txt")
    rename("temp.txt", "cache.txt")
    with open("cache.txt", "w") as cache:
        cache.write("")


def store_docid(docid_to_url):
    with open("docidToUrl.json", 'r') as docidToUrl:
        old_dict = json.load(docidToUrl)
    with open("docidToUrl.json", "w") as docidToUrl:
        old_dict.update(docid_to_url)
        json.dump(old_dict, docidToUrl, indent=4)


def main():
    docid_to_url = {}
    initialize_database()
    index = {}
    num_docs = 0
    website_id = 0
    threshold = 500
    threshold_count = 0
    for (dirpath, _, filenames) in walk('./DEV'):
        for file_name in filenames:  # looping through files in the directory DEV
            in_file = open(f"{dirpath}/{file_name}", "r")
            # load the json of each file which contains {url, content, encoding}
            website = json.load(in_file)
            # tokens are the list of words in the website loaded
            tokens = get_tokens_in_page(website["content"])
            word_frequency_dict = computeWordFrequencies(tokens) # built to check duplicate pages 
            if (check_duplicate_page(word_frequency_dict)):
                continue
                
            threshold_count += 1
            num_docs += 1
            website_id += 1  # get_hash(website['url'])
            store_doc_vector_length(website_id, tokens)
            docid_to_url[website_id] = website['url']
            for token in tokens:
                if token in index:  # If the token is already in the index just add 1
                    # if the website is inside the index, we increment the frequency of the token for that website
                    if website_id in index[token]:
                        index[token][website_id]["tf_idf"] += 1
                    else:  # if website is not inside the index, we add the website and initialize tf_idf as 1 for the current token
                        index[token]["num_docs"] += 1
                        index[token][website_id] = {"tf_idf": 1}
                else:
                    index[token] = {  # If the specific token is NOT in the index, initialize the token
                        "num_docs": 1,
                        website_id: {
                            "tf_idf": 1
                        }
                    }
            if(threshold_count > threshold):
                store_docid(docid_to_url)
                store_index(index)
                index.clear()
                index = {}
                docid_to_url = {}
                threshold_count = 0

    store_docid(docid_to_url)
    store_index(index)
    index.clear()
    index = {}
    store_docid(docid_to_url)
    docid_to_url = {}

    with open("Index.txt", "r") as index:
        num_of_line = 0
        for line in index:
            num_of_line += 1

    print("number of unique tokens in Index: ", num_of_line)
    print("Index file size:", path.getsize("Index.txt"))
    print("number of documents: ", num_docs)


main()
