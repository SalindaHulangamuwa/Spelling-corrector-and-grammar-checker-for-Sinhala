import pandas as pd
import re
from fuzzywuzzy import fuzz, process
import difflib
from typing import List, Dict, Tuple


class SinhalaSpellChecker:
    def __init__(self, dictionary_path: str, stopwords_path: str, suffixes_path: str, stem_dictionary_path: str):
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
        """Enhanced correction finding with prefix variations and multiple similarity metrics"""
        # Check if word is already correct
        if word in self.stopwords or word in self.dictionary:
            return [(word, 100)]
        
        # Generate prefix variations to check
        word_variations = self._generate_prefix_variations(word)
        
        # Comprehensive similarity calculation
        candidates = []
        for dict_word in self.dictionary:
            for variation in word_variations:
                # Stem both variation and dictionary word
                stemmed_variation = self._advanced_stemmer(variation)
                stemmed_dict_word = self._advanced_stemmer(dict_word)
                
                # Multiple similarity metrics
                phonetic_similarity = fuzz.ratio(
                    self._phonetic_key(stemmed_variation), 
                    self._phonetic_key(stemmed_dict_word)
                )
                
                string_similarity = fuzz.ratio(stemmed_variation, stemmed_dict_word)
                edit_similarity = fuzz.token_sort_ratio(stemmed_variation, stemmed_dict_word)
                
                # Sequence matcher for more nuanced similarity
                seq_matcher = difflib.SequenceMatcher(None, stemmed_variation, stemmed_dict_word)
                sequence_similarity = seq_matcher.ratio() * 100
                
                # Prefix similarity
                prefix_similarity = fuzz.ratio(variation[:3], dict_word[:3]) * 0.5
                
                # Combined weighted similarity
                combined_score = (
                    0.25 * phonetic_similarity + 
                    0.2 * string_similarity + 
                    0.15 * edit_similarity +
                    0.25 * sequence_similarity +
                    0.15 * prefix_similarity
                )
                
                candidates.append((dict_word, combined_score))
        
        # Sort, filter, and limit candidates
        candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
        unique_candidates = []
        seen = set()
        for candidate, score in candidates:
            if candidate not in seen and score >= threshold:
                unique_candidates.append((candidate, score))
                seen.add(candidate)
                if len(unique_candidates) == limit:
                    break
        
        return unique_candidates
    
    def spell_check(self, text: str) -> Dict[str, List[Tuple[str, int]]]:
        """Comprehensive spell checking"""
        words = re.findall(r'\S+', text)
        
        spelling_errors = {}
        for word in words:
            if word not in self.dictionary and word not in self.stopwords:
                corrections = self.find_corrections(word)
                if corrections:
                    spelling_errors[word] = corrections
        
        return spelling_errors
    
    def auto_correct(self, text: str) -> str:
        """Automatically correct text using best suggestions"""
        errors = self.spell_check(text)
        corrected_words = []
        
        for word in text.split():
            if word in errors:
                corrected_words.append(errors[word][0][0])  # Take the first suggestion
            else:
                corrected_words.append(word)
        
        return ' '.join(corrected_words)
