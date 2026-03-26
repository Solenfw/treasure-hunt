import random

def manhattan_dist(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def random_text():
    texts = [
        'Keep digging!',
        'Watch out for bombs!',
        'Hints are your friends.',
        'Trust your instincts!',
        'The treasure is close...'
    ]
    return random.choice(texts)
