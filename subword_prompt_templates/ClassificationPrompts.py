import re
from subword_prompt_templates.few_shot_examples import classification_examples


question = '''\
Q: Does the word {word} contains a subword of a {category}?'''


def generate_zero_shot(category, word):
    formated_question = question.format(category=category,
                                        word=word)
    # replace "a" to "an" if category start with vowels
    return re.sub(r'\ba(?=\s+[aeiou])', 'an', formated_question)


def generate_one_shot(category, word):
    return f'''\
### example question ###
{classification_examples.example1[category]}
### actual question ###
{generate_zero_shot(category, word)}
A:'''


def generate_few_shot(category, word):
    return f'''\
### example question 1 ###
{classification_examples.example1[category]}
### example question 2 ###
{classification_examples.example2[category]}
### example question 3 ###
{classification_examples.example3[category]}
### example question 4 ###
{classification_examples.example4[category]}
### actual question ###
{generate_zero_shot(category, word)}
A:'''


def generate_CoT(category, word):
    pass
 