__all__ = ['log', 'DataCategory', 'spacy_nlp', 'Token', 'RegularExpressionCompileError', 'check_and_compile_regular_expression', 'char_tokenizer', 'string_regex_matcher']

"""
Utilities file for common library components of SmartCompose.

Tokenizer used by Neural Language Model stays in this file
Going to be outdated once we standardize pre-tokenization.

Includes some utilities for pretty printing email addresses and concatenating them.

"""

import string
import os
import time
import datetime
import unicodedata
import logging
import re
import numpy as np
from enum import Enum
from collections import defaultdict
import spacy

from sc_utils.constants import Constants

PUNCTUATION_SET = set(string.punctuation)

class DataCategory(Enum):
    CONTAINS_PRIVATE_DATA = 1  # logged data contains compliant or otherwise potentially private data
    ONLY_PUBLIC_DATA = 2 # logged data only contains numbers or messages, no private data is present

class RegularExpressionCompileError(Exception):
    """Raised when regular expression can not be compiled"""
    pass

class Token:
    """Unit object for the output of tokenization (word token)"""
    def __init__(self, text=""):
        self.text = text

    def is_punct(self):
        """
        Checks whether the token is consisted with punctuations and whitespaces

        Arguments:
            N/A
        Returns:
            True if all characters are punctuations, otherwise False {bool}
        """
        # First remove all white spaces
        text_whitespace_removed = "".join(self.text.split())
        # Check whether remaining chars are punctuations
        for char in text_whitespace_removed:
            if char not in string.punctuation:
                return False
        return True

    def is_space(self):
        """
        Checks whether all characters in the token are whitespace characters
        
        Arguments:
            N/A
        Returns:
            True if all characters are whitespace characters, otherwise False {bool}
        """
        return self.text.isspace()

    def __str__(self):
        return self.text

spacy_tokenizer = None  # don't load the spacy tokenizer by default for utils.

logging.basicConfig(level=logging.INFO, format="%(message)s")


def log(level, data_category: DataCategory, message):
    """
    Log the message at a given level (from the standard logging package levels: ERROR, INFO, DEBUG etc).
    Add a datetime prefix to the log message, and a SystemLog: prefix provided it is public data.
    The data_category can be one of CONTAINS_PRIVATE_DATA or ONLY_PUBLIC_DATA.
    """
    message = f"{datetime.datetime.now()}\t{logging._levelToName[level]}\t{message}"

    if data_category == DataCategory.ONLY_PUBLIC_DATA:
        message = "SystemLog: " + message

    logging.log(level, message)


def spacy_nlp():
    """
    Do lazy loading of the spaCy English language small NLP model.
    Add the sentencizer as a standard pipeline member, and run it first by default.
    """
    global spacy_tokenizer
    # do on demand loading of spacy tokenizer
    if not spacy_tokenizer:
        # Fallback logic in case spacy model is not available on the container
        try:
            from spacy.lang.en import English  # only import the English LM for spacy if we need it
            # load the spacy English nlp tokenization processor. TODO: allow specification of different tokenizers
            spacy_tokenizer = spacy.load('en_core_web_sm')
        except IOError:
            log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, "Couldn't load spaCy English model, falling back to the model stored in repo.")
            spacy_local_path = os.path.join(os.path.dirname(__file__), "..", "metrics", "spacy_en_model")
            if not os.path.isdir(spacy_local_path):
                log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, "spaCy English model not present in default location, must be running test framework")
                log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, f"cwd is: {os.getcwd()}")
                spacy_alternate_local_path = os.path.join(os.path.dirname(__file__), "..", "smartcompose", "metrics", "spacy_en_model")
                if not os.path.isdir(spacy_alternate_local_path): # this is the path from the unit testing CI framework if starting under SmartCompose folder
                    log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, "spaCy English model expected at %s or %s does not exist. Exiting" % (spacy_local_path, spacy_alternate_local_path))
                    exit(-1)
                else: # when running from unit testing CI framework
                    log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, "loading model from disk for test path %s" % spacy_alternate_local_path)
                    spacy_tokenizer = English().from_disk(spacy_alternate_local_path)
            else:
                spacy_tokenizer = English().from_disk(spacy_local_path)

        log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, "spaCy English model loaded, adding sentencizer for fast sentence breaking.")
        sentence_boundary_detection = spacy_tokenizer.create_pipe('sentencizer')
        spacy_tokenizer.add_pipe(sentence_boundary_detection, first=True) # reason to do this explained here: https://github.com/explosion/spaCy/issues/3569

    return spacy_tokenizer


def check_and_compile_regular_expression(regex_str: str):
    """
    Compiles the regular expression string
    If it fails to compile, raise a RegularExpresionCompileError
    Arguments:
        regex_str {str} -- regular expression to compile
    Returns:
        compiled regular expression object {Pattern}
    """
    try:
        # According to https://docs.python.org/3/library/re.html, Python will cache most recent compiled regular expression, 
        # so we don't do an implicit caching for re.compile output
        regex_compiled = re.compile(regex_str)
    except:
        raise RegularExpressionCompileError

    return regex_compiled


def char_tokenizer(input_str: str, sep_chars="", del_chars=""):
    """
    Python version of CharTokenizer in mlgtools
    First parse based on characters in sepChars and then remove characters in delChars for each token
    Arguments:
        input_str {str} -- input string to tokenize
        sep_chars {str} -- characters to be used for tokenization (string)
        del_chars {str} -- tokenization characters to be removed after tokenization (string)
    Returns:
        Tuple (list of tokens, list of intertokens)
    """
    regex_sepchars_compiled = None
    regex_delchars_compiled = None

    if sep_chars:
        regex_sepchars = "[" + sep_chars + "]+"
        regex_sepchars_compiled = check_and_compile_regular_expression(regex_sepchars)

    if del_chars:
        regex_delchars = "[" + del_chars + "]+"
        regex_delchars_compiled = check_and_compile_regular_expression(regex_delchars)

    # Tokenize with sep_chars, generate output intertokens & tokens (Token object)
    output_tokens = []
    output_intertokens = []

    if regex_sepchars_compiled is not None:
        prev_idx = 0
        match_iter = regex_sepchars_compiled.finditer(input_str)

        try:
            cur_match = next(match_iter)

            # If the first match does not start from the beginning, add an empty intertoken
            if cur_match.start() != 0:
                output_intertokens.append(Token())

            while True:
                try:
                    # If there is a match from the beginning, do not produce a token
                    if cur_match.start() != 0:
                        output_tokens.append(Token(input_str[prev_idx:cur_match.start()]))

                    # Add matched parts into intertokens
                    output_intertokens.append(Token(cur_match.group()))
                    prev_idx = cur_match.end()
                    cur_match = next(match_iter)

                except StopIteration:
                    break

        except StopIteration:
            # This means that there is no match. We just add an empty intertoken
            output_intertokens.append(Token())

        # Write leftovers to tokens, and add empty intertoken
        if prev_idx != len(input_str):
            output_tokens.append(Token(input_str[prev_idx:]))
            output_intertokens.append(Token())

    else:
        # If there is no separator chars, write whole string a single token
        output_tokens.append(Token(input_str))

    # delete chars from delChars in tokens/intertokens
    if regex_delchars_compiled:
        for i, output_token in enumerate(output_tokens):
            output_tokens[i] = Token(regex_delchars_compiled.sub('', output_token.text))
        for i, output_intertoken in enumerate(output_intertokens):
            output_intertokens[i] = Token(regex_delchars_compiled.sub('', output_intertoken.text))

    return output_tokens, output_intertokens


def string_regex_matcher(input_str: str, regex: str, replacement_str=""):
    """
    Python version of StringRegexMatcher in mlgtools.
    Replaces all substring matched with regular expression (regex) with replacement string (replacement_str).

    Arguments:
        input_str {str} -- input string to match
        regex {str} -- regular expression to match
        replacement_str {str} -- replacement string for string matched with regex
    returns:
        string removed replacement_str if it is set, or otherwise the original string {str}
    """
    # log error if regex is None or empty
    if not regex:
        log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA,
            '_string_regex_matcher: regex is None or empty. Returning original sentence.')
        return input_str

    # Compile the regular expression
    regex_compiled = check_and_compile_regular_expression(regex)

    # Return the string with replacing matched substrings with replacement_str
    return regex_compiled.sub(replacement_str, input_str)


def remove_line_breaks(input_string: str):
    """
    Removes any line breaks from the input string

    Arguments:
        input_string {str} -- input string to remove line breaks
    Returns:
        string without line breaks {str}
    """
    return string_regex_matcher(input_string, Constants.TOKENIZER_FIND_LINEBREAK_RE, replacement_str="")


def filter_tokens(tokens: list, filters: list, remove_whitespace=False):
    """
    Remove any literal strings in filters from tokens.
    Also remove any tokens that are punctuation or whitespace.
    Return the filtered tokens list.

    Arguments:
        tokens {list} -- list of Tokens object (word tokens)
        filters {list} -- list of literals to filter out
        remove_whitespace {bool} -- remove any starting/trailing whitespace on each token if it is set True
    
    Returns:
        list of filtered tokens {list}
    """
    answer = tokens
    # Apply all literal string filters
    for str_match in filters:
        answer = filter(lambda tok: tok.text != str_match, answer)
    # Filter all punctuation and whitespace tokens
    answer = filter(lambda tok: not tok.is_punct() and not tok.is_space(), answer)
    
    # Removes any starting / trailing white spaces in each token
    if remove_whitespace:
        answer = [Token(token.text.strip()) for token in answer]

    return answer


def get_current_body_only(text: str):
    """
    Strip prior message content from the body text of an email.
    TODO: Refactor AvocadoReader class to make use of this.
    """
    # split at header block and return original body of this email
    items = text.split(Constants.REPLY_HEADER_1)
    res = items[0].split(Constants.REPLY_HEADER_2)
    return res[0]


def get_prior_body_only(text: str):
    """
    Strip current message content from the body text of an email.
    See if there's any prior message content to report. Only take
    the most recent prior message in the thread.
    TODO: Consider whether we should retain or discard the metadata that's present
        in the prior messages. These are usually From:, Date:, To:, Subject.
        The ODIN MessageReply pairs view explicitly mirrors everything.
    """
    # split at header block and return original body of this email
    items = text.split(Constants.REPLY_HEADER_1)
    prior = ""
    if len(items) > 1:
        prior = items[1]
    else:
        res = items[0].split(Constants.REPLY_HEADER_2)
        if len(res) > 1:
            prior = res[1]
    if prior:
        return get_current_body_only(prior)
    else:
        return None


def unicode_escape(data):
    """Escapes all unicode characters as well as special ASCII characters like \n \t \v \r \f"""
    return data.encode("unicode-escape").decode("utf-8") if data else data


def unicode_unescape(data):
    """
    Unescape the strings that were encoded in to an escaped form. This is needed to
    allow string.split() to operate on whitespace like \n, which in escaped form are \\n.
    """
    return data.encode("utf-8").decode("unicode-escape") if data else data


def remove_punct(sentence: str):
    """
    Removes the punctuation (defined in string.punctation) from the sentence

    Arguments:
        sentence {str} -- sentence to remove punctuation
    Returns:
        sentence after removing punctuation {str}
    """
    return ' '.join([t for t in sentence.split() if len(set(t) - PUNCTUATION_SET) > 0])


def word_count(sentence: str, tokenizer):
    """
    Count the number of word-only tokens in the sentence. The sentence is just a string.
    This is more complex than just using a len(sentence.split()) but handles punctuation 
    and white space tokens more consistently.

    Arguments:
        sentence {str} -- sentence to count words
        tokenizer {Tokenizer} -- tokenizer instance to use for word tokenization
    Returns:
        word count {int}
    """
    tokenized_words, _ = tokenizer.tokenize_into_words(sentence)
    filtered_tokenized_words = filter_tokens(tokenized_words, [])
    return len(list(filtered_tokenized_words))


def average_or_zero(score_list):
    """
    Compute the numpy average of the list or return 0 if the list is empty.

    Arguments:
        score_list {list} -- list with scores
    Returns:
        average value of scores in the score_list, 0 if the list is empty {float}
    """
    if score_list:  # empty lists cause average and std dev to complain
        return np.average(score_list)
    return 0.0


def std_or_zero(score_list):
    """
    Compute the numpy standard deviation or return 0 if the list is empty.

    Arguments:
        score_list {list} -- list with scores
    Returns:
        standard deviation value of scores in the score_list, 0 if the list is empty {float}
    """
    if score_list:
        return np.std(score_list)
    return 0.0


def average_std_or_zero(score_list):
    """
    compute average and standard deviation of the list or return 0 if the list is empty.

    Arguments:
        score_list {list} -- list with scores
    Returns:
        average, standard deviation value of scores in the score_list, 0 if the list is empty {Tuple (float,float)}
    """
    return average_or_zero(score_list), std_or_zero(score_list)


def var_or_zero(score_list):
    """
    Compute the numpy variance or return 0 if the list is empty.

    Arguments:
        score_list {list} -- list with scores
    Returns:
        variance value of scores in the score_list, 0 if the list is empty {float}
    """
    if score_list:
        return np.var(score_list)
    return 0.0


def build_prefix_dict(index_to_word):
    """build_prefix_dict creates a trie (using a dict) for character prefixes."""
    start = time.time()
    temporary_dictionary = {}
    for index, word in enumerate(index_to_word):
        if word.startswith("<") and word.endswith(">"):   # special tokens
            continue
        for i in range(len(word) + 1):
            key = word[:i]
            if key not in temporary_dictionary:
                temporary_dictionary[key] = [index]
            else:
                temporary_dictionary[key].append(index)
    prefix_dict = {key: np.asarray(value) for key, value in temporary_dictionary.items()}

    log(logging.INFO,
        DataCategory.ONLY_PUBLIC_DATA,
        (f"Time to build character TRIE {time.time() - start}. Size {len(prefix_dict)} "
         f"(vect size {sum([len(k) for k in prefix_dict.keys()])})"))

    return prefix_dict


def pretty_print_email_address(email_address):
    """
    Formats email address into a standardized
    "Firstname Lastname <email@example.com>" format string.
    email_address input should be formatted to common schema.
    """
    if Constants.EMAILADDRESS_COMMON_SCHEMA in email_address:
        email_address = email_address[Constants.EMAILADDRESS_COMMON_SCHEMA]

    address = email_address[Constants.ADDRESS_COMMON_SCHEMA]
    name = email_address[Constants.NAME_COMMON_SCHEMA]

    log(logging.DEBUG,
        DataCategory.CONTAINS_PRIVATE_DATA,
        f"pretty print name: {name} address: {address}")

    firstname = ""
    lastname = ""
    if not name:  # make sure we actually obtained a name for this address but if not just return the address
        if not address:
            return ""
        else:
            return address
    else:
        if ',' in name:  # assume this has been formatted as: lastname, firstname
            lastname = name[:name.find(',')].strip()
            firstname = name[name.find(',') + 1:].strip()
        elif ' ' in name:  # assume this has been formatted as: firstname lastname
            firstname = name[:name.find(' ')].strip()
            lastname = name[name.find(' ') + 1:].strip()
        else:  # just grab it all as firstname
            firstname = name.strip()
    return f"{firstname} {lastname} <{address}>"


def concatenate_multiple_addresses(addresses):
    """
    From a list of MARS format email addresses, pretty_print each one (Firstname Lastname <email@exampl.com>),
    and concatenate them using ;'s as separators.
    """
    pretty_addresses = []
    for address in addresses:
        pretty_address = pretty_print_email_address(address)
        if pretty_address and isinstance(pretty_address, str):  # check that we actually got some text back
            pretty_addresses.append(pretty_address)
    # join the pretty addresses together with semicolons or return an empty string (join on an empty list will be an empty string)
    return ';'.join(pretty_addresses)


def skip_lines_with_decode_error(input_file, buffer_size=8192):
    """
    Generator, reads file in binary and tries to decode lines into utf-8. yields lines in file along with number of lines skipped due to decoding errors since last line yielded.
    Arguments:
        input_file {str} -- path to input file
        buffer_size {int} -- number of bytes to read at once
    """
    newline_byte, = '\n'.encode('utf-8')
    with open(input_file, 'rb') as fi:
        buffer = fi.read(buffer_size)
        binary_line = b""
        last_newline = 0
        while buffer != b"": # empty if eof
            for i, byte in enumerate(buffer):
                # found newline, append results to current line
                if byte == newline_byte:
                    binary_line += buffer[last_newline:i]
                    last_newline = i + 1 # skip newline
                    try:
                        line = binary_line.decode('utf-8').strip()
                        yield line
                    except UnicodeDecodeError:
                        continue
                    binary_line = b""

            binary_line += buffer[last_newline:] # add remaining bytes to current line
            last_newline = 0
            buffer = fi.read(buffer_size)


def get_unicode_category_dict(text):
    """
    Method to get unicode category dictionary for input text - by iterating over each character
    Arguments:
        text {str} -- input string for unicode category dictionary has to be generated
    Returns:
        dictionary containing unicode character dictionary for input text {st}
    """
    unicode_dict = defaultdict(int)
    for ch in text:
        category = unicodedata.category(ch)
        unicode_dict[category] += 1
    return unicode_dict


def histogram_average(histogram: dict):
    """
    Compute an 'average' over all the entries in the histogram.
    Conceptually this works by extending out each dictionary item's key as many times by its corresponding value.
    Then just average the items.
    Assumes that the keys are ints (or string representations of ints), and that the value is an int that is 0 or greater.
    Returns the average or 0.0 if the histogram is empty.
    """
    if not histogram or not histogram.items():
        return 0.0
    count = 0
    total_sum = 0
    for item in histogram.items():
        count = count + item[1]
        total_sum = total_sum + int(item[0]) * item[1]
    if count == 0: # if there are items but their count is 0, then count can be 0
        return 0.0
    # otherwise we have a positive count
    return total_sum / count


def histogram_sum(histogram: dict):
    """
    Compute a 'sum' over all the entries in the histogram.
    Conceptually this works by extending out each dictionary item's key as many times by its corresponding value.
    Then just sum the items.
    Assumes that the keys are ints (or string representations of ints), and that the value is an int that is 0 or greater.
    Returns the sum or 0 if the histogram is empty.
    """
    if not histogram or not histogram.items():
        return 0
    total_sum = 0
    for item in histogram.items():
        total_sum = total_sum + int(item[0]) * item[1]
    return total_sum


def extract_email_id(unique_id: str, qcs=False):
    """
    The generate_evaluation script constructs unique ids for each evaluation point as:
    emailNumber-charPos.
    These are used consistently throughout for JSON format evaluation point files.

    For processing by QCS, these ids are pre-prended by dummyQuery, as in:
    dummyQuery-emailNumber-charPos.
    By default, we assume that we are extracting the email id from a JSON format file.
    If the arg qcs is set to True, then we try to process it in QCS format.

    If the unique_id can be parsed into two fields (three if QCS), the first field (second if QCS) is returned.
    If it can't, then the entire unique_id is returned.
    """
    fields = unique_id.split('-')
    if qcs and unique_id.startswith(Constants.QUERY_QCS) and len(fields) == 3:
        return fields[1]
    elif not qcs and len(fields) == 2: # JSON format
        return fields[0]
    else:
        return unique_id


def extract_char_position(unique_id: str, qcs=False):
    """
    The generate_evaluation script constructs unique ids for each evaluation point as:
    emailNumber-charPos.

    For processing by QCS, these ids are pre-prended by dummyQuery, as in:
    dummyQuery-emailNumber-charPos.
    By default, we assume that we are extracting the email id from a JSON format file.
    If the arg qcs is set to True, then we try to process it in QCS format.

    If id can be parsed into two fields (three if QCS) and the last one is not empty,
    the second field (third if QCS) is returned.
    If it can't, then None is returned.
    """
    fields = unique_id.split('-')
    if qcs and unique_id.startswith(Constants.QUERY_QCS) and len(fields) == 3 and fields[2]:
        return fields[2]
    elif not qcs and len(fields) == 2 and fields[1]:
        return fields[1]
    else:
        return None


def qcs_unique_id_from(qcs_line: str):
    """
    Assume we're working with the output from QCS query label tool, that was passed a QCS input line formatted by generate_evaluation.
    Return will be the first field in the line (typically of the form: dummyQuery-<emailId>-<charPos>,
    where emailId and charPos are ints.)
    """
    fields = qcs_line.split('\t')
    if fields:
        return fields[0]
