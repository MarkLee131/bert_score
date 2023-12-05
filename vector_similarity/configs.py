import torch
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
gpus = [0,1]

data_path='/mnt/local/Baselines_Bugs/PatchSleuth/data' 
os.makedirs(data_path,exist_ok=True)

train_filename    = 'train_data.csv'
validate_filename = 'validate_data.csv'
test_filename     = 'test_data.csv'



train_file=os.path.join(data_path, train_filename)
validate_file=os.path.join(data_path, validate_filename)
test_file=os.path.join(data_path, test_filename)
batch_size=64

save_dir='/mnt/local/Baselines_Bugs/CR_score/output'
os.makedirs(save_dir, exist_ok=True)

debug=False
device = torch.device("cuda" if torch.cuda.is_available() and not debug else 'cpu')

import pytz
from datetime import datetime

def get_singapore_time():
    singaporeTz = pytz.timezone("Asia/Singapore") 
    timeInSingapore = datetime.now(singaporeTz)
    currentTimeInSinapore = timeInSingapore.strftime("%H:%M:%S")
    # print("Current time in Singapore is: ", currentTimeInSinapore)
    print(currentTimeInSinapore)