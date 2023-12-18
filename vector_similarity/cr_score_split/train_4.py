import os
import pandas as pd
from tqdm import tqdm
import torch
import bert_score
from configs import *

os.environ['CUDA_VISIBLE_DEVICES'] = '4'

batch_size=400
torch.multiprocessing.set_sharing_strategy("file_system")

def get_cr_score(desc_tokens:list, commit_tokens:list):
    all_preds = bert_score.score(
        cands=commit_tokens,
        refs=desc_tokens,
        model_type='microsoft/codereviewer',
        return_hash=False,
        batch_size=batch_size,
        nthreads=20
    )
    
    return all_preds



if __name__ == '__main__':
    
    file = '/mnt/local/anonymous/train_split/train_data_part_0.csv'
    
    filename = file.split('/')[-1]
    
    print('Loading data...')
    df = pd.read_csv(file)
    print('Data loaded.')

    cves = df['cve'].unique().tolist()

    for cve in tqdm(cves, desc='Processing cves'):
        get_singapore_time()
        
        desc_tokens = df[df['cve'] == cve]['desc_token'].tolist()
        msg_tokens = df[df['cve'] == cve]['msg_token'].tolist()
        diff_tokens = df[df['cve'] == cve]['diff_token'].tolist()
        commit_tokens = [msg + ' ' + diff for msg, diff in zip(msg_tokens, diff_tokens)]
        all_preds = get_cr_score(desc_tokens, commit_tokens)
        Recall, Precision, F1 = all_preds
        
        # Convert tensors to numpy arrays
        Recall = Recall.numpy()
        Precision = Precision.numpy()
        F1 = F1.numpy()

        df.loc[df['cve'] == cve, 'Recall'] = Recall
        df.loc[df['cve'] == cve, 'Precision'] = Precision
        df.loc[df['cve'] == cve, 'F1'] = F1
        
    df.to_csv(os.path.join(cr_save_dir, filename), index=False)


