import random
import string


def random_string(length: int = 20) -> str:
    return "".join(random.sample(string.ascii_letters + string.digits, length))
