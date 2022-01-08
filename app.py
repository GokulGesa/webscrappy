import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json
import csv
import pandas as pd
from urllib.request import urlopen 
from flask import Flask, render_template, send_file

app = Flask(__name__)

@app.route('/')
def index():

    def getdata(url):
        r = requests.get(url)
        return r.text

    def get_links(website_link):
        html_data = getdata(website_link)
        soup = BeautifulSoup(html_data, "html.parser")
        list_links = []
        for link in soup.find_all("a", href=True):
            
            if (str(website_link) in str(link["href"])):
                print("Test 123")
            # Append to list if link starts with /
            if str(link["href"]).startswith("/"):
                link_with_www = website + link["href"][1:]
                print(link_with_www)                
                headers_std = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
                'Content-Type': 'text/html',
                }
                html = requests.get(link_with_www,headers=headers_std).text
                soup = BeautifulSoup(html,'lxml')
                product_special_price_class = "special-price"
                actual_price_class = "old-price"
                if link_with_www.startswith('https://giftkyade.com/'):
                    product_special_price_class = "special-price"
                    actual_price_class = "old-price"                    
                    product_names = soup.find_all("span",{"class":product_special_price_class})
                    product_prices = soup.find_all("span",{"class":product_special_price_class})
                    product_prices_old = soup.find_all("span",{"class":actual_price_class})
                    
                elif link_with_www.startswith('https://www.bewakoof.com/'):
                    product_special_price_class = "discountedPriceText"
                    actual_price_class = "actualPriceText"                   
                    product_names = soup.find_all("span",{"class":product_special_price_class})
                    product_prices = soup.find_all("span",{"class":product_special_price_class})
                    product_prices_old = soup.find_all("span",{"class":actual_price_class})  
                    
                product_names_df = []
                product_prices_df = []
                ratings_df = []
                main_page_urls_df = []
                product_prices_old_df = []
                for i in range(len(product_names)):
                    print(product_names[i].text.strip())
                    print(product_prices[i].text.strip())
                    print(product_prices_old[i].text.strip())
                    product_names_df.append(product_names[i].text.strip())
                    product_prices_df.append(product_prices[i].text.strip())
                    product_prices_old_df.append(product_prices_old[i].text.strip())
                 
                df = pd.DataFrame({'Product name':product_names_df,'special-price (INR)':product_prices_df,'old-price (INR)':product_prices_old_df})
                print(df.head())
                print(df)
                df.to_csv("Output.csv", index=False, mode='a', header=False)                                
        dict_links = dict.fromkeys(list_links, "Not-checked")
        return dict_links

    def get_subpage_links(l):
        for link in tqdm(l):
            if l[link] == "Not-checked":
                dict_links_subpages = get_links(link)
                l[link] = "Checked"
            else:
                dict_links_subpages = {}
            l = {**dict_links_subpages, **l}
        return l

    website = "https://giftkyade.com/"
    # website = "https://www.bewakoof.com/"
    dict_links = {website:"Not-checked"}

    counter, counter2 = None, 0
    while counter != 0:
        counter2 += 1
        dict_links2 = get_subpage_links(dict_links)
        counter = sum(value == "Not-checked" for value in dict_links2.values())
        print("")
        print("THIS IS LOOP ITERATION NUMBER", counter2)
        print("LENGTH OF DICTIONARY WITH LINKS =", len(dict_links2))
        print("NUMBER OF 'Not-checked' LINKS = ", counter)
        print("")
        file = open("Output.csv")
        csvreader = csv.reader(file)
        header = next(csvreader)
        print(header)
        rows = []
        for row in csvreader:
            rows.append(row)
        file.close()
        return send_file("Output.csv", as_attachment=True)
        
if __name__ == '__main__':
  app.run(debug=True)