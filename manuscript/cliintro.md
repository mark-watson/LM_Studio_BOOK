# Using the LM Studio Command Line Interface (CLI)

While the LM Studio UI application is convenient to use for chatting, using LM Studio as a RAG system, etc., the command line interface is also useful because a command line interface (CLI) is often a much faster way to get work done.

You can refer to the official documentation [https://lmstudio.ai/docs/cli](https://lmstudio.ai/docs/cli). Here we will look at a few examples:

## lms ls

```console
$ lms ls

You have 6 models, taking up 42.23 GB of disk space.

LLMs (Large Language Models)        PARAMS ARCHITECTURE  SIZE
qwen3moe                                                 13.29 GB
qwen3-30b-a3b-instruct-2507-mlx            qwen3_moe     17.19 GB
qwen/qwen3-30b-a3b-2507                    qwen3_moe     17.19 GB
google/gemma-3n-e4b                        gemma3n        5.86 GB  ✓ LOADED
liquid/lfm2-1.2b                           lfm2           1.25 GB

Embedding Models                   PARAMS      ARCHITECTURE          SIZE
text-embedding-nomic-embed-text-v1.5           Nomic BERT        84.11 MB
```

## lms load <model_key>

A model key is the first item displayed on an output line when you run **llm ls**.

```console
$ lms load google/gemma-3n-e4b 

Loading model "google/gemma-3n-e4b"...
Model loaded successfully in 13.59s. (5.86 GB)
To use the model in the API/SDK, use the identifier "google/gemma-3n-e4b:2".
To set a custom identifier, use the --identifier <identifier> option.
```

## lms unload

**lms unload** takes an optional <model_key>. If you don't specify a model key then you will be shown a list of loaded models and you can interactively unload models:

```console
$ lms unload

! Use the arrow keys to navigate, type to filter, and press enter to select.
! To unload all models, use the --all flag.

? Select a model to unload | Type to filter...
   qwen3-30b-a3b-instruct-2507-mlx
❯  google/gemma-3n-e4b  
```

## lms get

**lms get** supports searching for models on Huggingface by name and interactively downloading them. Here is an example:

```console
$ lms get llama-3.2 --mlx --gguf --limit 6
Searching for models with the term llama-3.2
No exact match found. Please choose a model from the list below.

! Use the arrow keys to navigate, and press enter to select.

? Select a model to download (Use arrow keys)
❯ [Staff Pick] Hermes 3 Llama 3.2 3B 
  [Staff Pick] Llama 3.2 1B Instruct 4bit 
  [Staff Pick] Llama 3.2 3B Instruct 4bit 
  [Staff Pick] Llama 3.2 1B 
  [Staff Pick] Llama 3.2 3B 
  DavidAU/Llama-3.2-8X3B-MOE-Dark-Champion-Instruct-uncensored-abliterated-18.4B-GGUF 
```

## Server Statsu and Control

```console
$ lms server status
The server is running on port 1234.
Marks-Mac-mini:api_introduction $ lms server stop
Stopped the server on port 1234.
Marks-Mac-mini:api_introduction $ lms server start
Starting server...
Success! Server is now running on port 1234
Marks-Mac-mini:api_introduction $ lms ps

   LOADED MODELS   

Identifier: google/gemma-3n-e4b
  • Type:  LLM 
  • Path: google/gemma-3n-e4b
  • Size: 5.86 GB
  • Architecture: gemma3n
```
