from langchain_community.tools import TavilySearchResults
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from typing_extensions import Annotated, List, TypedDict
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

load_dotenv()

class BlogState(TypedDict):
    messages: Annotated[List, add_messages]
    blog_title: str
    research_notes: str
    outline: str
    blog_content: str
    approval: bool
    feedback: str

graph_builder = StateGraph(BlogState)
llm = ChatGroq(model="gemma2-9b-It")

def input_node(state: BlogState):
    # Extract the last message content properly
    last_message = state['messages'][-1] if state['messages'] else ""
    user_content = last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    input_prompt = f"""Given the user input: "{user_content}", extract the blog title/topic.
    Please return only the topic and nothing else."""
    
    response = llm.invoke(input_prompt)
    return {
        "blog_title": response.content
    }

# Initialize tool
tool = TavilySearchResults(max_results=3)
llm_with_tools = llm.bind_tools(tools=[tool])

def research_node(state: BlogState):
    research_prompt = f"""
    Use the Tavily search tool to find the latest developments, news, and statistics about: "{state['blog_title']}".
    Please search the web using the Tavily tool and return your findings.
    """
    
    response = llm_with_tools.invoke([HumanMessage(content=research_prompt)])
    
    return {
        "messages": [response]  # Add the response to messages
    }

def extract_research(state: BlogState):
    """Extract research content from tool calls and responses"""
    messages = state["messages"]
    blog_title = state["blog_title"]
    
    # Look for tool calls and their results in messages
    research_content = []
    
    for msg in messages:
        if hasattr(msg, 'content') and msg.content:
            research_content.append(msg.content)
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                if hasattr(tool_call, 'args'):
                    research_content.append(f"Search query: {tool_call.args}")
    
    # Combine all research content
    all_research = "\n".join(research_content)
    
    # Ask LLM to extract and format the research
    extraction_prompt = f"""From the following research data about "{blog_title}", extract and organize the key information:

Research Data:
{all_research}

Please organize this into clear bullet points covering:
- Key facts and statistics
- Recent developments
- Important findings
- Market data (if applicable)

Return only the organized research findings as bullet points."""
    
    response = llm.invoke(extraction_prompt)
    
    return {
        "research_notes": response.content or f"Research completed for {blog_title}"
    }

def outline_generator(state: BlogState):
    outline_prompt = f"""Based on the research notes below, generate a detailed blog outline for the topic: "{state['blog_title']}"

Research Notes:
{state['research_notes']}

Create a structured outline with:
1. Introduction
2. Main sections (3-5 sections)
3. Conclusion

Make it engaging and informative."""
    
    response = llm.invoke(outline_prompt)
    return {
        "outline": response.content,
        "messages": [response]
    }

def blog_generator(state: BlogState):
    blog_prompt = f"""Write a comprehensive and engaging blog post based on the following information:

Blog Title: {state['blog_title']}

Research Notes:
{state['research_notes']}

Blog Outline:
{state['outline']}

Instructions:
- Write a complete, well-structured blog post following the outline
- Include an engaging introduction that hooks the reader
- Develop each main section with detailed content based on the research notes
- Use the research findings to support your points with facts and statistics
- Write in a professional yet accessible tone
- Include smooth transitions between sections
- End with a compelling conclusion that summarizes key points
- Aim for 800-1200 words
- Make it informative, engaging, and valuable to readers

Please write the complete blog post now:"""
    
    response = llm.invoke(blog_prompt)
    return {
        "blog_content": response.content,
        "messages": [response]
    }

def human_review(state: BlogState):
    """Human review node with interrupt for outline approval"""
    result = interrupt({
        "task": "Review the blog outline and approve or provide feedback for revision.",
        "blog_title": state["blog_title"],
        "outline": state["outline"],
        "research_notes": state["research_notes"],
        "question": "Do you approve this outline?"
    })
    
    # The result will contain the human's decision
    approved = result.get("approved", False)
    feedback = result.get("feedback", "")
    
    return {
        "approval": approved,
        "feedback": feedback,
        "messages": [HumanMessage(content=f"Human review completed. Approved: {approved}")]
    }

def revision_needed(state: BlogState):
    """Check if revision is needed based on approval"""
    return "revise_outline" if not state.get('approval', False) else "blog_generator"

def revise_outline(state: BlogState):
    """Revise the outline based on human feedback"""
    feedback = state.get('feedback', 'Please improve the outline')
    
    revision_prompt = f"""The current outline was not approved. Please revise and improve based on this feedback:

FEEDBACK: {feedback}

Current Title: {state['blog_title']}
Current Outline: {state['outline']}
Research Notes: {state['research_notes']}

Create a better, more engaging outline that:
- Addresses the specific feedback provided
- Has clearer structure
- Better incorporates the research findings
- Is more compelling and reader-friendly

Provide the revised outline:"""
    
    response = llm.invoke(revision_prompt)
    return {
        "outline": response.content,
        "approval": False,  # Reset approval for next review
        "feedback": "",  # Clear previous feedback
        "messages": [HumanMessage(content="Outline revised based on feedback")]
    }

# Creating the graph
graph_builder.add_node("input_node", input_node)
graph_builder.add_node("research_node", research_node)
graph_builder.add_node("tools", ToolNode(tools=[tool]))
graph_builder.add_node("extract_research", extract_research)
graph_builder.add_node("outline_generator", outline_generator)
graph_builder.add_node("human_review", human_review)
graph_builder.add_node("revise_outline", revise_outline)
graph_builder.add_node("blog_generator", blog_generator)

# Set entry point
graph_builder.set_entry_point("input_node")

# Add the edges
graph_builder.add_edge("input_node", "research_node")

# Fixed conditional edges
graph_builder.add_conditional_edges(
    "research_node",
    tools_condition,
    {
        "tools": "tools",  # If tools need to be called
        "extract_research": "extract_research"  # If no tools needed, go to extract
    }
)

# Add edge from tools back to extract_research
graph_builder.add_edge("tools", "extract_research")
graph_builder.add_edge("extract_research", "outline_generator")
graph_builder.add_edge("outline_generator", "human_review")

# Conditional edges based on human approval
graph_builder.add_conditional_edges(
    "human_review",
    revision_needed,
    {
        "revise_outline": "revise_outline",
        "blog_generator": "blog_generator"
    }
)

# Add edge from revision back to human review for re-approval
graph_builder.add_edge("revise_outline", "human_review")
graph_builder.add_edge("blog_generator", END)

# Compile the graph with checkpointer for interrupts
checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

