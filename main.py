from dotenv import load_dotenv
import os
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from rag_setup import get_retriever_tools
from web_operations import (
    fetch_job_description_from_url,
    extract_company_name_from_text
)
from prompts import (
    get_keywords_analysis_messages,
    get_tailor_summary_messages,
    get_tailor_skills_messages,
    get_tailor_experience_messages,
    get_tailor_name_desc_messages,
    get_check_length_messages,
    get_cover_letter_messages,
    get_interest_answer_messages
)
from pdf_operations import save_all_outputs

load_dotenv()

# Initialize LLM with GPT-5 (using gpt-4o as latest available model)
# Update to "gpt-5" when available through OpenAI API
llm = ChatOpenAI(model="gpt-5", temperature=0.4)
#llm = ChatOpenAI(model="o3")

# Get retriever tools
retriever_tools = get_retriever_tools()
llm_with_tools = llm.bind_tools(retriever_tools)

# Create tools dictionary
tools_dict = {tool.name: tool for tool in retriever_tools}


class AgentState(TypedDict):
    """State for the resume tailoring agent."""
    messages: Annotated[List, add_messages]
    job_description: str | None
    input_method: str | None  # "text" or "url"
    job_url: str | None  # Original URL if provided
    keywords_analysis: str | None  # Step A
    tailored_summary: str | None  # Step B
    tailored_skills: str | None  # Step C
    tailored_experience: str | None  # Step D
    tailored_name_desc: str | None  # Step E
    length_check_result: str | None
    cover_letter: str | None
    interest_answer: str | None
    company_name: str | None
    output_files: dict | None


def get_job_description(state: AgentState) -> AgentState:
    """Node 1: Get job description from user input (text or URL)."""
    print("\n" + "="*80)
    print("STEP 1: Getting Job Description")
    print("="*80)
    
    # This will be populated by the CLI before invoking the graph
    # Just verify it exists
    if not state.get("job_description"):
        raise ValueError("Job description not provided")
    
    print(f"✓ Job description received ({len(state['job_description'])} characters)")
    print(f"  Input method: {state.get('input_method', 'text')}")
    
    # Extract company name
    company_name = state.get("company_name")
    if not company_name:
        # Pass URL if available for better extraction
        job_url = state.get("job_url")
        company_name = extract_company_name_from_text(state["job_description"], url=job_url)
        print(f"  Extracted company name: {company_name}")
    
    return {"company_name": company_name}


def analyze_keywords(state: AgentState) -> AgentState:
    """Node 2: Analyze keywords, tools, verbs, methods from JD."""
    print("\n" + "="*80)
    print("STEP 2: Analyzing Keywords and Key Terms")
    print("="*80)
    
    messages = get_keywords_analysis_messages(state["job_description"])
    
    # Call LLM with tools
    response = llm_with_tools.invoke(messages)
    
    # Check if tools were called
    if hasattr(response, 'tool_calls') and response.tool_calls:
        # Execute tool calls
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            print(f"  Using tool: {tool_name}")
            
            if tool_name in tools_dict:
                result = tools_dict[tool_name].invoke(tool_args)
                tool_results.append(str(result))
        
        # Call LLM again with tool results
        messages.append({"role": "assistant", "content": str(response.content)})
        messages.append({"role": "user", "content": "\n\n".join(tool_results)})
        response = llm.invoke(messages)
    
    keywords_analysis = response.content
    print(f"✓ Keywords analysis complete ({len(keywords_analysis)} characters)")
    
    return {"keywords_analysis": keywords_analysis}


def tailor_summary(state: AgentState) -> AgentState:
    """Node 3: Tailor professional summary."""
    print("\n" + "="*80)
    print("STEP 3: Tailoring Professional Summary")
    print("="*80)
    
    messages = get_tailor_summary_messages(
        state["job_description"],
        state["keywords_analysis"]
    )
    
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            print(f"  Using tool: {tool_name}")
            
            if tool_name in tools_dict:
                result = tools_dict[tool_name].invoke(tool_args)
                tool_results.append(str(result))
        
        messages.append({"role": "assistant", "content": str(response.content)})
        messages.append({"role": "user", "content": "\n\n".join(tool_results)})
        response = llm.invoke(messages)
    
    tailored_summary = response.content
    print(f"✓ Summary tailored ({len(tailored_summary)} characters)")
    
    return {"tailored_summary": tailored_summary}


def tailor_skills(state: AgentState) -> AgentState:
    """Node 4: Tailor skills section."""
    print("\n" + "="*80)
    print("STEP 4: Tailoring Skills Section")
    print("="*80)
    
    messages = get_tailor_skills_messages(
        state["job_description"],
        state["keywords_analysis"]
    )
    
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            print(f"  Using tool: {tool_name}")
            
            if tool_name in tools_dict:
                result = tools_dict[tool_name].invoke(tool_args)
                tool_results.append(str(result))
        
        messages.append({"role": "assistant", "content": str(response.content)})
        messages.append({"role": "user", "content": "\n\n".join(tool_results)})
        response = llm.invoke(messages)
    
    tailored_skills = response.content
    print(f"✓ Skills tailored ({len(tailored_skills)} characters)")
    
    return {"tailored_skills": tailored_skills}


def tailor_experience(state: AgentState) -> AgentState:
    """Node 5: Tailor experience bullets."""
    print("\n" + "="*80)
    print("STEP 5: Tailoring Experience Bullets")
    print("="*80)
    
    messages = get_tailor_experience_messages(
        state["job_description"],
        state["keywords_analysis"]
    )
    
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            print(f"  Using tool: {tool_name}")
            
            if tool_name in tools_dict:
                result = tools_dict[tool_name].invoke(tool_args)
                tool_results.append(str(result))
        
        messages.append({"role": "assistant", "content": str(response.content)})
        messages.append({"role": "user", "content": "\n\n".join(tool_results)})
        response = llm.invoke(messages)
    
    tailored_experience = response.content
    print(f"✓ Experience tailored ({len(tailored_experience)} characters)")
    
    return {"tailored_experience": tailored_experience}


def tailor_name_desc(state: AgentState) -> AgentState:
    """Node 6: Tailor professional title and specialization."""
    print("\n" + "="*80)
    print("STEP 6: Tailoring Professional Title & Specialization")
    print("="*80)
    
    messages = get_tailor_name_desc_messages(
        state["job_description"],
        state["keywords_analysis"]
    )
    
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            print(f"  Using tool: {tool_name}")
            
            if tool_name in tools_dict:
                result = tools_dict[tool_name].invoke(tool_args)
                tool_results.append(str(result))
        
        messages.append({"role": "assistant", "content": str(response.content)})
        messages.append({"role": "user", "content": "\n\n".join(tool_results)})
        response = llm.invoke(messages)
    
    tailored_name_desc = response.content
    print(f"✓ Title/Specialization tailored ({len(tailored_name_desc)} characters)")
    
    return {"tailored_name_desc": tailored_name_desc}


def check_resume_length(state: AgentState) -> AgentState:
    """Node 7: Check if resume fits on one page and condense if needed."""
    print("\n" + "="*80)
    print("STEP 7: Checking Resume Length (One-Page Requirement)")
    print("="*80)
    
    messages = get_check_length_messages(
        state["tailored_summary"],
        state["tailored_skills"],
        state["tailored_experience"],
        state["tailored_name_desc"]
    )
    
    response = llm.invoke(messages)
    length_check = response.content
    
    print(f"✓ Length check complete")
    
    # Check if condensing was needed
    if "TOO_LONG" in length_check.upper():
        print("  ⚠ Resume was too long - condensed versions provided")
        
        # Try to extract condensed sections from the response
        # The LLM should provide revised sections if too long
        # We'll update the state with condensed versions if provided
        # This is a simple heuristic - could be improved with structured output
        
        # For now, just store the result and let the user review
        return {
            "length_check_result": length_check,
            "messages": [AIMessage(content="Resume length checked and adjusted if needed.")]
        }
    else:
        print("  ✓ Resume fits on one page")
        return {
            "length_check_result": length_check,
            "messages": [AIMessage(content="Resume length verified - fits on one page.")]
        }


def generate_cover_letter(state: AgentState) -> AgentState:
    """Node 8: Generate cover letter."""
    print("\n" + "="*80)
    print("STEP 8: Generating Cover Letter")
    print("="*80)
    
    messages = get_cover_letter_messages(
        state["job_description"],
        state["company_name"],
        state["tailored_summary"],
        state["tailored_skills"],
        state["tailored_experience"]
    )
    
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            print(f"  Using tool: {tool_name}")
            
            if tool_name in tools_dict:
                result = tools_dict[tool_name].invoke(tool_args)
                tool_results.append(str(result))
        
        messages.append({"role": "assistant", "content": str(response.content)})
        messages.append({"role": "user", "content": "\n\n".join(tool_results)})
        response = llm.invoke(messages)
    
    cover_letter = response.content
    print(f"✓ Cover letter generated ({len(cover_letter)} characters)")
    
    return {"cover_letter": cover_letter}


def generate_interest_answer(state: AgentState) -> AgentState:
    """Node 9: Generate 'why interested' answer."""
    print("\n" + "="*80)
    print("STEP 9: Generating Interest Answer")
    print("="*80)
    
    messages = get_interest_answer_messages(
        state["job_description"],
        state["company_name"]
    )
    
    response = llm_with_tools.invoke(messages)
    
    # Handle tool calls
    if hasattr(response, 'tool_calls') and response.tool_calls:
        tool_results = []
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            print(f"  Using tool: {tool_name}")
            
            if tool_name in tools_dict:
                result = tools_dict[tool_name].invoke(tool_args)
                tool_results.append(str(result))
        
        messages.append({"role": "assistant", "content": str(response.content)})
        messages.append({"role": "user", "content": "\n\n".join(tool_results)})
        response = llm.invoke(messages)
    
    interest_answer = response.content
    print(f"✓ Interest answer generated ({len(interest_answer)} characters)")
    
    return {"interest_answer": interest_answer}


def save_outputs(state: AgentState) -> AgentState:
    """Node 10: Save all outputs to files."""
    print("\n" + "="*80)
    print("STEP 10: Saving Outputs")
    print("="*80)
    
    output_dir = os.path.join(os.path.dirname(__file__), "outputs")
    
    output_files = save_all_outputs(
        output_dir=output_dir,
        company_name=state["company_name"],
        job_description=state["job_description"],
        keywords_analysis=state["keywords_analysis"],
        tailored_summary=state["tailored_summary"],
        tailored_skills=state["tailored_skills"],
        tailored_experience=state["tailored_experience"],
        tailored_name_desc=state["tailored_name_desc"],
        cover_letter=state["cover_letter"],
        interest_answer=state["interest_answer"]
    )
    
    print("\n" + "="*80)
    print("ALL OUTPUTS SAVED SUCCESSFULLY")
    print("="*80)
    print(f"Text file: {output_files['text_file']}")
    if output_files['pdf_file']:
        print(f"PDF file:  {output_files['pdf_file']}")
    print("="*80)
    
    return {"output_files": output_files}


# Build the graph
graph_builder = StateGraph(AgentState)

# Add nodes
graph_builder.add_node("get_job_description", get_job_description)
graph_builder.add_node("analyze_keywords", analyze_keywords)
graph_builder.add_node("tailor_summary", tailor_summary)
graph_builder.add_node("tailor_skills", tailor_skills)
graph_builder.add_node("tailor_experience", tailor_experience)
graph_builder.add_node("tailor_name_desc", tailor_name_desc)
graph_builder.add_node("check_resume_length", check_resume_length)
graph_builder.add_node("generate_cover_letter", generate_cover_letter)
graph_builder.add_node("generate_interest_answer", generate_interest_answer)
graph_builder.add_node("save_outputs", save_outputs)

# Add edges (linear flow)
graph_builder.add_edge(START, "get_job_description")
graph_builder.add_edge("get_job_description", "analyze_keywords")
graph_builder.add_edge("analyze_keywords", "tailor_summary")
graph_builder.add_edge("tailor_summary", "tailor_skills")
graph_builder.add_edge("tailor_skills", "tailor_experience")
graph_builder.add_edge("tailor_experience", "tailor_name_desc")
graph_builder.add_edge("tailor_name_desc", "check_resume_length")
graph_builder.add_edge("check_resume_length", "generate_cover_letter")
graph_builder.add_edge("generate_cover_letter", "generate_interest_answer")
graph_builder.add_edge("generate_interest_answer", "save_outputs")
graph_builder.add_edge("save_outputs", END)

# Compile the graph
resume_agent = graph_builder.compile()


if __name__ == "__main__":
    print("Resume Tailoring Agent")
    print("This module should be run via CLI interface")
    print("Run: python cli.py")

