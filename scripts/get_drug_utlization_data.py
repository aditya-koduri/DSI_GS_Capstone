import requests
import pathlib
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from sys import argv
from tqdm import tqdm
from pandas_profiling import ProfileReport


chrome_options = Options()
chrome_options.add_argument("--headless")
filepath = pathlib.Path(__file__).parent.resolve()
chromedriver_path = pathlib.Path(filepath,"chromedriver")
browser = webdriver.Chrome(executable_path=chromedriver_path,options=chrome_options)

def download_csv(link,button_attrs):
    browser.get(link)
    soup = BeautifulSoup(browser.page_source,"lxml")
    download_link = soup.find("a",attrs=button_attrs)["href"]
    download_link = "/".join(["https://data.medicaid.gov/",download_link])
    df = pd.read_csv(download_link)
    return df

# Got this url from web page html code

def save_to_csv(url,output_path,token,button_args,title_key,data_src = "aaData"):
    response = requests.get(url)
    data = response.json()[data_src]
    final_data = None
    for x in tqdm(data):
        name = x[title_key]
        if token in name:
            link = x["Link"]
            try:
                df = download_csv(link,button_args)
                if final_data is None:
                    final_data = df
                else:
                    final_data = pd.concat([data,df])
            except:
                continue
    print("Size of the final csv is",final_data.shape)
    final_data.to_csv(output_path,index=False)

def download_data():
    #Download utilization data
    # Got this url from web page html code
    url = "https://www.medicaid.gov/sites/default/files/2021-08/drug-utilization-july.json"
    token= "All States"
    title_key = "Name"
    button_args = {"class":"ds-c-button ds-c-button--transparent ds-u-text-align--left ds-u-font-weight--normal"}
    output_path = pathlib.Path(str(argv[1]),"{0}_drug_utilization.csv".format(token))

    save_to_csv(url,output_path,token,button_args,title_key)

    #Download drug costs
    url = "https://www.medicaid.gov/sites/default/files/2021-08/federal-upper-limit-August2021.json"
    token= "Federal Upper Limit"
    title_key = "Type"
    button_args = {"class":"ds-c-button ds-c-button--transparent ds-u-text-align--left ds-u-font-weight--normal"}
    output_path = pathlib.Path(str(argv[1]),"{0}_drug_cost.csv".format(token))

    save_to_csv(url,output_path,token,button_args,title_key)

def describe_data(df,title):
    profile = ProfileReport(df, title=title,explorative = True)
    path_to_csv = pathlib.Path(str(argv[1]),"{0}.html".format(title))
    profile.to_file(path_to_csv)


if __name__ == "__main__":

    download_data()
    data_path = str(argv[1])

    drug_util_df = pd.read_csv(pathlib.Path(data_path,"All States_drug_utilization.csv"))
    describe_data(drug_util_df,"All States Drug Utilization")
    drug_util_df = pd.read_csv(pathlib.Path(data_path,"Federal Upper Limit_drug_cost.csv"))
    describe_data(drug_util_df,"Federal Upper Limit Drug Cost")