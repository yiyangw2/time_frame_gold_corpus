import re
import pandas as pd

import re
def create_regex_list(terms_file:str):
    """Creates a list of regex expressions of
    short term orientation"""

    # opens the specified dict_file in "r" (read) mode
    with open(terms_file,"r") as file:
        # reads the content of the file line-by-line
        # and creates a list of terms
        terms = file.read().splitlines()

    # creates a list of regex expressions by adding
    # word boundary (\b) anchors to the beginning and
    # the ending of each FLS term
    terms_regex = [re.compile(r'\b' + term.strip() + r'\b') for term in terms]
    return terms_regex


def get_future_year_regex(future_year):
    return [re.compile(r"[^$,]\b" + str(y) + r"\b(?!(%|,\d|.\d))") 
            for y in range(future_year + 1, future_year + 10)]


# alternative fls_terms
from itertools import product, chain
import re

first_words = ["next", "incoming", "coming", "upcoming", "subsequent", 
               "following"]
second_words = ["fiscal", "month", "period", "quarter", "year"]

# Note that "'ll" is an addition to original list
first_search = ["'ll", "will", "future"] + \
      [first + ' ' + second 
       for first, second in product(first_words, second_words)]
       
template = ["we $word", "and $word", "but $word", "do not $word",
            "company $words", "corporation $words", "firm $words",
            "management $words", "and $words", "but $words", 
            "does not $word", "is $past_tense", "are $past_tense",
            "not $past_tense", "is $pres_part", "are $pres_part", 
            "not $pres_part", "normally $word",
            "normally $words", "currently $word", "currently $words",
            "also $word", "also $words"]

verbs = ["aim", "anticipate", "assume", "commit", "estimate", 
         "expect", "forecast", "foresee", "hope", "intend",
         "plan", "project", "seek", "target"]

def past_tense(word):
    if word == "commit":
        return "committed"
    elif word == "plan":
        return "planned"
    elif word == "foresee":
        return "foreseen"
    elif word == "seek":
        return "sought"
    elif re.search("e$", word):
        return word + "d"
    else:
        return word + "ed"

def present_participle(word):
    if word == "commit":
        return "committing"
    elif word == "plan":
        return "planning"
    elif re.search("[^e]e$", word):
        return re.sub("e$", "ing", word)
    else:
        return word + "ing"

def complete_template(word):
    from string import Template
    words = word + "s"
    past = past_tense(word)
    part = present_participle(word)
    return [Template(str).substitute(word=word, words=words,
                              past_tense=past, pres_part=part) 
            for str in template]

def flatten(list_of_lists):
    return list(chain.from_iterable(list_of_lists))
    
second_search = flatten([complete_template(verb) for verb in verbs])

all_search = first_search + second_search
fls_terms_regex = [re.compile(r'\b' + term.strip() + r'\b') for term in all_search]


# fls_terms_regex = create_regex_list(r"fls_terms2.txt")
def is_forward_looking(sentence:str, future_year=None):
    """Returns whether sentence is forward-looking."""
    # fls_terms_regex = create_regex_list(r"fls_terms2.txt")
    fls_terms_regex = [re.compile(r'\b' + term.strip() + r'\b') for term in all_search]

    if future_year:
        regex = get_future_year_regex(future_year) + fls_terms_regex
    else:
        regex = fls_terms_regex
    for term in regex:
        if term.search(sentence.lower()):
            return True
    return False
  
def count_term(text:str, regex):
    """Returns the number of long-term oriented."""
    text = text.lower()
    count = 0
    for term in regex:
      count = count + len(re.findall(term, text))
    return count

def is_term(text:str, regex): 
  return count_term(text, regex) > 0

# def is_qt_term(text:str): 
#   return is_term(text, create_regex_list(r"qt_terms2.txt"))

def is_qt_term(sentence:str, future_year=None):
    """Returns whether sentence contains time frames."""
    if future_year:
        regex = get_future_year_regex(future_year) + create_regex_list(r"qt_terms2.txt")
    else:
        regex = create_regex_list(r"qt_terms2.txt")
    for term in regex:
        if term.search(sentence.lower()):
            return True
    return False

def is_future_year(text, future_year):
    return is_term(text, get_future_year_regex(future_year))

def print_stats(df, type = 'fl'):
    var = type
    var_cal = type + '_cal'

    tn = sum((df[var] == df[var_cal]) & ~df[var_cal])
    fp = sum((df[var] != df[var_cal]) & df[var_cal])
    fn = sum((df[var] != df[var_cal]) & ~df[var_cal])
    tp = sum((df[var] == df[var_cal]) & df[var_cal])

    print("Accuracy {:.2f}%".format( 100 * (tp + tn)/(tp + tn + fp + fn)))
    if tp + fp > 0:
        print("Precision {:.2f}%".format( 100 * tp/(tp + fp)))
    if tp + fn > 0:
        print("True positive rate {:.2f}%".format( 100 * tp/(tp + fn)))
