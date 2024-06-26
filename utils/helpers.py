import re

from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

from human_benchmark import human_benchmark

def fix_a_an(sentence):
    '''replace "a" to "an" if needed'''
    return re.sub(r'\ba(?=\s+[aeiou])', 'an', sentence)


def generate_llm_response(client, prompt, model, temperature=0, max_tokens=128):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ],
        model=model,
        temperature = temperature,
        max_tokens = max_tokens
    )
    response = chat_completion.choices[0].message.content
    return response


def match_answer(response):
    raw_pattern = rf'\W*(Yes|No|[A-D])\W*\b'
    pattern = rf'{raw_pattern}|\W*The correct .* (is|are){raw_pattern}|\W*Answer{raw_pattern}'
    match = re.match(pattern, response)
    if match:
        chosen_letter = [m for m in match.groups() if m is not None][-1]
        return chosen_letter
    else:
        return None


def evaluate_response(response, gold):   
    match = match_answer(response)
    if match == gold:
        return True
    else:
        return False


def fix_xlabel(xlabel):
    xlabel = xlabel.replace('_', '-')
    xlabel = xlabel.replace('decomposite', 'decomposed')
    xlabel = xlabel[0].upper() + xlabel[1:]

    return xlabel


def plot_results(pv, type, radnom_line=None):
    '''type: multi or classification'''
    ax = pv.T.plot(kind='bar')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x*100:.0f}%'))
    ax.set_ylabel('Accuracy', fontsize=12)
    new_xlabels = [fix_xlabel(text.get_text()) for text in ax.get_xticklabels()]
    ax.set_xticklabels(new_xlabels)
    humans_result = human_benchmark.get_human_benchmark(type)['mean_score']
    ax.axhline(y=humans_result, color='navy', label='human') # human benchmark
    if radnom_line:
        ax.axhline(y=radnom_line, color='gray', linestyle='--', label='random')#random
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()