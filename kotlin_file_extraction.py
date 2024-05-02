import os
import re
import json

def find_kotlin_files(start_dir):
    """
    This function takes a root directory and finds all kotlin files (i.e. files with .kt extension) in that folder. 
    It saves the paths to all the kotlin files as a list of strings
     
    Parameters : 
        start_dir (String): 
    
    Returns:
        kotlin_files (list[String]): list of all the kotlin files
    """
    kotlin_files = []
    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if file.endswith('.kt'):
                full_path = os.path.join(root, file)
                kotlin_files.append(full_path)
    return kotlin_files

def extract_methods(files, to_print = True):
    """
    This function takes a kotlin file and parses through it to find each method with accompanied docstring.
     
    Parameters : 
        files (String): the kotlin file at interest
        to_print (Boolean): boolean variable allowing the function to print intra-process information 

    Returns:
        methods_with_docstrings (list[String]): list of all kotlin methods
    """
    fail = 0
    methods_with_docstrings = []
    for file in files:
        f = open(file, 'r').read()

        pattern = r"/\*\*[\s\S]*?\*/\s*(?:public\s+|private\s+|tailrec\s+|protected\s+)?fun\s+\w+\([\s\S]*?\)\s*:\s*\w+\s*\{[\s\S]*?\}"

        matches = re.findall(pattern, f, re.DOTALL)
        if to_print:
            if len(matches) == 0 :
                print('\033[36m' + f"I found no methods in the file {file}" + "\033[30m")
                fail +=1
            else :
                print('\033[3m' + f"I found methods in the file {file}" + "\033[30m")

        for match in matches:
            methods_with_docstrings.append(match.strip())

    if to_print:
        print('\033[36m' + f"Number of files that I didn't find a method in {fail}" + "\033[30m")

    return methods_with_docstrings

def create_kotlin_jsonl(methods_with_docstrings, filename):
    """
    This function takes a list of kotlin methods, and creates a list of dictionaries.
    Each dictonary has a docstring, modifier, signature and body. 
    It saves those dictionaries in a jsonl file under the name _filename_
     
    Parameters : 
        methods_with_docstrings (list[String]): list of kotlin methods
        filename (String): filename for the jsonl kotlin dataset

    """
    with open(filename, "w") as outfile:
    
        pattern = r"""
                    (?P<docstring>/\*\*[\s\S]*?\*/)
                    \s*
                    (?P<modifiers>(public\s+|private\s+|protected\s+)?\s*)?
                    (?P<signature>fun\s+\s*\w+\s*\([^)]*\)\s*:\s*\w+)
                    \s*
                    (?P<body>\{[\s\S]*?\})"""
        for c, method in enumerate(methods_with_docstrings):
            match = re.search(pattern, method, re.VERBOSE)
            if match:
                docstring = match.group('docstring')
                docstring = re.sub(r'[^\w\s]', '', docstring).replace("\n", "")
                docstring = re.sub(r'\s+', ' ', docstring)
                modifier = match.group('modifiers')
                signature = match.group('signature')
                body = match.group('body').replace("\n", "<EOL>")
                body = re.sub(r'\s+', ' ', body)
                dict = {"docstring" : docstring, 
                        "modifier" : modifier,
                        "signature" : signature, 
                        "body" : body}

                json.dump(dict, outfile)
                if c != len(methods_with_docstrings)-1 :
                    outfile.write("\n")


if __name__ == "__main__":

    start_dir = "kotlin"
    kotlin_files = find_kotlin_files(start_dir)
    print(f"There are {len(kotlin_files)} Kotlin files")
    methods_with_docstrings = extract_methods(kotlin_files, False)
    # for method in methods_with_docstrings:
    #     print(method)
    #     print("\n---\n") 
    print('\033[35m' + f"The number of extracted methods is {len(methods_with_docstrings)}")
    create_kotlin_jsonl(methods_with_docstrings, "big_kotlin.jsonl")

