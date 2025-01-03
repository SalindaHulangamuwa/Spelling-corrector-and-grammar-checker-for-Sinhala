import os
from sinhala_spell_checker import SinhalaSpellChecker
from sinhala_grammar_checker import SinhalaGrammarChecker


class SinhalaTextProcessor:
    def __init__(self, spell_checker_config: dict):
        """
        Initialize the text processor with spell checker and grammar checker.
        """
        self.spell_checker = SinhalaSpellChecker(
            dictionary_path=spell_checker_config["dictionary_path"],
            stopwords_path=spell_checker_config["stopwords_path"],
            suffixes_path=spell_checker_config["suffixes_path"],
            stem_dictionary_path=spell_checker_config["stem_dictionary_path"]
        )
        self.grammar_checker = SinhalaGrammarChecker()

    def process_text(self, text: str) -> str:
        """
        Process the input text by correcting spelling for all non-subject and non-verb words,
        then checking grammar.
        """
        # Step 1: Tokenize and identify subject, object, and verb
        words = text.split()
        if len(words) < 3:
            return "Sentence too short. Please provide a sentence with Subject, Object, and Verb."

        # Grammar checker POS tagging to identify subject and verb
        tokenized_sentences = [
            self.grammar_checker.tokenizer.tokenize(f'{ss}.') 
            for ss in self.grammar_checker.tokenizer.split_sentences(text)
        ]
        pos_tags = self.grammar_checker.tagger.predict(tokenized_sentences)

        if not pos_tags or not pos_tags[0]:
            return "Unable to analyze the sentence."

        tokens = tokenized_sentences[0]
        tags = pos_tags[0]

        subject = None
        verb = None

        # Find subject and verb dynamically
        for i, (token, tag) in enumerate(tags):
            if tag == 'PRP' and not subject:
                subject = token
            if tag.startswith('V') and not verb:
                verb = token

        if not subject or not verb:
            return "Sentence lacks a clear subject or verb."

        # Step 2: Correct spelling for all words except subject and verb
        corrected_words = []
        for word in words:
            if word != subject and word != verb:
                corrected_word = self.spell_checker.auto_correct(word)
                corrected_words.append(corrected_word)
            else:
                corrected_words.append(word)

        corrected_text = ' '.join(corrected_words)
        print(f"Text after Spell Checking: {corrected_text}")

        # Step 3: Grammar Check
        print("Running Grammar Checker...")
        # Split corrected_text into sentences by '.'
        sentences = corrected_text.split(".")
        
        # Process each sentence individually and store grammar results
        grammar_results = []
        for sentence in sentences:
            if sentence.strip():  # Check if the sentence is not empty
                grammar_result = self.grammar_checker.check_grammar(sentence.strip())
                grammar_results.append(grammar_result)
        
        return grammar_results


# Configuration for the spell checker
spell_checker_config = {
    "dictionary_path": 'data-spell-checker.xlsx',  # Path to the dictionary file
    "stopwords_path": 'stop words.txt',            # Path to the stopwords file
    "suffixes_path": "suffixes_list.txt",          # Path to the suffixes list file
    "stem_dictionary_path": "stem_dictionary.txt"  # Path to the stem dictionary file
}

# Ensure all files exist
for file_path in spell_checker_config.values():
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

# Initialize the Sinhala Text Processor
text_processor = SinhalaTextProcessor(spell_checker_config)

# Input Sentences
input_sentences = [
    "අපි කඩේ යයි.අපි උදේට කඩෙන කමු.",
    "මම අද ගදර යයි.අපි හෙට ගමට යම.",
    "අපි හෙට නුවර යන්නෙමි.මම දැන් වැවට යම.",
    "මම ඔයාට අදරය කරයි.මම ඔයාගේ ගෙදර යයි.",
    "අපි උත්සාහයෙන් වැඩ කරමි.අපි කොහොමහරි දිනයි."
]

# Process each sentence
print("\nProcessing Input Sentences...")
results = []
for sentence in input_sentences:
    print(f"\nProcessing: {sentence}")
    result = text_processor.process_text(sentence)
    results.append(result)

# Final Output: Print each grammar check result separately
print("\nFinal Output: Grammar Check Results")
for i, res in enumerate(results):
    print(f"\nResults for Sentence {i + 1}:")
    for grammar_result in res:
        print(f"Grammar Check Result: {grammar_result}")
