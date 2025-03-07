import json
import re
import pickle

stress_re = '.*[012]'
 
# Opening JSON file
with open('g2p.json') as json_file:
    data = json.load(json_file)

with open("cmudict.rep") as syll_file:
    syllable_dict_lines = syll_file.readlines()

syllable_dict = {}


for line in syllable_dict_lines:
    if(line[0]=='#'):
        continue
    split1 = line.replace('\n','').split('  ')
    sylls = []
    for syll in split1[1].split(' - '):
        sylls.append(len(syll.split(' ')))
    syllable_dict[split1[0]] = sylls


import csv

candidates = []

good_candidates = []

words_in_data = []
missing_words = []

limited_candidates = {}

non_zero_stress = ["AA0", "AO0", "AE0", "AW0", "EH0", "EY0", "OY0", "UH0", "0"]

with open('shaw.csv') as srccsv:
    srccsv_reader = csv.reader(srccsv, delimiter=',')
    candidates = {}

    one_but_not_other = []
    two_but_not_other = []
    next(srccsv_reader)
    for row in srccsv_reader:

        word1 = row[5].lower()
        word2 = row[7].lower()
        blend = row[0].lower()

        if word1 in data and word1.upper() in syllable_dict:

            

            input_word1 = data[word1]
            words_in_data.append((word1,data[word1]))

            
            input_word1["syll_count"] = len(syllable_dict[word1.upper()])
            j = 0
            segment_countdown = syllable_dict[word1.upper()][j]
            phonemes = input_word1["phonemes"]
            syll_position = ["-"] * len(phonemes)

            post_vocalic = False
            for i in range(len(phonemes)):
                if phonemes[i] == '_':
                    continue

                if any(vowel in phonemes[i] for vowel in ["0","1","2"] ):
                    syll_position[i] = "nucleus"
                    post_vocalic = True

                elif phonemes[i] != '_':
                    if post_vocalic:
                        syll_position[i] = "coda"
                    else:
                        syll_position[i] = "onset"
                
                segment_countdown = segment_countdown - 1
                if '|' in syll_position[i]:
                        segment_countdown = segment_countdown -1
                if segment_countdown <= 0:
                    j = j + 1
                    if j < len(syllable_dict[word1.upper()]):
                        segment_countdown = syllable_dict[word1.upper()][j] + segment_countdown
                    post_vocalic = False
                
            input_word1["syll_position"] = syll_position 

        else:
            missing_words.append(word1)
            input_word1 = None

        if word2 in data and word2.upper() in syllable_dict:

            if word2.upper() == 'UTILITARIAN':
                print('whats goin on here')

            input_word2 = data[word2]
            words_in_data.append((word2,data[word2]))
                    
            input_word2["syll_count"] = len(syllable_dict[word2.upper()])

            j = 0
            segment_countdown = syllable_dict[word2.upper()][j]
            phonemes = input_word2["phonemes"]
            syll_position = ["-"] * len(phonemes)

            post_vocalic = False
            for i in range(len(phonemes)):

                if phonemes[i] == '_':
                    continue

                if any(vowel in phonemes[i] for vowel in ["0","1","2"] ):
                    syll_position[i] = "nucleus"
                    post_vocalic = True

                elif phonemes[i] != '-':
                    if post_vocalic:
                        syll_position[i] = "coda"
                    else:
                        syll_position[i] = "onset"
                        
                segment_countdown = segment_countdown - 1
                if '|' in syll_position[i]:
                        segment_countdown = segment_countdown -1
                if segment_countdown <= 0:
                    j = j + 1
                    if j < len(syllable_dict[word2.upper()]):
                        segment_countdown = syllable_dict[word2.upper()][j] + segment_countdown
                    post_vocalic = False
                
            input_word2["syll_position"] = syll_position 

        else:
            missing_words.append(word2)
            input_word2 = None

        if input_word1 != None and input_word2 != None:
            candidates[blend] = []
            limited_candidates[blend] = []
            
            word1_substrings = []
            word2_substrings = []
            if blend == "brunch":
                print('brunch time!')
            word1_len = len(input_word1["phonemes"])
            word2_len = len(input_word2["phonemes"])
            if blend == 'stagflation':
                print("let's check this one out")



            ##feature system 

            #active developement zone

            w1_syll_indxs = [seg for seg in input_word1["phonemes"] if re.match(stress_re,seg)]
            w1_prim_stress_indx = [indx for indx, seg in enumerate(w1_syll_indxs) if '1' in seg][0]
            w1_right_stress = input_word1["syll_count"] - w1_prim_stress_indx
            w1_left_stress = w1_prim_stress_indx + 1
            w1_num_sylls = len(w1_syll_indxs)

            
            w2_syll_indxs = [seg for seg in input_word2["phonemes"] if re.match(stress_re,seg)]
            w2_prim_stress_indx = [indx for indx, seg in enumerate(w2_syll_indxs) if '1' in seg][0]
            w2_right_stress = input_word2["syll_count"] - w2_prim_stress_indx
            w2_left_stress = w2_prim_stress_indx + 1
            w2_num_sylls = len(w2_syll_indxs)


            for i in range(0,word1_len):
                if input_word1["phonemes"][i] == '_':
                    continue
                w1_bound_coda = int((input_word1["syll_position"][i] == "coda" and len(input_word1["syll_position"])==i+1) or (input_word1["syll_position"][i] == "coda" and input_word1["syll_position"][i+1]!="coda"))
                w1_bound_onset = int(input_word1["syll_position"][i] == "onset" and  input_word1["syll_position"][i+1]!="onset")
                w1_bound_nucleus = int(input_word1["syll_position"][i] == "nucleus")
                
                w1_sub = input_word1["phonemes"][0:i+1]
                w1_sub_syll_indxs = [seg for seg in w1_sub if re.match(stress_re,seg)]
                
                w1_prop_surv_syll = len(w1_sub_syll_indxs)/w1_num_sylls

                w1_prop_surv_seg = len(list(filter(('_').__ne__,w1_sub)))/len(list(filter(('_').__ne__,input_word1["phonemes"])))
                

                for j in range(0,word2_len):
                    if input_word2["phonemes"][word2_len-j-1] == '_':
                        continue
                    switch_at_w2_prim = int('1' in input_word2["phonemes"][word2_len-j-1])
                    w2_bound_coda = int(input_word2["syll_position"][word2_len-j-1] == "coda" and (len(input_word2["syll_position"])==word2_len-j or input_word2["syll_position"][word2_len-j]!="coda"))
                    w2_bound_onset = int(input_word2["syll_position"][word2_len-j-1] == "onset" and (word2_len-j-1==0 or  (word2_len >= j + 2 and input_word2["syll_position"][word2_len-j-2]!="onset")))
                    w2_bound_nucleus = int(input_word2["syll_position"][word2_len-j-1] == "nucleus")

                    w2_sub = input_word2["phonemes"][word2_len-j-1:word2_len]
                    w2_sub_syll_indxs = [seg for seg in w2_sub if re.match(stress_re,seg)]
                
                    w2_prop_surv = len(w2_sub_syll_indxs)/w2_num_sylls
                    w2_prop_surv_seg = len(list(filter(('_').__ne__,w2_sub)))/len(list(filter(('_').__ne__,input_word2["phonemes"]))) #delete me, and mirror in w1




                    blend_candidate_phon = w1_sub + w2_sub


                    blend_candidate_phon_no_ = list(filter(('_').__ne__,blend_candidate_phon))

                    w1_prim_stress_surv = 0
                    w1_seg_no_ = list(filter(('_').__ne__,input_word1["phonemes"]))
                    w1_surv_seg = 0
                    w1_surv_syll = 0
                    for k in range(len(w1_seg_no_)):
                        if len(blend_candidate_phon_no_) > k and blend_candidate_phon_no_[k] == w1_seg_no_[k]:
                            w1_surv_seg+=1
                            if re.match(stress_re,w1_seg_no_[k]):
                                w1_surv_syll+=1
                                if '1' in w1_seg_no_[k]:
                                    w1_prim_stress_surv = 1
                        else:
                            break
                    
                    w1_prop_surv_seg = w1_surv_seg/len(w1_seg_no_)
                    w1_prop_surv_syll = w1_surv_syll/w1_num_sylls

                    w2_prim_stress_surv = 0
                    w2_seg_no_ = list(filter(('_').__ne__,input_word2["phonemes"]))
                    w2_surv_seg = 0
                    w2_surv_syll = 0
                    for l in range(len(w2_seg_no_)):
                        if len(blend_candidate_phon_no_) > l and  blend_candidate_phon_no_[len(blend_candidate_phon_no_) - l-1] == w2_seg_no_[len(w2_seg_no_) - l-1]:
                            w2_surv_seg+=1
                            if re.match(stress_re,w2_seg_no_[len(w2_seg_no_) - l-1]):
                                w2_surv_syll+=1
                                if '1' in w2_seg_no_[len(w2_seg_no_) - l-1]:
                                    w2_prim_stress_surv = 1

                        else:
                            break
                    w2_prop_surv_seg = w2_surv_seg/len(w2_seg_no_)
                    w2_prop_surv_syll = w2_surv_syll/w2_num_sylls
                    overlap = int(w2_surv_seg + w1_surv_seg > len(blend_candidate_phon_no_))
                    if overlap:
                        syll_struct_w1_no_ = list(filter(('_').__ne__,input_word1["syll_position"]))
                        w1_bound_coda = int((syll_struct_w1_no_[k] == "coda" and (len(syll_struct_w1_no_)<=k+1 or  syll_struct_w1_no_[k+1]!="coda")))
                        w1_bound_onset = int(syll_struct_w1_no_[k] == "onset" and  syll_struct_w1_no_[k+1]!="onset")
                        w1_bound_nucleus = int(syll_struct_w1_no_[k] == "nucleus")

                        syll_struct_w2_no_ = list(filter(('_').__ne__,input_word2["syll_position"]))
                        l_indx = len(syll_struct_w2_no_)-l-1
                        w2_bound_coda = int(syll_struct_w2_no_[l_indx] == "coda" and (l_indx == 0 or syll_struct_w2_no_[l_indx-1]!="coda"))
                        w2_bound_onset = int(syll_struct_w2_no_[l_indx] == "onset" and (syll_struct_w2_no_[l_indx]==0 or (syll_struct_w2_no_[l_indx-1]!="onset")))
                        w2_bound_nucleus = int(input_word2["syll_position"][word2_len-j-1] == "nucleus")

                    blend_candidate_nuc = [seg for seg in blend_candidate_phon if re.match(stress_re,seg)]
                    blend_cand_num_sylls = len(blend_candidate_nuc)
                    blend_candidate_prim_stress_indx = [indx for indx, seg in enumerate(blend_candidate_nuc) if '1' in seg]
                    if blend_candidate_prim_stress_indx == []:
                        blend_candidate_prim_stress_indx = 0
                    else:
                        blend_candidate_prim_stress_indx = blend_candidate_prim_stress_indx[0]
                    blen_candidate_left_stress = blend_candidate_prim_stress_indx + 1
                    blen_candidate_right_stress = blend_cand_num_sylls - blend_candidate_prim_stress_indx

                    
                    output_graphemes = input_word1["graphemes"][0:i+1] + input_word2["graphemes"][word2_len-j-1:word2_len]
                    output_ortho = ''.join(output_graphemes).replace('|','')
                    correct_output = int(output_ortho == blend)

                    #do not consider candidates which result in a duplication of an input word 
                    # nor any that preserve all segments of both words (do not meet definition of blends )
                    if output_ortho == word1 or output_ortho == word2 or(w1_prop_surv_seg == 1.0 and w2_prop_surv_seg == 1.0 and overlap == 0):
                        continue

                    if ''.join(blend_candidate_phon_no_) in ''.join(w1_seg_no_) or ''.join(blend_candidate_phon_no_) in ''.join(w2_seg_no_):
                        print('here')


                    identical_phon = next((x for x in candidates[blend] if x["phonemes"] == blend_candidate_phon), None)
                    if identical_phon == None:
                        candidates[blend].append({
                            "blend": blend,
                            "phonemes": blend_candidate_phon, 
                            "graphemes": output_graphemes,
                            "orthography": output_ortho, 
                            "word1_len": w1_num_sylls, 
                            "word2_len": w2_num_sylls, 
                            "w1_prop_surv_syll": w1_prop_surv_syll,
                            "w1_prop_surv_seg" : w1_prop_surv_seg,
                            "w2_prop_surv_syll": w2_prop_surv_syll,
                            "w2_prop_surv_seg" : w2_prop_surv_seg,
                            "overlap": overlap,
                            "blend_cand_num_sylls": blend_cand_num_sylls,
                            "w1_left_stress": w1_left_stress,
                            "w2_left_stress": w2_left_stress,
                            "w1_right_stress": w1_right_stress,
                            "w2_right_stress": w2_right_stress,
                            "w1_switchpoint": w1_surv_syll,
                            "w2_switchpoint": w2_surv_syll,
                            "w1_bound_onset": w1_bound_onset,
                            "w1_bound_coda": w1_bound_coda,
                            "w1_bound_nucleus": w1_bound_nucleus,
                            "w2_bound_onset": w2_bound_onset,
                            "w2_bound_coda": w2_bound_coda,
                            "w2_bound_nucleus": w2_bound_nucleus,
                            "w1_prim_stress_surv": w1_prim_stress_surv,
                            "w2_prim_stress_surv": w2_prim_stress_surv,
                            "switch_at_w2_prim": switch_at_w2_prim,
                            "correct_output": correct_output
                            })
                    elif identical_phon["orthography"] != output_ortho and output_ortho == blend:
                        identical_phon["orthography"] = output_ortho
                        identical_phon["correct_output"] = 1
                    
                    



eval = []
blends_not_found = []
for blend in candidates.keys():
    found_match = 0
    for candidate in candidates[blend]:
        

        if blend ==candidate["orthography"]:
            found_match = 1
        
    if found_match == 0:
        blends_not_found.append((blend,candidates[blend]))


    eval.append(found_match)

for missed in blends_not_found:
    del candidates[missed[0]]

num_found = sum(eval)
num_total = len(eval)
print(num_found/num_total)
print("end")

def format_output(phonemes):
    phonemes = ' '.join(phonemes)
    phonemes = phonemes.replace("|"," ").replace(" _","").replace('AY0','AY2').replace('_ ','')+'\n'
    phonemes = re.sub(r'AA0|AO0|AE0|AW0|EH0|EY0|OY0|UH0','AH0',phonemes)
    

    return phonemes


with open('candidates_w_labels.p', 'wb') as pickle_file:
    pickle.dump(candidates, pickle_file)


with open('candidates_align.txt','w') as outtxt:
    for word in candidates.keys():
        outtxt.write('BLEND FORM'+word+'\n')
        for split in candidates[word]:
            outtxt.write(format_output(split["phonemes"]))


# with open('correct_candidates.txt','w') as outtxt:
#     for data in good_candidates:
#         outtxt.write(data["blend"]+'\t'+ str(data["word1_removed"]) + '\t'+ str(data["word2_removed"]) + '\t'+ str(data["word1_len"]) +'\t'+ str(data["word2_len"]) +'\n')
#         for split in candidates[word]:
#             outtxt.write(format_output(split["phonemes"]))

# with open('bad_candidates.txt','w') as outtxt:
#     for blend in candidates:
#         for data in candidates[blend]:
#             if data["blend"] not in good_candidates:
#                 outtxt.write(data["blend"] +'\t'+ str(data["word1_removed"]) + '\t'+ str(data["word2_removed"]) + '\t'+ str(data["word1_len"]) +'\t'+ str(data["word2_len"]) +'\n')
#                 for split in candidates[word]:
#                     outtxt.write(format_output(split["phonemes"]))


# with open('filtered_candidates.txt','w') as outtxt:
#     for word in candidates.keys():
#         outtxt.write('BLEND FORM'+word+'\n')
#         for split in limited_candidates[word]:
#             outtxt.write(format_output(split["phonemes"]))