import re

from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter


def fix_a_an(sentence):
    '''replace "a" to "an" if needed'''
    return re.sub(r'\ba(?=\s+[aeiou])', 'an', sentence)


def generate_llm_response(client, prompt, model, temperature=0, max_tokens=256):
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


def plot_results(pv, radnom_line): # TODO: plot the human line correct (get value directly from the code)
    ax = pv.T.plot(kind='bar')
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x*100:.0f}%'))
    ax.set_ylabel('Accuracy', fontsize=12)
    ax.axhline(y=0.97, color='navy', label='human') # human benchmark
    if radnom_line:
        ax.axhline(y=radnom_line, color='gray', linestyle='--', label='random')#random
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
    plt.show()