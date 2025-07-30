# Preface

LM Studio allows you to run LLMs locally on your own computer. The LM Studio app is not open source but it is free to use for personal use and/or internal business purposes. I suggest, dear reader, that you read their [terms of service](https://lmstudio.ai/app-terms). You can also bookmark LM Studio’s [online documentation](https://lmstudio.ai/docs/app).

I (Mark Watson) have been a paid AI Practitioner and Researcher since 1982. Since 2013 I have worked on AI-related projects at Google, Capital One, and five startups. You can read more about me at [https://markwatson.com](https://markwatson.com).

## Setup LM Studio

This book serves as your comprehensive guide to LM Studio, a powerful desktop application designed for developing and experimenting with Large Language Models (LLMs) locally on your computer. Building on your foundational knowledge of running local models, perhaps from reading the book “Ollama in Action: Building Safe, Private AI with LLMs, Function Calling and Agents” (read free online: [https://leanpub.com/ollama/read](https://leanpub.com/ollama/read) for the alternative local LLM tool Ollama, this book will delve specifically into how LM Studio empowers you to leverage your computer's CPU and, optionally, its GPU, to run openly available LLMs such as Llama 3.3, Phi-4, and Gemma 3. LM Studio provides a familiar chat interface and robust search and download functionality via Hugging Face, making it incredibly intuitive to get started. It supports running LLMs using llama.cpp on Mac, Windows, and Linux, and additionally supports Apple's MLX on Apple Silicon Macs, ensuring broad compatibility.

To begin our journey with LM Studio, the process is straightforward: first, install the latest version of the application for your operating system from [https://lmstudio.ai/downloa](https://lmstudio.ai/download). Once installed, you will download your preferred LLM directly within LM Studio from the Discover tab, choosing from curated options or searching for specific models. I will often use the model **google/gemma-3n-e4b** in this book because is is a small yet highly effective model.

After downloading the app, install with the "developer option" and then install at least one model, the next step is to load the model into your computer's memory via the Chat tab, a process that allocates the necessary memory for the model's weights and parameters. LM Studio also enhances your interaction by allowing you to chat with documents entirely offline, a feature known as "RAG" (Retrieval Augmented Generation), enabling completely private and local document interaction.

For streamlined workflows, LM Studio introduces Presets, which allow you to bundle system prompts and other inference parameters like Temperature, Top P, or Max Tokens into reusable configurations, and you can even set Per-model Defaults for load settings such as GPU offload or context size.

A significant focus of this book will be on leveraging LM Studio as a local API endpoint for your applications and scripts. LM Studio provides a REST API that allows you to interact with your local models programmatically. You'll learn how to utilize both the OpenAI Compatibility API and the newer LM Studio REST API (beta), enabling seamless integration with existing tools and new development. The LM Studio product offers dedicated client libraries, including lmstudio-python and lmstudio-js. This book will particularly emphasize Python client code examples, guiding you through building custom applications that harness the power of your locally running LLMs.

Beyond core functionality, LM Studio offers advanced capabilities that we will explore. These include features like Structured Output, Tools and Function Calling, and Speculative Decoding, which can significantly enhance your LLM interactions. 

Additionally, with the introduction of Model Context Protocol (MCP) Host capabilities in LM Studio 0.3.17, you can connect MCP servers to your app, enabling advanced functions like model and dataset search. **It is crucial to be aware that some MCP servers can run arbitrary code, access local files, and use your network connection, so caution is advised when installing MCPs from untrusted sources.** Throughout your journey, remember that the LM Studio community on Discord is a valuable resource for support, sharing knowledge, and discussing everything from models to hardware.

By the end of this book, you will not only be proficient in running and managing various LLMs locally within LM Studio's intuitive environment but also expert in integrating these powerful models into your own applications via its versatile API.

### Advantages of Running Local LLMs

A main theme of this book are the advantages of running models privately on either your personal computer or a computer at work. While many commercial LLM API venders like OpenAI, Google, and Anthropic may have options to not reuse your prompt data and the output generated from your prompts to train their systems,
there is no better privacy and security than running open weight
models on your own hardware. There have been many tech news articles warning that often commercial LLM API venders store your data even after you ask for it to be deleted.

After a short tutorial on running the LM Studio application interactively, this book is largely about running Large Language Models (LLMs) on your own hardware using LM Studio.

To be clear dear reader, although I have a strong preference to running smaller LLMs on my own hardware, I also frequently use commercial LLM API vendors like Anthropic, OpenAI, ABACUS.AI, GROQ, and Google to take advantage of features like advanced models and scalability using cloud-based hardware.

## About the Author

I am an AI practitioner and consultant specializing in large language models, LangChain/Llama-Index integrations, deep learning, and the semantic web. I have authored over 20 books on topics including artificial intelligence, Python, Common Lisp, deep learning, Haskell, Clojure, Java, Ruby, the Hy language, and the semantic web. I have 55 U.S. patents. Please check out my home page and social media: my personal web site [https://markwatson.com](https://markwatson.com), [X/Twitter](https://x.com/mark_l_watson), [my Blog on Blogspot](https://mark-watson.blogspot.com), and [my Blog on Substack](https://marklwatson.substack.com)

## Requests from the Author

This book will always be available to read free online at [https://leanpub.com/LMstudio/read](https://leanpub.com/LMstudio/read).

That said, I appreciate it when readers purchase my books because the income enables me to spend more time writing.

### Hire the Author as a Consultant

I am available for short consulting projects. Please see [https://markwatson.com](https://markwatson.com).

## Why Should We Care About Privacy?

Running local models can enhance privacy when dealing with sensitive data. Let's delve into why privacy is crucial and how LM Studio contributes to improved security.

Why is privacy important?

Privacy is paramount for several reasons:

- Protection from Data Breaches: When data is processed by third-party services, it becomes vulnerable to potential data breaches. Storing and processing data locally minimizes this risk significantly. This is especially critical for sensitive information like personal details, financial records, or proprietary business data.
- Compliance with Regulations: Many industries are subject to stringent data privacy regulations, such as GDPR, HIPAA, and CCPA. Running models locally can help organizations maintain compliance by ensuring data remains under their control.
- Maintaining Confidentiality: For certain applications, like handling legal documents or medical records, maintaining confidentiality is of utmost importance. Local processing ensures that sensitive data isn't exposed to external parties.
- Data Ownership and Control: Individuals and organizations have a right to control their own data. Local models empower users to maintain ownership and make informed decisions about how their data is used and shared.
- Preventing Misuse: By keeping data local, you reduce the risk of it being misused by third parties for unintended purposes, such as targeted advertising, profiling, or even malicious activities.


