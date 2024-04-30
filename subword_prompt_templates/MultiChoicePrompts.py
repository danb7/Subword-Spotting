import random
from utils import helpers
from subword_prompt_templates import few_shot_examples

class MultiChoicePrompts():
    def __init__(self, question='''\
Subword is a standalone word that exists within a longer word that contains it, and its meaning is arbitrary from the longer word one's.
Question: Which one of the following words contains a subword of a {category}?
    A. {choice1}
    B. {choice2}
    C. {choice3}
    D. {choice4}
Answer: ''',
answer_aid='''[Your answer here, just the correspond letter and the word, without any explanation or additional text]'''):
        self.question = question
        self.example = self.question + '{answer}'
        self.answer_aid = answer_aid


    def generate(self, technique, category, choice1, choice2, choice3, choice4, **kwargs):
        if technique=='zero_shot':
            prompts = self._generate_zero_shot(category, choice1, choice2, choice3, choice4, direct=True, **kwargs)
        
        elif technique=='one_shot':
            prompts = self._generate_one_shot(category, choice1, choice2, choice3, choice4, **kwargs)

        elif technique=='few_shot':
            prompts = self._generate_few_shot(category, choice1, choice2, choice3, choice4, **kwargs)

        elif technique.lower()=='cot':
            prompts = self._generate_CoT(category, choice1, choice2, choice3, choice4, **kwargs)

        elif technique=='decomposite':
            prompts = self._generate_decomposite(category, choice1, choice2, choice3, choice4, **kwargs)
            
        else:
            raise Exception("technique must be one of ['zero_shot', 'one_shot', 'few_shot', 'cot', 'decomposite']")
        
        return prompts
        

    def _generate_zero_shot(self, category, choice1, choice2, choice3, choice4, ans_aid=True, direct=False):
        formated_question = self.question.format(category=category,
                                                 choice1=choice1, 
                                                 choice2=choice2, 
                                                 choice3=choice3, 
                                                 choice4=choice4)
        if direct:
            direct_instruct = 'Start your response with the correct letter and the correspond word. In case of doubt, answer according to the most probable answer.'
            last_index = formated_question.rfind('Answer')
            formated_question = formated_question[:last_index] + direct_instruct + '\n' + formated_question[last_index:]
        if ans_aid:
            formated_question += self.answer_aid
        return helpers.fix_a_an(formated_question) # replace "a" to "an" if category start with vowels


    def _generate_one_shot(self, category, choice1, choice2, choice3, choice4, answer=''):
        correct_word = few_shot_examples.positive_examples[category][0][0]
        correspond_subword = few_shot_examples.positive_examples[category][0][1]
        correct_position = random.randint(1, 4)
        correct_choice_letter = str(correct_position).translate(str.maketrans("1234", "ABCD"))
        choices = few_shot_examples.negative_examples[category][:3]
        choices.insert(correct_position-1, correct_word)
        if answer:
            answer = answer.format(correct_choice=correct_choice_letter,
                                   correct_word=correct_word,
                                   correct_subword=correspond_subword,
                                   category=category)
        else:
            answer = f'{correct_choice_letter}. {correct_word}'
        one_shot_question = f'''### example question ###
{self.example.format(category=category,
choice1=choices[0],
choice2=choices[1],
choice3=choices[2],
choice4=choices[3],
answer=answer)}

### actual question ###
{self._generate_zero_shot(category, choice1, choice2, choice3, choice4)}'''
        
        return helpers.fix_a_an(one_shot_question)


    def _generate_few_shot(self, category, choice1, choice2, choice3, choice4, answer='', shots=4):
        few_shot_question = ''
        correct_words = few_shot_examples.positive_examples[category]
        if answer:
            answers = [answer.format(correct_choice=str((i%4)+1).translate(str.maketrans("1234", "ABCD")),
                                     correct_word=correct_words[i][0],
                                     correct_subword=correct_words[i][1],
                                     category=category) for i in range(shots)]
        else:
            answers = [f'{str((i%4)+1).translate(str.maketrans("1234", "ABCD"))}. {correct_words[i][0]}' for i in range(shots)]
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
        few_shot_question += self._generate_zero_shot(category, choice1, choice2, choice3, choice4)

        return helpers.fix_a_an(few_shot_question)


    def _generate_CoT(self, category, choice1, choice2, choice3, choice4, shot='one'):
        cot_answer = '''{correct_choice}. Since the word {correct_word} contains the subword \
{correct_subword}, which is a {category}, the correct answer is {correct_choice}. {correct_word}.'''
        if shot == 'one':
            cot_question = self._generate_one_shot(category, choice1, choice2, choice3, choice4, cot_answer)
        elif shot == 'few':
            cot_question = self._generate_few_shot(category, choice1, choice2, choice3, choice4, cot_answer)
        else:
            raise Exception("Not valid 'shot' parameter. Need to be 'one' or 'few'")
        
        return helpers.fix_a_an(cot_question)


    def _generate_decomposite(self, category, choice1, choice2, choice3, choice4):
        decomposite_question = f'''\
Read the question below and understand what the question is asking for and the criteria for selecting the correct answer. 
Examine each word provided in the options carefully and Break down each word into its component parts or subwords.
Determine if any of the subwords within each word match the name of a {category}. 
Choose the word that contains a subword of a {category} according to the criteria given in the question.
Verify your answer, double-check your selection to ensure it meets all the requirements specified in the question.
Start your response with the correct letter and the correspond word. In case of doubt, answer according to the most probable answer.
{self._generate_zero_shot(category, choice1, choice2, choice3, choice4)}'''
        
        return helpers.fix_a_an(decomposite_question)