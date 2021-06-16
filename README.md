# API-Research

**Dependencies:**

page_crawler.py:

_selenium,
pandas,
bs4 (beautiful soup),
codecs,
csv,
requests,
urllib_

_ALSO REQUIRES A CHROMEDRIVER EXECULTIBLE TO BE STORES IN THE C DRIVE_

LDA_clustering.py

_pandas,
gensim,
nltk,
numpy,
os,
yaml,
random,
pickle,
matplotlib.pyplot,
page_crawl (the other .py file in this repository),
seaborn_

_ALSO REQUIRES 'final_rapid.csv', 'config.yaml' FILES and 'data', 'models' FOLDERS
TO BE PRESENT IN PROJECT FOLDER_

**Resources:**

The following resources were used in creating the code for 'LDA_clustering.py':

_https://humboldt-wi.github.io/blog/research/information_systems_1819/is_lda_final/
https://towardsdatascience.com/topic-modeling-and-latent-dirichlet-allocation-in-python-9bf156893c24
https://towardsdatascience.com/lets-build-an-article-recommender-using-lda-f22d71b7143e_

**Misc:**

Files created using page_crawler.py are not included. The 'final_rapid.csv' file was created by running a CSV created by 
the scrape_pages() function, into an SQL server to clean up the data. 
