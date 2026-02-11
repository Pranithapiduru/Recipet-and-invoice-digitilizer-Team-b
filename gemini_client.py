import json  # Standard IDE sync complete
import google.generativeai as genai  # type: ignore
from ai.prompts import RECEIPT_EXTRACTION_PROMPT, DATA_ANALYSIS_PROMPT, CHAT_WITH_DATA_PROMPT  # type: ignore

class GeminiClient:
    """
    Client for interacting with Google Gemini 1.5 Flash for receipt analysis.
    """
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API Key is required")
        
        genai.configure(api_key=api_key)  # type: ignore
        
        # Dynamic Model Selection
        self.model = None
        try:
            # List available models to find one that works
            available_models = []
            for m in genai.list_models():  # type: ignore
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            
            # Prioritize models
            preferred_order = ["models/gemini-1.5-flash", "models/gemini-1.5-pro", "models/gemini-pro"]
            
            # Check for matches
            for preferred in preferred_order:
                if preferred in available_models:
                    self.model = genai.GenerativeModel(preferred)  # type: ignore
                    # print(f"Selected Gemini Model: {preferred}")
                    break
            
            # If no strict match, look for partials
            if not self.model:
                for m in available_models:
                    if "flash" in m:
                        self.model = genai.GenerativeModel(m)  # type: ignore
                        break
                
            if not self.model and available_models:
                 self.model = genai.GenerativeModel(available_models[0])  # type: ignore
                 
        except Exception as e:
            print(f"Error listing models: {e}. Falling back to default.")

        # Hard fallback if listing failed or no model found
        if not self.model:
             self.model = genai.GenerativeModel("gemini-1.5-flash")  # type: ignore

    def _generate_content_safe(self, prompt_parts):
        if not self.model:
            raise RuntimeError("Gemini model not initialized")
        try:
            return self.model.generate_content(prompt_parts)
        except Exception as e:
             # Logic for 404 is now mostly handled by init choice, but keep safety
            if "404" in str(e) or "not found" in str(e).lower():
                 # If current failed, try Pro legacy one last time
                 print("Current model failed, trying gemini-pro")
                 return genai.GenerativeModel("gemini-pro").generate_content(prompt_parts)  # type: ignore
            raise e

    def extract_receipt(self, image):
        """
        Sends the receipt image to Gemini 1.5 Flash for structured extraction.
        Returns a dict matching the schema or None on failure.
        """
        try:
            response = self._generate_content_safe([RECEIPT_EXTRACTION_PROMPT, image])
            text = response.text.strip()
            
            # Use regex to find the JSON block
            import re
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                json_str = match.group()
                data = json.loads(json_str)
                
                # Ensure all required keys exist with defaults
                defaults = {
                    "bill_id": "UNKNOWN",
                    "vendor": "Unknown Vendor",
                    "category": "Uncategorized",
                    "date": "2024-01-01",
                    "amount": 0.0,
                    "tax": 0.0,
                    "subtotal": 0.0,
                    "items": []
                }
                
                for key, default in defaults.items():
                    if key not in data:
                        data[key] = default
                    elif data[key] is None:
                        data[key] = default
                        
                # Type safety for amount/tax
                try:
                    data["amount"] = float(data["amount"])
                except:
                    data["amount"] = 0.0
                    
                try:
                    data["tax"] = float(data["tax"])
                except:
                    data["tax"] = 0.0
                    
                try:
                    data["subtotal"] = float(data["subtotal"])
                except:
                    data["subtotal"] = 0.0

                return data
            return None
        except Exception as e:
            print(f"Error extracting receipt: {e}")
            return None

    def generate_insights(self, data_summary):
        """
        Generates spending insights based on the dataframe summary string.
        """
        try:
            prompt = f"{DATA_ANALYSIS_PROMPT}\n\nData:\n{data_summary}"
            response = self._generate_content_safe(prompt)
            return response.text
        except Exception as e:
            return f"Error generating insights: {e}"

    def chat_with_data(self, query, context_str):
        """
        Answers user questions based on the provided data context.
        """
        try:
            prompt = CHAT_WITH_DATA_PROMPT.format(context=context_str, question=query)
            response = self._generate_content_safe(prompt)
            return response.text
        except Exception as e:
            return "Sorry, I encountered an error analyzing the data."
