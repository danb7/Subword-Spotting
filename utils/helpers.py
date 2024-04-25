import re


def fix_a_an(sentence):
    '''replace "a" to "an" if needed'''
    return re.sub(r'\ba(?=\s+[aeiou])', 'an', sentence)


def generate_llm_response(client, prompt, model, temperature=0, max_tokens=100):
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


def evaluate_response(prompt_type, response, gold):
    '''prompt_type: multi\classification'''

    if prompt_type == 'multi':
        pattern = rf'\W*{re.escape(gold)}\W*\b'
        match = re.match(pattern, response)
    elif prompt_type == 'classification':
        pattern = rf'\W*{gold}\b'
        match = re.match(pattern, response)
    else:
        raise Exception('prompt type need to be multi or classification')

    if match:
        return True
    else:
        return False