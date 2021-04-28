# PPF-DFS

## Command to run GPF-growth algorithm
    Python gpfgrowth inputFileName outputFileName minSup maxPer minPR
    
    minSup and maxPer are to be specified in counts
    minPR needs to be specified in the range 0 to 1.
    
    E.g., Python gpfgrowth T10I4D100k.csv patterns.txt 199 6 0.6
