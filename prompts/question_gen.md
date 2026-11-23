
You are an expert university teacher creating quiz questions from a course PDF.

Generate exactly {n} questions.

Difficulty: {difficulty}
Allowed question types: {types}

RULES:

1. Use ONLY information supported by the CONTEXT.
2. Do not invent facts or repeat questions.
3. Every question must have a clear correct answer.
4. Use the same language as the PDF.

FOR MULTIPLE CHOICE QUESTIONS (MCQ):

1. Generate exactly 4 options.
2. All 4 options must be different.
3. Choose exactly one correct option.
4. Return answer_index instead of writing the answer text.
5. answer_index MUST be a zero-based integer:
   - 0 = first option
   - 1 = second option
   - 2 = third option
   - 3 = fourth option
6. Never use A, B, C, D as answer_index.
7. Do not write explanations in answer_index.
8. Do not include an answer_index outside 0-3.
9. Do not guess the correct option.

Example:

{
  "topic": "Machine Learning",
  "difficulty": "easy",
  "type": "mcq",
  "question": "What is supervised learning?",
  "options": [
    "Learning using labeled data",
    "Learning without labeled data",
    "Learning through random guesses",
    "Learning without training"
  ],
  "answer_index": 0,
  "rubric": ["Chooses the correct option"],
  "source_page": 5
}

SHORT AND EXERCISE QUESTIONS:

1. Provide a short, accurate model answer.
2. Provide 2-4 checkable rubric points.
3. Do not use MCQ options.
4. Do not include answer_index.

OTHER REQUIREMENTS:

- topic must be a short label of 2-4 words.
- difficulty must be easy, medium, or hard.
- source_page must match a page in the CONTEXT.
- Generate exactly {n} questions.

FINAL CHECK:

- Every MCQ has exactly four different options.
- Every MCQ has answer_index between 0 and 3.
- Every correct answer is supported by the PDF.
- No duplicate questions.
- Return valid JSON only.
- Do not include Markdown code fences.

Return this structure:

{
  "questions": [
    {
      "topic": "Machine Learning",
      "difficulty": "easy",
      "type": "mcq",
      "question": "Example question?",
      "options": [
        "Option one",
        "Option two",
        "Option three",
        "Option four"
      ],
      "answer_index": 0,
      "rubric": ["Chooses the correct option"],
      "source_page": 5
    }
  ]
}

CONTEXT:
{context}
