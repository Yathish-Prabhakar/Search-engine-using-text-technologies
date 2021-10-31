# Search-engine-using-text-technologies

A simple search engine which takes queries as inputs and returns documents from a collection which match the given query.  
The queries can be simple words, phrases, booleans or contain proximity.  
The results are ranked based on TFIDF and the top 150 documents are retrieved for each query.  
Pre-processing of text is included which implements stopping, stemming(Porter stemming), tokenization and case folding.  
A sample collection of doucments along with the results are attached.  
  
trec.5000.xml - Sample collection of 5000 documents  
index.txt - Positional inverted index for the given collection  
queries.boolean.txt - Sample boolean queries  
results.boolean.txt - Results for boolean queries  
queries.ranked.txt - Sample queries for ranked retrieval  
results.ranked.txt - Results for ranked queries
