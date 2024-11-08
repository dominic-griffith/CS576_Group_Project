import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
import sentencepiece

def generate_api_command(model, tokenizer, text, device, max_length=50):
    model.eval()
    input_ids = tokenizer.encode(text, return_tensors='pt').to(device)
    with torch.no_grad():
        generated_ids = model.generate(
            input_ids=input_ids,
            max_length=max_length,
            num_beams=5,
            early_stopping=True
        )
    pred = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    return pred

def main():
    # Specify the path to your saved model
    model_path = 'content/model_save/'

    # Load the tokenizer
    tokenizer = T5Tokenizer.from_pretrained(model_path)

    # Load the model
    model = T5ForConditionalGeneration.from_pretrained(model_path)
    model.eval()

    # Move the model to the appropriate device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model.to(device)

    print("Welcome to the Home Assistant Command Parser!")
    print("Type 'exit' to quit.")
    while True:
        user_input = input("Enter a command: ")
        if user_input.lower() == 'exit':
            break
        api_command = generate_api_command(model, tokenizer, user_input, device)
        print(f"Parsed API Command: {api_command}")
        print("-" * 50)

if __name__ == "__main__":
    main()
