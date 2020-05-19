"""
Common constants used across multiple metrics and ngrams modules.
"""
class Constants():
    """
    All the constants declared here are held within the Constants class to provide easy namespacing.
    """
    # Metrics constants
    CHAR_TYPING_TIME = 0.3  # sec = 40wpm or 200cpm
    READ_TIME_PER_CHAR = 0.048  # sec = 250wpm
    CORRECT_PREDICTION_MULTIPLIER = 0.9   # pulled out of a hat
    COMPARE_METRIC_MATCH_WARNING_THRESHOLD = 1.0   # warn user if <100% of input data matched in control and treatment
    COMPARE_METRIC_MATCH_ERROR_THRESHOLD = 0.95   # throw error if <95% of input data matched in control and treatment
    MAX_QAS_CANDIDATES = 300    # maximum number of candidates dumped from QAS. This is due to known QAS out of memory error in Aether

    # MARS format email info
    EMAILADDRESS_LIST_MARS_SCHEMA = "emailaddresslist"

    # Delimiters that separate messages within body content
    REPLY_HEADER_1 = "-----Original Message-----"
    REPLY_HEADER_2 = "----- Original Message -----"

    # Common schema keys that unifiy Avocado,  O.com consumer, commercial datasets
    ID_COMMON_SCHEMA = "id" # All emails will be tagged with an id, which allows for easier grouping by email in stats.
    # Avocado provides an avocado id; Sniff Tests provide their own id; compliant data will use msg_Id.
    SENDER_COMMON_SCHEMA = "from" # the sender of the email, there can be only one
    TORECIPIENTS_COMMON_SCHEMA = "torecipients" # the set of To: line recipients of the email
    CCRECIPIENTS_COMMON_SCHEMA = "ccrecipients" # the set of Cc: line recipients of the email
    EMAILADDRESS_COMMON_SCHEMA = "emailaddress" # emailaddresses consist of two fields, name and address
    NAME_COMMON_SCHEMA = "name" # this is the name of the sender or recipient, e.g. Firstname Lastname
    ADDRESS_COMMON_SCHEMA = "address" # this is the actual email address e.g. name@example.com
    SUBJECT_COMMON_SCHEMA = "subject" # the subject line of the email
    UNIQUEBODY_COMMON_SCHEMA = "uniquebody" # no html, latest message in thread
    PRIORUNIQUEBODY_COMMON_SCHEMA = "prioruniquebody" # no html, previous message in thread; or empty if first message
    SENTDATETIME_LOCAL_COMMON_SCHEMA = "sentdatetime_local" # the creation date for the email, when it was being composed (local time)
    SENTDATETIME_UTC_COMMON_SCHEMA = "sentdatetime_utc" # the creation date for the email, when it was being composed (utc time)
    HASATTACHMENTS_COMMON_SCHEMA = "hasattachments" # "false" or "true"

    BODY_COMMON_SCHEMA = "body"

    # keys specific to Avocado
    CONTENT = "content"
    SENTDATETIME = "sentdatetime"
    AVOCADO_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

    # Json data exchange tags with the SmartComposeClient service wrapper
    UNIQUE_ID_TAG = "UniqueId"
    FROM_TAG = "From"
    TO_TAG = "To"
    SUBJECT_TAG = "Subject"
    BODY_TAG = "Body"
    BODY_CONTINUED_TAG = "BodyContinued"
    CURSOR_POSITION_TAG = "CursorPosition"
    CANDIDATE_COUNT_TAG = "TotalCandidateCount"
    SUGGESTIONS_TAG = "Suggestions"
    SUGGESTION_TAG = "Suggestion"
    SCORE_TAG = "Score"
    LATENCY_TAG = "Latency"

    # QCS input field names
    QUERY_QCS = "dummyQuery"
    BODY_QCS = "body"
    SUBJECT_QCS = "subject"
    CURSOR_POSITION_QCS = "cursorPosition"
    FROM_FIRSTNAME_QCS = "from_firstName"
    FROM_LASTNAME_QCS = "from_lastName"
    TO_FIRSTNAMES_QCS = "to_firstNames"
    TO_LASTNAMES_QCS = "to_lastNames"

    # Mode specific keys
    BODY_MODE = "body"
    SUBJECT_BODY_MODE = "subj+body"

    # Json data for metrics tags
    METRICS_AVG_TAG = '-average'
    METRICS_SD_TAG = '-stddev'
    TIME_SAVED_TAG = "TimeSaved"
    CHARACTER_SURPLUS_TAG = "CharSurplus"
    WORD_SURPLUS_TAG = "WordSurplus"
    SUGGEST_SURPLUS_TAG = "SuggestSurplus"
    CHARACTER_HISTOGRAM_TAG = "CharHistogram"
    WORD_HISTOGRAM_TAG = "WordHistogram"
    CHARACTER_HISTOGRAM_AVERAGE_TAG = "CharHistogramAverage"
    WORD_HISTOGRAM_AVERAGE_TAG = "WordHistogramAverage"
    SKIPPED_EVAL_POINT_TAG = "Skipped"

    # Json data for summary metrics tags
    EMAILS_AVG = "EmailsAvg-"
    EMAILS_SD = "EmailsSd-"
    EMAILS_COUNT_TAG = "Emails-Count"
    SENTENCES_AVG = "SentencesAvg-"
    SENTENCES_SD = "SentencesSd-"
    SENTENCES_COUNT_TAG = "Sentences-Count"
    EVALUATION_POINTS_COUNT_TAG = "EvaluationPoints-Count"
    EVALUATION_POINTS_SKIPPED_COUNT_TAG = "EvaluationPointsSkipped-Count"

    FIRST_SENTENCES_AVG = "FirstSentencesAvg-"
    FIRST_SENTENCES_SD = "FirstSentencesSd-"
    FIRST_SENTENCES_COUNT_TAG = "FirstSentences-Count"
    LAST_SENTENCES_AVG = "LastSentencesAvg-"
    LAST_SENTENCES_SD = "LastSentencesSd-"
    LAST_SENTENCES_COUNT_TAG = "LastSentences-Count"

    EMAILS_AVG_TIME_SAVED_TAG = EMAILS_AVG + TIME_SAVED_TAG
    EMAILS_SD_TIME_SAVED_TAG = EMAILS_SD + TIME_SAVED_TAG
    EMAILS_AVG_CHARACTER_SURPLUS_TAG = EMAILS_AVG + CHARACTER_SURPLUS_TAG
    EMAILS_SD_CHARACTER_SURPLUS_TAG = EMAILS_SD + CHARACTER_SURPLUS_TAG
    EMAILS_AVG_WORD_SURPLUS_TAG = EMAILS_AVG + WORD_SURPLUS_TAG
    EMAILS_SD_WORD_SURPLUS_TAG = EMAILS_SD + WORD_SURPLUS_TAG
    EMAILS_AVG_SUGGEST_SURPLUS_TAG = EMAILS_AVG + SUGGEST_SURPLUS_TAG
    EMAILS_SD_SUGGEST_SURPLUS_TAG = EMAILS_SD + SUGGEST_SURPLUS_TAG

    SENTENCES_AVG_TIME_SAVED_TAG = SENTENCES_AVG + TIME_SAVED_TAG
    SENTENCES_SD_TIME_SAVED_TAG = SENTENCES_SD + TIME_SAVED_TAG
    SENTENCES_AVG_CHARACTER_SURPLUS_TAG = SENTENCES_AVG + CHARACTER_SURPLUS_TAG
    SENTENCES_SD_CHARACTER_SURPLUS_TAG = SENTENCES_SD + CHARACTER_SURPLUS_TAG
    SENTENCES_AVG_WORD_SURPLUS_TAG = SENTENCES_AVG + WORD_SURPLUS_TAG
    SENTENCES_SD_WORD_SURPLUS_TAG = SENTENCES_SD + WORD_SURPLUS_TAG
    SENTENCES_AVG_SUGGEST_SURPLUS_TAG = SENTENCES_AVG + SUGGEST_SURPLUS_TAG
    SENTENCES_SD_SUGGEST_SURPLUS_TAG = SENTENCES_SD + SUGGEST_SURPLUS_TAG

    FIRST_SENTENCES_AVG_TIME_SAVED_TAG = FIRST_SENTENCES_AVG + TIME_SAVED_TAG
    FIRST_SENTENCES_SD_TIME_SAVED_TAG = FIRST_SENTENCES_SD + TIME_SAVED_TAG
    FIRST_SENTENCES_AVG_CHARACTER_SURPLUS_TAG = FIRST_SENTENCES_AVG + CHARACTER_SURPLUS_TAG
    FIRST_SENTENCES_SD_CHARACTER_SURPLUS_TAG = FIRST_SENTENCES_SD + CHARACTER_SURPLUS_TAG
    FIRST_SENTENCES_AVG_WORD_SURPLUS_TAG = FIRST_SENTENCES_AVG + WORD_SURPLUS_TAG
    FIRST_SENTENCES_SD_WORD_SURPLUS_TAG = FIRST_SENTENCES_SD + WORD_SURPLUS_TAG
    FIRST_SENTENCES_AVG_SUGGEST_SURPLUS_TAG = FIRST_SENTENCES_AVG + SUGGEST_SURPLUS_TAG
    FIRST_SENTENCES_SD_SUGGEST_SURPLUS_TAG = FIRST_SENTENCES_SD + SUGGEST_SURPLUS_TAG

    LAST_SENTENCES_AVG_TIME_SAVED_TAG = LAST_SENTENCES_AVG + TIME_SAVED_TAG
    LAST_SENTENCES_SD_TIME_SAVED_TAG = LAST_SENTENCES_SD + TIME_SAVED_TAG
    LAST_SENTENCES_AVG_CHARACTER_SURPLUS_TAG = LAST_SENTENCES_AVG + CHARACTER_SURPLUS_TAG
    LAST_SENTENCES_SD_CHARACTER_SURPLUS_TAG = LAST_SENTENCES_SD + CHARACTER_SURPLUS_TAG
    LAST_SENTENCES_AVG_WORD_SURPLUS_TAG = LAST_SENTENCES_AVG + WORD_SURPLUS_TAG
    LAST_SENTENCES_SD_WORD_SURPLUS_TAG = LAST_SENTENCES_SD + WORD_SURPLUS_TAG
    LAST_SENTENCES_AVG_SUGGEST_SURPLUS_TAG = LAST_SENTENCES_AVG + SUGGEST_SURPLUS_TAG
    LAST_SENTENCES_SD_SUGGEST_SURPLUS_TAG = LAST_SENTENCES_SD + SUGGEST_SURPLUS_TAG

    SUGGESTIONS_SHOWN_COUNT_TAG = "SuggestionsShown"
    SUGGESTIONS_ACCEPTED_COUNT_TAG = "SuggestionsAccepted"
    CASR_TAG = "ComposeAcceptedSuggestionRate"

    PRECISION_AT_ONE_TAG = "P@1"
    RECALL_AT_TAG = "R@"
    MRR_TAG = "MRR"

    PRECISION_AT_ONE_AVG_TAG = PRECISION_AT_ONE_TAG + METRICS_AVG_TAG
    PRECISION_AT_ONE_SD_TAG = PRECISION_AT_ONE_TAG + METRICS_SD_TAG
    MRR_AVG_TAG = MRR_TAG + METRICS_AVG_TAG
    MRR_SD_TAG = MRR_TAG + METRICS_SD_TAG

    SIMPLE_PRECISION_TAG = 'Simple_Precision'
    CGOR_TAG = 'CGOR'
    CGOR_TOPK_TAG = 'CGOR-Topk'
    CGOR_TOKEN_TAG = 'CGOR-Token'
    CGOR_COMPLEX_TAG = 'CGOR-Complex'
    CGOR_BASIC_TAG = 'CGOR-Basic'

    SIMPLE_PRECISION_AVG_TAG = SIMPLE_PRECISION_TAG + METRICS_AVG_TAG
    SIMPLE_PRECISION_SD_TAG = SIMPLE_PRECISION_TAG + METRICS_SD_TAG
    CGOR_AVG_TAG = CGOR_TAG + METRICS_AVG_TAG
    CGOR_SD_TAG = CGOR_TAG + METRICS_SD_TAG
    CGOR_TOPK_AVG_TAG = CGOR_TOPK_TAG + METRICS_AVG_TAG
    CGOR_TOPK_SD_TAG = CGOR_TOPK_TAG + METRICS_SD_TAG
    CGOR_TOKEN_AVG_TAG = CGOR_TOKEN_TAG + METRICS_AVG_TAG
    CGOR_TOKEN_SD_TAG = CGOR_TOKEN_TAG + METRICS_SD_TAG
    CGOR_COMPLEX_AVG_TAG = CGOR_COMPLEX_TAG + METRICS_AVG_TAG
    CGOR_COMPLEX_SD_TAG = CGOR_COMPLEX_TAG + METRICS_SD_TAG
    CGOR_BASIC_AVG_TAG = CGOR_BASIC_TAG + METRICS_AVG_TAG
    CGOR_BASIC_SD_TAG = CGOR_BASIC_TAG + METRICS_SD_TAG

    # Tokenizer specific constants
    TOKENIZER_TRAINING_RULE = {"'s": " 's", "'ve": " 've", "'t": " 't", "'re": " 're", "'d": " 'd", "'ll": " 'll", 
                                '’': " '", ',': ' , ', '"': ' " ', '!': ' ! ', '(': ' ( ', ')': ' ) ', '?': ' ? ', 
                                '.': ' . ', ':': ' : ', ';': ' ; '}
    TOKENIZER_TRAINING_SEPERATOR = " "
    TOKENIZER_INFERENCE_SEPARATOR = ' ,\.:;!\?`%\^\&%\#\$\*\+\/\(\)@><"'
    TOKENIZER_INFERENCE_DELETE = "'"
    TOKENIZER_FIND_LAST_SENTENCE_RE = '.*[\.\?\!\r\n]\s*'
    TOKENIZER_FIND_SENTENCE_RE = '[^\.\?\!\r\n]*[\.\?\!\r\n]+\s*'
    TOKENIZER_FIND_LINEBREAK_RE = '[\r\n]+'

    # QAS output specific constants
    QAS_FEATUREIDS_FILE = ".FeatureIds.output.txt"
    QAS_EXTERNAL_WORDS = "external_words"
    QAS_EXTERNAL_SUGGESTIONS = "external_suggestions"
    QAS_EXTERNAL_CANDIDATES = "external_top300_completion_candidates"
    QAS_CANDIDATE_COUNT = "external_candidate_count"

    # useful for finding values in logs
    LOG_MARKER_LEFT = "@@@<<<"
    LOG_MARKER_RIGHT = ">>>@@@"
    LOG_MARKER_FORMAT = "@@@<<<%s>>>@@@"
    LOG_MARKER_REGEX = r"@@@<<<(.*)>>>@@@"