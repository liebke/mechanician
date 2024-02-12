# Daring Mechanician

[**Daring Mechanician** ](https://github.com/liebke/mechanician) is a Python library for building tools that use AI by building tools that AIs use. 

The approach of providing tools to Generative AIs to use can be described as **Tool Augmented Generation** (TAG) and the Generative AIs that use tools as **Tool Augmented Generative AIs** (TAG AIs).

*Daring Mechanician* provides tools for building, testing, and tuning *TAG AIs* and the tools that these AIs use, including support for AI-driven testing and AI-assisted *tuning* of the instruction sets given to an AI that we call **Instruction Auto-Tuning** (IAT).


# Tool Augmented Generation (TAG)

The **Tool Augmented Generation** (**TAG**) approach provides AIs with external tools, databases, and interfaces to enhance their knowledge, capabilities, and interaction with other systems.

This approach leverages the "**Function Calling**", or "**Tool Calling**", capabilities available in several Large Language Models and is meant to complement other approaches to augmenting Foundation Models, like **Fine Tuning** (FT) and **Retrieval Augmented Generation** (RAG). 

In contrast to **Retrieval Augmented Generation** (RAG), which uses a knowledge base to retrieve information and augment the prompt sent to the AI, **Tool Augmented Generation** (TAG) provides the AI with tools so that it can retrieve information itself, and also perform actions across multiple systems, databases, and interfaces.

>NOTE: You can build a RAG application using a TAG AI to create a **RAGTAG AI** Application.

Foundation Models are inherently limited by the scope of their training data and the static nature of that data, *Tool Augmented Generative AI* can access up-to-date information, perform computations, and interact with external systems; extending Generative AIs from pure knowledge repositories to active participants in information processing and generation.

This approach enhances the AI's problem-solving skills, creativity, and ability to provide accurate, up-to-date information.


## Designing Tools for AIs to Use

TAG AIs can be observed to problem solve, learning to use tools effectively through feedback provided by the tools themselves, so it is necessary for the tools to provide effective feedback, often through natural language, when reporting errors or providing results.

AIs will learn from their mistakes and successes, if the tools provide feedback that the AI can learn from.

See [Getting Started with Daring Mechanician](#getting-started-with-daring-mechanician) for an example of how to use the **Tool Augmented Generation** (TAG) approach to build a **Movie Database Assistant**.


## Instruction Tuning (IT)

In addition to learning from the feedback provided by the tools they use, TAG AIs can learn from the feedback they receive from users.

But since TAG AIs do not necessarily undergo further training, or Fine Tuning, that permanently encodes what they learned, they can only learn within the context window where feedback is received, and must start from scratch during the next session.

In order to make these learned behaviors persistent, they must be captured through a process of **Instruction Tuning**, where the initial instructions provided to the AI, the instructions provided for the tools the AI can use, and the feedback provided by those tools are revised and improved, incorporating lessons learned during interactions with users.

This process starts with creating an initial set of *AI Instructions*, *Tool Instructions*, and *Tool Feedback*, that are used to guide the AI's behavior and responses, and then iteratively refining those instructions and tool feedback based on the AI's performance during interactions with users.

At the start of this process, the prompting provided to the AI often consists of explict and detailed steps, but as the process proceeds, it is often discoverd that the AI does not need such detailed prompting, and that more general prompts can be used to guide the AI's behavior, and it will work out the details on its own.

In order to speed up this process, it is useful to use an **Evaluator AI** that acts as an *user surrogate*, interactively eliciting responses from the AI as the two work through multi-step tasks.

## Instruction Auto-Tuning (IAT)

By observing an AI's interactions with users and other AIs, an *Instructor AI* can refine and update the AI's current instructions and the instructions describing the tools the AI can use.

The Instructor AI is provided the AI's current set of instructions, instructions for the tools used by the AI, and the transcript of interactions between the AI and a User (or Evaluator AI), including the AI tool calls and responses.

See [Getting Started with Instruction Auto-Tuning](#getting-started-with-instruction-auto-tuning) for an example of how to use the **Instruction Auto-Tuning** (IAT) process to refine the instructions for a **Movie Database Assistant**.


## AI-Driven Testing

See [Getting Started with AI-Driven Testing](#getting-started-with-ai-driven-testing) for an example of how to use the **AI-Driven Testing** process to test a **Movie Database Assistant**.
