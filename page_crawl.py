"""
Collection of functions used by Owen Rowader to scrape
Rapid API's collection of APIs for information, and to scrape google for possible information on
if the RapidAPI API's have SLA info.

Uses both selenium and requests to scrape, the libraries used can be seen below

REQUIRES A CHROMEDRIVER EXECUTABLE STORED IN THE C DRIVE TO WORK
"""



from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import pandas as pd
from bs4 import BeautifulSoup
import codecs
import csv
import requests
import urllib


#random headers and dictionaries used when calling the functions below (the calls of the functions have been removed)
dictionary = {}
headers = ['Sr. No', 'API Name', 'API URL', 'API Category', 'API Description', 'API Methods']
cat_dictionary = []
cnt = 0
link_list = []
headers_qos = ['Num', 'Page Alive', 'Url', 'Popularity', 'Latency', 'Service Level']
headers_sla = ['Num', 'Page Alive', 'Url', 'Terms of Use Found', 'Product Website Found', 'Website Link', 'SLA info Found']
headers_google = ['Name', 'website', 'Url',  'first 5 links', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
qos_dict = {}


#When given a base url and a scraping url it will scrape the category page of rapidAPI
#Will also work with the collections page fo rapidAPI
#for instance b_url = rapidapi.com and s_url = rapidapi.com/categories
def scrape_links(b_url, s_url):


    #category dictionary
    cat_dictionary = []

    base_url = b_url
    url = s_url

    #get web page
    data = requests.get(url)
    soup = BeautifulSoup(data.text, 'lxml')

    #get to where category types are stored
    whole_table = soup.find('div', class_='ItemGrid')
    all_rows = whole_table.find_all('div', class_ = 'ItemCard')

    #get the page links from each category
    for i in all_rows:
        api_name = i.find('span', class_='Text').text
        endpoint= i.find('a').get('href')
        final_api_link = base_url + endpoint
        #print(final_api_link)
        #cnt += 1
        #print(cnt)
        cat_dictionary.append(final_api_link)

    return cat_dictionary

#when given a rapid api page of APIs (in the form of a dictionary), scrape info about each API
#usually used after scrape_links()
def scrape_pages(dict):
    global cnt
    i = 0

    #launch driver
    driver = webdriver.Chrome("C:\chromedriver.exe")

    #there are 46 categories to scrape on RapidAPI
    while i < 46:

        #get link to category page and load it up
        link = dict[i]
        url = link
        driver.get(url)
        driver.fullscreen_window()
        notEnd = True
        i += 1

        #while not at the last API in the category
        while notEnd is True:
            nameNum = 0

            #wairt for page to load
            try:
                WebDriverWait(driver, 5).until(
                    lambda x: x.find_elements_by_class_name('ItemCard')
                )
            except TimeoutException:
                notEnd = False
                break


            apis = driver.find_elements_by_class_name('ItemCard')

            #get info about APIs
            for element in apis:
                all_methods  = ''
                link = element.find_element_by_class_name('CardLink').get_attribute('href')
                name = element.find_element_by_css_selector(".body1.bold.ApiName").text
                nameNum += 1
                desc = element.find_element_by_class_name("CardContent").text

                #this info doesn't appear unless hovered over by a mouse
                hover_element = element.find_element_by_class_name("ProductCard")
                hover = ActionChains(driver).move_to_element(hover_element)
                hover.perform()

                try:
                    WebDriverWait(driver, 5).until(
                        lambda x: x.find_element_by_css_selector('.badge.badge-info.badge-pill')
                    )
                except TimeoutException:
                    break

                #try to get the category of an API
                try:
                    category = driver.find_element_by_css_selector('.badge.badge-info.badge-pill').get_attribute('innerHTML')
                except NoSuchElementException:
                    category_xt = driver.find_element_by_xpath('/html/body/div/div/div/div/div/header/div/div/h2').text
                    category = category_xt[0:len(category_xt)-5]

                try:
                    infoPop = driver.find_element_by_class_name('EndpointPreview')
                except NoSuchElementException:
                    infoPop = 'null'

                #try to see if there are any preview methods
                if infoPop != 'null':
                    actions = infoPop.find_elements_by_class_name('EndpointRow')
                else:
                    all_methods = 'None'
                    actions = ''


                #store all info about all preview methods
                for row in actions:
                    method = ''
                    m_desc = ''
                    m_name = ''
                    try:
                        method += row.find_element_by_css_selector('.EndpointMethod.bold.POST').text  + ' ' + row.find_element_by_class_name('EndpointName').text + ': ' + row.find_element_by_css_selector('.EndpointDescription.caption').text + ' '

                    except NoSuchElementException:
                        j = 0

                    try:
                        method += row.find_element_by_css_selector('.EndpointMethod.bold.GET').text  + ' ' + row.find_element_by_class_name('EndpointName').text + ': ' + row.find_element_by_css_selector('.EndpointDescription.caption').text + ' '
                    except NoSuchElementException:
                        j = 0

                    try:
                        method += row.find_element_by_css_selector('.EndpointMethod.bold.PUT').text  + ' ' + row.find_element_by_class_name('EndpointName').text + ': ' + row.find_element_by_css_selector('.EndpointDescription.caption').text + ' '

                    except NoSuchElementException:
                        j = 0

                    try:
                        method += row.find_element_by_css_selector('.EndpointMethod.bold.PATCH').text  + ' ' + row.find_element_by_class_name('EndpointName').text + ': ' + row.find_element_by_css_selector('.EndpointDescription.caption').text + ' '

                    except NoSuchElementException:
                        j = 0

                    try:
                        method += row.find_element_by_css_selector('.EndpointMethod.bold.DELETE').text  + ' ' + row.find_element_by_class_name('EndpointName').text + ': ' + row.find_element_by_css_selector('.EndpointDescription.caption').text + ' '
                    except NoSuchElementException:
                        j = 0

                    all_methods += method

                #store info in dictonary
                cnt += 1
                dictionary[cnt] = [cnt, name, link, category, desc, all_methods]

                #move mouse so popup doesn't block HTML elements
                hover_element = driver.find_element_by_class_name('slider')
                hover = ActionChains(driver).move_to_element(hover_element)
                hover.perform()

            button = ''

            #see if we can go to the next page
            try:
                button = driver.find_element_by_css_selector("[aria-label='Go to next page']").get_attribute('aria-disabled')
            except NoSuchElementException:
                try:
                    button = driver.find_element_by_css_selector("[aria-label='Go to next page']").get_attribute('aria-disabled')
                except NoSuchElementException:
                    notEnd = False

            #if we can, go to the next page, otherwise, signal we are at the end
            if(button is None):
                hover_element = driver.find_element_by_css_selector("[aria-label='Go to next page']")
                hover = ActionChains(driver).move_to_element(hover_element)
                hover.perform()
                driver.find_element_by_css_selector("[aria-label='Go to next page']").click()
            else:
                notEnd = False

            #print(url + ' had ', end = '')
            #print(nameNum, end = '')
            #print(' APIs')

#given a dictionary, the headers, and a file name to store, creat a CSV file
def write_to_csv(dict, head, file_name):
    data_frame = pd.DataFrame.from_dict(data=dict,
                                        orient='index',
                                        columns=head)
    print(data_frame.head())
    data_frame.to_csv(file_name, index=False)

#given a csv file in the format of [name, url, category, description, methods], and a dictionary
#scrape the qos information of an API from its web page
#usually used after scrape_pages()
def get_qos(file, qos_dict):
    i = 1

    #convert to csv to a usable list
    link_list = csv_to_list(file)

    #while not at the end of the list, get QoS information, if available, from a RapidAPI API's page
    while i < len(link_list):
        page_alive = True
        qos_list = ['n/a', 'n/a', 'n/a']

        data = requests.get(link_list[i][1])
        soup = BeautifulSoup(data.text, 'lxml')

        page = soup.find('div', class_='TopRow center-content')

        if page is None:
            page_alive = False
            
        else:
            prodMet = page.find('div', class_ = 'ProductMetrics')
            metrics = prodMet.find_all('div', class_ = 'Metric')
            number = ' '
            for metric in metrics:
                name = metric.find('div', class_= 'Label').text
                name = name[1: len(name)]
                number += metric.find('h2').text
                #print(name)
                #print(number)

                if 'Popularity' in name:
                    qos_list[0] = number
                elif 'Latency' in name:
                    qos_list[1] = number
                elif 'Service' in name:
                    qos_list[2] = number


        #store info in a dictionary
        qos_dict[i - 1] = [i, page_alive, link_list[i][1], qos_list[0], qos_list[1], qos_list[2]]
        #print(qos_dict[i - 1])
        i += 1

#Convert a CSV file to a list
def csv_to_list(file):
    link_list = []

    with codecs.open(file, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        link_list = list(reader)

    return link_list

#given a CSV file in the form of [name, url, category, description, methods], and a dictionary
#scrape the details page of a RapidAPI api for any information regarding a possible SLA
#usually used after scrape_pages()
def get_page_terms(file, dict):
    i = 1

    #convert file to a list
    link_list = csv_to_list(file)

    #while not at the end of our links, check an API's page for a ToU, Product Website, or mention of an SLA
    while i < len(link_list):
        page_alive = True
        sla_list = [False, False, False]
        sla = []
        data = requests.get(link_list[i][1] + '/details')
        soup = BeautifulSoup(data.text, 'lxml')

        #check to see if page is loaded, if not, the link is invalid
        page = soup.find('div', class_='Details')

        if page is None:
            page_alive = False
        else:
            sla = ['', '', '', '', '']
            link = 'n/a'
            Tu = soup.find(text = lambda text: text and 'Terms of use' in text)
            Pw = soup.find(text = lambda text: text and 'Product Website' in text)
            sla[0] = soup.find(text = lambda text: text and ' SLA ' in text)
            sla[1] = soup.find(text = lambda text: text and ' sla ' in text)
            sla[2] = soup.find(text = lambda text: text and ' service level agreement ' in text)
            sla[3] = soup.find(text = lambda text: text and ' Service Level Agreement ' in text)
            sla[4] = soup.find(text = lambda text: text and ' Service level agreement ' in text)

            #if a ToU is found, store that it was
            if Tu is not None:
                sla_list[0] = True
            #if a product website tab is found, get the website and store that we found one
            if Pw is not None:
                sla_list[1] = True
                website = soup.find('a', text='Product Website')
                link = website.get('href')
            #if any possible mention of an SLA is found, store it
            if sla[0] is not None or sla[1] is not None or sla[2] is not None or sla[3] is not None or sla[4] is not None:
                sla_list[2] = True

        #store info in dictionary
        dict[i - 1] = [i, page_alive, link_list[i][1], sla_list[0], sla_list[1], link, sla_list[2]]
        #print(dict[i-1])
        i += 1

#given a CSV file in the form of [name, url, associated website], and a dictionary
#scrape google and store any links that might possibly be related to an SLA agreement for a given API found on RapidAPI
#used after scrape_pages() and get_page_terms() using a csv made by combining info scraped by both these functions
def scrape_google(file, dict):
    i = 1

    #convert file to a list
    search_list = csv_to_list(file)

    #launch driver, the reason we use a driver here is that some google elements dont load
    #unless it detects an actual user
    driver = webdriver.Chrome("C:\chromedriver.exe")

    while i < len(search_list):

        #every 20 elements searched, close driver and reopen, this avoids Bot detection
        if (i % 20 == 0):
            driver.close()
            driver = webdriver.Chrome("C:\chromedriver.exe")

        #search the api name and service level agreement
        search_terms = urllib.parse.quote_plus( search_list[i][0] + ' api service level agreement')
        count = 0
        rel_count = 0
        driver.get('https://google.com/search?q=' + search_terms)
        soup = BeautifulSoup(driver.page_source, 'lxml')
        search = soup.find(id = 'search')
        results = search.find_all(class_ = 'g')
        result_list = ['n/a','n/a','n/a','n/a','n/a']

        #for all results on the first page, store them if they are relevant (up to 10 results)
        for result in results:
            notG = False

            sla = ['', '', '','']
            title = result.find('div', class_ = 'yuRUbf')
            if title is None:
                notG = True
            if notG != True:
                link = title.find('a').get('href')

                #we count it as relevant if the associated wehbsite is included in a search result link
                if search_list[i][2] in link and search_list[i][2] != 'n/a' and count < 10:
                    result_list[count] = link
                    count += 1
                    rel_count += 1

                #otherwise we count it if the api name AND (service level agreement OR terms of use OR terms of service) are included in the result (not including the 'missing' tab)
                else:
                    sla[0]= result.find(text = lambda text: text and 'service level agreement' in text.lower())
                    sla[1] = result.find(text = lambda text: text and 'terms of service' in text.lower())
                    sla[2] = result.find(text = lambda text: text and 'terms of use' in text.lower())
                    sla[3] = result.find(text = lambda text: text and  search_list[i][0].lower() in text.lower())

                    if sla[3] is not None and (sla[0] is not None or sla[1] is not None or sla[2] is not None) and count < 10:

                        missing = result.find('div', class_='IsZvec').find('div', class_='TXwUJf')

                        if missing is None:
                            name = result.find(text = lambda text: text and  search_list[i][0].lower() in text.lower())
                            x = 0
                        else:
                            name = missing.find(text = lambda text: text and  search_list[i][0].lower() in text.lower())
                            missing = missing.find(text = lambda text: text and  'missing' in text.lower())




                        if (name is not None and missing is not None):
                            count += 1
                        else:
                            result_list[count] = link
                            count += 1
                            rel_count +=1
                    else:
                        count += 1


        dict[i-1] = [search_list[i][0], search_list[i][2], search_list[i][1], rel_count, result_list[0], result_list[1], result_list[2], result_list[3], result_list[4], result_list[5], result_list[6], result_list[7], result_list[8], result_list[9]]
        #print(dict[i-1])
        i += 1
