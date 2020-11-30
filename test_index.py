from sys import platform
curr_offset = 0
offset_list = []
with open("test_index.txt", "r") as index:
    for line in index:
        print("Current line length is", len(line))
        offset_list.append(curr_offset)
        curr_offset+=len(line)+1
        

with open("test_index.txt", "r") as index:
    
    if platform.startswith("darwin"):
        print('mac')
    else:
        print('windows')

    index.seek(14)
    line = index.readline()
    print(line)




