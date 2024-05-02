import torch
import json
import re
from fuzzywuzzy import fuzz
from transformers import AutoModelForCausalLM, AutoTokenizer

def format_code(s):
    """
    This function is used for parsing the CodeXGLUE python dataset
    and the big_kotlin dataset. Those datasets includes <EOL> and 
    <INDENT>/<DEDENT> tags, used for representing methods on a signle line. 
    
    This function recreates the otiginal structure of the code
     
    Parameters : 
        s (String): code with tags <EOL> and <INDENT>/<DEDENT>
    
    Returns:
        _ (String): code
    """
    lines = s.replace('<EOL>', '\n').split('\n')
    indent_level = 0
    indent_size = 3 
    formatted_lines = []

    for line in lines:
        if '<INDENT>' in line:
            indent_level += 1
            line = line.replace('<INDENT>', '')
        if '<DEDENT>' in line:
            indent_level -= 1
            line = line.replace('<DEDENT>', '')
        
        if line.strip():
            indented_line = ' ' * (indent_size * indent_level) + line
            formatted_lines.append(indented_line)
        else:
            formatted_lines.append(line)
    
    return '\n'.join(formatted_lines)

def truncate_model_output_python(model_output):
    """
    This function takes raw output from a query to a pretrained transformer model
    and parses it such that only the queried method is selected. 
    This is getting done by using the indents python code uses to scope methods.
     
    Parameters :  
        model_output (string): python code
    
    Returns:
        _ (String): python code (only method)
    """
    indent = "   "
    parsed_output = ""
    for line in model_output.split("\n")[1:]:
        if line.startswith(indent) :
            parsed_output += line + "\n"
        else : 
            break
    return parsed_output

def gen_python_code(model, tokenizer, model_input):
    """
    This function takes a pretrained transformer model with tokenizer and queries the model to generate 
    python method given its signature and docstring. The model output is then parsed and returned.
     
    Parameters : 
        model (AutoModelForCausalLM): pretrained transformer
        tokenizer (AutoTokenizer): pretrained tokenizer 
        model_input (dict): python dict consisting of signature, docstring, body
    
    Returns:
        _ (String): python code
    """
    signature = model_input['signature']
    docstring = model_input['docstring']

    network_input = f'''{signature}  \n """{docstring}"""'''

    print("###############################")
    print("The input I pass to the network : ")
    print(network_input)

    inputs = tokenizer(network_input, return_tensors="pt", return_attention_mask=False).to(device)

    outputs = model.generate(**inputs, max_length=200)
    model_output = tokenizer.batch_decode(outputs)[0]

    print("###############################")
    print("Before I parse it : ")
    print(model_output)

    return truncate_model_output_python(model_output)

def truncate_model_output_kotlin(model_output):
    """
    This function takes raw output from a query to a pretrained transformer model
    and parses it such that only the queried method is selected. 
    This is getting done by using the {} kotlin code uses to scope methods.
     
    Parameters :  
        model_output (string): kotlin code
    
    Returns:
        _ (String): kotlin code (only method)
    """
    regex = r"\{[\s\S]*?\}"
    match = re.search(regex, model_output, re.DOTALL)
    if match == None :
        regex = r"\{[\s\S]*"
        match = re.search(regex, model_output, re.DOTALL)
        return match[0] if match != None else model_output
    return match[0]

def gen_kotlin_code(model, tokenizer, model_input):
    """
    This function takes a pretrained transformer model with tokenizer and queries the model to generate 
    python method given its signature and docstring. The model output is then parsed and returned.
     
    Parameters : 
        model (AutoModelForCausalLM): pretrained transformer
        tokenizer (AutoTokenizer): pretrained tokenizer 
        model_input (dict): kotlin dict consisting of signature, docstring, body
    
    Returns:
        _ (String): kotlin code
    """
    signature = model_input['signature']
    docstring = model_input['docstring']

    network_input = f'/*{docstring}*/ \n {signature}'

    print("###############################")
    print("The input I pass to the network : ")
    print(network_input)

    inputs = tokenizer(network_input, return_tensors="pt", return_attention_mask=False).to(device)

    outputs = model.generate(**inputs, max_length=200)
    model_output = tokenizer.batch_decode(outputs)[0]

    return truncate_model_output_kotlin(model_output)

if __name__ == "__main__":
    device = torch.device("mps") # note : this needs to be changed to whatever machine this code is run on

    model = AutoModelForCausalLM.from_pretrained("microsoft/phi-1_5", torch_dtype="auto").to(device)
    tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-1_5")


    example_case = 74
    # f = open('codexglue_method_generation/train.jsonl', 'r')                        # ---> for python
    f = open('big_kotlin.jsonl', 'r')                                               # ---> for kotlin
    model_input = [json.loads(jline) for jline in f]
    f.close()

    # model_output = gen_python_code(model, tokenizer, model_input[example_case])     # ---> for python
    model_output = gen_kotlin_code(model, tokenizer, model_input[example_case])     # ---> for kotlin


    print("###############################")
    print("After I parsed it: ")
    print('\033[35m' + model_output + '\033[30m') 

    print("###############################")
    print("What the real output is : ")
    real_output = format_code(model_input[example_case]['body'])
    print("\033[0;36m" + real_output + '\033[30m')

    print("The closeness is : ", fuzz.ratio(model_output, real_output))

