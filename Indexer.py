from hashlib import sha224
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from os import walk, rename, path
from collections import OrderedDict
from operator import getitem
import re
import json



def get_tokens_in_page(content):
    # gets the list of tokens in the website content
    soup = BeautifulSoup(content, "html.parser")
    scripts = soup.find_all('script')
    for _ in scripts:
        soup.script.extract()
    styles = soup.find_all('style')
    for _ in styles:
        soup.style.extract()
    tokens_found = soup.get_text()
    tokens = [token.lower()
              for token in re.findall("[a-zA-Z0-9]+", tokens_found)]
    return tokens


def get_hash(url):
    return sha224(url.encode("utf-8")).hexdigest()


def initialize_database():
    try:
        with open("Index.txt", 'w') as index:
            index.write("")
        with open("cache.txt", "w") as cache:
            cache.write("")
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


def main():
    initialize_database()
    index = {}
    num_docs = 0
    website_id = 0
    threshold = 500
    threshold_count = 0
    for (dirpath, _, filenames) in walk('./DEV'):
        for file_name in filenames:  # looping through files in the directory DEV
            threshold_count += 1
            num_docs += 1
            in_file = open(f"{dirpath}/{file_name}", "r")
            # load the json of each file which contains {url, content, encoding}
            website = json.load(in_file)
            # tokens are the list of words in the website loaded
            tokens = get_tokens_in_page(website["content"])
            website_id += 1  # get_hash(website['url'])
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
                store_index(index)
                index.clear()
                index = {}
                threshold_count = 0

    store_index(index)
    index.clear()
    index = {}

    with open("Index.txt", "r") as index:
        num_of_line = 0
        for line in index:
            num_of_line += 1
    print("number of unique tokens in Index: ", num_of_line)
    print("Index file size:", path.getsize("Index.txt"))
    print("number of documents: ", num_docs)


main()
