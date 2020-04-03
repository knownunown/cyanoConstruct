import random


##=============================================================================##

def get_data_list(fname): ##opens, parses through excel sheet
    contents = []
    try:
        with open(fname, "r") as fname:
            for line in fname.readlines():
                line = line.split(",")
                contents.append(line)
            return contents
    except FileNotFoundError:
        return -1


#only need to load it once
assemblycode = get_data_list("assemblycode.csv")

## Go through optimal list first 
##=============================================================================##

def findseq(term): #returns sequence associated with elm. name
    GOIstart = assemblycode.index(['GOI', 'GOIseq\n'])
    GOIend = assemblycode.index(['Term', 'Termseq\n'])
    seq = ""
    for i in range(len(assemblycode)):
        if assemblycode[i][0] == term:
            
            if i >= GOIstart and i <= GOIend: ##if term is a gene of interest, TG appended to start
                seq += "TG"
            seq += assemblycode[i][1]
            return seq
    raise Exception("Entry not in data.")
    #return "(Entry not in Data)"

##=============================================================================##

def choice_spacer(ls, spacerchoice): ##creates randomly ordered spacer list, variety of fidelity
    options = ["A", "G", "C", "T"]
    firstspacers = []
    endspacers = []
    if spacerchoice == '98.5%':
        spacers = ['TGCC', 'GCAA', 'ACTA', 'TTAC', 'CAGA', 'TGTG', 'GAGC', 'AGGA', 'ATTC', 'CGAA', 'ATAG', "AAGG", "AAAA", "ACCG"]
    elif spacerchoice == '98.1%':
        spacers = ['AGTG', 'CAGG', 'ACTC', 'AAAA', 'AGAC', 'CGAA', 'ATAG', 'AACC', 'TACA', 'TAGA', 'ATGC', 'GATA', 'CTCC', 'GTAA', 'CTGA', 'ACAA','AGGA', 'ATTA', 'ACCG', 'GCGA']
    elif spacerchoice == '95.8%':
        spacers = ['CCTC', 'CTAA', 'GACA', 'GCAC', 'AATC', 'GTAA', 'TGAA','ATTA', 'CCAG', 'AGGA', 'ACAA', 'TAGA', 'CGGA', 'CATA', 'CAGC', 'AACG', 'CTCC', 'ACCA', 'AGTG', 'GGTA', 'GCGA', 'AAAA', 'ATGA']
    elif spacerchoice == '91.7%':
        spacers = ['TACA', 'CTAA', 'GGAA', 'GCCA', 'CACG', 'ACTC', 'CTTC', 'TCAA', 'GATA', 'ACTG', 'AAGC', 'CATA', 'GACC', 'AGGA', 'ATCG', 'AGAG', 'ATTA', 'CGGA', 'TAGA', 'AGCA', 'TGAA', 'CCAG', 'GTGA', 'ACGA', 'ATAC', 'AAAA', 'AAGG', 'CAAC']
    elif spacerchoice == "random":
        spacers = makespacers(ls)
    for i in range(len(spacers)):
        firstspacers.append(random.choice(options) + random.choice(options) + spacers[i])
        endspacers.append(spacers[i]+random.choice(options) + random.choice(options[:3]))
    random.shuffle(firstspacers, random.random)
    random.shuffle(endspacers, random.random)
    while len(firstspacers) < len(ls)-1:
        firstspacers.append(str(random.choice(options)+random.choice(options)+random.choice(options)
              +random.choice(options)+random.choice(options)+random.choice(options[:3])))
        endspacers.append(str(random.choice(options)+random.choice(options)+random.choice(options)
              +random.choice(options)+random.choice(options)+random.choice(options[:3])))
    return (firstspacers, endspacers)


##=============================================================================##

def makespacers(ls):  ##creates a 6-nucleotide random seq for each spacer, no repeats
    spacers = []
    options = ["A", "G", "C", "T"]
    for i in range(len(ls)): 
        new = str(random.choice(options)+random.choice(options)+random.choice(options)
              +random.choice(options)+random.choice(options)+random.choice(options[:3]))
        while new in spacers:
            new = str(random.choice(options)+random.choice(options)+random.choice(options)+
              random.choice(options)+random.choice(options)+random.choice(options[:3]))
        spacers.append(new)
    return spacers

##=============================================================================##
    
def findTM(seq, TMgoal):
    try:
        TM = 0
        numA = 0
        numT = 0
        numG = 0
        numC = 0
        i = 0
        seq = list(seq)
        while TM - TMgoal > 1 or TM -TMgoal < -1:
            if seq[i] == "A":
                numA +=1
            elif seq[i] == "T":
                numT +=1
            elif seq[i] == "G":
                numG +=1
            elif seq[i] == "C":
                numC +=1
            TM = 64.9 + 41*(numG+numC-16.4)/(numA+numT+numG+numC)
            i += 1
        seq = ''.join(seq)
        gccontent1 = (numG +numC)/(len(seq[0:i]))
        gccontent1 = round(gccontent1, 4) * 100
        gccontent1 = str(gccontent1)+" %"
        j, TM2, gccontent2 = findsecondTM(seq, TMgoal)
        if i +j > len(seq):
            return("TM not possible", "No sequence possible","No GC %", "TM not possible", "No sequence possible", "No GC%")
        return(round(TM, 4), seq[0:i], gccontent1, round(TM2,4), seq[j:], gccontent2)
    except IndexError:
        seq = ''.join(seq)
        return("TM not possible", "No sequence possible", "", "", "", "")

def findsecondTM(seq, TMgoal):
    TM2 = 0
    numA = 0
    numT = 0
    numG = 0
    numC = 0
    i = -2 ## compensates for the "\n" at the end of elm.
    seq = list(seq)
    while TM2 - TMgoal > 1 or TM2 -TMgoal < -1:
        if seq[i] == "A":
            numA +=1
        elif seq[i] == "T":
            numT +=1
        elif seq[i] == "G":
            numG +=1
        elif seq[i] == "C":
            numC +=1
        TM2 = 64.9 + 41*(numG+numC-16.4)/(numA+numT+numG+numC)
        i -= 1
    gccontent2 = (numG +numC)/(len(seq[i:]))
    gccontent2 = round(gccontent2, 4) * 100
    gccontent2 = str(gccontent2)+" %"
    seq = ''.join(seq)
    return(i, TM2, gccontent2)
    
##=============================================================================##    

def printToWeb(outputString, string):
    outputString[0] = outputString[0] + "\n" + string

def createseq(elements, names, fidelity, tmgoal):
    outputString = [""]
    
    start = "GAAGAC"
    end = "GTCTTC"
    comp_seq = ''
    
    fileContents = {}
    
    for i in range(len(elements)): #gets specific inputs for each element
        elements[i] = findseq(names[i]) #converts inputs to sequence in datasheet
        
    #printToWeb(outputString, str(elements))
        
    firstspacers, endspacers =  choice_spacer(elements, fidelity)

    printToWeb(outputString, "\n Sequence with spaces between spacers and elements: ") ##Prints with spaces, each element on own line
    printToWeb(outputString, "\n"+"("+"TTTGCC  "+ " " + elements[0] + " " + endspacers[0] + end + ")")
    comp_seq += 'TTTGCC' + elements[0].strip('\n') + endspacers[0] + end
    
    #need to print out the promoter sequence here
    #with open(("%s.fasta") % names[0], 'w') as outputfile:
    #    print("TTTGCC"+elements[0].strip('\n')+endspacers[0]+end, file=outputfile)
    
    fileContents[("%s.fasta") % names[0]]= ("TTTGCC"+elements[0].strip('\n')+endspacers[0]+end)
    
    if len(elements) > 1:
        for i in range(len(elements)-2):
            printToWeb(outputString, "("+start+firstspacers[i] + " " + elements[i+1] + " " +  endspacers[i+1]+end+")")
            #with open(("%s.fasta") % names[i+1], 'w') as outputfile:
            #    print(start+firstspacers[i]+elements[i+1].strip('\n')+endspacers[i+1]+end, file=outputfile)
            
            fileContents[("%s.fasta") % names[i+1]] = (start+firstspacers[i]+elements[i+1].strip('\n')+endspacers[i+1]+end)
            
            comp_seq += start + firstspacers[i].strip('\n') + elements[i+1].strip('\n') + endspacers[i+1].strip('\n') + end
        printToWeb(outputString, "("+start+firstspacers[-1] + " " + elements[-1] + " " + "  GCAAGG"+")")
        #with open(("%s.fasta") % names[-1], 'w') as outputfile:
        #    print(start+firstspacers[-1]+elements[-1].strip('\n')+"GCAAGG", file=outputfile)
        
        fileContents[("%s.fasta") % names[-1]] = (start+firstspacers[-1]+elements[-1].strip('\n')+"GCAAGG")
        
        comp_seq += start + firstspacers[-1].strip('\n') + elements[-1].strip('\n') + 'GCAAGG'
        
    printToWeb(outputString, "\n Sequence without spaces between spacers and elements: ")##Prints without spaces, each element on own line
    printToWeb(outputString, "\n"+"TTTGCC"+ elements[0] + endspacers[0] + end)
    if len(elements) > 1:
        for i in range(len(elements)-2):
            printToWeb(outputString, start + firstspacers[i]+ elements[i+1] + endspacers[i+1] + end)
        printToWeb(outputString, start + firstspacers[-1] + elements[-1] + "GCAAGG")

    tmgoal = float(tmgoal) #tm value
    #prints with spaces and breaks at tm value
    firstTM, firstseq, gccontent1, lastTM, lastseq, gccontent2 = findTM(elements[0], tmgoal)
    printToWeb(outputString, "\n Sequence with elements split at the goal TM, spaces between elements and spacers: ")##Prints with spaces, each element on own line, each element split at TM melting spots
    printToWeb(outputString, "\n"+"Left primer for "+names[0])
    printToWeb(outputString, "Left spacer: "+"TTTGCC "+"\n"+"TM: "+str(firstTM)+
          "\nPrimer sequence: "+firstseq+"\nPrimer length: "+str(len(firstseq))+"\nGC Content: "+str(gccontent1)+
          "\n\nRight primer for "+names[0] +"\nRight spacer: "+endspacers[0]+end+"\nTM: "+
          str(lastTM)+"\nPrimer sequence: "+lastseq[:-1]+"\nPrimer length: "+str(len(lastseq)-1)+
          "\nGC Content: "+str(gccontent2)+"\n")   
    #with open('%s Left Primer.fasta' % names[0], 'w') as outputfile:
    #    print("TTTGCC"+firstseq, file=outputfile)
    #with open('%s Right Primer.fasta' % names[0], 'w') as outputfile:
    #    print(lastseq[:-1]+endspacers[0]+end, file=outputfile)
        
    fileContents['%s Left Primer.fasta' % names[0]] = ("TTTGCC"+firstseq)
    fileContents['%s Right Primer.fasta' % names[0]] = (lastseq[:-1]+endspacers[0]+end)
    
    if len(elements) > 1:
        for i in range(1, len(elements)-1):
            firstTM, firstseq,gccontent1, lastTM, lastseq, gccontent2 = findTM(elements[i], tmgoal)
            printToWeb(outputString, "\n"+"Left primer for "+names[i])
            printToWeb(outputString, "Left spacer: "+start+firstspacers[i]+"\n"+"TM: "+str(firstTM)+
                  "\nPrimer sequence: "+firstseq+"\nPrimer length: "+str(len(firstseq))+"\nGC Content: "+str(gccontent1)+
                  "\n\nRight primer for "+names[i] +"\nTM: "+str(lastTM)+
                  "\nPrimer sequence: "+lastseq[:-1]+"\nPrimer length: "+str(len(lastseq)-1)+"\n"+"Right spacer: "+endspacers[i]+end+"\nGC Content: "+str(gccontent2))
            #with open('%s Left Primer.fasta' % names[i], 'w') as outputfile:
            #    print(start+firstspacers[i]+firstseq, file=outputfile)
            #with open('%s Right Primer.fasta' % names[i], 'w') as outputfile:
            #    print(lastseq[:-1]+endspacers[i]+end, file=outputfile)
            
            fileContents['%s Left Primer.fasta' % names[i]] = (start+firstspacers[i]+firstseq)
            fileContents['%s Right Primer.fasta' % names[i]] = (lastseq[:-1]+endspacers[i]+end)
                
        firstTM,firstseq, gccontent1,lastTM, lastseq, gccontent2 = findTM(elements[-1], tmgoal)
        printToWeb(outputString, "\n"+"Left primer for "+names[-1])
        printToWeb(outputString, "Left spacer: "+start+firstspacers[-1]+"\n"+"TM: "+str(firstTM)+
              "\nPrimer sequence: "+firstseq+"\nPrimer length: "+str(len(firstseq))+"\nGC Content: "+str(gccontent1)+
              "\n\nRight primer for "+names[-1] +"\nTM: "+str(lastTM)+
              "\nPrimer sequence: "+lastseq[:-1]+"\nPrimer length: "+str(len(lastseq)-1)+"\n"+"Right spacer: "+"GCAAGG"+"\nGC Content: "+str(gccontent2)) 
        #with open('%s Left Primer.fasta' % names[-1], 'w') as outputfile:
        #    print(start+firstspacers[-1]+firstseq, file=outputfile)
        #with open('%s Right Primer.fasta' % names[-1], 'w') as outputfile:
        #    print(lastseq[:-1]+"GCAAGG", file=outputfile)
        
        fileContents['%s Left Primer.fasta' % names[-1]] = (start+firstspacers[-1]+firstseq)
        fileContents['%s Right Primer.fasta' % names[-1]] = (lastseq[:-1]+"GCAAGG")
    
    #with open('Complete Sequence.fasta', 'w') as outputfile:
    #    print(comp_seq, file=outputfile)
    
    fileContents["Complete Sequence.fasta"] = comp_seq
    
    return(outputString[0], fileContents)

##==================================================
## add GC%
## add primer len
## label primer pieces
## add deltaG
##
##====================================================================================
