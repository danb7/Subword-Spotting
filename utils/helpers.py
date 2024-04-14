import re


def fix_a_an(sentence):
    '''replace "a" to "an" if needed'''
    return re.sub(r'\ba(?=\s+[aeiou])', 'an', sentence)