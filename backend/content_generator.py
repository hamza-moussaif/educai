from langchain_community.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from dotenv import load_dotenv
import json
import requests
import re

load_dotenv()

class ContentGenerator:
    def __init__(self):
        self.api_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if not self.api_token:
            raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables")
        
        self.model_id = "mistralai/Mistral-7B-Instruct-v0.2"
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_id}"
        self.headers = {"Authorization": f"Bearer {self.api_token}"}

    def _generate_text(self, prompt):
        # Ajout d'instructions spécifiques pour le format JSON
        system_prompt = """Tu es un assistant qui génère du contenu pédagogique. 
        IMPORTANT: Ta réponse doit être UNIQUEMENT un tableau JSON valide, sans texte supplémentaire.
        Ne mets pas de texte avant ou après le JSON.
        Ne génère qu'un seul tableau JSON.
        Assure-toi que le JSON est bien formaté et valide."""
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        response = requests.post(
            self.api_url,
            headers=self.headers,
            json={
                "inputs": full_prompt,
                "parameters": {
                    "max_new_tokens": 1000,
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Error from Hugging Face API: {response.text}")
            
        return response.json()[0]["generated_text"]

    def _clean_json_response(self, response):
        # Supprimer tout texte avant le premier '['
        response = response[response.find('['):]
        
        # Supprimer tout texte après le dernier ']'
        response = response[:response.rfind(']')+1]
        
        # Supprimer les numéros d'exercices et le texte associé
        response = re.sub(r'\d+er?\s+exercice:\s*', '', response)
        
        # Nettoyer les espaces et les retours à la ligne
        response = response.strip()
        
        # Remplacer les virgules entre les objets par des virgules correctement formatées
        response = re.sub(r'}\s*,\s*{', '}, {', response)
        
        return response

    def _parse_response(self, response):
        try:
            # Nettoyer la réponse
            cleaned_response = self._clean_json_response(response)
            
            # Essayer de parser le JSON
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            # Si le parsing échoue, essayer de nettoyer davantage
            try:
                # Trouver tous les objets JSON valides
                json_objects = re.findall(r'\{[^}]+\}', cleaned_response)
                if json_objects:
                    # Créer un tableau avec tous les objets trouvés
                    json_array = f"[{','.join(json_objects)}]"
                    return json.loads(json_array)
                else:
                    raise ValueError("No valid JSON objects found in response")
            except Exception as e:
                raise ValueError(f"Failed to parse response: {str(e)}\nResponse: {response}")

    def generate_qcm(self, subject, grade_level, difficulty, quantity):
        prompt = f"""
        Génère {quantity} questions QCM sur le sujet "{subject}" pour le niveau {grade_level}.
        Le niveau de difficulté doit être {difficulty}/10.
        Format JSON attendu:
        [
            {{
                "question": "Question text",
                "options": ["Option 1", "Option 2", "Option 3", "Option 4"],
                "correctAnswer": 0
            }}
        ]
        """
        result = self._generate_text(prompt)
        return {"questions": self._parse_response(result)}

    def generate_exercises(self, subject, grade_level, difficulty, quantity):
        prompt = f"""
        Génère {quantity} exercices pratiques sur le sujet "{subject}" pour le niveau {grade_level}.
        Le niveau de difficulté doit être {difficulty}/10.
        Format JSON attendu:
        [
            {{
                "statement": "Énoncé de l'exercice",
                "solution": "Solution détaillée"
            }}
        ]
        """
        result = self._generate_text(prompt)
        return {"exercises": self._parse_response(result)}

    def generate_fill_in_the_blanks(self, subject, grade_level, difficulty, quantity):
        prompt = f"""
        Génère {quantity} textes à trous sur le sujet "{subject}" pour le niveau {grade_level}.
        Le niveau de difficulté doit être {difficulty}/10.
        Format JSON attendu:
        [
            {{
                "text": "Texte avec [TROU1] et [TROU2]",
                "answers": ["Réponse1", "Réponse2"]
            }}
        ]
        """
        result = self._generate_text(prompt)
        return {"texts": self._parse_response(result)}

    def generate_summary(self, subject, grade_level, difficulty, quantity):
        prompt = f"""
        Génère {quantity} fiches de synthèse sur le sujet "{subject}" pour le niveau {grade_level}.
        Le niveau de difficulté doit être {difficulty}/10.
        Format JSON attendu:
        [
            {{
                "content": "Contenu de la synthèse"
            }}
        ]
        """
        result = self._generate_text(prompt)
        return {"summaries": self._parse_response(result)}

    def generate_concept_map(self, subject, grade_level, difficulty, quantity):
        prompt = f"""
        Génère {quantity} descriptions de schémas conceptuels sur le sujet "{subject}" pour le niveau {grade_level}.
        Le niveau de difficulté doit être {difficulty}/10.
        Format JSON attendu:
        [
            {{
                "description": "Description du schéma conceptuel"
            }}
        ]
        """
        result = self._generate_text(prompt)
        return {"maps": self._parse_response(result)}

    def generate_all_content(self, form_data):
        try:
            content = {}
            
            if form_data.get('contentTypes', {}).get('qcm'):
                content['qcm'] = self.generate_qcm(
                    form_data['subject'],
                    form_data['gradeLevel'],
                    form_data['difficulty'],
                    form_data['quantity']
                )
            
            if form_data.get('contentTypes', {}).get('exercises'):
                content['exercises'] = self.generate_exercises(
                    form_data['subject'],
                    form_data['gradeLevel'],
                    form_data['difficulty'],
                    form_data['quantity']
                )
            
            if form_data.get('contentTypes', {}).get('fillInTheBlanks'):
                content['fillInTheBlanks'] = self.generate_fill_in_the_blanks(
                    form_data['subject'],
                    form_data['gradeLevel'],
                    form_data['difficulty'],
                    form_data['quantity']
                )
            
            if form_data.get('contentTypes', {}).get('summary'):
                content['summary'] = self.generate_summary(
                    form_data['subject'],
                    form_data['gradeLevel'],
                    form_data['difficulty'],
                    form_data['quantity']
                )
            
            if form_data.get('contentTypes', {}).get('conceptMap'):
                content['conceptMap'] = self.generate_concept_map(
                    form_data['subject'],
                    form_data['gradeLevel'],
                    form_data['difficulty'],
                    form_data['quantity']
                )
            
            return content
        except Exception as e:
            raise Exception(f"Error generating content: {str(e)}") 