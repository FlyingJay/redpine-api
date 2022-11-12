from django.core.exceptions import ValidationError
import re


def validate_markdown(value):
    """ 
    the motivation here is to provide a whitelist of markdown input that can be used. 

    in general, we want users to be able to use the following features:

    - numeric & bullet lists (1., *)
    - headings (#)
    - paragraphs (line breaks)
    - bold / italics (*, _)

    """
    WHITELIST = [
        'A-Z', # alphanumeric
        'a-z', # alphanumeric 
        '0-9', # alphanumeric
        '#', # headings
        '\.', # literal period, for numeric lists & end of sentence
        '\*', # for bullet lists, emphasis
        '\_', # markdown emphasis
        '\s', # space character
        '\-\!\(\)\"\'\:\,\/', # potentially used characters
    ]
    matcher = re.compile('^[{}]*$'.format(''.join(WHITELIST)))
    offending_matcher = re.compile('([^{}]*)'.format(''.join(WHITELIST)))

    if not matcher.match(value):
        raise ValidationError('restricted characters found in markdown string "{}"'.format(value))


def non_negative(value):
    if value < 0:
        raise ValidationError('Negative values are not allowed.')


def less_than(target, this):
    if this > target:
        raise ValidationError('Amount is too low.')

