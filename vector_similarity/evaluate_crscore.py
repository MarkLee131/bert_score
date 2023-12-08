### Used to evaluate the performance of CR_Score.

import os
from tqdm import tqdm
import pandas as pd

DATA_DIR = '/mnt/local/Baselines_Bugs/CR_score/output'

SAVE_DIR = '/mnt/local/Baselines_Bugs/CR_score/evaluate/cr_similarity'
os.makedirs(SAVE_DIR, exist_ok=True)
    
### calculate the Top@K recall by using the rank info
def recall(metric, k_list=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 50, 100], save_path=os.path.join(SAVE_DIR, 'recall_CR.csv')):
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
def mrr(metric, save_path=os.path.join(SAVE_DIR, 'MRR_CR.csv')):
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
def manual_efforts(metric, k_list=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20, 30, 50, 100], save_path=os.path.join(SAVE_DIR, 'manualefforts_CR.csv')):
    manual_efforts_info = pd.DataFrame(columns=['Top@k', 'manual_efforts'])
    manual_efforts_info.to_csv(save_path, index=False)
    
    for k in tqdm(k_list):
        rank_info = pd.read_csv(os.path.join(SAVE_DIR, f'rankinfo_{metric}.csv'))
        rank_info['manual_efforts'] = rank_info['rank'].apply(lambda x: x if x <= k else k)
        manual_efforts = rank_info['manual_efforts'].sum() / len(rank_info)
        print('Top@{} manual efforts: {}'.format(k, manual_efforts))
        manual_efforts_info_iter = pd.DataFrame([[k, manual_efforts]], columns=['Top@k', 'manual_efforts'])
        manual_efforts_info_iter.to_csv(save_path, mode='a', header=False, index=False)



if __name__ == "__main__":
    

    ### read cr_score similarity data
    print("Step 1/3: read cr_score similarity data")
    test_crscore = pd.read_csv(os.path.join(DATA_DIR, 'crscore_test_data.csv'))
    
    ### we need to drop some columns: desc_token, msg_token, diff_token
    test_crscore = test_crscore.drop(columns=['desc_token', 'msg_token', 'diff_token'], axis=1)
    
    test_cve = test_crscore.groupby('cve')

    print("Verify the number of cve:")
    cve_list = test_crscore['cve'].unique().tolist()
    print('cve list length: {}'.format(len(cve_list)))
    cve_set = set(cve_list)
    print('cve set length: {}'.format(len(cve_set)))


    for metric in ['Recall', 'Precision', 'F1']:
        print('Processing metric: {}'.format(metric))
        
        ### calculate the average rank of patch commit for each cve
        ### by using label to determine whether the commit is a patch commit
        print("Step 2/3: calculate the average rank of patch commit for each cve")
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
        
        print("Step 3/3: calculate the recall, MRR and manual efforts")
        
        recall(metric, save_path=os.path.join(SAVE_DIR, f'recall_{metric}.csv'))
        mrr(metric, save_path=os.path.join(SAVE_DIR, f'MRR_{metric}.csv'))
        manual_efforts(metric, save_path=os.path.join(SAVE_DIR, f'manualefforts_{metric}.csv'))
        