import os
import pandas as pd
import py7zr
import subprocess
import urllib.request
import logging as log

from pathlib import Path
from datetime import datetime
from util import save_csv


log.basicConfig(filename='app.log', filemode='w', \
    format='%(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)
URL = "https://www.eea.europa.eu/data-and-maps/data/industrial-reporting-under-the-industrial-3/eu-registry-e-prtr-lcp/industrial-reporting-database-v4-march-2021/at_download/file"

cwd = Path.cwd()
csv_path = cwd / 'prtr_csv'
download_path = cwd / 'prtr_downloads'
db_path = cwd/ 'prtr_db_files'
csv_path.mkdir(exist_ok=True)
download_path.mkdir(exist_ok=True)
db_path.mkdir(exist_ok=True)


def main():
    log.debug('\n\n\nPRTR Data')
    download_and_extract_dbfile(URL, str(download_path), str(db_path))
    pd_data = export_and_merge_tables_from_db(db_path)
    save_csv(pd_data, str(csv_path))
    
def download_and_extract_dbfile(URL:str, download_path: str, db_path: str) -> None:
    file_name = str(datetime.now().strftime("%m_%d_%Y_%H:%M:%S"))+'.zip'
    log.info('file_name')

    with urllib.request.urlopen(URL) as url:
        with open(str(download_path) + '/' +file_name, 'wb') as f:
            f.write(url.read())
            log.info('DB file downloaded')
    with py7zr.SevenZipFile(str(download_path) + '/' +file_name, mode='r') as z:
        z.extractall(str(db_path))
        log.info('DB file extracted')
    os.rename(str(db_path)+'/Industrial Reporting Database v4 - March 2021.accdb',str(db_path)+'/db.accdb')

def export_and_merge_tables_from_db(db_path: str) -> pd:
    subprocess.call(f'mdb-export {db_path}/db.accdb 2_ProductionFacility > {db_path}/2_ProductionFacility.csv', shell=True)
    subprocess.call(f'mdb-export {db_path}/db.accdb 2f_PollutantRelease > {db_path}/2f_PollutantRelease.csv', shell=True)
    log.info('epporting 2 db tables 2_ProductionFacility 2f_PollutantRelease')
    prod_facility = pd.read_csv(f'{db_path}/2_ProductionFacility.csv')
    prod_facility = prod_facility[['Facility_INSPIRE_ID','nameOfFeature','parentCompanyName','city','postalCode', 'countryCode']]

    pollutant_release = pd.read_csv(f'{db_path}/2f_PollutantRelease.csv')
    pollutant_release = pollutant_release.loc[pollutant_release['reportingYear'] == 2019] 
    pollutant_release = pollutant_release[['Facility_INSPIRE_ID', 'pollutantName', 'totalPollutantQuantityKg']]
    df = prod_facility.merge(pollutant_release, on = 'Facility_INSPIRE_ID', how = 'inner').drop('Facility_INSPIRE_ID',axis=1)
    log.info('merge completed')
    return df

if __name__ == '__main__':
    main() 