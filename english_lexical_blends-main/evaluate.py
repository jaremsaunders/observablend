import pickle
import re
best_candidates = {}

with open('candidates_w_labels.p', 'rb') as pickle_file:
    candidates = pickle.load(pickle_file)

with open("BLICKOutputForCandidates_align.txt") as scores_file:
    
    next(scores_file)

    scores = scores_file.readlines()

    
    current_blend = ''
    for score_line in scores:
        if 'BLEND FORM' in score_line:
            if current_blend in best_candidates:
                best_candidates[current_blend] = [*set(best_candidates[current_blend])] 

            blend = score_line.split('\t')[0].replace('BLEND FORM','')

            best_candidates[blend] = []

            current_blend = blend
            i = 0
        else:
            candidate = score_line.split('\t')[0]

            if candidate == "_":
                score = float(999999999)
            else:
                score = float(score_line.split('\t')[2])

                cand_blend = candidates[blend]

                candidates[blend][i]["score"] = score

    
            if len(best_candidates[current_blend]) == 0 or best_candidates[current_blend][0][1] > score:
                best_candidates[current_blend] = [(i, score, candidate)]
            elif best_candidates[current_blend][0][1] == score:
                best_candidates[current_blend].append((i, score, candidate))

            i = i + 1

eval = []

selected_candidates = []

for blend in best_candidates.keys():
    correct = 0
    if blend in best_candidates: #take this line out later
        for scored_candidate in best_candidates[blend]:
            attempted_blend = ''.join(candidates[blend][scored_candidate[0]]["graphemes"]).replace('|','').replace('_','')
        #print(attempted_blend)
        if blend in best_candidates:
            if attempted_blend == blend:
                correct = 1
                #print('RIGHT',attempted_blend)
            else:
                #print('WRONG goal:',blend, "but got:",attempted_blend)
                selected_candidates.append(candidate)
    eval.append(correct)


def format_output(phonemes):
    phonemes = ' '.join(phonemes)
    phonemes = phonemes.replace("|"," ").replace(" _","").replace('AY0','AY2').replace('_ ','')+'\n'
    phonemes = re.sub(r'AA0|AO0|AE0|AW0|EH0|EY0|OY0|UH0','AH0',phonemes)
    

    return phonemes


with open('all_scored_candidates.txt','w') as outtxt:
    for blend in candidates.keys():
        for data in candidates[blend]:

            #print('\t'.join(str(feat) for feat in list(data.values())))

            outtxt.write('\t'.join(str(feat) for feat in list(data.values()))+'\n')





accuracy = sum(eval)/len(eval)

print(accuracy)
