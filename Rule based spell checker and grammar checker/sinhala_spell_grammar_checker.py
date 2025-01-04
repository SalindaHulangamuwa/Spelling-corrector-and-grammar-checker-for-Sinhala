import os
from sinhala_spell_checker import SinhalaSpellChecker
from sinhala_grammar_checker import SinhalaGrammarChecker

def read_suffixes_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # Read lines and remove any whitespace/newlines
            suffixes = [line.strip() for line in file if line.strip()]    
        return suffixes
    except FileNotFoundError:
        print(f"Error: Cannot find file {file_path}")
        return []
    except Exception as e:
        print(f"Error reading file: {str(e)}")
        return []

def check_word_with_suffixes(checking_word, base_word, suffixes_list):
    # First check if the checking_word starts with the base_word
    if not checking_word.startswith(base_word):
        return False, None
    
    # Get the part after the base word
    remaining_part = checking_word[len(base_word):]
    
    # If there's no remaining part and checking_word equals base_word
    if not remaining_part and checking_word == base_word:
        return True, base_word
    
    # Check if the remaining part matches any suffix
    for suffix in suffixes_list:
        potential_word = base_word + suffix
        if potential_word == checking_word:
            return True, potential_word
            
    return False, None


class SinhalaTextProcessor:
    def _init_(self, spell_checker_config: dict):
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
        
        # Load the suffixes list
        self.suffixes_list = read_suffixes_from_file(spell_checker_config["suffixes_path"])

    def _get_base_word(self, word: str) -> str:
        base_word = self.spell_checker._advanced_stemmer(word)
        return base_word

    def _is_word_misspelled(self, word: str) -> bool:
        # Check if the word exists in the dictionary
        if word in self.spell_checker.dictionary:
            return False  # Word is correctly spelled
        
        # Find the base word
        base_word = self._get_base_word(word)
        
        # Check if any variations of the base word match the given word
        valid, matched_word = check_word_with_suffixes(word, base_word, self.suffixes_list)
        if valid:
            return True  # Word is valid as a variation of its base
        
        # If no match, the word is considered misspelled
        return False

    def _correct_word(self, word: str) -> str:
        if self._is_word_misspelled(word):
            # Check the word with the spell checker
            corrected_word = self.spell_checker.auto_correct(word)
            return corrected_word
        return word

    def process_text(self, text: str) -> str:
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
                corrected_word = self._correct_word(word)
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
    "අපි හෙට නුවර යමි.මම දැන් වැවට යමු.",
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