def save_txt(text, fn):
    with open(fn, 'w') as f:
        f.write(text)


def load_txt(fn):
    with open(fn, 'r') as f:
        ret = f.read()
    return ret
