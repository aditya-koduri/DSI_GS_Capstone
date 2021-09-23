import requests
import pathlib
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sys import argv

chrome_options = Options()
chrome_options.add_argument("--headless")
filepath = pathlib.Path(__file__).parent.resolve()
chromedriver_path = pathlib.Path(filepath,"chromedriver")
browser = webdriver.Chrome(executable_path=chromedriver_path,options=chrome_options)

def download_csv(link):
    browser.get(link)
    soup = BeautifulSoup(browser.page_source,"lxml")
    download_link = soup.find("a",attrs={"class":"ds-c-button ds-c-button--transparent ds-u-text-align--left ds-u-font-weight--normal"})["href"]
    download_link = "/".join(["https://data.medicaid.gov/",download_link])
    print(download_link)
    df = pd.read_csv(download_link)
    return df

# Got this url from web page html code
url = "https://www.medicaid.gov/sites/default/files/2021-08/drug-utilization-july.json"
output_path = str(argv[1])
response = requests.get(url)
data = response.json()["aaData"]

final_data = None
for x in data:
    name = x["Name"]
    if "All States" in name:
        link = x["Link"]
        try:
            df = download_csv(link)
            if final_data is None:
                final_data = df
            else:
                final_data = pd.concat([data,df])
        except:
            continue
final_data.to_csv(output_path,index=False)