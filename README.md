# Spelling-corrector-and-grammar-checker-for-Sinhala

This project aims to develop a Sinhala spell and grammar checker that detects and corrects spelling and 
grammatical errors in Sinhala text. It includes a spell checker for automatic error correction and a 
grammar checker to identify and fix contextual grammatical issues. Three AI approaches such as Rule
based, LLM-based, and Retrieval-Augmented Generation with Fine-tuned LLM(XLM-RoBERTa) models 
were evaluated for grammar correction. The most effective approach was selected and tested on five 
paragraphs to measure its accuracy in spelling corrections and grammar suggestions. 



Spell Corrector

![image](https://github.com/user-attachments/assets/aebcc45a-9f99-485d-ba7c-fb2663bc47fe)
![image](https://github.com/user-attachments/assets/37f31f3f-103d-4edb-bf52-151e25bcba78)


1. Rule-Based AI Approach: 
The Sinhala spell and grammar checker uses rule-based AI to correct spelling and grammar errors in 
Sinhala text. It leverages a preprocessed dictionary, phonetic mapping, stemming, and suffix matching to 
identify spelling mistakes and applies similarity metrics for corrections. The grammar checker ensures 
proper subject-verb agreement and word order using a POS tagger, offering accurate corrections for 
spelling and grammar.


![image](https://github.com/user-attachments/assets/dd137a68-102a-4a42-8a5e-88eadfd4f702)
![image](https://github.com/user-attachments/assets/9cff48c5-62ae-4d78-b2c4-199b843faf94)


Retrieval-Augmented Generation (RAG) approach: 
The Sinhala grammar and spell checker uses a RAG approach with LangChain and Google's Gemini model 
to detect and correct errors in Sinhala sentences. It processes grammar rules from a JSON file, splits 
them into chunks for embedding, and stores them in a FAISS vector store for efficient retrieval. Upon 
receiving an input sentence, the system retrieves relevant grammar rules, constructs a prompt, and uses 
Gemini to generate corrections and explanations. The combination of LangChain, FAISS, and Gemini 
allows for accurate and fast error detection and correction.

![image](https://github.com/user-attachments/assets/5b1106ea-191f-4f1b-8ad6-04aaa14e267c)
![image](https://github.com/user-attachments/assets/9e95d49c-0083-4d14-9e9d-f7c5e3f7e4f9)
![image](https://github.com/user-attachments/assets/c8aaaec4-d528-4e38-909d-a6dc2f694d37)
![image](https://github.com/user-attachments/assets/e5b9c088-9b7a-4c76-a4ee-d6c80a165a09)
![image](https://github.com/user-attachments/assets/a516e092-41f9-4fdd-b005-8f7c2364166e)


Fine-tuned LLM approach with the XLM-RoBERTa model: 
The Sinhala grammar and spell checker uses a fine-tuned XLM-RoBERTa model for classifying sentences 
as grammatically correct or incorrect. It processes sentences through tokenization, fine-tunes the model 
with the AdamW optimizer, and evaluates grammar issues like subject-verb agreement and sentence 
structure. The trained model is optimized and ready for deployment to detect and suggest corrections 
for errors in Sinhala sentences. 

![image](https://github.com/user-attachments/assets/c5cf218f-50a8-4868-99ea-6c6c7538fe50)
![image](https://github.com/user-attachments/assets/0827c746-31b5-44a6-982f-2ba875469fd8)


![image](https://github.com/user-attachments/assets/f75c840c-dfe7-4f3f-a7ef-121c6d16e110)
