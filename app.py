import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.types import Command
import uuid
from graph import graph

# Configure Streamlit page
st.set_page_config(
    page_title="AI Blog Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if 'blog_state' not in st.session_state:
    st.session_state.blog_state = None

if 'current_step' not in st.session_state:
    st.session_state.current_step = "input"

if 'awaiting_review' not in st.session_state:
    st.session_state.awaiting_review = False

if 'blog_topic' not in st.session_state:
    st.session_state.blog_topic = ""

# App title and description
st.title("🤖 BlogBolt :  AI Blog Generator")
st.markdown("Create comprehensive, well-researched blog posts with AI assistance and human oversight.")

# Sidebar for process tracking
with st.sidebar:
    st.header("📋 Process Status")
    
    # Define steps with order
    step_order = ["input", "research", "outline", "review", "feedback", "generate", "complete"]
    step_info = {
        "input": ("🎯", "Topic Input"),
        "research": ("🔍", "Research"),
        "outline": ("📋", "Outline Generation"),
        "review": ("👤", "Human Review"),
        "feedback": ("📝", "Provide Feedback"),
        "generate": ("✍️", "Blog Generation"),
        "complete": ("✅", "Complete")
    }
    
    # Get current step index
    try:
        current_index = step_order.index(st.session_state.current_step)
    except ValueError:
        current_index = 0
    
    # Display progress
    for i, step_id in enumerate(step_order):
        if step_id in step_info:
            icon, name = step_info[step_id]
            
            if step_id == st.session_state.current_step:
                st.markdown(f"**{icon} {name}** ← Current")
            elif i < current_index:
                st.markdown(f"✅ {name}")
            else:
                st.markdown(f"⏳ {name}")

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    # Step 1: Topic Input
    if st.session_state.current_step == "input":
        st.header("🎯 Enter Blog Topic")
        
        topic = st.text_input(
            "What would you like to write a blog about?",
            placeholder="e.g., Latest developments in artificial intelligence",
            value=st.session_state.blog_topic
        )
        
        if st.button("🚀 Start Blog Generation", type="primary", disabled=not topic.strip()):
            st.session_state.blog_topic = topic
            st.session_state.current_step = "research"
            
            # Create thread config
            thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            with st.spinner("🔍 Researching topic and generating outline..."):
                try:
                    # Start the graph execution
                    result = graph.invoke({
                        "messages": [HumanMessage(content=f"Write a blog about {topic}")],
                        "blog_title": "",
                        "research_notes": "",
                        "outline": "",
                        "blog_content": "",
                        "approval": False,
                        "feedback": ""
                    }, config=thread_config)
                    
                    st.session_state.blog_state = result
                    
                    # Check if we hit an interrupt (human review needed)
                    if '__interrupt__' in result:
                        st.session_state.current_step = "review"
                        st.session_state.awaiting_review = True
                    else:
                        st.session_state.current_step = "complete"
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

    # Step 2: Human Review
    elif st.session_state.current_step == "review" and st.session_state.awaiting_review:
        st.header("👤 Review Generated Outline")
        
        if st.session_state.blog_state:
            # Display blog information
            st.subheader("📝 Blog Title")
            st.write(st.session_state.blog_state.get('blog_title', 'Not generated'))
            
            st.subheader("🔍 Research Notes")
            with st.expander("View Research Notes", expanded=False):
                st.write(st.session_state.blog_state.get('research_notes', 'Not available'))
            
            st.subheader("📋 Generated Outline")
            outline = st.session_state.blog_state.get('outline', 'Not available')
            st.markdown(outline)
            
            st.divider()
            
            # Review options
            st.subheader("✅ Review Decision")
            
            col_approve, col_reject = st.columns(2)
            
            with col_approve:
                if st.button("✅ Approve Outline", type="primary", use_container_width=True):
                    # Resume with approval
                    thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
                    
                    with st.spinner("✍️ Generating blog content..."):
                        try:
                            result = graph.invoke(
                                Command(resume={
                                    "approved": True,
                                    "feedback": ""
                                }),
                                config=thread_config
                            )
                            
                            st.session_state.blog_state = result
                            st.session_state.current_step = "complete"
                            st.session_state.awaiting_review = False
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"Error generating blog: {str(e)}")
            
            with col_reject:
                if st.button("❌ Request Revision", type="secondary", use_container_width=True):
                    st.session_state.current_step = "feedback"
                    st.rerun()

    # Step 3: Feedback for revision
    elif st.session_state.current_step == "feedback":
        st.header("📝 Provide Feedback for Revision")
        
        feedback = st.text_area(
            "What would you like to improve in the outline?",
            placeholder="e.g., Add more technical details, include market analysis, focus more on recent developments...",
            height=100
        )
        
        col_submit, col_back = st.columns(2)
        
        with col_submit:
            if st.button("🔄 Submit Feedback", type="primary", disabled=not feedback.strip()):
                thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}
                
                with st.spinner("🔄 Revising outline based on your feedback..."):
                    try:
                        result = graph.invoke(
                            Command(resume={
                                "approved": False,
                                "feedback": feedback
                            }),
                            config=thread_config
                        )
                        
                        st.session_state.blog_state = result
                        st.session_state.current_step = "review"
                        st.session_state.awaiting_review = True
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error revising outline: {str(e)}")
        
        with col_back:
            if st.button("← Back to Review", type="secondary"):
                st.session_state.current_step = "review"
                st.rerun()

    # Step 4: Final Result
    elif st.session_state.current_step == "complete":
        st.header("✅ Blog Generation Complete!")
        
        if st.session_state.blog_state:
            # Display final blog
            st.subheader("📝 Blog Title")
            blog_title = st.session_state.blog_state.get('blog_title', 'Untitled')
            st.write(f"**{blog_title}**")
            
            st.subheader("📄 Final Blog Content")
            blog_content = st.session_state.blog_state.get('blog_content', 'No content generated')
            
            # Display content in a nice format
            st.markdown(blog_content)
            
            st.divider()
            
            # Restart option
            if st.button("🔄 Generate New Blog", type="primary", use_container_width=True):
                # Reset all session state
                st.session_state.thread_id = str(uuid.uuid4())
                st.session_state.blog_state = None
                st.session_state.current_step = "input"
                st.session_state.awaiting_review = False
                st.session_state.blog_topic = ""
                st.rerun()

# Right column - Information and tips
with col2:
    st.header("💡 Tips")
    
    with st.expander("🎯 Topic Selection", expanded=True):
        st.markdown("""
        **Good topics include:**
        - Current technology trends
        - Industry developments  
        - Market analysis
        - Product reviews
        - Educational content
        
        **Be specific** for better results!
        """)
    
    with st.expander("👤 Review Process"):
        st.markdown("""
        **During review:**
        - Check if outline covers key points
        - Ensure logical flow
        - Verify research quality
        - Request specific improvements
        
        **Feedback examples:**
        - "Add more recent statistics"
        - "Include competitor analysis"
        - "Focus on practical applications"
        """)
    
    with st.expander("📊 About This Tool"):
        st.markdown("""
        This AI Blog Generator:
        - Researches your topic automatically
        - Creates structured outlines
        - Allows human oversight
        - Generates comprehensive content
        
        **Powered by:**
        - LangGraph for workflow
        - Groq for AI generation
        - Tavily for web research
        """)

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🤖 AI Blog Generator • Built with Streamlit & LangGraph
    </div>
    """, 
    unsafe_allow_html=True
)