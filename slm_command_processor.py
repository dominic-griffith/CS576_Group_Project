import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

class SLMCommandProcessor:
    def __init__(self, model_name='vincenthuynh/SLM_CS576', device='cpu'):
        # Load the model and tokenizer
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)
        self.device = device
        self.model.to(self.device)

    def generate_api_command(self, text, max_length=50):
        """
        Generates an API command from a natural language command using the SLM model.
        
        Parameters:
        text (str): Natural language command
        max_length (int): Maximum length for the generated command

        Returns:
        str: The generated API command
        """
        try:
            input_ids = self.tokenizer.encode(text, return_tensors='pt').to(self.device)
            with torch.no_grad():
                generated_ids = self.model.generate(input_ids=input_ids, max_length=max_length, num_beams=5, early_stopping=True)
            return self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        except Exception as e:
            return None  # Return None if there's an error in processing
