import os
import pandas as pd

from datetime import datetime

#return recent downloaded file
def get_latest_download_file(download_path: str) -> str:
    path = str(download_path)
    os.chdir(path)
    files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
    newest = files[-1]
    return newest

def save_csv(pd_data: pd, csv_path:str) -> None:
    csv_file_name = str(datetime.now().strftime("%m_%d_%Y_%H:%M:%S"))
    with open(str(csv_path) + '/' + csv_file_name +'.csv',"w", encoding ="utf-8") as f:
        f.write(pd_data.to_csv())