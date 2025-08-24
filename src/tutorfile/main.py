import os
import openai


def generate_lessons(
    client: openai.OpenAI,
    model: str,
    topic: str,
    topic_description: str = "",
    num_lessons: int = 10,
    existing_lessons: list[dict[str, str]] | None = None,
    source_text: str | None = None,
    strict_source_text_adherence: bool = False,
) -> list[dict[str, str]]:
    """
    Generate a series of interactive tutorial lessons using AI.

    Args:
        client: OpenAI client instance
        model: Name of the model to use
        topic: Main subject of the tutorials
        topic_description: Additional context for the lessons
        num_lessons: Number of lessons to generate
        existing_lessons: Previously generated lessons to build upon
        source_text: Information to base lessons upon
        strict_source_text_adherence: If source text should be the sole source of information

    Returns:
        List of dictionaries containing lesson names and content
    """
    lessons = existing_lessons or []

    base_prompt = """You are helping create an interactive tutorial series in the style of vimtutor - the classic, hands-on tutorial that teaches vim by having users actively edit a text file while reading instructions. Vimtutor brilliantly teaches through guided practice rather than passive reading. Users learn by doing, with each concept building on previous ones through actual usage.

Your task is to write a single lesson that brings this same hands-on, progressive learning approach to {subject}. Here is some additional information your student added for the lesson: {subject_detail} The lesson should stand alone as a text file that guides users through active learning exercises.

Please respond with ONLY the text of the lesson itself - no meta-discussion or explanations to me. The lesson should be immediately usable by an end user.

Teaching approach requirements:
1. The lesson should take 10-15 minutes to complete
2. Start with absolute basics, assuming no prior knowledge
3. Use progressive disclosure - introduce concepts one at a time
4. Include frequent, small exercises that build on working examples - these should only assume knowledge already shared in the tutorial
5. Each exercise should build confidence through small wins
6. Include clear feedback loops (what success looks like)
7. Use a friendly, conversational tone
8. End with a mini-challenge that combines the lesson's concepts
9. Include suggestions for further exploration
10. Be sure to build a real understanding of the topic - for example if teaching optimization with python, don't just show a scipy function, explain the formulas and ideas behind it.
11. Under no circumstances whatsoever should you make up information. If you are not completely certain of what you are teaching, it is better to have the lesson have less than to make up anything.

Format requirements:
1. Use clear section headers with ASCII decoration
2. Include brief explanations before each new concept
3. Present information in digestible chunks
4. Mark exercises clearly with "EXERCISE N:"
5. Include descriptions of expected outcomes
6. End with a "CHALLENGE" section
7. Include a "FURTHER EXPLORATION" section

[If this is a tool-based tutorial (e.g., programming, SQL):]
Start with brief instructions for accessing the necessary tools. For example:
- For Python: "To follow along, open your terminal and type 'python' to start the Python interpreter"
- For SQL: "You'll need access to a SQL database. One easy way is..."

[If this is a concept-based tutorial (e.g., economics, history):]
Structure exercises as interactive activities like:
- "Write down your prediction before continuing"
- "Try to explain this concept in your own words"
- "Draw a diagram showing..."
- "Compare these two scenarios..."

The lesson should follow this structure:
1. Welcome and tool setup (if applicable)
2. First concept with clear example
3. Exercise applying that concept
4. Second concept building on first
5. Exercise combining concepts
6. Progressive complexity
7. Final challenge
8. Suggested explorations

Remember to:
- Keep each step small and manageable
- Provide clear success criteria
- Encourage active learning
- Make examples relevant to the subject
- Celebrate learning milestones
- Set up concepts needed in lesson 2"""

    for lesson_num in range(len(lessons) + 1, num_lessons + 1):
        prev_lessons_text = ""
        if lessons:
            recent_lessons = lessons[-10:]
            prev_lessons_text = "\n\n".join(
                f"Lesson {i+1}: {lesson['content']}"
                for i, lesson in enumerate(recent_lessons)
            )

        prompt = base_prompt.format(subject=topic, subject_detail=topic_description)

        if prev_lessons_text:
            prompt += (
                f"\n\nCopied below are the earlier lesson(s):\n{prev_lessons_text}"
            )

        if source_text:
            prompt += f"\n\nCopied below is source text the user provided to base the lessons on.\n{source_text}"

            if strict_source_text_adherence:
                prompt += "\nPlease use the user-provided source text exclusively to generate the lessons. All facts and topics should come from this source text. If there is not enough content in the text for sufficiently new lessons or source text was not provided, please let the user know in the lesson, along with the topic you think would make sense for the current lesson and possible freely-available sources, like Wikipedia. Again, do not under any circumstances add facts or lessons not contained in the provided text."

        elif strict_source_text_adherence:
            raise Exception(
                "strict_source_text_adherence was set to True, but no source_text was provided. Please set strict_source_text_adherence to False or add source_text with content to use for the lessons."
            )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Please write lesson {lesson_num}"},
            ],
        )

        lesson_content = response.choices[0].message.content

        lessons.append(
            {"name": f"Lesson {lesson_num}: {topic}", "content": lesson_content}
        )

    return lessons


def read_lessons_from_folder(folder_path: str) -> list[dict[str, str]]:
    """
    Read lessons from a folder created by write_lessons_to_files.

    Args:
        folder_path: Path to the directory containing lesson files

    Returns:
        List of dictionaries containing lesson names and content,
        sorted by lesson number

    Raises:
        FileNotFoundError: If the folder doesn't exist
        ValueError: If lesson files don't match expected format
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    lessons = []

    # Get all .txt files in the directory
    files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]

    # Sort files to ensure correct lesson order
    files.sort()

    for filename in files:
        # Extract lesson number and name
        try:
            # Expected format: "01 - Lesson 1: Topic.txt"
            file_path = os.path.join(folder_path, filename)

            # Remove the .txt extension and split on " - "
            parts = filename[:-4].split(" - ", 1)
            if len(parts) != 2:
                raise ValueError(f"Invalid filename format: {filename}")

            lesson_name = parts[1]

            # Read the content
            with open(file_path, "r") as f:
                content = f.read()

            lessons.append({"name": lesson_name, "content": content})

        except Exception as e:
            raise ValueError(f"Could not process {filename}: {str(e)}")

    return lessons


def write_lessons_to_folder(lessons: list[dict[str, str]], topic: str) -> None:
    """
    Write generated lessons to text files in a directory.

    Args:
        lessons: List of lesson dictionaries
        topic: Topic name used for directory naming
    """
    dir_name = f"{topic.lower()}tutor"
    os.makedirs(dir_name, exist_ok=True)

    for i, lesson in enumerate(lessons, 1):
        filename = f"{dir_name}/{i:02d} - {lesson['name']}.txt"
        with open(filename, "w") as f:
            f.write(lesson["content"])
