# Code completion task

There are several ways to do code complitions - on a token, line, method, or document level. 
In this task it was not clearly stipulated on what level the code complition needs to be. 
However, given that the links provided pointed to *method* complition dataset this is what I will be trying to achieve. 
For that, I would need to create a dataset, similar to Python CodeXGLUE, having _signature, docstring, and body_ for each method. 

Before I started with parsing the Kotlin files using Python, I need to familiarse myself with Kotlin files. 
I first considered a smaller project ([this one](https://github.com/TheAlgorithms/Kotlin), the methods of which can be found in ```small_kotlin.jsonl```) and developed the _kotlin method extraction_ based on this one. 
To parse the files and create the kotlin method dataset, I decided to use regular expressions and code it in Python. I am aware of the shortcomings of this approach - as you can see from my Kotlin parser there are many methods that are ignored, because of a missing asterix or an extra line after the docstring. Some might argue that this approach is then prefered exactly because it extracts only "proper" code, written in accordance to rules. I am not the one to judge in this case. If time had allowed me, I would have taken a different approach - e.g. using IntelliJ IDEA and writing a plug-in that extracts the methods from the Kotlin files. 

## How to make the _Kotlin method dataset_
```
git clone https://github.com/JetBrains/kotlin.git
python run kotlin_file_extraction.py
```
Running that code would result in the the dataset ```big_kotlin.jsonl``` - there are 745 methods in this file

## Downloading the python method dataset and loading the model
To get the python dataset I ran the following in the terminal : 
```
git clone https://huggingface.co/datasets/microsoft/codexglue_method_generation
```
_Note : an alternative is to use the dataset as inpurt from Python library datasets_

After creating the Kotlin dataset and downloading the Python one, I tried using the pretrained language model Phi 1.5. Important point of consideration is how would the result of the model be truncated. I found that the model generates the function I've asked for and then continues to generate code - giving an example or writing anotheer functions. 

The simplest solution I though of is to look at the indentation. Luckily, python is a language in which indentation plays a big role of defining the scope of classes, functions, and methods in general. Thus I decided to cut the generated result when there is no indent anymore. Similarly for Kotlin, I would orient myself by the {} brakets. This of course is the simplest solution, which neglects many alternatives.

Now that I have the "ground truth" from the dataset and a generated code, the next big problem is to consider how to compare the solutions. This is a big task/problem that requires research by itself. While reading about codeXGLUE, I noticed that the evaluator used in the project makes use of a python libabry _fuzzywuzzy_ [link](https://github.com/microsoft/CodeXGLUE/tree/main/Code-Code/Method-Generation#evaluator)

Run the code in file ```model_phi-1-5.py``` to see how the model manages to generate code. So comment and uncomment depending on weather you want python or kotlin code generation. 

The next step would be to fine-tune it. This is done by training the model. For that I need to separate the ```big_kotlin.jsonl``` to traning, development and testing parts and use the _fuzzywuzzy_ as a loss function. Due to computational and time limitations I did not implement this.

## Main points for improvement
- Kotlin parser
- Model output parser
- Evaluation function

As discussed above the current method of extracting kotlin methods from files is not foolproof and needs improvement. Making use of plugins would be better given that in ideal situations we would like to expand the dataset beyond methods. The hardcoding through regex would pose a challenge in those cases. 

The output of the model is long and needs to be parsed. The current methods I have used (based on indents and {}) is not sufficient. This is a major point of improvement, because it is linked to the way the model is queried. 

Lastly, the evaluation funciton is not complex enough for quality fine-tuning of the model. 
