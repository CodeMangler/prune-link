import random
import string

__author__ = 'CodeMangler'

class NameGenerator:
    VALID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

    def generate(self, length):
        random_id = []
        for i in range(0, length):
            random_id.append(random.choice(NameGenerator.VALID_CHARS))
        return string.join(random_id, '')

