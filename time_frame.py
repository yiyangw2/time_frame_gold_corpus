import re
import pandas as pd

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
    terms_regex = [re.compile(r'\b' + term + r'\b') for term in terms]
    return terms_regex

fls_terms_regex = create_regex_list(r"fls_terms2.txt")

def get_future_year_regex(future_year):
    return [re.compile(r"[^$,]\b" + str(y) + r"\b(?!(%|,\d|.\d))")
            for y in range(future_year + 1, future_year + 10)]

def is_forward_looking(sentence:str, future_year=None):
    """Returns whether sentence is forward-looking."""
    fls_terms_regex = create_regex_list(r"fls_terms2.txt")

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

def is_qt_term(text:str):
  return is_term(text, create_regex_list(r"qt_terms2.txt"))

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
