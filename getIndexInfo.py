import pickle
with open('index', 'rb') as database:
  index = pickle.load(database)
  print(index['num_tokens'])