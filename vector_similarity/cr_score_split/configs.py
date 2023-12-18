import pytz
from datetime import datetime
import os

cr_save_dir='/mnt/local/anonymous/output'
os.makedirs(cr_save_dir, exist_ok=True)

def get_singapore_time():
    singaporeTz = pytz.timezone("Asia/Singapore") 
    timeInSingapore = datetime.now(singaporeTz)
    currentTimeInSinapore = timeInSingapore.strftime("%H:%M:%S")
    print(currentTimeInSinapore)