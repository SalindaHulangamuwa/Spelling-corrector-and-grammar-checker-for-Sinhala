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
        Process the input text by first correcting the spelling of the middle word,
        then checking grammar.
        """
        # Step 1: Extract and correct the middle word (assumed to be the object)
        words = text.split()
        if len(words) < 3:
            return "Sentence too short. Please provide a sentence with Subject, Object, and Verb."
        
        middle_word_index = len(words) // 2
        middle_word = words[middle_word_index]

        corrected_word = self.spell_checker.auto_correct(middle_word)

        # Replace the middle word in the original sentence
        words[middle_word_index] = corrected_word
        corrected_text = ' '.join(words)
        print(f"Text after Spell Checking: {corrected_text}")

        # Step 2: Grammar Check
        print("Running Grammar Checker...")
        grammar_result = self.grammar_checker.check_grammar(corrected_text)

        return grammar_result


# Configuration for the spell checker
spell_checker_config = {
    "dictionary_path": 'data-spell-checker.xlsx',  # Path to the dictionary file
    "stopwords_path": 'stop words.txt',            # Path to the stopwords file
    "suffixes_path": "suffixes_list.txt",         # Path to the suffixes list file
    "stem_dictionary_path": "stem_dictionary.txt" # Path to the stem dictionary file
}

# Ensure all files exist
for file_path in spell_checker_config.values():
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

# Initialize the Sinhala Text Processor
text_processor = SinhalaTextProcessor(spell_checker_config)

# Input Sentences
input_sentences = [
    "මම ගදර යයි ",       
    "අපි කඩේට යයි",
    "අපි අදරය කරයි",
    "මම කෑම ගනිමු",
    "අපි රට යයි"
]

# Process each sentence
print("\nProcessing Input Sentences...")
results = []
for sentence in input_sentences:
    print(f"\nProcessing: {sentence}")
    result = text_processor.process_text(sentence)
    results.append(result)

# Final Output
print("\nFinal Output:")
for i, res in enumerate(results):
    print(f"Sentence {i + 1}: {res}")
