from sinling import SinhalaTokenizer, POSTagger, word_splitter

class SinhalaGrammarChecker:
    def _init_(self):
        self.tokenizer = SinhalaTokenizer()
        self.tagger = POSTagger()
        
    def get_verb_base(self, verb):
        split_result = word_splitter.split(verb)
        if split_result and 'base' in split_result and 'affix' in split_result:
            return split_result['base'], split_result['affix']
        return verb, ''
        
    def get_correct_suffix(self, subject):
        suffix_map = {
            "මම": "මි",
            "අපි": "මු",
        }
        return suffix_map.get(subject, "")
        
    def create_corrected_verb(self, verb_base, correct_suffix):
        
        return f"{verb_base}{correct_suffix}"
        
    def is_sov_order(self, pos_tags):
        
        if len(pos_tags) < 3:
            return False  # Sentence too short to be SOV
        
        subject_tag, object_tag, verb_tag = pos_tags[0][1], pos_tags[1][1], pos_tags[2][1]
        return subject_tag == 'PRP' and object_tag == 'NNC'or'NCV'or'JJ' and verb_tag.startswith('V')
        
    def check_verb_agreement(self, subject, verb):

        verb_base, affix = self.get_verb_base(verb)
        correct_suffix = self.get_correct_suffix(subject)
        
        if not correct_suffix:
            return True, "", None  # No rule for this subject
            
        if affix != correct_suffix:
            corrected_verb = self.create_corrected_verb(verb_base, correct_suffix)
            error_msg = f"Grammar error: Verb '{verb}' (base: {verb_base}, affix: {affix}) should end with '{correct_suffix}' when subject is '{subject}'"
            return False, error_msg, corrected_verb
            
        return True, "", None
        
    def check_grammar(self, sentence):
   
        tokenized_sentences = [self.tokenizer.tokenize(f'{ss}.') for ss in self.tokenizer.split_sentences(sentence)]
        pos_tags = self.tagger.predict(tokenized_sentences)
        
        if not pos_tags or not pos_tags[0]:
            return "Unable to analyze the sentence."
        
        tokens = tokenized_sentences[0]
        tags = pos_tags[0]
        
        # Ensure the sentence follows SOV structure
        if not self.is_sov_order(tags):
            return "Sentence does not follow SOV order."
        
        # Extract Subject and Verb
        subject = tokens[0]
        verb = tokens[-2]  # Assuming verb is second-to-last token
        
        # Check subject-verb agreement
        is_valid, error_message, correction = self.check_verb_agreement(subject, verb)
        if not is_valid:
            # Create corrected sentence by replacing the verb
            tokens[-2] = correction
            corrected_sentence = ' '.join(tokens[:-1])  
            return f"{error_message}\nSuggested correction: {corrected_sentence}"
            
        return "The sentence is grammatically correct."