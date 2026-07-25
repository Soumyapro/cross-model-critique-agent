# Cross-Model Critique Agent

A lightweight LangChain pipeline that pairs two different LLMs to answer, critique, and revise responses to logic puzzles. One model proposes an answer, a second model reviews it for errors or gaps, and the first model revises its answer based on that critique. A human user then judges whether the final answer is correct, building a live scoreboard over the course of a session.

**Live demo:** https://cross-model-critique-agent-sh54zjepkhmbftd4loknzr.streamlit.app/

## Motivation

Most LLM demos show a single model answering a single question. This project instead asks a narrower research-flavored question: can a second, independent model catch errors or overconfidence in a first model's reasoning, and does the resulting revision actually improve the answer?

Using two different models, rather than calling the same model twice, matters here. A model critiquing its own output tends to agree with itself. A genuinely different model, trained differently, is more likely to catch something the first model missed - or, just as informative, to confirm the first model was right in a way that is not simply self-agreement.

## How it works

The pipeline runs in three steps:

1. **Answer.** The first model is given a question and asked to reason through it step by step, ending with a clearly marked final answer.
2. **Critique.** A second model is shown the question and the first model's full answer, and is asked to evaluate the reasoning for errors, unstated assumptions, or gaps - not to solve the puzzle independently.
3. **Revise.** The first model is shown its original answer and the critique, and is asked to revise the answer if the critique identified a real problem, or to explain why the critique does not apply if it does not hold up.

All three outputs are shown in the interface, so the full reasoning trace is visible rather than just a final answer.

### Models

- **Answerer / Reviser:** Llama 3.1 8B Instant
- **Critic:** Llama 3.3 70B Versatile

The pairing is deliberate: a small, fast model produces the initial answer, and a substantially larger model is used only for the critique step, where deeper reasoning is more likely to be needed. This keeps the pipeline fast and inexpensive for the step that runs regardless of outcome, while reserving the more capable model for the step where catching subtle errors actually matters.

### Human-in-the-loop evaluation

Rather than pre-writing correct answers and grading responses automatically, correctness is judged live by the person using the app. This avoids a real problem with many logic puzzles: they are often ambiguous enough that automatic string-matching against a fixed answer is unreliable, and a human judge is arguably the more honest evaluator for this kind of task.

Each judged question is added to a running scoreboard for the session, tracking:

- how many questions have been judged
- what fraction were marked correct
- how often the final answer differed from the initial answer after critique

This turns every use of the app into a small, live experiment rather than a single fixed demo.

## Tech stack

- LangChain (LCEL chains for the answer, critique, and revise steps)
- Groq (inference provider for both models)
- Streamlit (interface and session-based scoreboard)
- python-dotenv (local environment variable management)

## Project structure

```
.
├── app.py                 # Streamlit interface
├── chain.py                # Core pipeline: prompts, models, chain logic
├── eval/
│   └── questions.json      # Sample logic puzzles for the "pick from list" mode
├── requirements.txt
├── .streamlit/
│   └── config.toml         # Theme configuration
└── .gitignore
```

`chain.py` contains no Streamlit code and can be run directly (`python chain.py`) to test the pipeline on a single hardcoded question from the terminal, independent of the interface.

## Running locally

1. Clone the repository and create a virtual environment:
   ```
   python -m venv venv
   ```
   Activate it, then install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root with a Groq API key:
   ```
   GROQ_API_KEY=your_key_here
   ```

3. Run the app:
   ```
   streamlit run app.py
   ```

## Possible extensions

- **Multi-round critique.** Right now the loop only runs once - answer, critique, revise, done. I'd like to let it keep going for a few rounds and stop once the answer stops changing. This would be closer to how real self-correction research works, and it would also show what happens when a model can't settle on an answer.
- **Confidence score.** I originally planned this but dropped it to keep things simple. Adding it back would mean the model says how confident it is in its first answer, and then I can check whether that confidence actually matched what the human judge decided. That would tell me if the model knows when it's likely wrong.
- **Switch model roles.** Right now one model always answers and the other always critiques. It would be interesting to let the user flip that - see what happens when the smaller model critiques the bigger one instead.
- **Automatic grading.** Right now a human judges every answer, which works fine for a small demo but doesn't scale. A future version could use a third model as a judge, comparing the answer to a known correct one, so I could test on way more questions without sitting there clicking buttons the whole time.
