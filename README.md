# Code completion task

There are several ways to do code complitions - on a token, line, method, or document level. 
In this task it was not clearly stipulated on what level the code complition needs to be. 
However, given that the links provided pointed to *method* complition dataset this is what I will be trying to achieve. 
For that, I would need to create a dataset, similar to Python CodeXGLUE, having _signature, docstring, and body_ for each method. 

Before I started with parsing the Kotlin files using Python, I need to familiarse myself with Kotlin files. 
I first considered a smaller project ([this one](https://github.com/TheAlgorithms/Kotlin)) and developed the _kotlin method extraction_ based on this one. 
To parse the files and create the kotlin method dataset, I decided to use regular expressions and code it in Python. I am aware of the shortcomings of this approach - as you can see from my Kotlin parser there are many methods that are ignored, because of a missing asterix or an extra line after the docstring. Some might argue that this approach is then prefered exactly because it extracts only "proper" code, written in accordance to rules. I am not the one to judge in this case. If time had allowed me, I would have taken a different approach - e.g. using IntelliJ IDEA and writing a plug-in that extracts the methods from the Kotlin files. 

## How to make the _Kotlin method dataset_
```
git clone https://github.com/JetBrains/kotlin.git
python run kotlin_file_extraction.py
```
Running that code would result in the the dataset ```big_kotlin.jsonl```

After creating the Kotlin dataset and downloading the Python one, I tried using the pretrained language model Phi 1.5. Important point of consideration is how would the result of the model be truncated. I found that the model generates the function I've asked for and then continues to generate code - giving an example or writing anotheer functions. 

The simplest solution I though of is to look at the indentation. Luckily, python is a language in which indentation plays a big role of defining the scope of classes, functions, and methods in general. Thus I decided to cut the generated result when there is no indent anymore. Similarly for Kotlin, I would orient myself by the {} brakets. This of course is the simplest solution, which neglects many alternatives.

Now that I have the "ground thruth" from the dataset and a generated code, the next big problem is to consider how to compare the solutions. This is a big task/problem that requires research by itself. While reading about codeXGLUE, I noticed that the evaluator used in the project makes use of a python libabry _fuzzywuzzy_ (https://github.com/microsoft/CodeXGLUE/tree/main/Code-Code/Method-Generation#evaluator)

The next step would be to fine-tune it. This is done by traning the model 

Main points for improvement:
- Kotlin parser
- Model output parser

## Code 

Start by running
git clone https://huggingface.co/datasets/microsoft/codexglue_method_generation
git clone https://github.com/JetBrains/kotlin.git
