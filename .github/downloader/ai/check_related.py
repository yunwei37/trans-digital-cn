import yaml
import json
import tempfile
import subprocess
import os
from pathlib import Path

def load_template(template_path):
    """Load the template file"""
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()

def get_ai_classification(title, link, snippet, gen_struct_path, template):
    """Ask AI to classify if the content is related"""
    # Define the JSON schema for classification
    schema = {
        "type": "object",
        "properties": {
            "is_related": {
                "type": "string",
                "enum": ["True", "False", "NotSure"],
                "description": "Whether the content is related to transgender/LGBTQ+ topics"
            }
        },
        "required": ["is_related"],
        "additionalProperties": False
    }

    # Create temporary files
    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as temp_input:
        # Fill in the template
        prompt = template.format(
            title=title or "Untitled",
            link=link,
            snippet=snippet or ""
        )
        temp_input.write(prompt)
        print(f"Prompt: {prompt}")
        temp_input_path = temp_input.name

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_schema:
        json.dump(schema, temp_schema)
        schema_file = temp_schema.name

    with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.json') as temp_output:
        temp_output_path = temp_output.name

    try:
        # Run gen_struct.py
        subprocess.run([
            'python', gen_struct_path,
            temp_input_path, temp_output_path, schema_file
        ], check=True)

        # Read the result
        with open(temp_output_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        print(f"Result: {result}")
        return result["is_related"].lower()  # Convert to lowercase to match YAML
    except Exception as e:
        print(f"Error during AI classification: {e}")
        return "unknown"
    finally:
        # Cleanup temporary files
        os.unlink(temp_input_path)
        os.unlink(temp_output_path)
        os.unlink(schema_file)

def main():
    # File paths
    links_path = Path('.github/links.yml')
    template_path = Path('.github/prompts/check_related.md.template')
    gen_struct_path = Path('.github/scripts/ai/gen_struct.py')

    # Load files
    with open(links_path, 'r', encoding='utf-8') as f:
        links_data = yaml.safe_load(f)

    template = load_template(template_path)

    # Process each unknown entry
    modified = False
    for url, data in links_data.items():
        if not data.get('is_related') or data.get('is_related') == 'unknown':
            print(f"Processing: {url}")
            result = get_ai_classification(
                data.get('title'),
                data.get('link'),
                data.get('snippet'),
                gen_struct_path,
                template
            )
            
            if result != 'unknown':
                data['is_related'] = result
                modified = True
                print(f"Updated {url} to {result}")
                # Write changes immediately
                with open(links_path, 'w', encoding='utf-8') as f:
                    yaml.dump(links_data, f, allow_unicode=True)
                print("Changes saved to links.yml")
            else:
                print(f"Skipping {url} because the result is unknown")
        else:
            print(f"Skipping {url} because the result is already known")

    # Remove final save since we're saving after each update
    if not modified:
        print("No changes were necessary")

if __name__ == "__main__":
    main()
