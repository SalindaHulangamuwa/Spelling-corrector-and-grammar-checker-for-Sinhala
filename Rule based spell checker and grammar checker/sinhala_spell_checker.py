import pandas as pd
import re
from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz
import difflib

class SinhalaSpellChecker:
    def _init_(self, dictionary_path: str, stopwords_path: str, suffixes_path: str, stem_dictionary_path: str):
        # Load dictionary
        self.data = pd.read_excel(dictionary_path)
        self.dictionary = self._preprocess_dictionary()
        
        # Load stopwords
        with open(stopwords_path, 'r', encoding='utf-8') as file:
            self.stopwords = set(file.read().splitlines())
        
        # Load suffixes from suffixes_list.txt
        with open(suffixes_path, 'r', encoding='utf-8') as file:
            self.suffix_rules = file.read().splitlines()
        
        # Load stem dictionary
        self.stem_dictionary = self._load_stem_dictionary(stem_dictionary_path)
        
        # Advanced phonetic mapping
        self.phonetic_mapping = self._create_advanced_phonetic_mapping()
        
        # Prefix and suffix variations
        self.prefix_variations = {
            'අ': ['ආ', 'අ'],
            'අද': ['ආද', 'අද'],
            'අන': ['ආන', 'අන']
        }
    
    def _load_stem_dictionary(self, stem_dictionary_path: str) -> Dict[str, str]:
        """Load stem dictionary from a file, where each line contains a word variation and its stem."""
        stem_dict = {}
        with open(stem_dictionary_path, 'r', encoding='utf-8') as file:
            for line in file:
                word, stem = line.strip().split('\t')
                stem_dict[word] = stem
        return stem_dict
    
    def _preprocess_dictionary(self) -> List[str]:
        """Advanced dictionary preprocessing"""
        correct_words = self.data[self.data['label'] == 1]['word']
        
        # Remove duplicates, convert to lowercase, remove special characters
        processed_words = set(
            re.sub(r'[^\u0D80-\u0DFF]', '', word.lower()) 
            for word in correct_words
        )
        
        return list(processed_words)
    
    def _create_advanced_phonetic_mapping(self) -> Dict[str, str]:
        """Comprehensive phonetic mapping for Sinhala characters"""
        return {
            'ක': 'k', 'ඛ': 'k', 'ග': 'g', 'ඝ': 'g',
            'ච': 'c', 'ජ': 'j', 'ඣ': 'j',
            'ට': 't', 'ඩ': 'd', 'ඨ': 't', 'ඪ': 'd',
            'ත': 't', 'ද': 'd', 'ධ': 'd',
            'ප': 'p', 'බ': 'b', 'භ': 'b',
            'ම': 'm', 'න': 'n', 'ණ': 'n',
            'ල': 'l', 'ළ': 'l',
            'ර': 'r', 'ඍ': 'r',
            'ව': 'v', 'ශ': 's', 'ෂ': 's', 'ස': 's', 
            'හ': 'h'
        }
    
    def _advanced_stemmer(self, word: str) -> str:
        """Advanced stemming with multiple suffix removal strategies and stem dictionary"""
        # First, check if the word exists in the stem dictionary
        if word in self.stem_dictionary:
            return self.stem_dictionary[word]
        
        # If not, apply suffix removal rules
        original_word = word
        for suffix in self.suffix_rules:
            if word.endswith(suffix):
                word = word[:-len(suffix)]
                break
        
        # If no suffix removed and word is too short, return original
        return word if len(word) > 2 else original_word
    
    def _phonetic_key(self, word: str) -> str:
        """Generate advanced phonetic key"""
        phonetic_key = ''
        for char in word:
            phonetic_key += self.phonetic_mapping.get(char, char)
        return phonetic_key
    
    def _generate_prefix_variations(self, word: str) -> List[str]:
        """Generate potential prefix variations of a word"""
        variations = [word]
        
        for prefix, alternates in self.prefix_variations.items():
            if word.startswith(prefix):
                for alt_prefix in alternates:
                    if prefix != alt_prefix:
                        variation = alt_prefix + word[len(prefix):]
                        variations.append(variation)
        
        return variations
    
    def find_corrections(self, word: str, limit: int = 5, threshold: int = 70) -> List[Tuple[str, int]]:
        """Find corrections based on similarity metrics and variations"""
        # Check if the word exists in the dictionary
        if word in self.stopwords or word in self.dictionary:
            return [(word, 100)]
        
        # Check if the word is a valid variation
        for variation in self._generate_prefix_variations(word):
            if variation in self.dictionary:
                return [(variation, 100)]
        
        # Find base word using advanced stemming
        base_word = self._advanced_stemmer(word)
        
        # Find closest matches based on similarity metrics
        candidates = []
        for dict_word in self.dictionary:
            # Check if the base word matches the dictionary word
            if base_word == dict_word:
                return [(dict_word, 100)]
            
            # Use multiple similarity metrics
            phonetic_similarity = fuzz.ratio(self._phonetic_key(word), self._phonetic_key(dict_word))
            string_similarity = fuzz.ratio(word, dict_word)
            edit_similarity = fuzz.token_sort_ratio(word, dict_word)
            
            # Sequence matcher for more nuanced similarity
            seq_matcher = difflib.SequenceMatcher(None, word, dict_word)
            sequence_similarity = seq_matcher.ratio() * 100
            
            combined_score = (
                0.25 * phonetic_similarity + 
                0.2 * string_similarity + 
                0.15 * edit_similarity +
                0.25 * sequence_similarity
            )
            
            if combined_score >= threshold:
                candidates.append((dict_word, combined_score))
        
        # Sort and return top candidates
        candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:limit]
        
        return candidates
    
    def spell_check(self, text: str) -> Dict[str, List[Tuple[str, int]]]:
        """Check and find spelling errors in the given text"""
        words = re.findall(r'\S+', text)
        
        spelling_errors = {}
        for word in words:
            if word not in self.dictionary and word not in self.stopwords:
                corrections = self.find_corrections(word)
                if corrections:
                    spelling_errors[word] = corrections
        
        return spelling_errors
    
    def auto_correct(self, text: str) -> str:
        """Automatically correct the text using the best suggestions"""
        errors = self.spell_check(text)
        corrected_words = []
        
        for word in text.split():
            if word in errors:
                corrected_words.append(errors[word][0][0])  # Take the first suggestion
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)