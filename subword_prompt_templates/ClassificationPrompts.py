from utils import helpers
from subword_prompt_templates import few_shot_examples

class ClassificationPrompts():
    def __init__(self, question='''\
Subword is a standalone word that exists within a longer word that contains it, and its meaning is arbitrary from the longer word one's.
Question: Does the word "{word}" contains a subword of a {category}?
Answer: ''',
answer_aid='''[Your answer here, just Yes/No, without any explanation or additional text]'''):
        self.question = question
        self.example = self.question + '{answer}'
        self.answer_aid = answer_aid

    
    def generate(self, technique, category, word, **kwargs):
        if technique=='zero_shot':
            prompts = self._generate_zero_shot(category, word, **kwargs)
        
        elif technique=='one_shot':
            prompts = self._generate_one_shot(category, word, **kwargs)

        elif technique=='few_shot':
            prompts = self._generate_few_shot(category, word, **kwargs)

        elif technique.lower()=='cot':
            prompts = self._generate_CoT(category, word, **kwargs)

        elif technique=='decomposite':
            prompts = self._generate_decomposite(category, word, **kwargs)
            
        else:
            raise Exception("technique must be one of ['zero_shot', 'one_shot', 'few_shot', 'cot', 'decomposite']")
        
        return prompts

    def _generate_zero_shot(self, category, word, ans_aid=True):
        formated_question = self.question.format(category=category,
                                                 word=word)
        if ans_aid:
            formated_question += self.answer_aid
        return helpers.fix_a_an(formated_question) # replace "a" to "an" if category start with vowels


    def _generate_one_shot(self, category, word, positive_answer='Yes.'):
        example_word = few_shot_examples.positive_examples[category][0][0]
        correspond_subword = few_shot_examples.positive_examples[category][0][1]
        one_shot_question =  f'''\
### example question ###
{self.example.format(category=category,
                     word=example_word, 
                     answer=positive_answer.format(example_word=example_word, 
                                                   example_subword=correspond_subword,
                                                   category=category))}

### actual question ###
{self._generate_zero_shot(category, word)}'''
        
        return helpers.fix_a_an(one_shot_question)


    def _generate_few_shot(self, category, word, positive_answer='Yes.', negative_answer='No.', shots=4):
        few_shot_question = ''
        positive_examples = few_shot_examples.positive_examples[category]
        negative_examples = few_shot_examples.negative_examples[category]
        if shots/2 > len(positive_examples): raise Exception(f'too large shots. maximum is {shots}')
        for i in range(int(shots/2)):
            # positive example
            few_shot_question += f'### example question {i*2+1} ###\n'
            few_shot_question += self.example.format(category=category, 
                                                word=positive_examples[i][0], 
                                                answer=positive_answer.format(example_word=positive_examples[i][0],
                                                                            example_subword=positive_examples[i][1],
                                                                            category=category)) + '\n'*2
            # negative example
            few_shot_question += f'### example question {i*2+2} ###\n'
            few_shot_question += self.example.format(category=category,
                                                word=negative_examples[i], 
                                                answer=negative_answer.format(example_word=negative_examples[i],
                                                                            category=category)) + '\n'*2
        
        few_shot_question += '### actual question ###\n' 
        few_shot_question += self._generate_zero_shot(category, word)
        
        return helpers.fix_a_an(few_shot_question)


    def _generate_CoT(self, category, word, shot='one'):
        positive_answer = '''Yes. Since the word {example_word} contains the subword \
{example_subword}, which is a {category}, the correct answer is Yes.'''
        negative_answer = '''No. Since the word {example_word} doesnt contains any subword \
of a {category}, the correct answer is No.'''

        if shot == 'one':
            cot_question = self._generate_one_shot(category, word, positive_answer)
        elif shot == 'few':
            cot_question = self._generate_few_shot(category, word, positive_answer, negative_answer)
        else:
            raise Exception("Not valid 'shot' parameter. Need to be 'one' or 'few'")
        
        return helpers.fix_a_an(cot_question)

    def _generate_decomposite(self, category, word):
        decomposite_question = f'''\
Read the question below and understand what the question is asking for and the criteria for determine the correct answer. 
Examine the word provided in the question carefully and Break it down into its component parts or subwords.
Determine if any of the subwords within the word match the name of a {category}. 
Answer with "Yes" or "No" only, without explanations.
Verify your answer, double-check your classification to ensure it meets all the requirements specified in the question.
{self._generate_zero_shot(category, word)}'''
        
        return helpers.fix_a_an(decomposite_question)
