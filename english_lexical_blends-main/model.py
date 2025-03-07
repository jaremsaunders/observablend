#import sklearn
import numpy as np
import pandas as pd
import random

from sklearn.linear_model import LogisticRegression
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import f_classif
from sklearn.preprocessing import PolynomialFeatures
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

def calculate_accuracy(probs,test_words):
    correct = []
    for blend in test_words:

        bi = blend_indices[blend]
        blend_probs = probs[bi[0]:bi[1]]

        p_blend = list(p[1] for p in blend_probs)

        best_candidate = p_blend.index(max(p_blend))


        if(labels[best_candidate+bi[0]] == 1):
            correct.append(data[best_candidate+blend_indices[blend][0]].replace('\n','') + '\t' + str(max(p_blend)))
    return len(correct)/len(test_words)

def cross_validate_feature_set(feature_set):
    k_fold_accuracies = []
    #print('tsting prop_stress_no_syll_str')
    for k in range(k_value):
        train_folds = fold_word_indices.copy()
        train_folds.pop(k)
        train_folds = [index for indices in train_folds for index in indices]
        test_fold = folds[k]
        

        train_folds_set = feature_set.loc[train_folds]
        train_folds_labels = labels.loc[train_folds]

        basic_model = LogisticRegression(random_state=0,solver='liblinear',max_iter=1000).fit(train_folds_set, train_folds_labels)
        accuracy = calculate_accuracy(basic_model.predict_proba(feature_set),test_fold)
        #print('k = ',k, ', accuracy = ' ,accuracy)
        k_fold_accuracies.append(accuracy)
    print('Mean accuracy: ', sum(k_fold_accuracies)/len(k_fold_accuracies))
    return sum(k_fold_accuracies)/len(k_fold_accuracies)
train_data = []
labels = []
blend_indices = {}

with open('all_scored_candidates.txt') as file:
    data = file.readlines()

i = 0
current_blend = ''
for line in data:
    data_line = line.replace('\n','').split('\t')

    if(data_line[0] not in blend_indices.keys()):
        if current_blend != '':
            blend_indices[current_blend].append(i)
        current_blend = data_line[0]
        blend_indices[current_blend] = [i]

    i = i + 1

    labels.append(float(data_line[27]))
    features = [float(feat) for feat in data_line[4:27]]
    features.append(float(data_line[28]))
    train_data.append(np.array(features))
blend_indices[current_blend].append(i)
labels = np.array(labels)
train_data = np.array(train_data)


blend_list = list(blend_indices.keys())
random.shuffle(blend_list)
train_test_split = int(len(blend_list)*.8)
train_word_set = blend_list[0:train_test_split]
test_word_set = blend_list[train_test_split:]

k_value = 10
folds = []
fold_word_indices = []
last_fold_i = 0
for k in range(k_value-1):
    next_fold_i = int(len(blend_list)/k_value*(k+1))
    folds.append(blend_list[last_fold_i:next_fold_i])
    last_fold_i = next_fold_i
folds.append(blend_list[last_fold_i:])

for k in range(len(folds)):
    fold_word_indices.append([])
    for word in folds[k]:
        for i in range(blend_indices[word][0],blend_indices[word][1]):
            fold_word_indices[k].append(i)






train_indices = []
for pair in train_word_set:
    for i in range(blend_indices[pair][0],blend_indices[pair][1]):
        train_indices.append(i)

test_indices = []
for pair in test_word_set:
    for i in range(blend_indices[pair][0],blend_indices[pair][1]):
        test_indices.append(i)

labels = pd.Series(labels)

dataframe = pd.DataFrame(train_data,columns=["word1_len","word2_len","w1_prop_surv_syll",
                            "w1_prop_surv_seg",
                            "w2_prop_surv_syll",
                            "w2_prop_surv_seg",
                            "overlap",
                            "blend_cand_num_sylls",
                            "w1_left_stress",
                            "w2_left_stress",
                            "w1_right_stress",
                            "w2_right_stress",
                            "w1_switchpoint",
                            "w2_switchpoint",
                            "w1_bound_onset",
                            "w1_bound_coda",
                            "w1_bound_nucleus",
                            "w2_bound_onset",
                            "w2_bound_coda",
                            "w2_bound_nucleus",
                            "w1_prim_stress_surv",
                            "w2_prim_stress_surv",
                            "switch_at_w2_prim",
                            "blick"
                            ])
corr_matrix = dataframe.corr()
print(dataframe)
print(corr_matrix["w1_bound_onset"],corr_matrix["w1_prop_surv_syll"])

from scipy.stats import pearsonr

#placeholder code, obtained via stackoverflow, user toto_tico 
def calculate_pvalues(df):
    dfcols = pd.DataFrame(columns=df.columns)
    pvalues = dfcols.transpose().join(dfcols, how='outer')
    for r in df.columns:
        for c in df.columns:
            tmp = df[df[r].notnull() & df[c].notnull()]
            pvalues[r][c] = round(pearsonr(tmp[r], tmp[c])[1], 4)
    return pvalues


num_stress_feats = dataframe[["overlap","blend_cand_num_sylls",
                            "w1_left_stress",
                            "w2_left_stress",
                            "w1_right_stress",
                            "w2_right_stress",
                            "w1_switchpoint",
                            "w2_switchpoint",
                            "w1_bound_onset",
                            "w1_bound_coda",
                            "w1_bound_nucleus",
                            "w2_bound_onset",
                            "w2_bound_coda",
                            "w2_bound_nucleus",
                            "w1_prim_stress_surv",
                            "w2_prim_stress_surv",
                            "switch_at_w2_prim",
                            "blick"
                            ]]

num_stress_feats_no_coda = dataframe[["overlap",
                            "w1_left_stress",
                            "w2_left_stress",
                            "w1_right_stress",
                            "w2_right_stress",
                            "w1_switchpoint",
                            "w2_switchpoint",
                            "w1_bound_onset",
                            "w1_bound_coda",
                            "w1_bound_nucleus",
                            "w2_bound_onset",
                            "w2_bound_nucleus",
                            "w1_prim_stress_surv",
                            "w2_prim_stress_surv",
                            "switch_at_w2_prim",
                            "blick"
                            ]]
print(num_stress_feats.corr())

prop_stress_bound_feats_trimmed = dataframe[["w1_prop_surv_syll","w2_prop_surv_syll","overlap",
                                     "blend_cand_num_sylls","w1_left_stress","w2_left_stress", "w1_right_stress","w2_right_stress",
                                    "w1_bound_onset","w1_bound_coda","w1_bound_nucleus","w2_bound_onset", "w2_bound_coda","w2_bound_nucleus","switch_at_w2_prim","blick"]] #removed swithcpoint/prim_stress_surv

prop_stress_no_syll_str = dataframe[["w1_prop_surv_syll","w2_prop_surv_syll","overlap",
                                     "w1_left_stress","w2_left_stress", "w1_right_stress","w2_right_stress","blick"]]

corr_prop_stress_bound_feats = prop_stress_bound_feats_trimmed.corr()
p_vals = calculate_pvalues(prop_stress_bound_feats_trimmed)

print(corr_prop_stress_bound_feats)
print(p_vals)

print(corr_prop_stress_bound_feats)




for i in range(1,25):
    scaler = StandardScaler()
    scaler.fit(dataframe)
    scaled_df = scaler.transform(dataframe)

    pca_i = PCA(n_components=i,random_state=0)
    pca_i.fit(scaled_df)
    df_pca_i = pca_i.transform(scaled_df)
    print('performing PCR with ', i, ' principal components:')
    cross_validate_feature_set(pd.DataFrame(df_pca_i))


selector = SelectKBest(f_classif, k=15)
auto_select_f = pd.DataFrame(selector.fit_transform(dataframe, labels))
auto_feats = dataframe.columns[selector.get_support()]
data_best = dataframe[auto_feats]

corr_data_best = data_best.corr()
p_vals = calculate_pvalues(prop_stress_bound_feats_trimmed)

print(corr_data_best)
print(p_vals)


print("testing PCR")
cross_validate_feature_set(pd.DataFrame(df_pca_95))


print("testing num_stress_feats")
cross_validate_feature_set(num_stress_feats)
print("testing num_stress_feats_no_coda")
cross_validate_feature_set(num_stress_feats_no_coda)


print("testing full dataset")
cross_validate_feature_set(dataframe)
print("testing subset features dataset")
cross_validate_feature_set(prop_stress_bound_feats_trimmed)
print("testing strict subset features dataset")
cross_validate_feature_set(prop_stress_no_syll_str)
print("testing automatic 15 best")
cross_validate_feature_set(auto_select_f)



# for k in range(1,25):

#     auto_select_f = SelectKBest(f_classif, k=k).fit_transform(dataframe, labels)
#     auto_f_model = LogisticRegression(random_state=0,solver='liblinear').fit(auto_select_f, labels)
#     print("With k = ", k ," best features, accuracy = ", calculate_accuracy(auto_f_model.predict_proba(auto_select_f)))
test_set = dataframe.loc[test_indices]
print(test_set)
training_set = dataframe.loc[train_indices]

train_labels = labels.loc[train_indices]
test_labels = labels.loc[test_indices]
print(test_labels)

k_fold_accuracies = []
poly = PolynomialFeatures(3)

poly_dataframe = poly.fit_transform(prop_stress_bound_feats_trimmed)

for k in range(k_value):
    train_folds = fold_word_indices.copy()
    train_folds.pop(k)
    train_folds = [index for indices in train_folds for index in indices]
    test_fold = folds[k]
    

    train_folds_set = prop_stress_bound_feats_trimmed.loc[train_folds]
    train_folds_labels = labels.loc[train_folds]

    poly_train = poly.fit_transform(train_folds_set)
    basic_model = LogisticRegression(random_state=0,solver='liblinear',max_iter=1000).fit(poly_train, train_folds_labels)
    accuracy = calculate_accuracy(basic_model.predict_proba(poly_dataframe),test_fold)
    print('k = ',k, ', accuracy = ' ,accuracy)
    k_fold_accuracies.append(accuracy)
print('Mean accuracy: ', sum(k_fold_accuracies)/len(k_fold_accuracies))




auto_select_f = SelectKBest(f_classif, k=15).fit_transform(dataframe, labels)
basic_model = LogisticRegression(random_state=0,solver='liblinear',max_iter=1000).fit(training_set, train_labels)
print(calculate_accuracy(basic_model.predict_proba(dataframe),test_word_set))
poly = PolynomialFeatures(3)
poly_auto = poly.fit_transform(training_set)

# auto_f_model = LogisticRegression(random_state=0,solver='liblinear',max_iter=5000).fit(poly_auto, labels)
# print(calculate_accuracy(auto_f_model.predict_proba(poly_auto)))

prop_model = LogisticRegression(random_state=0,solver='liblinear',max_iter=5000).fit(prop_stress_bound_feats, labels)
prop_trim_model = LogisticRegression(random_state=0,solver='liblinear').fit(prop_stress_bound_feats_trimmed, labels)

print(calculate_accuracy(prop_model.predict_proba(prop_stress_bound_feats)))
print(calculate_accuracy(prop_trim_model.predict_proba(prop_stress_bound_feats_trimmed)))



clf = LogisticRegression(random_state=0,solver='liblinear').fit(dataframe, labels)
probs = clf.predict_proba(train_data)
predicts = clf.predict(train_data)
print(clf.coef_,clf.intercept_)


correct = []
false_pos = []





for blend in blend_indices:

    bi = blend_indices[blend]
    blend_probs = probs[blend_indices[blend][0]:blend_indices[blend][1]]

    p_blend = list(p[1] for p in blend_probs)

    best_candidate = p_blend.index(max(p_blend))


    if(labels[best_candidate+blend_indices[blend][0]] == 1):
        correct.append(data[best_candidate+blend_indices[blend][0]].replace('\n','') + '\t' + str(max(p_blend)))
    else:
        false_pos.append(data[best_candidate+blend_indices[blend][0]].replace('\n','') + '\t' + str(max(p_blend)))

with open('final_correct_predictions.txt','w') as good_outfile:
    good_outfile.write('\n'.join(correct))

with open('final_incorrect_predictions.txt','w') as wrong_outfile:
    wrong_outfile.write('\n'.join(false_pos))


print(len(correct)/len(blend_indices))
print(p_blend)

# for blend in blend_indices:
#     probs




