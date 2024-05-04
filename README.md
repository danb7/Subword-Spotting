# Subword-Spotting
NLP course Final Project

by: Daniel Bazar 314708181 & Lior Krengel 315850594

## Goal
1) identify a linguistic or language-related phenomenon or task that an LLM does not perform well on.
2) demonstrate that it indeed does not perform well on this task.
3) analyze and quantify the patterns of failure.

## The linguistic task
we demonstrate a type of word puzzle that involves identifying embedded words within other words. Specifically, this puzzle asks to find a subword that is also the name of an object from some category (for example, colors, animals, etc.). while humans perform well on this task, LLM doesnt.  
example question:
<pre>
which one of the following words contains a subword of an animal?
a. guitar
<b>b. million</b> (contains "lion")
c. pasta
d. house
</pre>

## Methodology of evaluation
### Dataset
We designed a dataset of subwords for different categories. here are few examples:
|  Category | Subword |    Word   |           Mulitple Wrong Options          |
|:---------:|:-------:|:---------:|:-----------------------------------:|
|  vehicle  |   car   |  scarcely |    ['asked' 'service' 'thinking']   |
|   animal  |   rat   | operation |     ['dinner' 'finding' 'water']    |
| body_part |   hip   |  shipping |     ['sharp' 'center' 'little']     |
| body_part |  ankle  | thankless | ['decision' 'physical' 'technique'] |
| body_part |   ear   |  research |     ['never' 'object' 'picture']    |
|   animal  |   cat   | education |     ['people' 'change' 'still']     |
|   animal  |   boar  |   aboard  |     ['indeed' 'husband' 'blood']    |
| body_part |   rib   | described |   ['picked' 'feeling' 'operation']  |
|  vehicle  |   bus   |   abuse   |     ['drink' 'whether' 'beside']    |
| body_part |   lip   |  slipped  |      ['never' 'sight' 'public']     |
|   animal  |   ant   |   wanted  |      ['james' 'called' 'black']     |
| body_part |  chest  | orchestra |      ['letter' 'every' 'table']     |
| body_part |   eye   |  conveyed |    ['always' 'house' 'possible']    |
| body_part |   toe   |  potatoes |   ['secret' 'regular' 'direction']  |
|   animal  |   bat   |   debate  |    ['father' 'governor' 'reason']   |
| body_part |   leg   |  college  |   ['result' 'advantage' 'second']   |
|   animal  |   owl   | knowledge |    ['school' 'russian' 'looked']    |
| body_part |   arm   |   farmer  |   ['directly' 'could' 'provided']   |

### Experiments
We conducted experiments under various prompting techniques (zero-shot, one-shot, few-shot, CoT, decompsed), question formats (multiple-choice and Yes/No),
and different LLMs (Mixtral-8x7B, OLMo 7B, and Llama 3 8B).

### Human benchmark
To create the human benchmark, we created 18 forms using Google Forms. See all forms in the `human_benchmark` folder.
The average accuracy of humans is **97.2%** in multiple-choice questions and **96.8%** in Yes/No questions. 

## Results
|                 |         | Zero-shot | One-shot | Few-shot | CoT-one | CoT-few | Decomposite |
|-----------------|---------|-----------|----------|----------|---------|---------|-------------|
| Multiple-choice | OLMo    | 35.0%     | 23.3%    | 25.0%    | 30.0%   | 25.0%   | 18.3%       |
|                 | Llama   | 26.7%     | 23.3%    | 36.7%    | 25.0%   | 45.0%   | 28.3%       |
|                 | Mixtral | 50.0%     | 41.7%    | 53.3%    | 50.0%   | 58.3%   | 48.3%       |
|                 | Random  |   25.0%   |          |          |         |         |             |
|                 | Human   |   97.2%   |          |          |         |         |             |
|    Yes/   No    | OLMo    | 50.0%     | 50.0%    | 51.7%    | 50.0%   | 52.5%   | 49.2%       |
|                 | Llama   | 49.2%     | 55.8%    | 57.5%    | 57.5%   | 61.7%   | 51.7%       |
|                 | Mixtral | 59.2%     | 75.8%    | 55.8%    | 60.8%   | 55.0%   | 72.5%       |
|                 | Random  |   50.0%   |          |          |         |         |             |
|                 | Human   |   96.8%   |          |          |         |         |             |

![multi_plot](https://github.com/danb7/Subword-Spotting/tree/8d5c758bb367b1fde43ce9eefc860cc41b345f4b/images/multi_plot.png)
![classification_plot](https://github.com/danb7/Subword-Spotting/tree/8d5c758bb367b1fde43ce9eefc860cc41b345f4b/images/YesNO_plot.png)
