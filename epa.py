import pandas as pd
import time
import logging as log

from datetime import datetime
from pathlib import Path
from pandas.core.frame import DataFrame
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from util import get_latest_download_file, save_csv

log.basicConfig(filename='app.log', filemode='w', \
    format='%(asctime)s - %(levelname)s - %(message)s', level=log.DEBUG)
cwd = Path.cwd() #current working directory
download_path = cwd/'epa_downloads'
csv_path = cwd / 'epa_csv'
download_path.mkdir(exist_ok=True)
csv_path.mkdir(exist_ok=True)

#chromium options
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
        "download.default_directory": str(download_path),
})
driver = webdriver.Chrome(options = chrome_options)
URL = "https://edap.epa.gov/public/extensions/TRISearchPlus/TRISearchPlus.html"

def main():
    try:
        log.info('\n\n\nGET EPA DATA')
        navigate_and_download_xlsx(driver, URL)
    except Exception as e:
        print(e)
        log.info(e)
        driver.close()

    try:
        file_name = get_latest_download_file(str(download_path))
        pd_data = pd.read_excel(str(download_path/file_name), engine='openpyxl') #xlsx to pandas pandas data frame
        pd_data = pd_data[['TRI Facility Name',
                                 'Parent Company',
                                 'State',
                                 'ZIP Code',
                                 'Releases (lb)'
                                 ]]# selecting required columns
        log.info(str(csv_path))
        save_csv(pd_data, str(csv_path))
    except Exception as e:
        print(e)
        log.info(e)

def element_click(xpath: str, wait_time: int = 0) -> None:
    elem = driver.find_element_by_xpath(xpath)
    elem.click() #for closing pop up modals if any
    time.sleep(wait_time)

def navigate_and_download_xlsx(driver: webdriver, URL: str) -> None:
    driver.get(URL)
    #sleep for 5 sec to allow JS to complete the render
    time.sleep(5)
    log.info('navigating through website')
    element_click('/html/body')
    
    #selecting options
    element_click('//*[@id="nav-tab-custom-tables"]', 2)
    element_click('//*[@id="table-download-1-dimensions"]/label[5]/input') #zip
    element_click('//*[@id="table-download-1-dimensions"]/label[6]/input') #city
    element_click('//*[@id="table-download-1-dimensions"]/label[8]/input') #state
    element_click('//*[@id="table-download-1-dimensions"]/label[10]/input') #parent company
    
    #Scrolling up to top the page. To set the view 
    driver.find_element_by_tag_name('body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(.5)

    #selecting most recent year from the filter
    element_click('//*[@id="qlik-content"]/div[2]/div[2]/button', 1) #selecting filter
    element_click('//*[@id="filter_year"]/div/article/div[1]/div', .5)
    element_click('/html/body/div[31]/div/div/div/ng-transclude/div/div[3]/div/article\
    /div[1]/div/div/div/div[2]/div[1]/div/ul/li[1]')# selcting year
    element_click('html/body/div[4]/button')# closing filter
    element_click('/html/body/div[5]/div/div[3]/div[11]/div/div/div/div[2]/div[2]/div\
    /qliksense-card/paper-card/div[2]/paper-icon-button[1]',2)
    log.info('Started downloading the xlsx file')
    #check to see if the file is fully downloaded
    fileends = "crdownload"

    while True:
        file_name = get_latest_download_file(download_path)
        time.sleep(1)
        if "crdownload" not in file_name: break;
    driver.close()
    log.info('Finished downloading xlsx file ')


if __name__ == '__main__':
    main()