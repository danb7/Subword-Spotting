import nltk
from nltk.corpus import brown, stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd
from collections import Counter
import numpy as np 
import sys
import inspect
import os
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from subword_prompt_templates import MultiChoicePrompts, ClassificationPrompts
from openai import OpenAI
import gensim.downloader as dl
word2vec_model = dl.load("word2vec-google-news-300")

# Function to lemmatize words
def lemmatize_word(word, stop_words):
    if not all(char.isalpha() for char in word) or (word in stop_words):
        # Return the word unchanged if it contains digits
        return None
    
    return lemmatizer.lemmatize(word)

def read_categories_files():
    item_types = ['animal', 'body_part', 'vehicle_list', 'color', 'food', 'fruit', 'musical']
    types_dict = {}
    for item_type in item_types:
        with open(f'categories_word_list\\{item_type}_list.txt', 'r') as file:
            file_contents = [line.strip().lower() for line in file.readlines()]

        types_dict[item_type] = file_contents

    return types_dict

def get_subwords_per_item(word2vec_model, types_dict, corpus_base_word, words_freq):
    subwords_list_tuple = [] 
    word2_vec_vocab = word2vec_model.vocab
    for word in corpus_base_word:
        for item_category, items in types_dict.items():
            for sub_word in items:
                if (sub_word in word) and (not sub_word == word) and (word2_vec_vocab.get(sub_word) and word2_vec_vocab.get(word)) and\
                    (words_freq[sub_word] != 0 and words_freq[word] != 0):
                    subwords_list_tuple.append((word2vec_model.similarity(sub_word, word), item_category, sub_word, words_freq[sub_word], word, words_freq[word]))  
    
    return subwords_list_tuple

def generate_random_questions(word2vec_model, evaluation_dataset_df, raw_dataset_df, corpus_word_freq_df, K=3):
    random_answers_per_word = []
    word2_vec_vocab = word2vec_model.vocab
    corpus_word_freq_df = corpus_word_freq_df.sort_values(by='Word_freq', ascending=False)
    p_most_freq = 1000
    for _, row in evaluation_dataset_df.iterrows():
        for _, corpus_row in corpus_word_freq_df.iterrows():
            if (word2_vec_vocab.get(row['Subword']) and word2_vec_vocab.get(corpus_row['Word'])):
                corpus_word_freq_df['Subword_Similiarity'] = word2vec_model.similarity(row['Subword'], corpus_row['Word'])
            else:
                corpus_word_freq_df['Subword_Similiarity']

        my_categories_subwords = raw_dataset_df[raw_dataset_df['Category'] == row['Category']]
        other_categories_words = corpus_word_freq_df[~corpus_word_freq_df.index.isin(my_categories_subwords['Word'])]
        other_categories_words = other_categories_words[~other_categories_words.index.isin(my_categories_subwords['Subword'])]
        other_categories_words.loc[:,'Weights'] = other_categories_words['Word_freq'] / other_categories_words['Word_freq'].sum()
        #Get only the P first most freq words and those with length greater than 3
        other_categories_words = other_categories_words[:p_most_freq]
        other_categories_words = other_categories_words[other_categories_words.index.str.len() >= 5]
        selected_wrong_words = np.random.choice(other_categories_words[:p_most_freq].index, size=K, replace=False)
        random_answers_per_word.append((row['Category'], row['Subword'], row['Word'], selected_wrong_words))

    return random_answers_per_word

# Download brown corpus
# nltk.download('brown')
# nltk.download('wordnet')
# nltk.download('stopwords')
lemmatizer = WordNetLemmatizer()
# Get all words from the Brown corpus
stop_words = set(stopwords.words('english'))
brown_words = brown.words()
brown_words = list(lemmatize_word(word.lower(), stop_words) for word in brown_words if lemmatize_word(word.lower(), stop_words) is not None)
# Lemmatize each word and keep only the base form
base_words = set(brown_words)
corpus_base_word = list(base_words)
corpus_word_freq = Counter(brown_words)
corpus_word_freq_df = pd.DataFrame(corpus_word_freq.values(), corpus_word_freq.keys(), columns=["Word_freq"])
evaluation_dataset_df = pd.read_csv("datasets\\dataset_for_evaluation.csv")
raw_dataset_df = pd.read_csv("datasets\\raw_dataset.csv")
random_answers_per_word = generate_random_questions(word2vec_model, evaluation_dataset_df, raw_dataset_df, corpus_word_freq_df)
random_answers_per_word_df = pd.DataFrame(random_answers_per_word, columns=["Category", "Subword", "Word", "Mulitple_Options"])
random_answers_per_word_df.to_csv("datasets\\dataset_for_evaluation_multiple_options.csv")

TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
client = OpenAI(
  api_key=TOGETHER_API_KEY,
  base_url='https://api.together.xyz/v1',
)
cnt = 1
response_list = []
for question in random_answers_per_word:
    choices = list(question[3])
    choices.insert(cnt%2, question[2])
    # prompt = ClassificationPrompts.generate_zero_shot(category=question[0],
    #                                         word=question[2])
    prompt = MultiChoicePrompts.generate_zero_shot(category=question[0],
                                                choice1=choices[0],
                                                choice2=choices[1],
                                                choice3=choices[2],
                                                choice4=choices[3])
    #print(f"The answer is: {question[2]}. Please provide a single-word answer from the following options. {prompt}")
    chat_completion = client.chat.completions.create(
    messages=[
        {
        "role": "user",
        #"content": f"Answer with \"Yes\" or \"No\" only, without explanations. {prompt}",
        "content": f"{prompt}",
        }
    ],
    model="MISTRALAI/MIXTRAL-8X7B-INSTRUCT-V0.1",
    temperature = 0
    )
    response_list.append((prompt, chat_completion.choices[0].message.content))

pd.DataFrame(response_list).to_csv("response_list_llama.csv")