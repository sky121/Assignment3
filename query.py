

import sys
import math
seek_index = dict()


def create_seek_index():
    global seek_index
    curr_offset = 0
    with open("Index.txt", "r") as index:
        for line in index:
            token = line.split(',')[0].split(':')[0]
            seek_index[token] = curr_offset
            curr_offset += (len(line)+1)

def merge_lists(list1, list2):
    '''
    line_list = [[]1, []2, []3, ... []99999]
    merged = []
    done = False
    while not done:
        merge 1 and 2 with common docs
        if merged empty:
            return None
        else merge merged and 3
    keep going until either merged is empty or we run out of docs in linelist
    '''
    return_list = []
    for docs1 in list1:
        for docs2 in list2:
            if(docs1.split(':')[0] == docs2.split(':')[0]):
                return_list.append(docs1)
                return_list.sort(key=lambda x: x.split(':')[1], reverse=True)
    return return_list
    
        
             
             
def search(query):
    top_url_list = []
    tokens = query.split(' ')
    line_list = []
    with open("Index.txt", "r") as index:
        for token in tokens:
            offset = seek_index[token]
            index.seek(offset)
            line = index.readline().split(",")
            line_list.append(line)
    line_list.sort(key=lambda x: x[0].split(':')[1])
    if(len(line_list) == 1):
        return line_list[0][1:]

    indx = 2
    current_line = merge_lists(line_list[0][1:], line_list[1][1:])
    while indx<len(tokens):
        current_line = merge_lists(current_line, line_list[indx][1:])
        indx +=1
    top_url_list = current_line[:5]
    return top_url_list


def main():
    create_seek_index()  
    user_query = input("enter query: ")
    while(user_query != "quit()"):
        top_url_list = search(user_query)
        print(top_url_list)
        user_query = input("enter query: ")

main()