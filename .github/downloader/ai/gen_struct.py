import os
import json
import openai
import argparse
from openai import OpenAI
from dotenv import load_dotenv
import base64

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')
model_name = os.getenv('OPENAI_MODEL_NAME')
if not model_name:
    model_name = "gpt-4o"
temperature = os.getenv('OPENAI_TEMPERATURE')
if not temperature:
    temperature = 0.7
client = OpenAI()

def read_file(file_path):
    """Read the content of the input file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def write_file(file_path, content):
    """Write the content to the output file."""
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def encode_image(image_path):
    """Encode image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_cleanup_content(content, schema, image_path=None):
    """Send the prompt and content to OpenAI's API and get the structured content."""
    
    messages = [
        {"role": "system", "content": f"You are a helpful assistant that generates structured output based on the following JSON schema: {json.dumps(schema)}"}
    ]

    # Prepare user message with optional image
    if image_path:
        base64_image = encode_image(image_path)
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": content
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        })
    else:
        messages.append({"role": "user", "content": content})

    completion = client.chat.completions.create(
        model=model_name,
        messages=messages,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "schema": schema,
                "strict": True
            }
        }
    )

    return json.loads(completion.choices[0].message.content)

def main():
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Generate a structured version of a text file using OpenAI's GPT-4."
    )
    parser.add_argument('input_file', help='Path to the input .txt file')
    parser.add_argument('output_file', help='Path to save the structured output file')
    parser.add_argument('schema_file', help='Path to the JSON schema file')
    parser.add_argument('--image', help='Optional path to an image file', default=None)

    args = parser.parse_args()

    try:
        # Read input file
        input_content = read_file(args.input_file)

        # Read schema file
        schema = json.loads(read_file(args.schema_file))

        # Generate structured content with optional image
        structured_content = generate_cleanup_content(input_content, schema, args.image)

        # Write to output file
        write_file(args.output_file, json.dumps(structured_content, indent=2))

        print(f"Successfully processed '{args.input_file}' and saved structured output to '{args.output_file}'.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
