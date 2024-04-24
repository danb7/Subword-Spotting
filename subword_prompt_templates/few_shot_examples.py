positive_examples = { # TODO: change to examples for words that didnt in the dataset
    'animal': [('million', 'lion'), ('pants', 'ant'), ('beer', 'bee'), ('scatter', 'cat')],

    'color': [('credit', 'red'), ('abluent', 'blue'), ('stingray', 'gray'), ('marigold', 'gold')],

    'fruit': [('pearl', 'pear'), ('sublime', 'lime'), ('oliver', 'olive'), ('grape', 'grapevine')], #apple\grappled

    'food': [('piece', 'pie'), ('price', 'rice'), ('butterfly', 'butter'), ('breadth', 'bread')],# cream\scream

    'vehicle': [('training', 'train'), ('struck', 'truck'), ('ambush', 'bus'), ('scary', 'car')],#Boathouse

    'body_part': [('clip', 'lip'), ('diagnose', 'nose'), ('deliver', 'liver'), ('interface', 'face')],
}

negative_examples = {
    'animal': ['book', 'printer', 'guitar', 'pasta', 'glass', 'house', 'camera', 'milk', 'envelope', 'shoes', 'clock', 'mirror', 'matrix', 'paper'],
    'color': ['house', 'lamp', 'book', 'shoes', 'phone', 'guitar', 'truck', 'wallet', 'lantern', 'television', 'blanket', 'picked', 'father', 'drink'],
    'fruit': ['book', 'printer', 'guitar', 'pasta', 'glass', 'house', 'camera', 'milk', 'envelope', 'shoes', 'clock', 'mirror', 'matrix', 'paper'],
    'food': ['book', 'printer', 'guitar', 'keys', 'glass', 'house', 'camera', 'puzzle', 'envelope', 'shoes', 'clock', 'mirror', 'matrix', 'paper'],
    'vehicle': ['book', 'printer', 'guitar', 'keys', 'glass', 'house', 'camera', 'puzzle', 'envelope', 'shoes', 'clock', 'mirror', 'matrix', 'paper'],
    'body_part': ['book', 'printer', 'guitar', 'keys', 'blanket', 'house', 'camera', 'puzzle', 'envelope', 'truck', 'clock', 'mirror', 'matrix', 'paper'],
}