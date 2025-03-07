import csv
from g2p_en  import G2p
import pickle

g2p = G2p()

with open('shaw.csv') as srccsv:
    srccsv_reader = csv.reader(srccsv, delimiter=',')
    candidates = {}

    next(srccsv_reader)
    for row in srccsv_reader:
        word1 = g2p(row[5])
        word2 = g2p(row[7])
        blend = g2p(row[0])

        for i in range(len(blend)):
            if '0' in blend[i] and blend[i] != 'AH0':
                blend[i] = 'AH0'
        
        blend = ' '.join(blend)

        candidates[blend] = []

        print("---------------------------")
        print("GOAL BLEND: ", blend)
        print("word 1: ", word1)
        print("word 2: ", word2)
        print("----candidates----")


        for i in range(0,len(word1)):
            for j in range(0,len(word2)):
                candidates[blend].append(word1[0:len(word1)-i]+word2[j:])
                print(word1[0:len(word1)-i]+word2[j:])


for word in candidates.keys():
    for candidate in candidates[word]:
        for i in range(len(candidate)):
            if '0' in candidate[i] and candidate[i] != 'AH0':
                candidate[i] = 'AH0'

with open('candidates.txt','w') as outtxt:
    for word in candidates.keys():
        outtxt.write('BLEND FORM'+word+'\n')
        for split in candidates[word]:
            outtxt.write(' '.join(split)+'\n')


eval = []
for blend in candidates.keys():
    match = 0
    for candidate in candidates[blend]:
        if ' '.join(candidate) == blend:
            match = 1

    eval.append(match)

# with open('chosen_candidates.txt','w') as outtxt:
#     for data in candidates:
#         for candidate in 
#         outtxt.write(data["blend"]+'\t'+ str(data["word1_removed"]) + '\t'+ str(data["word2_removed"]) + '\t'+ str(data["word1_len"]) +'\t'+ str(data["word2_len"]) +'\n')
#         for split in candidates[word]:
#             outtxt.write(format_output(split["phonemes"]))

print(sum(eval)/len(eval))



        
        # sentence = phonemizer(row[0] + ' ' + row[1] + ' ' + row[2], lang='en_us')
        # split_sent = sentence.split(' ')
        # blend = split_sent[0]
        # first_input = split_sent[1]
        # second_input = split_sent[2]

        # outdata.append(([blend, first_input, second_input]))