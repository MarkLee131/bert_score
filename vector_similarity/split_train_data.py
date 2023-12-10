import os
import pandas as pd
from tqdm import tqdm

train_file =  '/mnt/local/kaixuan_cuda11/Baselines_Bugs/PatchSleuth/data/train_data.csv'

# Function to split train data into four parts
def split_train_data(train_file, save_dir='/mnt/local/kaixuan/train_split', num_splits=4):
    # Create directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)

    try:
        train_df = pd.read_csv(train_file)
    except Exception as e:
        print(f"Error reading train file: {e}")
        return

    unique_cve = train_df['cve'].unique()
    grouped_cve = train_df.groupby('cve')
    total_cve = len(unique_cve)

    # Splitting the data
    for i in tqdm(range(num_splits)):
        start = int(i * total_cve / num_splits)
        end = int((i + 1) * total_cve / num_splits) if i != num_splits - 1 else total_cve

        tmp_cve = unique_cve[start:end]
        tmp_df = pd.concat([grouped_cve.get_group(cve) for cve in tmp_cve])
        tmp_df.to_csv(os.path.join(save_dir, f'train_data_part_{i}.csv'), index=False)

if __name__ == '__main__':
    split_train_data(train_file=train_file, num_splits=4)
