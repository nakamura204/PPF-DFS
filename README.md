# PPF-DFS

## Command to run GPF-growth algorithm
    python GPFgrowth.py inputFileName outputFileName minSup maxPer minPR
    
    minSup and maxPer are to be specified in counts
    minPR needs to be specified in the range 0 to 1.
    
    E.g., python GPFgrowth.py T10I4D100k.csv patterns.txt 5 5000 0.6
    
    
## Command to run PPF-DFS algorithm
    python PPF_DFS.py inputFileName outputFileName minSup maxPer minPR
    
    minSup and maxPer are to be specified in counts.
    minPR needs to be specified in the range 0 to 1.
    
    E.g., python PPF_DFS.py temporal_T10I4D100K.csv patterns.txt 5 5000 0.6
