"""
Implementation of SmartCompose Tokenizers.
We are currently supporting three different tokenizers,
TrainingTokenizer -- mimics the tokenization method used for tokenizing words for training LM in QAS
InferenceTokenizer -- mimics the tokenization method used for tokenizing words for trie lookup
SpacyTokenizer -- uses spaCy's default word/sentence tokenizer
Sentence tokenizer for Training/Inference tokenizer is based on finding last sentence in QAS,
which uses !, ?, ., \\r, \\n and trailing white spaces to split the last sentence.
Note: if you need sentences without trailing spaces, make sure you strip the sentences before you use.

Used in Aether Modules:
    [SmartCompose][Non-Compliant] Python Tokenizer
    [SmartCompose][Compliant] Python Tokenizer
"""

import re
import os
import codecs
import argparse
import logging
import sys
import copy
import sys
import traceback
import shutil
from pathlib import Path


from sc_utils.constants import Constants
from sc_utils.scrubber import scrub_exc_message
from sc_utils.generic import *

# --------------------------------------------------------------------------------------------
# Useful functions for tokenization

def get_default_tokenizer():
    """
    Returns an instance of default tokenizer. 
    Currently we are using TrainingTokenizer in utils/tokenizer.py as the default one.
    Please consider using this function when you are using a tokenizer, so that we can easily replace to a new one if needed.

    Arguments:
        N/A
    Returns:
        tokenizer instance {Tokenizer}
    """
    return TrainingTokenizer()


def sentence_tokenizer(input_str: str, find_sentence_re=Constants.TOKENIZER_FIND_SENTENCE_RE):
    """
    Sentence tokenizer used for training / inference tokenizer
    In default, it partitions into sentences with the same rule in find_last_sentence function
    Basically partitions into sentences same to the find_last_sentence function,
    Sentence is defined as text with zero or more character(s) ends with one or more [.,?,!,\\r,\\n] and additional trailing whitespaces.

    FUTURE: we may want not to split sentences with two or three consecutive periods as spaCy does,
    but it was not easy to perfectly understand their rule (sentences with '..', '..!.' do not split while '.!..' split)

    Arguments:
        input_str {str} -- input string to tokenize
        find_sentence_re {str} -- regular expression to define a sentence(s),
                                we use Constants.TOKENIZER_FIND_LAST_SENTENCE_RE ('.*[\.\?\!\\r\\n]\s*') as default
    returns:
        list of sentences (+ remaining sentence piece at the end) tokenzied with tokenizer {list}
    """
    regex_find_sentence_compiled = check_and_compile_regular_expression(find_sentence_re)

    # iterator of matched sentences with find_sentence_re
    sentence_matches = regex_find_sentence_compiled.finditer(input_str)

    sentence_end_pos = 0
    sentences = []

    for sentence_match in sentence_matches:
        # This gives the whole match returned, which is a sentence
        sentences.append(sentence_match.group())
        # Save the end position to find any remaining sentence piece after last sentence
        sentence_end_pos = sentence_match.end()

    # Use last sentence's end position to check whether there is a remaining sentence piece.
    # match.end() gives the index starting from 1, so it can be used as a start index for the list
    if sentence_end_pos < len(input_str):
        sentences.append(input_str[sentence_end_pos:])

    return sentences


def multi_replace(input_str: str, replacements: dict, replacements_regex_str: str):
    """
    Given a string and a replacement map, it returns the replaced string.
    Code was from https://gist.github.com/bgusach/a967e0587d6e01e889fd1d776c5f3729

    Arguments:
        input_str {str} -- string to execute replacements on
        replacements {dict} -- replacement dictionary {value to find: value to replace}
        replacements_regex_str {str} -- regex that matches any of the substrings to replace
    Returns:
        filtered string {str}
    """
    # re automatically uses a cache of compiled re by running re.compile
    regex_compiled = check_and_compile_regular_expression(replacements_regex_str)
    # For each match, look up the new string in the replacements
    return regex_compiled.sub(lambda match: replacements[match.group()], input_str)


def find_last_sentence(input_str: str):
    """
    Find last sentence from email body, which functions same to the one in QAS last_sentence pipeline
    This function is not used in current tokenizer implementations,
    but we remain the implementation here if we need in future

    Arguments:
        input_str {str} -- input string to find last sentence
    Returns:
        last sentence {list}
    """
    return string_regex_matcher(input_str, Constants.TOKENIZER_FIND_LAST_SENTENCE_RE, replacement_str='')


def get_tokenizer_instance(tokenizer_mode: str):
    """
    A helper function to initialize a tokenizer instance.
    This function is used in scripts for generating AEther modules that require a tokenization.

    Arguments:
        tokenizer_mode {str} -- tokenizer mode to initialize. Currently it supports [train, inference, spacy]
    Returns:
        A tokenizer instance {Tokenizer}
    """
    tokenizer = None
    
    # Initialize tokenizer based on the argument tokenizer
    if tokenizer_mode == "train":
        tokenizer = TrainingTokenizer()
    elif tokenizer_mode == "inference":
        tokenizer = InferenceTokenizer()
    elif tokenizer_mode == "spacy":
        tokenizer = SpaCyTokenizer()
    
    return tokenizer

# --------------------------------------------------------------------------------------------
# Tokenizer base class
class Tokenizer:
    """
    Base Class for Tokenization.
    Child class should implement tokenize_into_words, tokenize_into_sentences function.
    """
    # --------------------------------------------------------------------------------------------
    # APIs for tokenization

    def tokenize_into_words(self, input_string: str):
        """
        Virtual function that implements the word tokenization

        Arguments:
            input_string {str} -- input string to tokenize
        Returns:
            list of words {Token}
        """
        raise NotImplementedError()

    def tokenize_into_sentences(self, input_string: str):
        """
        Virtual function that implements the sentence tokenization

        Arguments:
            input_string {str} -- input string to tokenize
        Returns:
            list of sentences {list}
        """
        raise NotImplementedError()

    def tokenize_into_sentences_and_words(self, input_string: str):
        """
        Tokenize into sentences and then tokenize into words for each sentence

        Arguments:
            input_string {str} -- input string to tokenize
        Returns:
            list of list of word tokens {list}
        """
        sentences = self.tokenize_into_sentences(input_string)
        
        output_list = []
        for sentence in sentences:
            tokens, _ = self.tokenize_into_words(sentence)
            output_list.append(tokens)
        
        return output_list

# --------------------------------------------------------------------------------------------
# Tokenizer instances (training, inference, spaCy)

class TrainingTokenizer(Tokenizer):
    """
    Tokenizer used for training LM. Mimics one implemented in QCS.
    It first replaces substring based on rules in replacements dictionary,
    and then tokenizes based on separator_chars
    This is the default one we are using for all tokenization on SmartCompose.

    Arguments:
            replacements {dict} -- dictionary rules to replace substring from the input string
            separator_chars {str} -- each char in the string will be used to tokenize input string
    """
    def __init__(self, replacements=Constants.TOKENIZER_TRAINING_RULE,
                 separator_chars=Constants.TOKENIZER_TRAINING_SEPERATOR):
        Tokenizer.__init__(self)

        # Place longer ones first to keep shorter substrings from matching where the longer ones should take place
        # For instance given the replacements {'ab': 'AB', 'abc': 'ABC'} against the string 'hey abc', it should produce
        # 'hey ABC' and not 'hey ABc'
        self.replacements = replacements
        replacements_sorted_list = sorted(replacements, key=len, reverse=True)
        # Create a big OR regex that matches any of the substrings to replace
        self.replacements_regex_str = '|'.join(map(re.escape, replacements_sorted_list))
        self.separator_chars = separator_chars

    def tokenize_into_words(self, input_string: str):
        """
        Word tokenizer for 'training' tokenizer. First replaces substring with the rules in replacements dictionary,
        and then tokenizes based on separtor_chars

        Arguments:
            input_string {str} -- string to tokenize
        Returns:
            Tuple {(list of tokens, list of intertokens)}
        """
        replaced_strs = multi_replace(input_string, self.replacements, self.replacements_regex_str)
        return char_tokenizer(replaced_strs, sep_chars=self.separator_chars, del_chars='')

    def tokenize_into_sentences(self, input_string: str):
        """
        Sentence tokenizer for 'training' tokenizer.
        Uses default sentence tokenizer.

        Arguments:
            input_string {str} -- string to tokenize
        Returns:
            list of sentences {list}
        """
        return sentence_tokenizer(input_string)


class InferenceTokenizer(Tokenizer):
    """
    Tokenizer used for inference. Mimics one implemented in QCS.
    It tokenizes using characters in separator_chars, and then for each token removes characters from delete_chars.

    Arguments:
        separator_chars {str} -- each char in the string will be used to tokenize input string
        delete_char {str} -- each car in the string will be removed from each token
    """
    def __init__(self, separator_chars=Constants.TOKENIZER_INFERENCE_SEPARATOR, delete_chars=Constants.TOKENIZER_INFERENCE_DELETE):
        Tokenizer.__init__(self)
        self.separator_chars = separator_chars
        self.delete_chars = delete_chars

    def tokenize_into_words(self, input_string: str):
        """
        Word tokenizer for 'inference' tokenizer. Tokenizes based on separtor_chars,
        and then removes all characters in the delete_chars.

        Arguments:
            input_string {str} -- string to tokenize
        Returns:
            Tuple {(list of tokens, list of intertokens)}
        """
        return char_tokenizer(input_string, sep_chars=self.separator_chars, del_chars=self.delete_chars)

    def tokenize_into_sentences(self, input_string: str):
        """
        Sentence tokenizer for 'inference' tokenizer.
        Uses default sentence tokenizer.

        Arguments:
            input_string {str} -- string to tokenize
        Retunrs:
            list of sentences {list}
        """
        return sentence_tokenizer(input_string)


class SpaCyTokenizer(Tokenizer):
    """
    Tokenizer using spaCy library.
    Disables all other features in spaCy and just loads the tokenizing module.

    Arguments:
        N/A
    """
    def __init__(self):
        Tokenizer.__init__(self)
        self.spacy_nlp = spacy_nlp()

    def tokenize_into_words(self, input_string: str):
        # This will eventually do both sentence_tokenizer and word_tokenizer. To match the APIs, we have word_tokenizer and sentence_tokenizer separately
        tokenized = self.spacy_nlp(input_string, disable=['tagger', 'parser', 'ner'])
        tokens = []
        intertokens = []
        # use the spaCy Token iterator
        for token in tokenized:
            # Get the token text and make our Token object
            tokens.append(Token(token.text))
            # Get the intertoken, which is whitespace_ in spaCy
            # TODO: not sure if we can also get the first intertoken with spaCy (if first token does not start at index 0),
            # we are getting only trailing spaces for now.
            intertoken = token.whitespace_ if token.whitespace_ else ""
            intertokens.append(Token(intertoken))
        return tokens, intertokens

    def tokenize_into_sentences(self, input_string: str):
        tokenized = self.spacy_nlp(input_string, disable=['tagger', 'parser', 'ner'])
        return list(map(lambda tokenized_sentence: tokenized_sentence.string, tokenized.sents))


# --------------------------------------------------------------------------------------------
# Script to run tokenizer
def tokenizer_wrapper(tokenizer, text, line_count, args):
    try:
        # Tokenize into words
        if args.type == 'word':
            tokens, _ = tokenizer.tokenize_into_words(text)
            tokenized_text = " ".join(str(token) for token in tokens)
            return tokenized_text
        # Tokenize into sentences
        elif args.type == 'sentence':
            sentences = "\n".join(tokenizer.tokenize_into_sentences(text))
            return sentences
        # Something wrong with the tokenizer type
        else:
            log(logging.ERROR, DataCategory.ONLY_PUBLIC_DATA, f"Something wrong with argument 'type', current tokenizer type is: {args.type}")
            exit(1)
    except RegularExpressionCompileError:
        log(logging.ERROR, DataCategory.ONLY_PUBLIC_DATA, "Regular Expression is wrong, compilation failed")
        exit(1)
    except Exception as error:
        # if something is wrong with tokenizing the input line, write a log and exit
        log(logging.ERROR, DataCategory.ONLY_PUBLIC_DATA, 
            f"line {line_count} had parsing error {type(error).__name__}")
        log(logging.ERROR, DataCategory.CONTAINS_PRIVATE_DATA, 
            f"len(line)={len(text)} len(line.strip())={len(text)} line={text}")
        exit(1)


def run_tokenizer(args):
    """script to run tokenizer for generating AEther module"""
    tokenizer = get_tokenizer_instance(args.mode)
    if not tokenizer:
        log(logging.ERROR, DataCategory.ONLY_PUBLIC_DATA, f"Something wrong with argument 'mode', current tokenizer mode is: {args.mode}")
        exit(1)

    # Create directory if needed
    if args.output_to_file:
        os.makedirs(os.path.basename(args.output_dir_path), exist_ok=True)
        output_path = args.output_dir_path
    else:
        output_dir = args.output_dir_path
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, f"Created output directory:{output_dir}")
        output_path = os.path.join(args.output_dir_path, 'tokenized.txt')

    log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, f"Start running tokenizer (mode: {args.mode}, type: {args.type})")
    log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, f"Start processing file: {args.input_file_path}")
    log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, f"Output file path: {output_path}")
    if args.input_is_tsv:
        log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, f"Intepreting input as tsv with separator {args.delimiter}, ignoring columns {args.ignore_cols}")
    line_count = 0

    # Run tokenizer for each line and write. We are assuming the input file is in utf-8
    with open(output_path, 'w', encoding='utf-8') as writer, open(args.input_file_path, 'r', encoding='utf-8') as reader:
        for line in reader:
            line_count += 1
            if args.input_is_tsv:
                items = line.strip().split(args.delimiter)
                output_items = []
                for i, item in enumerate(items):
                    if i in args.ignore_cols:
                        output_items.append(item)
                    else:
                        tokenized_text = tokenizer_wrapper(tokenizer, item, line_count, args)
                        if args.type == "sentence":
                            # escape newline characters
                            tokenized_text = tokenized_text.replace('\n', '\\n')
                        output_items.append(tokenized_text)

                output_row = args.delimiter.join(output_items) + '\n'
                writer.write(output_row)
            else:
                writer.write(tokenizer_wrapper(tokenizer, line.strip(), line_count, args) + '\n')

    log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, f"# of lines processed: {line_count}")
    log(logging.INFO, DataCategory.ONLY_PUBLIC_DATA, "End running tokenizer")


def init():
    try:
        # Parsing arguments
        parser = argparse.ArgumentParser(allow_abbrev=False)

        parser.add_argument("--input_is_tsv", type=bool, default=False, help="bool determining whether to use tsv related options")
        parser.add_argument("--delimiter", type=str, default=' ', help="optional, delimiter to use if parsing a tsv type file")
        parser.add_argument("--ignore_cols", type=int, nargs='+', help='indices of columns to ignore if parsing a tsv', default=[])
        parser.add_argument("-m", "--mode", choices=["train", "inference", "spacy"], default="train", help="Tokenizer to use [train, inference, spacy]")
        parser.add_argument("-t", "--type", choices=["word", "sentence"], default="word", help="Whether to use word tokenizer or sentence tokenizer")

        parser.add_argument('--output', default='outputdir')
        
        global args
        args, _ = parser.parse_known_args()

        if args.input_is_tsv:
            args.delimiter = codecs.decode(args.delimiter, 'unicode_escape')
        args.ignore_cols = set(args.ignore_cols) # faster lookup
        print("Args:")
        print(args)
        sys.stdout.flush()

        
        print("Output dir:", Path(args.output))
        os.makedirs(args.output, exist_ok = True)

    except BaseException as exc:
        print(exc)
        traceback.print_exc()
        raise

def run(batch_files):
    result = []
    local_args = copy.copy(args) 
    local_args.output_to_file = True

    print(f"Batch size = {len(batch_files)}")

    for file_name in batch_files:
        local_args.input_file_path = file_name
        local_args.output_dir_path = Path(args.output) / Path(file_name).name

        print(f"Start tokenizing {file_name}")
        run_tokenizer(local_args)
        result.append(file_name)
    
    print(f"Current batch complete.")
    return result
