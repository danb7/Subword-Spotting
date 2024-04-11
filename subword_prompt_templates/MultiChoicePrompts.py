import re
from subword_prompt_templates.few_shot_examples import multi_choice_examples


question = '''\
Q: which one of the following words contains a subword of a {category}?
a. {choice1}
b. {choice2}
c. {choice3}
d. {choice4}'''


def generate_zero_shot(category, choice1, choice2, choice3, choice4):
    formated_question = question.format(category=category,
                                        choice1=choice1, 
                                        choice2=choice2, 
                                        choice3=choice3, 
                                        choice4=choice4)
    # replace "a" to "an" if category start with vowels
    return re.sub(r'\ba(?=\s+[aeiou])', 'an', formated_question)


def generate_one_shot(category, choice1, choice2, choice3, choice4):
    return f'''\
### example question ###
{multi_choice_examples.example1[category]}
### actual question ###
{generate_zero_shot(category, choice1, choice2, choice3, choice4)}
A:'''


def generate_few_shot(category, choice1, choice2, choice3, choice4):
    return f'''\
### example question 1 ###
{multi_choice_examples.example1[category]}
### example question 2 ###
{multi_choice_examples.example2[category]}
### example question 3 ###
{multi_choice_examples.example3[category]}
### example question 4 ###
{multi_choice_examples.example4[category]}
### actual question ###
{generate_zero_shot(category, choice1, choice2, choice3, choice4)}
A:'''


def generate_CoT(category, word):
    pass