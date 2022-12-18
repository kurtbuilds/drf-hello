from typing import Optional, get_origin, get_args, Union


def is_optional(field):
    return get_origin(field) is Union and type(None) in get_args(field)


a = Optional[int]

print(is_optional(a))
