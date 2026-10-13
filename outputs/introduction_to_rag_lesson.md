# Introduction to RAG

Welcome to your first lesson on RAG! If you are new to artificial intelligence, you might wonder how computers can answer specific questions about private or new information. Today, we will learn how this works in a simple way.

RAG stands for **Retrieval-Augmented Generation** and explains that it looks up relevant information in documents before an AI model writes an answer.

---

## Why RAG Matters and When It Is Useful

Artificial intelligence models are trained on vast amounts of public data, but they do not know everything. For example, a standard AI model does not know your company's internal rules, your school's unique handbook, or yesterday's news.

This topic matters because it bridges that gap. RAG is useful when you need accurate answers based on specific files, manuals, or company policies without having to retrain a complex AI model from scratch.

---

## How the RAG Workflow Works

Here is how the process works in four simple steps:

1. You type a question into the system.
2. The system searches through your stored files to find the most useful text.
3. The system feeds both your question and the found text into the AI model.
4. The AI model reads the text and writes a helpful answer for you.

---

## How Questions Lead to Retrieval and Generation

When you ask a question, the system uses **retrieval** to scan through a collection of **documents** to find the exact paragraphs that match your topic. Retrieval means searching through documents to find relevant information.

Once those matching texts are found, they are handed over to the **model**. Generation means the AI writes an answer using the information it receives. This ensures the final response is based on real facts rather than guesses.

---

## A Practical Example

Let us look at a real-world scenario to see how this works in practice.

* **Question:** What is the remote work policy for employees?
* **Relevant Document Information:** "Employee Handbook Section 4.2: Full-time staff members are permitted to work remotely up to two days per week, provided they submit their schedule to their manager in advance."
* **Resulting Answer:** According to Section 4.2 of the Employee Handbook, full-time staff members can work remotely up to two days per week if they submit their schedule to their manager in advance.

---

## Limitations of RAG

While this method is powerful, it is not perfect. One major limitation is that retrieving documents does not guarantee that every generated answer is correct. If the stored files contain errors, outdated rules, or confusing instructions, the AI might repeat those mistakes in its final response.

---

## Summary

In this lesson, you learned that Retrieval-Augmented Generation helps artificial intelligence answer questions using specific files. We covered the workflow steps, the meaning of key technical terms, and how searching through documents improves the final response. While it depends heavily on the quality of your stored files, it remains a fantastic tool for getting accurate, document-based answers.
