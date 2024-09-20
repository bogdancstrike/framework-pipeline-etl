import json
import random
import string


def clean_list(l):
    return [[x for x in y if x] for y in l]


def load_json(file):
    with open(file, 'rt') as fin:
        return json.load(fin)


def eval_file(file):
    with open(file, 'rt') as fin:
        return eval(fin)


def rnd_no(i):
    # return str(uuid.uuid4().int >> 4*16)[0:i]
    return ''.join(random.choice(string.digits) for _ in range(i))


def getor(obj, key, default=None):
    return obj.get(key, default) if obj and key in obj and obj[key] else default
