# Daring Mechanician

The [**Daring Mechanician** ](https://github.com/liebke/mechanician) project provides several Python packages for building Generative AI-enabled applications where the AIs themselves are provided tools to use, an approach that can be described as **Tool Augmented Generation** (**TAG**), and the tool-wielding Generative AIs can be described as **Tool Augmented Generative AIs** (**TAG AIs**).

The core `mechanician` package provides modules for building, testing, and tuning *TAG AIs* and the tools that these AIs use, including support for AI-driven testing and AI-assisted *tuning* of the instruction sets given to an AI that we call **Instruction Auto-Tuning** (IAT). 

The `mechanician-openai` package provides `AIConnectors` for both OpenAI's *Chat* API and *Assistants* API, and there are plans to create connectors for more LLMs with *tool-call* support, especially local LLMs.

The `mechanician-arangodb` module provides `AITools` that let AIs interact with the [ArangoDB](https://arangodb.com) graph database.


# Tool Augmented Generation (TAG)

Foundation Models are inherently limited by the scope of their training data and the static nature of that data, **Tool Augmented Generation** (**TAG**) provides AIs with tools that let them interact with databases, APIs, and code libraries, enhancing their knowledge and capabilities and giving them access to up-to-date information, the ability to perform computations, and to interact with external systems, and can provide them a form of memory that spans multiple *context windows*, like what OpenAI announced [here](https://openai.com/blog/memory-and-new-controls-for-chatgpt).

In contrast to **Retrieval Augmented Generation** (RAG), which uses a knowledge base to retrieve information and augment the *prompt* sent to an AI, **Tool Augmented Generative AIs** can retrieve information themselves, and also perform actions across multiple systems, databases, and APIs, extending *Generative AIs* from pure knowledge repositories to active participants in information processing and generation.

>NOTE: You can build a RAG application using a TAG AI to create a **RAGTAG AI** Application.

*TAG* leverages the "**Function Calling**", or "**Tool Calling**", capabilities available in several Large Language Models, including *OpenAI's GPT*, and is meant to complement other approaches to augmenting Foundation Models, like **Retrieval Augmented Generation** (RAG) and **Fine Tuning** (FT). 


## Designing Tools for AIs to Use

TAG AIs can be observed performing multi-step problem solving, driven by the feedback provided by their tools, and learning to use those tools effectively through that feedback, so it is necessary for the tools to provide effective feedback, often through natural language, when reporting errors or providing results.

Generative AIs will learn from their mistakes and successes, if the tools provide feedback that the AI can learn from.

See [Getting Started with Daring Mechanician](#getting-started-with-daring-mechanician) for an example of how to build a **Tool Augmented Generative AI** (TAG AI).


## Instruction Tuning (IT)

In addition to learning from the feedback provided by the tools they use, TAG AIs can learn from the feedback they receive from users.

But since TAG AIs do not necessarily undergo further training, or Fine Tuning, that permanently encodes what they learned, they can only learn within the *context window* where feedback is received, and must start from scratch during the next session.

In order to make these learned behaviors persistent, they must be captured through a process of **Instruction Tuning**, or *prompt engineering*, where the initial instructions provided to the AI, the instructions provided for the tools the AI can use, and the feedback provided by those tools are revised and improved, incorporating lessons learned during interactions with users.

This process starts with creating an initial set of *AI Instructions*, *Tool Instructions*, and *Tool Feedback*, that are used to guide the AI's behavior and responses, and then iteratively refining those instructions and tool feedback based on the AI's performance during interactions with users.

At the start of this process, the prompting provided to the AI often consists of explicit and detailed steps, but as the process proceeds, you sometimes discover that the AI doesn't need such detailed prompting, and that more general prompting approach can be used, letting it will work out the details on its own, and other times you discover the reverse where the AI makes incorrect assumptions, and more explicit prompting is required.

In order to speed up this process, it is useful to use an **Evaluator AI** that acts as an *user surrogate*, interactively eliciting responses from the AI as the two work through multi-step tasks. See [Getting Started with AI-Driven Testing](#getting-started-with-ai-driven-testing) for more information on *Evaluator AIs*.

## Instruction Auto-Tuning (IAT)

By observing an AI's interactions with users and other AIs, an *Instructor AI* can refine and update the AI's current instructions and the instructions describing the tools the AI can use.

The Instructor AI is given the AI's current set of instructions, instructions for the tools used by the AI, and the transcript of interactions between the AI and a User (or Evaluator AI), including the AI *tool calls* and responses.

See [Getting Started with Instruction Auto-Tuning](#getting-started-with-instruction-auto-tuning) for an example of how to use the **Instruction Auto-Tuning** (IAT) process to refine the instructions for a **Movie Database Assistant**.


## AI-Driven Testing

See [Getting Started with AI-Driven Testing](#getting-started-with-ai-driven-testing) for an example of how to use the **AI-Driven Testing** process.
