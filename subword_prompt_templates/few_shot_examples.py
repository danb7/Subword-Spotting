positive_examples = { # TODO: change to examples for words that didnt in the dataset (still partial)
    'animal': [('million', 'lion'), ('pants', 'ant'), ('health', 'eal'), ('sealed', 'seal')],

    'color': [('credit', 'red'), ('blueprint', 'blue'), ('stingray', 'gray'), ('marigold', 'gold')],

    'fruit': [('pearl', 'pear'), ('sublime', 'lime'), ('oliver', 'olive'), ('grape', 'grapevine')],

    'food': [('piece', 'pie'), ('maurice', 'rice'), ('started', 'tart'), ('moreover', 'oreo')],

    'vehicle': [('training', 'train'), ('boatswain', 'boat'), ('business', 'bus'), ('carried', 'car')],

    'body_part': [('fingerprint', 'finger'), ('organization', 'organ'), ('footage', 'foot'), ('interface', 'face')],
}

negative_examples = {
    'animal': ['book', 'printer', 'guitar', 'pasta', 'glass', 'house', 'camera', 'milk', 'envelope', 'shoes', 'clock', 'mirror', 'matrix', 'paper'],
    'color': ['house', 'lamp', 'book', 'shoes', 'phone', 'guitar', 'truck', 'wallet', 'lantern', 'television', 'blanket', 'picked', 'father', 'drink'],
    'fruit': ['book', 'printer', 'guitar', 'pasta', 'glass', 'house', 'camera', 'milk', 'envelope', 'shoes', 'clock', 'mirror', 'matrix', 'paper'],
    'food': ['book', 'printer', 'guitar', 'keys', 'glass', 'house', 'camera', 'puzzle', 'envelope', 'shoes', 'clock', 'mirror', 'matrix', 'paper'],
    'vehicle': ['book', 'printer', 'guitar', 'keys', 'glass', 'house', 'camera', 'puzzle', 'envelope', 'shoes', 'clock', 'mirror', 'matrix', 'paper'],
    'body_part': ['book', 'printer', 'guitar', 'keys', 'blanket', 'house', 'camera', 'puzzle', 'envelope', 'truck', 'clock', 'mirror', 'matrix', 'paper'],
}