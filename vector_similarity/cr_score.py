import os
import pandas as pd
from tqdm import tqdm
import torch
import bert_score
from configs import *

def get_cr_score(desc_token, commit_token):
    all_preds = bert_score.score(
        cands=[commit_token],
        refs=[desc_token],
        model_type='microsoft/codereviewer',
        return_hash=False,
        batch_size=batch_size
    )
    avg_scores = [s.mean(dim=0) for s in all_preds]
    return avg_scores[0].cpu().item(), avg_scores[1].cpu().item(), avg_scores[2].cpu().item()

def process_file(file):
    df = pd.read_csv(file, chunksize=10000)
    all_rows = []
    for chunk in tqdm(df, desc=f'Processing file: {file}'):
        chunk['msg_token'] = chunk['msg_token'].apply(lambda x: x if not pd.isna(x) else ' ')
        chunk['diff_token'] = chunk['diff_token'].apply(lambda x: x if not pd.isna(x) else ' ')

        for _, row in chunk.iterrows():
            P, R, F1 = get_cr_score(row['desc_token'], row['msg_token'] + ' ' + row['diff_token'])
            new_row = row.drop(['desc_token', 'msg_token', 'diff_token'])
            new_row['P'] = P
            new_row['R'] = R
            new_row['F1'] = F1
            all_rows.append(new_row)


    results_df = pd.DataFrame(all_rows)
    file_prefix = os.path.splitext(os.path.basename(file))[0].split('_')[0]
    save_path = os.path.join(save_dir, f'results_{file_prefix}.csv')
    results_df.to_csv(save_path, index=False)
    print(f'Saved results to {save_path}')

if __name__ == '__main__':
    torch.multiprocessing.set_sharing_strategy("file_system")
    torch.set_num_threads(10)

    files = [test_file, validate_file, train_file]
    for file in files:
        process_file(file)
