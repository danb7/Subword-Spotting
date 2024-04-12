import re
from subword_prompt_templates.few_shot_examples import multi_choice_examples


question = '''\
Q: which one of the following words contains a subword of a {category}?
a. {choice1}
b. {choice2}
c. {choice3}
d. {choice4}
A: '''


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
{generate_zero_shot(category, choice1, choice2, choice3, choice4)}'''


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
{generate_zero_shot(category, choice1, choice2, choice3, choice4)}'''


# TODO:
def generate_CoT(category, choice1, choice2, choice3, choice4):
    pass


def generate_decomposite(category, choice1, choice2, choice3, choice4):
    decomposite_question = f'''\
Read the question below and understand what the question is asking for and the criteria for selecting the correct answer. 
Examine each word provided in the options carefully and Break down each word into its component parts or subwords.
Determine if any of the subwords within each word match the name of a {category}. 
Choose the word that contains a subword of a {category} according to the criteria given in the question.
Verify your answer, double-check your selection to ensure it meets all the requirements specified in the question.
{generate_zero_shot(category, choice1, choice2, choice3, choice4)}'''
    
    decomposite_question = re.sub(r'\ba(?=\s+[aeiou])', 'an', decomposite_question)
    return decomposite_question