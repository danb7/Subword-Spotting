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

def generate_random_questions(selection_base_df, corpus_word_freq_df):
    #selection_filtered_df = selection_base_df[(selection_base_df['Similarity'] <= 0.3) & (selection_base_df['Word_freq'] >= 10)]
    filtered_df = selection_base_df[(selection_base_df['Similarity'] < 0.1) &
                                    (selection_base_df['Word'].str.len() - 2 >= selection_base_df['Subword'].str.len())]
    selection_filtered_df = filtered_df.loc[filtered_df.groupby('Subword')['Word_freq'].idxmax()]
    grouped = selection_filtered_df.groupby('Category')
    random_questions = []
    for category, group in grouped:
        # Randomly select 10 "Subword" entries weighted by "Subword_freq"
        categories_subwords_distinct = group.drop_duplicates(subset=['Subword'])
        choices_size = 5 if len(categories_subwords_distinct) >= 5 else len(categories_subwords_distinct)
        selected_subwords = np.random.choice(categories_subwords_distinct['Subword'],
                                            size=choices_size,
                                            replace=False,
                                            p = categories_subwords_distinct['Subword_freq'] / categories_subwords_distinct['Subword_freq'].sum()
                                        )
        my_categories = selection_filtered_df[selection_filtered_df['Category'] == category]
        other_categories = corpus_word_freq_df[~corpus_word_freq_df.index.isin(selection_base_df[selection_base_df['Category'] == category]['Word'])]
        other_categories = other_categories[~other_categories.index.isin(selection_base_df[selection_base_df['Category'] == category]['Subword'])]
        # Iterate over each selected "Subword"
        for subword in selected_subwords:
            #other_categories = selection_base_df[selection_base_df['Category'] != category]
            category_words = my_categories[my_categories['Subword'].isin([subword])]
            other_categories_weights = other_categories['Word_freq'] / other_categories['Word_freq'].sum()
            catergory_words_weights = category_words['Word_freq'] / category_words['Word_freq'].sum()
            # Randomly select 3 "Word" entries weighted by "Word_freq" from other categories
            selected_wrong_words = np.random.choice(other_categories.index, size=3, replace=False, p=other_categories_weights)
            # Randomly select 1 "Word" entries weighted by "Word_freq" from my category
            selected_correct_words = np.random.choice(category_words['Word'], size=1, replace=False, p=catergory_words_weights)
            # Create a DataFrame with the selected "Subword" and "Word" entries
            random_questions.append((category, subword, selected_correct_words[0], selected_wrong_words))

    return random_questions

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
selection_base_df = pd.read_csv("datasets\\dataset.csv")
random_questions = generate_random_questions(selection_base_df, corpus_word_freq_df)

TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
client = OpenAI(
  api_key=TOGETHER_API_KEY,
  base_url='https://api.together.xyz/v1',
)
cnt = 1
response_list = []
# prompt = ClassificationPrompts.generate_zero_shot(category='animal',
#                                              word='want')
# chat_completion = client.chat.completions.create(
# messages=[
#     {
#     "role": "user",
#     #"content": f"Answer with \"Yes\" or \"No\" only, without explanations. {prompt}",
#     "content": f"{prompt}",
#     }
# ],
# model="MISTRALAI/MISTRAL-7B-INSTRUCT-V0.2",
# temperature = 0
# )
# print(prompt, chat_completion.choices[0].message.content)

for question in random_questions:
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