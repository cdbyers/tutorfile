# tutorfile

Inspired by vimtutor, tutorfile lets you build text-based interactive tutorials using AI. It generates step-by-step lessons that emphasize learning by doing, with each concept building on previous ones through hands-on practice.

Like any LLM output, tutorfile's lessons can contain inaccuracies. Exercise particular caution with unfamiliar topics or subjects that may be outside LLMs' reliable knowledge base. To improve accuracy, you can provide source material and enable strict adherence mode.

## Quickstart

```python
import openai
from tutorfile import generate_lessons, write_lessons_to_folder

client = openai.OpenAI()

# Create an interactive regex tutorial
lessons = generate_lessons(
    client=client,
    model="gpt-4o",
    topic="Regular Expressions",
    topic_description="""
    Lessons on regular expressions using Python's re module and interactivity through IPython
    """,
    num_lessons=10
)

write_lessons_to_folder(lessons, "regex")
```

![XKCD Comic about Regular Expressions](https://imgs.xkcd.com/comics/regular_expressions.png)

*From [XKCD](https://xkcd.com/208/), also you after regextutor*

## Using Source Material

You can provide source material to ensure accuracy:

```python
with open('source_document.txt', 'r') as f:
    source_text = f.read()

lessons = generate_lessons(
    client=client,
    model="gpt-4o",
    topic="Topic",
    topic_description="Description",
    source_text=source_text,
    strict_source_text_adherence=True 
)
```
Extensive source material can cause the prompt for the LLM to exceed the available context, leading to potential errors. 

The strict_source_text_adherence argument defaults to False. True means the LLM will be asked to exclusively use the text from source_text to inform lessons.

## Building on Existing Lessons

Load existing lessons and generate more:

```python
from tutorfile import read_lessons_from_folder, generate_lessons, write_lessons_to_folder

# Read existing lessons
existing_lessons = read_lessons_from_folder("regextutor")

# Generate additional lessons
new_lessons = generate_lessons(
    client=client,
    model="gpt-4o",
    topic="Regular Expressions",
    topic_description="Advanced concepts",
    num_lessons=15,  # Will generate lessons 11-15
    existing_lessons=existing_lessons
)

# Write all lessons to folder
write_lessons_to_folder(new_lessons, "regex")
```
## Installation

```bash
pip install tutorfile
```

