from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Define state structure
class InterviewState(TypedDict):
    intro: str
    current_stage: str
    stage_answers: Dict[str, List[str]]

class State(TypedDict):
    interview: InterviewState
    report: Dict[str, str]

# Node functions
def intro_agent(state: Dict) -> Dict:
    print("AI: Tell me about yourself.")
    user_input = input("You: ")
    state["interview"]["intro"] = user_input
    state["interview"]["stage_answers"]["intro"].append(user_input)
    state["interview"]["current_stage"] = "intro_followup"
    return {"interview": state["interview"]}

def tech_question_agent(state: Dict) -> Dict:
    print("AI: What technologies are you most comfortable with?")
    user_input = input("You: ")
    state["interview"]["stage_answers"]["tech"].append(user_input)
    state["interview"]["current_stage"] = "tech_followup"
    return {"interview": state["interview"]}

def behavior_question_agent(state: Dict) -> Dict:
    print("AI: Tell me about a time you faced a challenge at work.")
    user_input = input("You: ")
    state["interview"]["stage_answers"]["behavior"].append(user_input)
    state["interview"]["current_stage"] = "behavior_followup"
    return {"interview": state["interview"]}

def followup_agent(state: Dict) -> Dict:
    stage = state["interview"]["current_stage"].replace("_followup", "")
    last_answer = state["interview"]["stage_answers"][stage][-1]

    prompt = f"""
You are a professional interviewer. Generate a thoughtful follow-up question based on this response:
"{last_answer}"
Follow-up Question:
"""
    followup_question = llm.invoke(prompt).content.strip()

    print(f"\nAI: {followup_question}")
    user_input = input("You: ")
    state["interview"]["stage_answers"][stage].append(user_input)

    # Decide next stage
    if stage == "intro":
        state["interview"]["current_stage"] = "tech"
    elif stage == "tech":
        state["interview"]["current_stage"] = "behavior"
    elif stage == "behavior":
        state["interview"]["current_stage"] = "complete"

    return {"interview": state["interview"]}

def report_generator(state: Dict) -> Dict:
    report_content = "## Interview Report\n\n"
    
    def get_score_and_reason(section_name: str, answers: List[str]) -> str:
        combined = " ".join(answers)
        prompt = f"""
You are a professional interviewer. Evaluate the following response(s) for the "{section_name}" section. Provide a short reason and a score out of 10.

Responses:
\"\"\"{combined}\"\"\"

Format:
Reason: <short reason>
Score: <number>/10
"""
        result = llm.invoke(prompt).content.strip()
        return result

    def append_section(section_title: str, answers: List[str]):
        nonlocal report_content
        if not answers:
            return
        
        report_content += f"### {section_title}\n"
        report_content += f"**Primary Response**: {answers[0]}\n\n"
        if len(answers) > 1:
            report_content += f"**Follow-up Response**: {answers[1]}\n\n"
        
        score_feedback = get_score_and_reason(section_title, answers)
        report_content += f"{score_feedback}\n\n"

    append_section("Introduction", state["interview"]["stage_answers"]["intro"])
    append_section("Technical Skills", state["interview"]["stage_answers"]["tech"])
    append_section("Behavioral Assessment", state["interview"]["stage_answers"]["behavior"])

    report_content += "### Overall Assessment\n"

    print("\n Final Interview Report:")
    print(report_content)

    return {"report": {"content": report_content}}

# Build graph
builder = StateGraph(State)

# Add nodes
builder.add_node("intro", intro_agent)
builder.add_node("intro_followup", followup_agent)
builder.add_node("tech_question", tech_question_agent)
builder.add_node("tech_followup", followup_agent)
builder.add_node("behavior_question", behavior_question_agent)
builder.add_node("behavior_followup", followup_agent)
builder.add_node("report_generator", report_generator)

# Set entry
builder.set_entry_point("intro")

# Transitions
builder.add_edge("intro", "intro_followup")
builder.add_edge("intro_followup", "tech_question")
builder.add_edge("tech_question", "tech_followup")
builder.add_edge("tech_followup", "behavior_question")
builder.add_edge("behavior_question", "behavior_followup")
builder.add_edge("behavior_followup", "report_generator")
builder.add_edge("report_generator", END)

# Initialize interview state
initial_state = {
    "interview": {
        "intro": "",
        "current_stage": "intro",
        "stage_answers": {
            "intro": [],
            "tech": [],
            "behavior": []
        }
    },
    "report": {}
}

# Compile and run
graph = builder.compile()
graph.invoke(initial_state)
