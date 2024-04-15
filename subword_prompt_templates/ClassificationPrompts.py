from utils import helpers
from subword_prompt_templates import few_shot_examples


question = '''\
Q: Does the word {word} contains a subword of a {category}?
A: '''

example = question + '{answer}'


def generate_zero_shot(category, word):
    formated_question = question.format(category=category,
                                        word=word)
    return helpers.fix_a_an(formated_question) # replace "a" to "an" if category start with vowels


def generate_one_shot(category, word, positive_answer='Yes'):
    example_word = few_shot_examples.positive_examples[category][0][0]
    correspond_subword = few_shot_examples.positive_examples[category][0][1]
    one_shot_question =  f'''\
### example question ###
{example.format(category=category, 
                word=example_word, 
                answer=positive_answer.format(example_word=example_word, 
                                              example_subword=correspond_subword,
                                              category=category))}

### actual question ###
{generate_zero_shot(category, word)}'''
    
    return helpers.fix_a_an(one_shot_question)


def generate_few_shot(category, word, positive_answer='Yes', negative_answer='No', shots=4):
    few_shot_question = ''
    positive_examples = few_shot_examples.positive_examples[category]
    negative_examples = few_shot_examples.negative_examples[category]
    if shots/2 > len(positive_examples): raise Exception(f'too large shots. maximum is {shots}')
    for i in range(int(shots/2)):
        # positive example
        few_shot_question += f'### example question {i*2+1} ###\n'
        few_shot_question += example.format(category=category, 
                                            word=positive_examples[i][0], 
                                            answer=positive_answer.format(example_word=positive_examples[i][0],
                                                                          example_subword=positive_examples[i][1],
                                                                          category=category)) + '\n'*2
        # negative example
        few_shot_question += f'### example question {i*2+2} ###\n'
        few_shot_question += example.format(category=category,
                                            word=negative_examples[i], 
                                            answer=negative_answer.format(example_word=negative_examples[i],
                                                                          category=category)) + '\n'*2
    
    few_shot_question += '### actual question ###\n' 
    few_shot_question += generate_zero_shot(category, word)
    
    return helpers.fix_a_an(few_shot_question)


def generate_CoT(category, word, shot='one'):
    positive_answer = '''Since the word {example_word} contains the subword \
{example_subword}, which is a {category}, the correct answer is Yes'''
    negative_answer = '''Since the word {example_word} doesnt contains any subword \
of a {category}, the correct answer is No'''

    if shot == 'one':
        cot_question = generate_one_shot(category, word, positive_answer)
    elif shot == 'few':
        cot_question = generate_few_shot(category, word, positive_answer, negative_answer)
    else:
        raise Exception("Not valid 'shot' parameter. Need to be 'one' or 'few'")
    
    return helpers.fix_a_an(cot_question)

def generate_decomposite(category, word):
    decomposite_question = f'''\
Read the question below and understand what the question is asking for and the criteria for determine the correct answer. 
Examine the word provided in the question carefully and Break it down into its component parts or subwords.
Determine if any of the subwords within the word match the name of a {category}. 
Answer with "Yes" or "No" only, without explanations.
Verify your answer, double-check your classification to ensure it meets all the requirements specified in the question.
{generate_zero_shot(category, word)}'''
    
    return helpers.fix_a_an(decomposite_question)