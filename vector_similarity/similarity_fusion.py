'''
Try to fuse the similarity of CR_score and TF-IDF_score and then calculate the recall, MRR and manual efforts
'''
import os
import pandas as pd
from tqdm import tqdm

DATA_DIR = '/mnt/local/Baselines_Bugs/PatchSleuth/TF-IDF'
SAVE_DIR = '/mnt/local/Baselines_Bugs/CR_score/evaluate/fusion'
# SAVE_DIR = '/mnt/local/Baselines_Bugs/CR_score/evaluate/fusion_unnormalized'
# SAVE_DIR = '/mnt/local/Baselines_Bugs/CR_score/evaluate/fusion_weighted/0.4_0.6' ## 0.4 for CR_score, 0.6 for TF-IDF_score
# SAVE_DIR = '/mnt/local/Baselines_Bugs/CR_score/evaluate/fusion_weighted/0.6_0.4' ## 0.6 for CR_score, 0.4 for TF-IDF_score
# SAVE_DIR = '/mnt/local/Baselines_Bugs/CR_score/evaluate/fusion_weighted/0.3_0.7' ## 0.3 for CR_score, 0.7 for TF-IDF_score
# SAVE_DIR = '/mnt/local/Baselines_Bugs/CR_score/evaluate/fusion_weighted/0.45_0.55' ## 0.45 for CR_score, 0.55 for TF-IDF_score

os.makedirs(SAVE_DIR, exist_ok=True)


    
### calculate the Top@K recall by using the rank info
def recall(metric, k_list=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 50, 100], save_path=os.path.join(SAVE_DIR, 'recall_TFIDF.csv')):
    recall_info = pd.DataFrame(columns=['Top@k', 'recall'])
    recall_info.to_csv(save_path, index=False)

    for k in k_list:
        rank_info = pd.read_csv(os.path.join(SAVE_DIR, f'rankinfo_{metric}.csv'))
        rank_info['recall'] = rank_info['rank'].apply(lambda x: 1 if x <= k else 0)
        recall = rank_info['recall'].sum() / len(rank_info)
        print('Top@{} recall: {}'.format(k, recall))
        recall_info_iter = pd.DataFrame([[k, recall]], columns=['Top@k', 'recall'])
        recall_info_iter.to_csv(save_path, mode='a', header=False, index=False)
        print('Top@{} recall info saved'.format(k))

### calculate the MRR
def mrr(metric, save_path=os.path.join(SAVE_DIR, 'MRR_TFIDF.csv')):
    rank_info = pd.read_csv(os.path.join(SAVE_DIR, f'rankinfo_{metric}.csv'))
    rank_info['reciprocal_rank'] = rank_info['rank'].apply(lambda x: 1 / x)
    mrr = rank_info['reciprocal_rank'].sum() / len(rank_info)
    print('MRR: {}'.format(mrr))
    mrr_info = pd.DataFrame([[mrr]], columns=['MRR'])
    mrr_info.to_csv(save_path, index=False)
    print('MRR info saved')
    
### calculate the average manual efforts for Top@K
'''
if rank <= k: 
    manual_efforts = rank
else: 
    manual_efforts = k
'''
def manual_efforts(metric, k_list=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 50, 100], save_path=os.path.join(SAVE_DIR, 'manualefforts_TFIDF.csv')):
    manual_efforts_info = pd.DataFrame(columns=['Top@k', 'manual_efforts'])
    manual_efforts_info.to_csv(save_path, index=False)
    
    for k in tqdm(k_list):
        rank_info = pd.read_csv(os.path.join(SAVE_DIR, f'rankinfo_{metric}.csv'))
        rank_info['manual_efforts'] = rank_info['rank'].apply(lambda x: x if x <= k else k)
        manual_efforts = rank_info['manual_efforts'].sum() / len(rank_info)
        print('Top@{} manual efforts: {}'.format(k, manual_efforts))
        manual_efforts_info_iter = pd.DataFrame([[k, manual_efforts]], columns=['Top@k', 'manual_efforts'])
        manual_efforts_info_iter.to_csv(save_path, mode='a', header=False, index=False)

def normalized_tfidf(tfidf_data):
    '''
    normalize the similarity scores of TF-IDF to [0, 1] and save into a new column named `similarity_normalized`
    '''
    ## group by cve
    test_cve = tfidf_data.groupby('cve')
    
    for cve, group in tqdm(test_cve, desc='normalize the similarity scores of TF-IDF to [0, 1]'):
        # first sort the rows according to the similarity score
        group = group.sort_values(by='similarity', ascending=False)
        similarity_scores = group['similarity'].tolist()
        max_score = max(similarity_scores)
        min_score = min(similarity_scores)
        normalized_scores = [(score - min_score) / (max_score - min_score) for score in similarity_scores]
        tfidf_data.loc[group.index, 'similarity_normalized'] = normalized_scores
        
    return tfidf_data
    
    

if __name__ == "__main__":
    
    ### we evaluate the performance of CR_score and TF-IDF_score on test data first.
    ## columns are: cve,owner,repo,commit_id,similarity,label

    ### read tfidf similarity data
    print("Step 1/4: read the similarity data")
    tfidf_data = pd.read_csv(os.path.join(DATA_DIR, 'test_data_TFIDF.csv'))

    test_crscore = pd.read_csv('/mnt/local/Baselines_Bugs/CR_score/output/crscore_test_data.csv')
    test_crscore.drop(['desc_token', 'msg_token', 'diff_token'], axis=1, inplace=True)
    
    ### we need to normalize the similarity scores of TF-IDF to [0, 1]
    print("Step 2/4: normalize the similarity scores of TF-IDF to [0, 1]")
    # tfidf_data = normalized_tfidf(tfidf_data)
    
    # tfidf_data.drop(['similarity'], axis=1, inplace=True)
    
    
    ### merge the two dataframes
    print("Step 3/4: merge the two dataframes")
    fusion_df = pd.merge(tfidf_data, test_crscore, on=['cve', 'owner', 'repo', 'commit_id', 'label'], how='left')
    
    # ### calculate the average similarity score of patch commit for each cve for each metric and save into
    # ### a three new columns named `fused_recall`, `fused_precision` and `fused_f1`
    
    ### normalized
    # fusion_df['fused_recall'] = (fusion_df['Recall'] + fusion_df['similarity_normalized']) / 2
    # fusion_df['fused_precision'] = (fusion_df['Precision'] + fusion_df['similarity_normalized']) / 2
    # fusion_df['fused_f1'] = (fusion_df['F1'] + fusion_df['similarity_normalized']) / 2
    
    
    # #### unnormalized
    # fusion_df['fused_recall'] = (fusion_df['Recall'] + fusion_df['similarity']) / 2
    # fusion_df['fused_precision'] = (fusion_df['Precision'] + fusion_df['similarity']) / 2
    # fusion_df['fused_f1'] = (fusion_df['F1'] + fusion_df['similarity']) / 2
    
    ### weighted, and the weight for CR_score is 0.45
    fusion_df['fused_recall'] = (fusion_df['Recall'] * 0.45 + fusion_df['similarity'] * 0.55)
    fusion_df['fused_precision'] = (fusion_df['Precision'] * 0.45 + fusion_df['similarity'] * 0.55)
    fusion_df['fused_f1'] = (fusion_df['F1'] * 0.45 + fusion_df['similarity'] * 0.55)
    
    
    test_cve = fusion_df.groupby('cve')
    ### calculate the average rank of patch commit for each cve

    ### calculate the average similarity score of patch commit for each cve for each metric
    for metric in ['fused_recall', 'fused_precision', 'fused_f1']:
        
        print('Processing metric: {}'.format(metric))

        ### calculate the average rank of patch commit for each cve
        rank_info = pd.DataFrame(columns=['cve', 'rank'])
        rank_info.to_csv(os.path.join(SAVE_DIR, f'rankinfo_{metric}.csv'), index=False)

        for cve, group in tqdm(test_cve):
            # first sort the rows according to the similarity score
            group = group.sort_values(by=metric, ascending=False)
            average_rank = 0
            #### maybe there are multiple patch commits for one cve
            patch_rows = group[group['label'] == 1]
            ranks = []
            for _, row in patch_rows.iterrows():
                ### get the rank by using the index of the row
                rank = group.index.get_loc(row.name) + 1
                ranks.append(rank)
            average_rank = sum(ranks) / len(ranks)
            rank_info_iter = pd.DataFrame([[cve, average_rank]], columns=['cve', 'rank'])
            rank_info_iter.to_csv(os.path.join(SAVE_DIR, f'rankinfo_{metric}.csv'), mode='a', header=False, index=False)
            # print('cve: {}, average rank: {}'.format(cve, average_rank))
        print('rank info saved for {}'.format(metric))
        
        print("Step 4/4: calculate the recall, MRR and manual efforts")
        
        recall(metric, save_path=os.path.join(SAVE_DIR, f'recall_{metric}.csv'))
        mrr(metric, save_path=os.path.join(SAVE_DIR, f'MRR_{metric}.csv'))
        manual_efforts(metric, save_path=os.path.join(SAVE_DIR, f'manualefforts_{metric}.csv'))


