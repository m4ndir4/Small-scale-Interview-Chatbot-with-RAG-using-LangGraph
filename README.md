
# Interview Simulation System Documentation

## Overview  
Small scale implementation of RAG and LangGraph workflow for an interview chatbot. Consists of multiple agents performing different tasks such as retrieving documents, generating questions and creating candidate assessment reports.

## System Architecture  
The system is built using LangGraph, a framework for creating stateful, multi-step workflows with language models. The architecture consists of:  
- **State Management**: Uses TypedDict for type-safe state tracking during the interview  
- **Retrieval System**: Employs FAISS vector store for question retrieval and context-awareness  
- **LLM Integration**: Leverages OpenAI's GPT-4 for generating follow-up questions and reports  
- **Graph Workflow**: Defines a sequential interview process with conditional transitions  

## Core Components  

### Question Database  
Questions are organized into three categories:  
- **Introduction**: Questions about the candidate's background and general information  
- **Technical**: Questions assessing technical skills and experience  
- **Behavioral**: Questions evaluating soft skills and professional conduct  

Each question includes:  
- The question text  
- Context information about the question's purpose  

### Vector Storage and Retrieval  
The system uses a RAG approach:  
- Questions and category descriptions are converted to document objects  
- FAISS vector store indexes these documents using OpenAI embeddings  
- Semantic search retrieves relevant questions based on context  
- The system saves and loads embeddings locally for persistence  

## Interview Workflow Nodes  

| Node                      | Description                                           |
|---------------------------|-------------------------------------------------------|
| `intro_agent`             | Asks introduction questions and records responses     |
| `tech_question_agent`     | Asks technical skill questions and records responses  |
| `behavior_question_agent` | Asks behavioral questions and records responses       |
| `followup_agent`          | Generates contextual follow-up questions based on previous answers |
| `report_generator_with_rag` | Creates a comprehensive interview report with analysis |

## State Management  
The interview state tracks:  
- Current interview stage  
- Candidate responses by category  
- Original questions and their contexts  
- Report generation status  

## Interview Process Flow  

### Introduction Stage:  
- System retrieves and asks an introductory question  
- Records candidate response  
- Generates a follow-up question based on the response  
- Transitions to technical questions  

### Technical Stage:  
- System retrieves a relevant technical question  
- Records candidate response  
- Generates a follow-up question based on the response  
- Transitions to behavioral questions  

### Behavioral Stage:  
- System retrieves a behavioral question  
- Records candidate response  
- Generates a follow-up question based on the response  
- Transitions to report generation  

### Report Generation:  
- Analyzes all responses using RAG and LLM  
- Scores each section with reasoning  
- Provides an overall assessment  
- Outputs a structured interview report  

## Report Structure  

The generated interview report includes:

### Section Analysis for each interview stage:  
- Original question asked  
- Candidate's primary response  
- Follow-up response (if applicable)  
- Analysis of responses with strengths/weaknesses  
- Numerical score with reasoning  

### Overall Assessment:  
- Summary evaluation of the candidate  
- Key strengths identified  
- Areas for improvement  
- Final hiring recommendation  

## Setup and Configuration  

### Prerequisites  
- Python 3.8+  
- LangGraph library  
- LangChain library  
- OpenAI API key (set in `.env` file)  
- FAISS library for vector storage  

### Environment Variables  
Required environment variables in `.env`:  
```
OPENAI_API_KEY=your_api_key_here
```

### Installation  
```bash
pip install langgraph langchain-openai langchain-community faiss-cpu python-dotenv
```

### Running the System  
Initialize the system:  
```python
from interview_system import graph, initial_state

# Run the interview
graph.invoke(initial_state)
```

The system will:  
- Prompt the user with questions  
- Accept input responses  
- Process through the interview stages  
- Generate and display the final report  

## Customization Options  

### Adding New Question Categories  
To add a new question category:  
- Add the category and questions to the `interview_questions` dictionary  
- Create a new question agent function  
- Add the corresponding node to the graph  
- Update the graph transitions  

### Modifying Report Format  
The report format can be customized by:  
- Updating the `report_generator_with_rag` function  
- Modifying the prompt templates for section analysis  
- Adjusting the overall assessment prompt  

## Technical Implementation Details  

### RAG Implementation  
The system's RAG capabilities are implemented through:  
- Document creation from structured question data  
- Embedding generation using OpenAI's embedding model  
- Vector storage in FAISS for efficient similarity search  
- Context-aware retrieval during question selection and report generation  

### Follow-up Question Generation  
Follow-up questions are generated by:  
- Analyzing the previous candidate response  
- Using a prompt template tailored to the interview section  
- Leveraging the LLM to create a contextually relevant follow-up  
- Ensuring the follow-up explores areas mentioned in the candidate's answer  

### Scoring System  
Each interview section is scored using:  
- Analysis of responses against the original question context  
- LLM-based evaluation with a structured scoring prompt  
- Numerical scoring (out of 10) with justification  
- Integration of scores into the final report  
