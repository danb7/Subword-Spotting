from utils import helpers
from subword_prompt_templates import few_shot_examples

class MultiChoicePrompts():
    question = '''\
Subword is a standalone word that exists within a longer word that contains it, and its meaning is arbitrary from the longer word one's.
Question: Which one of the following words contains a subword of a {category}?
    A. {choice1}
    B. {choice2}
    C. {choice3}
    D. {choice4}
Answer: [Your answer here, just the correspond letter, without any explanation or additional text].
'''

    example = question + '{answer}'

    def generate_zero_shot(self, category, choice1, choice2, choice3, choice4):
        formated_question = self.question.format(category=category,
                                            choice1=choice1, 
                                            choice2=choice2, 
                                            choice3=choice3, 
                                            choice4=choice4)
        return helpers.fix_a_an(formated_question) # replace "a" to "an" if category start with vowels


    def generate_one_shot(self, category, choice1, choice2, choice3, choice4, answer=''):
        correct_word = few_shot_examples.positive_examples[category][0][0]
        correspond_subword = few_shot_examples.positive_examples[category][0][1]
        correct_position = 3
        choices =  few_shot_examples.negative_examples[category][:3]
        choices.insert(correct_position-1, correct_word)
        if answer:
            answer = answer.format(correct_word=correct_word,
                                correct_subword=correspond_subword,
                                category=category)
        else:
            answer = correct_word
        one_shot_question = f'''\
    ### example question ###
    {self.example.format(category=category,
                    choice1=choices[0],
                    choice2=choices[1],
                    choice3=choices[2],
                    choice4=choices[3],
                    answer=answer)}

    ### actual question ###
    {self.generate_zero_shot(category, choice1, choice2, choice3, choice4)}'''
        
        return helpers.fix_a_an(one_shot_question)


    def generate_few_shot(self, category, choice1, choice2, choice3, choice4, answer='', shots=4):
        few_shot_question = ''
        correct_words = few_shot_examples.positive_examples[category]
        if answer:
            answers = [answer.format(correct_word=correct_words[i][0],
                                correct_subword=correct_words[i][1],
                                category=category) for i in range(shots)]
        else:
            answers = [correct_words[i][0] for i in range(shots)]
        for i in range(shots):
            choices = few_shot_examples.negative_examples[category][i*3:i*3+3]
            choices.insert(i%4, correct_words[i][0])
            few_shot_question += f'### example question {i+1} ###\n'
            few_shot_question += self.example.format(category=category,
                                                choice1=choices[0],
                                                choice2=choices[1],
                                                choice3=choices[2],
                                                choice4=choices[3],
                                                answer=answers[i]) + '\n'*2
        few_shot_question += '### actual question ###\n' 
        few_shot_question += self.generate_zero_shot(category, choice1, choice2, choice3, choice4)

        return helpers.fix_a_an(few_shot_question)


    def generate_CoT(self, category, choice1, choice2, choice3, choice4, shot='one'):
        cot_answer = '''Since the word {correct_word} contains the subword \
    {correct_subword}, which is a {category}, the correct answer is {correct_word}'''
        if shot == 'one':
            cot_question = self.generate_one_shot(category, choice1, choice2, choice3, choice4, cot_answer)
        elif shot == 'few':
            cot_question = self.generate_few_shot(category, choice1, choice2, choice3, choice4, cot_answer)
        else:
            raise Exception("Not valid 'shot' parameter. Need to be 'one' or 'few'")
        
        return helpers.fix_a_an(cot_question)


    def generate_decomposite(self, category, choice1, choice2, choice3, choice4):
        decomposite_question = f'''\
    Read the question below and understand what the question is asking for and the criteria for selecting the correct answer. 
    Examine each word provided in the options carefully and Break down each word into its component parts or subwords.
    Determine if any of the subwords within each word match the name of a {category}. 
    Choose the word that contains a subword of a {category} according to the criteria given in the question.
    Verify your answer, double-check your selection to ensure it meets all the requirements specified in the question.
    {self.generate_zero_shot(category, choice1, choice2, choice3, choice4)}'''
        
        return helpers.fix_a_an(decomposite_question)