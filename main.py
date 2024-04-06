import requests
from bs4 import BeautifulSoup
from lxml import etree


def soup_func(url):
    header = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0'}
    r = requests.get(url, headers=header)
    return BeautifulSoup(r.text, 'lxml')


def pretiffy(soup):
    return soup.prettify()


def xpath(soup, path):
    return etree.HTML(str(soup)).xpath(path)[0].text






def get_paginations_links(url):
    soup = soup_func(url)
    # pagination list pages
    pagination_links = [link['href'] for link in soup.find_all('a', attrs={'class': 'ChoosePage'})][:-1:]
    pagination_links = ['/trending/forever?page=1'] + pagination_links
    
    return pagination_links


def jump_data(filname, data):
    import json
    with open(filname, 'w+') as f:
        json.dump(data, f , indent=4)
        

def scrape(pagination_links, base_url):
    all_data = []
    for pagination_link in pagination_links:

        URL = f"{base_url}{pagination_link}"

        #scarpe the actual pagination link page
        pagination_soup = soup_func(URL)

        # get the list of books of this actual page
        list_group = pagination_soup.find_all('li', attrs={'class': 'searchResultItem'})

        # insert into a dictionary format books detail
        data = []

        # get the link detail page of every book
        links_detail_book_page = [link.find('a', attrs={'itemprop': 'url'})['href'] for link in list_group]
        for books_detail in links_detail_book_page:
            NEW_URL = f"{base_url}{books_detail}"
            #book_detail = requests.get(NEW_URL)
            new_soup = soup_func(NEW_URL) #BeautifulSoup(book_detail.text, 'html.parser')
            publishers = [publisher.text for publisher in new_soup.find_all('a', attrs={'itemprop': 'publisher'})]
            try:
                isbn = [isbn.text for isbn in new_soup.find_all('dd', attrs={'class': 'object', 'itemprop': 'isbn'})]
                isbn10 = isbn[0]
                isbn15 = isbn[1]
            except:
                isbn10 = None
                isbn15 = None
            try:
                page = new_soup.find('span', attrs={'class':'edition-pages' ,'itemprop': 'numberOfPages'}).text
            except:
                page = None
            try:
                language = [language.a.text for language in new_soup.find_all('span', attrs={'itemprop':'inLanguage'})]
            except ValueError:
                language = None
            try:
                title = new_soup.find('h1', attrs={'class':'work-title', 'itemprop':'name'}).text
            except:
                title = None
            book_data = {
                    'title': title,
                    'author': new_soup.find('a', attrs={'itemprop': 'author'}).text, #xpath(new_soup, '//*[@id="contentBody"]/div[1]/div[3]/div[2]/span/h2[2]/a'),
                    'publication_date': xpath(new_soup, '//*[@id="contentBody"]/div[1]/div[3]/div[5]/div/div[1]/span'),
                    'page': page,
                    'language': ' '.join(language),
                    'publishers': f"{', '.join(publishers)}",
                    'description': xpath(new_soup, '//*[@id="contentBody"]/div[1]/div[3]/div[4]/div/p[1]'),
                    'isbn10': isbn10, #xpath(new_soup, '//*[@id="contentBody"]/div[1]/div[3]/div[9]/div[4]/dl/dd[4]'),
                    'isbn15': isbn15,
                    'image':new_soup.find('img', attrs={'itemprop': 'image'})['src'],
                    'genre':[a.text for a in new_soup.find_all('a', attrs={'data-ol-link-track' : "BookOverview|SubjectClick"})]
                    }
            data.append(book_data)
            break
        jump_data(f"scraped_data/page_{int(pagination_link[-1]) + 1}.json", data)
        all_data.append(data)
    jump_data('scraped_data/all.json', all_data)
    
    return all_data
