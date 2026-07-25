# importing required libraries
from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# loading dotenv
# environmental variables
load_dotenv()

# prompt for model_1
model_1_prompt = PromptTemplate.from_template("""
You are solving a logic puzzle. Read the question carefully and think through it step by step before giving your final answer.

Question: {question}

Instructions:
- Show your reasoning step by step.
- At the end, clearly state your final answer on its own line, starting with "Final Answer:"
""")

# prompt for model_2
model_2_prompt = PromptTemplate.from_template("""
You are a critical reviewer checking someone else's answer to a logic puzzle. Do not solve the puzzle from scratch — instead, carefully evaluate the reasoning given below.

Question: {question}

Proposed answer and reasoning:
{model_1_output}

Instructions:
- Check each step of the reasoning for errors, wrong assumptions, or logical gaps.
- Be specific about what is wrong, if anything.
- If the reasoning and final answer are correct, say so explicitly and clearly.
- If the reasoning or final answer is incorrect, explain exactly what is wrong and why.
""")

# prompt for model_1 revise step
model_1_revise = PromptTemplate.from_template("""
Here is a logic puzzle you previously answered, along with a critique of your answer.

Question: {question}

Your original answer:
{model_1_output}

Critique of your answer:
{model_2_output}

Instructions:
- If the critique identified real errors, revise your answer to fix them, and briefly explain what changed.
- If the critique was incorrect or unnecessary, keep your original answer and briefly explain why the critique doesn't apply.
- Clearly state your final revised answer on its own line, starting with "Final Answer:"
""")

# initializing the first model
model_1 = init_chat_model(
    model_provider="groq",
    model="llama-3.1-8b-instant"
)

# intializing the second model
model_2 = init_chat_model(
    model_provider="groq",
    model="llama-3.3-70b-versatile"
)

# building first chain for model_1
chain = (
    model_1_prompt | 
    model_1
)

# building second chain for model_2 which will act as critique
chain_2 = (
    model_2_prompt |
    model_2
)

# building third chain for model_3 which will revise
chain_3 = (
    model_1_revise |
    model_1
)


def get_answer(question):
    # response of model_1
    response_model_1 = chain.invoke({"question": question})
    return response_model_1.content


def get_critique(question, model_1_output):
    # also giving the output of response of model_1
    # response of model 2
    response_model_2 = chain_2.invoke(
        {
            "question": question,
            "model_1_output": model_1_output,
        }
    )
    return response_model_2.content


def get_revision(question, model_1_output, model_2_output):
    # giving the output of model_2
    # getting the final response
    response_model_revise = chain_3.invoke(
        {
            "question": question,
            "model_1_output": model_1_output,
            "model_2_output": model_2_output
        }
    )
    return response_model_revise.content


def run_pipeline(question):
    #running pipeline
    answer = get_answer(question)
    critique = get_critique(question, answer)
    revision = get_revision(question, answer, critique)

    return {
        "answer": answer,
        "critique": critique,
        "revision": revision
    }


if __name__ == "__main__":
    # asking questions
    question = "Three friends, Alex, Ben, and Carla, each own a different pet: a cat, a dog, and a fish. Alex does not own the cat. Ben does not own the dog or the fish. What pet does each person own?"

    result = run_pipeline(question)

    print(result["answer"])
    '''print("===========================================================")
    print(result["critique"])
    print("===========================================================")
    print("===========================================================")
    print(result["revision"])'''