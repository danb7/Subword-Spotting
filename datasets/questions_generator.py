import nltk
from nltk.corpus import brown, stopwords
from nltk.stem import WordNetLemmatizer
import pandas as pd
from collections import Counter
import numpy as np 
import sys
import inspect
import os
import re
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir) 
from subword_prompt_templates import MultiChoicePrompts, ClassificationPrompts
from openai import OpenAI
import gensim.downloader as dl
#word2vec_model = dl.load("word2vec-google-news-300")

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
        print(row['Word'])
        my_categories_subwords = raw_dataset_df[raw_dataset_df['Category'] == row['Category']]
        other_categories_words = corpus_word_freq_df[~corpus_word_freq_df.index.isin(my_categories_subwords['Word'])]
        other_categories_words = other_categories_words[~other_categories_words.index.isin(my_categories_subwords['Subword'])]
        #Get only the P first most freq words and those with length greater than 5
        other_categories_words = other_categories_words[other_categories_words.index.str.len() >= 5]
        other_categories_words = other_categories_words[:p_most_freq]
        for corpus_index, corpus_row in other_categories_words.iterrows():
            if (word2_vec_vocab.get(row['Subword']) and word2_vec_vocab.get(corpus_row.name)):
                other_categories_words.loc[corpus_index, 'Subword_Similiarity'] = abs(word2vec_model.similarity(row['Subword'], corpus_row.name))
            else:
                other_categories_words.loc[corpus_index, 'Subword_Similiarity'] = 0
        
        #Remove similiarty below 0.2
        other_categories_words = other_categories_words[(other_categories_words['Subword_Similiarity'] >= 0.1) & (other_categories_words['Subword_Similiarity'] <= 0.6)]
        other_categories_words.loc[:,'Weights'] = other_categories_words['Word_freq'] / other_categories_words['Word_freq'].sum()
        
        selected_wrong_words = np.random.choice(other_categories_words[:p_most_freq].index, size=K, replace=False, p=other_categories_words['Weights'])
        #selected_wrong_words = np.random.choice(other_categories_words[:p_most_freq].index, size=K, replace=False)
        random_answers_per_word.append((row['Category'], row['Subword'], row['Word'], selected_wrong_words))

    return random_answers_per_word

def generate_evaluation_set():
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

def create_Prompts():
    multiChoicePrompts = MultiChoicePrompts.MultiChoicePrompts()
    classificationPrompts = ClassificationPrompts.ClassificationPrompts()
    multiple_choice_answers_dict = {
        1: 'A',
        2: 'B',
        3: 'C',
        4: 'D'
    }
    dataset_for_evaluation_df = pd.read_csv("datasets\\dataset_for_evaluation.csv")
    cnt = 0
    prompts = []
    prompts_options = ['generate_zero_shot', 'generate_one_shot', 'generate_few_shot', 'generate_CoT', 'generate_decomposite']
    for index, row in dataset_for_evaluation_df.iterrows():
        mulitple_options_list = row['Mulitple_Options'].strip("[]").replace("'","").split(" ") # json
        #Create choices for multiple choices
        multiple_choices = mulitple_options_list
        multiple_choices.insert(cnt%4, row['Word'])
        #Create choice for classification
        classification_choices = []
        classification_choices.append(('Yes', row['Word']))
        classification_choices.append(('No', np.random.choice(mulitple_options_list)))
        for prompt_option in prompts_options:
            #Get multiple choice prompts
            multi_methods = getattr(multiChoicePrompts, prompt_option)
            #Prompts contains:
            # the prompt type, prompt options: few, one, zero shots/ cot, the letter or Yes/No of the correct answer, the correct word, prompt
            prompts.append((prompts_Types["Multiple"], 
                            prompt_option, 
                            multiple_choice_answers_dict[cnt%4 + 1], 
                            row['Word'], 
                            multi_methods(category=row['Category'],
                                choice1=multiple_choices[0],
                                choice2=multiple_choices[1],
                                choice3=multiple_choices[2],
                                choice4=multiple_choices[3]
                            )
            ))
            #Get classification choice prompts
            for choice in classification_choices:
                classification_methods = getattr(classificationPrompts, prompt_option)
                prompts.append((prompts_Types["Classification"],
                                prompt_option, choice[0], 
                                row['Word'], 
                                classification_methods(category=row['Category'],
                                    word=choice[1]
                                )
                ))
                
        cnt += 1
    
    return prompts

def response_Eval(prompt_type, choice_key, response):
    if prompt_type == prompts_Types["Multiple"]:
        match = re.search(r'(?:[A-D]\.|[A-D]\)|\[[A-D]\])', response) # TODO: generalize to all caps ABCD
    elif prompt_type == prompts_Types["Classification"]:
        match = re.search(r'\b(?:Yes|No)\b', response)

    if match:
        return match.group(0).strip(".") == choice_key # TODO: genralize this also
    else:
        print("a")

prompts_Types = {
    "Multiple": "Multiple choice",
    "Classification": "Classification prompt"
}
response_list = []
prompts = create_Prompts()
TOGETHER_API_KEY = os.environ.get("TOGETHER_API_KEY")
client = OpenAI(
  api_key=TOGETHER_API_KEY,
  base_url='https://api.together.xyz/v1',
)
for prompt_type, prompt_structure, choice_key, word, prompt in prompts:
    chat_completion = client.chat.completions.create(
    messages=[
        {
        "role": "user",
        "content": f"{prompt}",
        }
    ],
    # model="MISTRALAI/MIXTRAL-8X7B-INSTRUCT-V0.1",
    model = "MISTRALAI/MISTRAL-7B-INSTRUCT-V0.2",
    temperature = 0,
    max_tokens = 20
    )
    response = chat_completion.choices[0].message.content
    llm_response_eval = response_Eval(prompt_type, choice_key, response)
    response_list.append((prompt_type, prompt_structure, llm_response_eval, choice_key, word, prompt, response))


pd.DataFrame(response_list, columns=["Prompt Type", "Structure", "Evaluation", "Correct Answer", "Word", "Prompt", "Response"]).to_csv("response_list.csv")