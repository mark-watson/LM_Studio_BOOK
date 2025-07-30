# Using the LM Studio Command Line Interface (CLI)

While the LM Studio UI application is convenient to use for chatting, using LM Studio as a RAG system, etc., the command line interface is also useful because a command line interface (CLI) is often a much faster way to get work done.

You can refer to the official documentation [https://lmstudio.ai/docs/cli](https://lmstudio.ai/docs/cli). Here we will look at a few examples:

## lms ls

```console
$ lms ls

You have 10 models, taking up 85.23 GB of disk space.

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

