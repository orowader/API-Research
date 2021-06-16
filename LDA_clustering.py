"""
Collection of functions used by Owen Rowader to transform data scraped from RapidAPI
into a functioning LDA model that is able to recommend
similar APIs based on a user query 

The libraries used can be seen below
"""

import pandas as pd 
import gensim 
from gensim import models, similarities
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer
from nltk.stem.porter import *
import numpy as np
import os
import yaml 
import random
import pickle   
import matplotlib.pyplot as plt
import page_crawl as pc
import seaborn as sns
np.random.seed(2018)
import nltk
nltk.download('wordnet')


#needed to change the 'final_rapid.csv' into a file where the
#API's are indexed and their descriptions and methods are contained in one entry
def format_data():
    new_dict = {} 
    headers = ['index', 'api_name', 'api_url', 'api_category', 'api_desc + api_methods']

    #store final rapid as a list 
    initial_list = pc.csv_to_list('final_rapid.csv') 
    i = 1

    #create dictionary in the format we want
    while i < len(initial_list):
        new_cat = initial_list[i][3] + " " + initial_list[i][4] 
        new_dict[i-1] = [i-1, initial_list[i][0], initial_list[i][1], initial_list[i][2], new_cat]
        print(new_dict[i-1])
        i +=1
    
    #write formatted csv
    pc.write_to_csv(new_dict, headers, 'LDA_formatted_apis.csv')

#Function taken from: https://github.com/susanli2016/NLP-with-Python/blob/master/LDA_news_headlines.ipynb
#reduces words to their root form ex. tracking ---> track
def lemmatize_stemming(text):
    stemmer =SnowballStemmer('english')
    return stemmer.stem(WordNetLemmatizer().lemmatize(text, pos='v'))

#Function taken from: https://github.com/susanli2016/NLP-with-Python/blob/master/LDA_news_headlines.ipynb
#performs tokenization on text, removes stopwords, lemmatizes text, and removes words with 
#fewer than 3 characters 
def preprocess(text):
    result = []
    for token in gensim.utils.simple_preprocess(text):
        if token not in gensim.parsing.preprocessing.STOPWORDS and len(token) > 3:
            result.append(lemmatize_stemming(token))
    return result

#Function taken from: https://humboldt-wi.github.io/blog/research/information_systems_1819/is_lda_final/
#computes jaccard similarity between topics
# ***A statistic used for comparing the similarity and diversity of sample sets.
# ***J(A,B) = (A ∩ B)/(A U B)
# ***Goal is low Jaccard scores for coverage of the diverse elements
def jaccard_similarity(query, document):
    intersection = set(query).intersection(set(document))
    union = set(query).union(set(document))
    return float(len(intersection))/float(len(union))

#Function taken from: https://towardsdatascience.com/lets-build-an-article-recommender-using-lda-f22d71b7143e
#caculates a similarity matrix between a given query and our LDA model 
def get_similarity(lda, corpus, query_vector):
        index = similarities.MatrixSimilarity(lda[corpus])
        sims = index[query_vector]
        return sims

#Function taken from: https://towardsdatascience.com/lets-build-an-article-recommender-using-lda-f22d71b7143e
#Loads the dictionary and corpus created by the create_dict_corpus() function
def load_dict_corp():
    with open('config.yml') as fp:
        config = yaml.load(fp, Loader = yaml.FullLoader)
    fp.close()

    DICTIONARY_PATH = config['paths']['dictionary']
    CORPUS_PATH = config['paths']['corpus']

    with open(DICTIONARY_PATH, 'rb') as fp:
        dictionary = pickle.load(fp)
        fp.close()
    with open(CORPUS_PATH, 'rb') as fp:
        bow_corpus = pickle.load(fp)
        fp.close()

    return dictionary, bow_corpus

#Dictionary and Corpus loading/saving methods taken from: https://towardsdatascience.com/lets-build-an-article-recommender-using-lda-f22d71b7143e
#data formatting/pre-processing and dictionary/corpus creation taken from: https://towardsdatascience.com/topic-modeling-and-latent-dirichlet-allocation-in-python-9bf156893c24
#Creates a dictionary and corpus from the previouslly formatted API file.
def create_dict_corpus():

    #load the config file, tells where we're storing our dictionary and corpus path
    with open('config.yml') as fp:
        config = yaml.load(fp, Loader = yaml.FullLoader)
    fp.close()

    DICTIONARY_PATH = config['paths']['dictionary']
    CORPUS_PATH = config['paths']['corpus']

    #load the table into a list that stores the desc/methods and indexes
    data = pd.read_csv('LDA_formatted_apis.csv', error_bad_lines=False)
    data_text = data[['api_desc + api_methods']]
    data_text['index'] = data_text.index
    documents = data_text

    #pre-process the docs
    processed_docs = documents['api_desc + api_methods'].map(preprocess)

    #generate a bag of words on the data 
    dictionary = gensim.corpora.Dictionary(processed_docs)

    #Filter out tokens that appear in
    # ***less than 15 documents (absolute number) or
    # ***more than 0.5 documents (fraction of total corpus size, not absolute number).
    # ***after the above two steps, keep only the first 100000 most frequent tokens.
    dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)

    #generare corpus
    bow_corpus = [dictionary.doc2bow(doc) for doc in processed_docs]

    #save the dictionary and corpus 
    with open(DICTIONARY_PATH, 'wb') as fp:
        pickle.dump(dictionary, fp)
    fp.close()
    with open(CORPUS_PATH, 'wb') as fp:
        pickle.dump(bow_corpus, fp)
    fp.close()

#Methods used in function taken from: https://humboldt-wi.github.io/blog/research/information_systems_1819/is_lda_final/
#Using the dictionary and corpus generated in create_dict_corpus() we now generate multiple LDA 
#models and store their info in the models folder.
#
#We then run a test using jaccard similarity between the topics in the models, and plot the data
#Models with the lower jaccard score are usually better 
def optimal_lda_config():
    project_folder = os.getcwd()

    dictionary, bow_corpus = load_dict_corp() 

    #LDA will be generated with these numbers of topics 
    topicnums = [ 60, 70, 80, 85,  90, 95, 100, 105, 110]

    #generate and save models 
    #For the upcoming LDA model, we'll need to understand the following:
    #
    #num_topics: number of requested latent topics to be extracted from the training corpus.
    #passes: number of passes through the corpus during training.
    #update_every: number of documents to be iterated through for each update. 1 = iterative learning.
    #random state is 42, like in the article 
    ldamodels_bow = {}
    for i in topicnums:
        random.seed(42)
        if not os.path.exists(project_folder+'/models/ldamodels_bow_'+str(i)+'.lda'):
            ldamodels_bow[i] = models.LdaModel(bow_corpus, num_topics=i, random_state=42, update_every=1, passes=10, id2word=dictionary)
            ldamodels_bow[i].save(project_folder+'/models/ldamodels_bow_'+str(i)+'.lda')
            print('ldamodels_bow_{}.lda created.'.format(i))
        else: 
            print('ldamodels_bow_{}.lda already exists.'.format(i))

    lda_topics = {}
    for i in topicnums:
        lda_model = models.LdaModel.load(project_folder+'/models/ldamodels_bow_'+str(i)+'.lda')
        lda_topics_string = lda_model.show_topics(i)
        lda_topics[i] = ["".join([c if c.isalpha() else " " for c in topic[1]]).split() for topic in lda_topics_string]

    pickle.dump(lda_topics,open(project_folder+'/models/pub_lda_bow_topics.pkl','wb'))


    #generate similairties across ropics at each topic # level
    lda_stability = {}
    for i in range(0,len(topicnums)-1):
        jacc_sims = []
        for t1,topic1 in enumerate(lda_topics[topicnums[i]]):
            sims = []
            for t2,topic2 in enumerate(lda_topics[topicnums[i+1]]):
                sims.append(jaccard_similarity(topic1,topic2))    
            jacc_sims.append(sims)    
        lda_stability[topicnums[i]] = jacc_sims
    
    pickle.dump(lda_stability,open(project_folder+'/models/pub_lda_bow_stability.pkl','wb'))

    #plot to find eblow point and decide optimal # of topics
    lda_stability = pickle.load(open(project_folder+'/models/pub_lda_bow_stability.pkl','rb'))
    mean_stability = [np.array(lda_stability[i]).mean() for i in topicnums[:-1]]

    with sns.axes_style("darkgrid"):
        x = topicnums[:-1]
        y = mean_stability
        plt.figure(figsize=(20,10))
        plt.plot(x,y,label='Average Overlap Between Topics')
        plt.xlim([40, 130])
        plt.ylim([0, 0.25])
        plt.xlabel('Number of topics')
        plt.ylabel('Average Jaccard similarity')   
        plt.title('Average Jaccard Similarity Between Topics')
        plt.legend()    
        plt.show()


#Methods used in function taken from: https://towardsdatascience.com/lets-build-an-article-recommender-using-lda-f22d71b7143e
#Given a valid # of topics, it loads the LDA generated from that # earlier in optimal_lda_config()
#The user is then able to run a query against that model, and get a number of similar APIs based on that query 
def recommender(num_topics):
    project_folder = os.getcwd()

    #used to get API anmes after recommender generates indexes
    api_list = [] 
    api_list = pc.csv_to_list('final_rapid.csv') 

    #load info needed 
    dictionary, bow_corpus = load_dict_corp() 
    lda_model_final = models.LdaModel.load(project_folder +'/models/ldamodels_bow_'+str(num_topics)+'.lda')

    
    while True: 
        search_arg = input('\n\nPlease enter your search terms: ')

        #Pre-process query same way we did the original data 
        search_arg = preprocess(search_arg) 

        #create a bow from query 
        words = dictionary.doc2bow(search_arg)

        #show top identified words 
        print("\n\n Top words identified: ")
        for word in words:
            print("{} {}".format(word[0], dictionary[word[0]]))

        #generate a query vector using the words
        #then generate a similiarity matrix from the LDA and corpus
        #then display in descending order from most similar 
        query_vector = lda_model_final[words]
        sims = get_similarity(lda_model_final, bow_corpus, query_vector)
        sims = sorted(enumerate(sims), key=lambda item: -item[1])

        #display results
        idx = 0
        result = 20
        print("\nCheck out the links below:")
        while result > 0:
            pageid = 0
            print(api_list[sims[idx][0] + 1][0])
            result -= 1
            idx += 1


#If this is the first time running this program, run these functions first
#Otherwise, keep them commented out and just run the recommender 
"""
format_data()

load_dict_corp()

optimal_lda_config()
"""

recommender(100)
