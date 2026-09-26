import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
file_handler = logging.FileHandler("books_scraper.log")
file_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.addHandler(file_handler) 

books_list=[]
url = "https://books.toscrape.com"
try: 
    headers={"User-Agent" : "Mozilla/5.0 (windows NT 10.0; win64; x64) Applewebkit/537.36"}
    response = requests.get(url=url , timeout=(5,10) , headers=headers )
    response.encoding = "utf-8"                
    response.raise_for_status()
    
    logger.debug("The request was accepted and the response was sent")
    soup = BeautifulSoup (response.text , "lxml")
    books=soup.select("article.product_pod")
    for book in books :
        a={}
        name=book.select_one("h3>a")
        price=book.select_one("div.product_price>p.price_color")
        rating=book.select_one("p.star-rating")
        link=book.select_one("div.image_container>a")
        if name:
            book_name=name.get('title')
        else:
            book_name="Doesn't found"
        if price:
            book_price=price.get_text(strip=True)
        else:
            book_price="Doesn't found"
        if rating: 
            book_rating=rating.get('class')[1]
        else:
            book_rating="Doesn't found"
        if link:
            book_link=link.get('href')
        else:
            book_link="Doesn't found"
        book_dict={"Name":book_name , "Price":book_price , "Rating":book_rating , "Link":book_link}
        books_list.append(book_dict)
        
    logger.debug(books_list)
    logger.info(f"The number of books is: {len(books_list)}")

    df = pd.DataFrame(books_list)
        # print(df)
    logger.debug(f"Columns data type: {df.dtypes}")
    df["Price"]=df["Price"].str.replace("£" , "")
    df["Price"]=df["Price"].astype(float)
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
    number_of_unique_values=df["Name"].nunique()
    logger.info(f"Number of different books: {number_of_unique_values}")
    df.rename(columns={"Price":"Price (£)"} , inplace=True)
    df.info()  #doesn't need print()
    df=df.sort_values("Price (£)").reset_index(drop=True)

    df.to_csv("Books_scraping.csv" , index=False , encoding="utf-8-sig")

except requests.exceptions.HTTPError as e:
    logger.error(f"HTTP error: {e}")
except requests.exceptions.Timeout:
    logger.error("Server response delay — please try again")
except requests.exceptions.ConnectionError:
    logger.error("Internet outage or server not available")
except requests.exceptions.RequestException as e:
    logger.error(f"Request failed: {e}")
except Exception as e : 
    logger.error(f"Error found: {e}")

