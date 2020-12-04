# Assignment3

## ABOUT
Indexer.py and Query.py are the two components of our search engine where Indexer.py creates the inverted index from all the webpage documents and the Query.py is the user interface that retrieves the top webpage urls that match the query.

## DEPENDANCIES
    pip install beautifulsoup4
      instructions located here: https://www.crummy.com/software/BeautifulSoup/bs4/doc/

    DEV: folder containing all json files with webpages to scrape
    
## QUICK START
    run the indexer first: Python3 Indexer.py 

### Indexer.py
    To run the indexer, type the command: Python3 Indexer.py
    The Indexer.py will create 4 documents in the disk: index.txt, docidToUrl.json, cache.txt, and doc_vector_length.txt
    
    REQUIRES: DEV folder containing all json files with webpages to scrape

    index.txt is the inverted index corpus that we built. The format of the index.txt is as follow:
            Token:NumOfDoc,Document ID: term frequency 
    docidToUrl.json is a json file that associates each DocId to Url
    cache.txt is a temprry text file that contains nothing(you may delete it)
    doc_vector_length.txt is a text file that associated each docId with the sum of square of the term frequencies used in query.py
  
  
### query.py
  To start the search engine run: Python3 query.py
  
  The console will then display "enter query: "
  Input your query and press Enter

  The top 10 URLs will be displayed (if they exist) and the user will be asked if they would like to see more, shown by
        the "Show More? (yes/no)" line in console. Type "yes" if you would like to see more or "no" to enter a new query.

  NOTE: Did not implement quitting because keyword: QUIT may be a token you want to search.
        Instead you must use control C to quit or close the shell like how you would close your browser search engine.




