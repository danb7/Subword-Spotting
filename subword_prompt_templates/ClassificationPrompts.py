import re
from subword_prompt_templates.few_shot_examples import classification_examples


question = '''\
Q: Does the word {word} contains a subword of a {category}?
A: '''


def generate_zero_shot(category, word):
    formated_question = question.format(category=category,
                                        word=word)
    # replace "a" to "an" if category start with vowels
    return re.sub(r'\ba(?=\s+[aeiou])', 'an', formated_question)


def generate_one_shot(category, word, positive_answer='Yes'):
    return f'''\
### example question ###
{classification_examples.example1[category].format(positive_answer=positive_answer)}
### actual question ###
{generate_zero_shot(category, word)}'''


def generate_few_shot(category, word, positive_answer='Yes', negative_answer='No'):
    return f'''\
### example question 1 ###
{classification_examples.example1[category].format(positive_answer=positive_answer)}
### example question 2 ###
{classification_examples.example2[category].format(negative_answer=negative_answer)}
### example question 3 ###
{classification_examples.example3[category].format(positive_answer=positive_answer)}
### example question 4 ###
{classification_examples.example4[category].format(negative_answer=negative_answer)}
### actual question ###
{generate_zero_shot(category, word)}'''


def generate_CoT(category, word, shot='one'):
    # need to handle "the word" should be the example one
    positive_answer = f'''Since the word contains a subword of \
a {category}, the correct answer is Yes'''
    negative_answer = f'''Since the word doesnt contains any subword \
of a {category}, the correct answer is No'''
    
    positive_answer = re.sub(r'\ba(?=\s+[aeiou])', 'an', positive_answer)
    negative_answer= re.sub(r'\ba(?=\s+[aeiou])', 'an', negative_answer)

    if shot == 'one':
        cot_question = generate_one_shot(category, word, positive_answer)
    elif shot == 'few':
        cot_question = generate_few_shot(category, word, positive_answer, negative_answer)
    else:
        raise Exception("Not valid 'shot' parameter. Need to be 'one' or 'few'")
    
    return cot_question

def generate_decomposite(category, word):
    decomposite_question = f'''\
Read the question below and understand what the question is asking for and the criteria for determine the correct answer. 
Examine the word provided in the question carefully and Break it down into its component parts or subwords.
Determine if any of the subwords within the word match the name of a {category}. 
Answer with "Yes" or "No" only, without explanations.
Verify your answer, double-check your classification to ensure it meets all the requirements specified in the question.
{generate_zero_shot(category, word)}'''
    
    decomposite_question = re.sub(r'\ba(?=\s+[aeiou])', 'an', decomposite_question)
    return decomposite_question
