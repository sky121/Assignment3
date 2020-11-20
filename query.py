
#RANDOM COMMENT dadsfdsakf;
import sys
import math
import json
seek_index = dict()
docid_to_url = dict()

def create_seek_index():
    global seek_index
    curr_offset = 0
    with open("Index.txt", "r") as index:
        for line in index:
            token = line.split(',')[0].split(':')[0]
            seek_index[token] = curr_offset
            curr_offset += (len(line))
         

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
    list1_dict = dict()
    for docs1 in list1:
        list1_dict[docs1.split(':')[0]] = docs1.split(':')[1]
    for docs2 in list2:
        if(docs2.split(':')[0] in list1_dict):
            new_str = docs2.split(':')[0] + str(int(list1_dict[docs2.split(':')[0]]) + int(docs2.split(':')[1]))
            return_list.append(docs2)
    return return_list
    
        
             
             
def search(query):
    top_url_list = []
    tokens = query.split(' ')
    line_list = []
    with open("Index.txt", "r") as index:
        for token in tokens:
            if token.lower() not in seek_index:
                return []
            offset = seek_index[token.lower()]
            index.seek(offset)
            line = index.readline().rstrip().split(",")
            line_list.append(line)
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


def main():
    global docid_to_url
    create_seek_index()  
    with open("docidToUrl.json", 'r') as docidToUrl:
        docid_to_url = json.load(docidToUrl)
    user_query = input("enter query: ")
    while(user_query != "quit()"):
        top_url_list = search(user_query)
        #print(top_url_list)
        i = 0
        show_more=True
        while show_more:
            if(i>=len(top_url_list)):
                break
            docid = top_url_list[i]
            print(docid_to_url[docid.split(':')[0]])
            i+=1
            if(i%10==0):
                show = input("Show More? (yes/no)")
                if(show=='no'):
                    show_more=False
            

        user_query = input("enter query: ")

main() 