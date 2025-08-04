from langgraph.types import Command 
from graph import graph 
from langchain_core.messages import HumanMessage


if __name__ == "__main__":
    # Create a thread config
    thread_config = {"configurable": {"thread_id": "blog_creation_thread"}}
    
    # Initial invocation - will run until interrupt
    result = graph.invoke({
        "messages": [HumanMessage(content="Write a blog about NVIDIA stock developments")],
        "blog_title": "",
        "research_notes": "",
        "outline": "",
        "blog_content": "",
        "approval": False,
        "feedback": ""
    }, config=thread_config)
    
    # Check if we hit an interrupt (indicated by __interrupt__ key)
    if '__interrupt__' in result:
        print(f"Blog Title: {result.get('blog_title')}")
        print(f"\nResearch Notes:\n{result.get('research_notes')}")
        print(f"\nOutline for Review:\n{result.get('outline')}")
        
        # Human review loop
        while True:
            print("\n" + "="*50)
            print("HUMAN REVIEW REQUIRED")
            print("="*50)
            
            user_input = input("\nDo you approve this outline? (yes/no): ").strip().lower()
            approved = user_input in ['yes', 'y', 'true', 'approve', 'approved']
            
            feedback = ""
            if not approved:
                feedback = input("Please provide feedback for improvement: ").strip()
            
            # Resume with human decision
            result = graph.invoke(
                Command(resume={
                    "approved": approved,
                    "feedback": feedback
                }),
                config=thread_config
            )
            
            # Check if we hit another interrupt (revision cycle)
            if '__interrupt__' in result:
                print(f"\nOutline revised based on feedback.")
                print(f"Revised Outline:\n{result.get('outline')}")
                continue
            else:
                # No more interrupts - blog generation should be complete
                if approved and result.get('blog_content'):
                    print(f"\nBlog generation completed!")
                    print(f"\nFinal Blog Content:\n{result['blog_content']}")
                    break
                elif not approved:
                    print(f"\nRevised Outline:\n{result.get('outline')}")
                    continue
                else:
                    print(f"\nBlog generation failed - no content produced")
                    break
    
    else:
        # No interrupt - graph completed without human review
        print(f"Blog Title: {result.get('blog_title')}")
        print(f"\nFinal Blog Content:\n{result.get('blog_content')}")