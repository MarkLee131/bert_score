### Modified from: `similarity_fusion.py`
### Used to filter out the top 100 commits for each CVE.
'''
Try to fuse the similarity of CR_score and TF-IDF_score and then calculate the recall, MRR and manual efforts
'''
import os
import pandas as pd
from tqdm import tqdm

DATA_DIR = '/mnt/local/Baselines_Bugs/PatchSleuth/TF-IDF'
SAVE_DIR = '/mnt/local/Baselines_Bugs/CR_score/evaluate/fusion_unnormalized'
os.makedirs(SAVE_DIR, exist_ok=True)


if __name__ == "__main__":
    
    ### we evaluate the performance of CR_score and TF-IDF_score on test data first.
    ## columns are: cve,owner,repo,commit_id,similarity,label

    ### read tfidf similarity data
    print("Step 1: read the similarity data")
    tfidf_data = pd.read_csv(os.path.join(DATA_DIR, 'test_data_TFIDF.csv'))

    test_crscore = pd.read_csv('/mnt/local/Baselines_Bugs/CR_score/output/crscore_test_data.csv')


    ### merge the two dataframes
    print("Step 2: merge the two dataframes")
    fusion_df = pd.merge(tfidf_data, test_crscore, on=['cve', 'owner', 'repo', 'commit_id', 'label'], how='left')
    
    # Calculate the average similarity score of patch commit for each cve for f1 and save into `fused_f1`
    fusion_df['fused_f1'] = (fusion_df['F1'] + fusion_df['similarity']) / 2

    # Group by CVE and process each group
    test_cve = fusion_df.groupby('cve')

    # Initialize a list to store the top 100 rows for each CVE
    top_100_list = []

    for cve, group in tqdm(test_cve):
        # Sort the rows according to the fused_f1 score
        sorted_group = group.sort_values(by='fused_f1', ascending=False)

        # Select the top 100 rows
        top_100 = sorted_group.head(100)

        # Add the top 100 rows to the list
        top_100_list.append(top_100)

    # Concatenate all the top 100 DataFrames
    top_100_per_cve = pd.concat(top_100_list)


    # Drop the 'recall' and 'precision' columns if they exist
    top_100_per_cve = top_100_per_cve.drop(columns=['recall', 'precision'], errors='ignore')

    # Save the filtered data into a new CSV file
    
    top_100_per_cve.to_csv(os.path.join(SAVE_DIR, 'top_100_fusion.csv'), index=False)
    print(f"Step 3: save the top 100 results into {SAVE_DIR}/top_100_fusion.csv")
