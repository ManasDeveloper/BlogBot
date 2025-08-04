# 🤖 AI Blog Generator

An intelligent blog generation system with automated research, human-reviewed outlines, and AI-powered content creation. Built with LangGraph workflows, Groq LLM, Tavily search, and Streamlit UI.

## ✨ Features

- **🔍 Automated Research**: Uses Tavily search to gather latest information and statistics
- **📋 Intelligent Outline Generation**: Creates structured blog outlines based on research
- **👤 Human-in-the-Loop Review**: Interactive approval and revision workflow
- **✍️ AI Content Generation**: Produces comprehensive, well-written blog posts
- **🎨 Beautiful UI**: Clean, intuitive Streamlit interface
- **🔄 Revision Cycles**: Iterative improvement based on human feedback

## 🏗️ Architecture

The system uses LangGraph to orchestrate a multi-step workflow:

```
Input Topic → Research → Outline Generation → Human Review → Blog Generation
                ↑                              ↓
                └──── Revision Loop ←──────────┘
```

### Workflow Components:
- **Input Node**: Extracts blog topic from user input
- **Research Node**: Performs web search using Tavily
- **Extract Research**: Processes and organizes findings
- **Outline Generator**: Creates structured blog outline
- **Human Review**: Interactive approval with interrupt mechanism
- **Revise Outline**: Improves outline based on feedback
- **Blog Generator**: Creates final blog content

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key
- Tavily API key

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd ai-blog-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create .env file
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

### Running the Application

#### Streamlit Web Interface (Recommended):
```bash
streamlit run app.py
```

#### Command Line Interface:
```bash
python graph.py
```

## 📁 Project Structure

```
ai-blog-generator/
├── app.py              # Streamlit web interface
├── graph.py            # LangGraph workflow definition
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this)
└── README.md          # This file
```

## 🔧 Configuration

### Required API Keys:
- **Groq API**: For LLM inference (get from [Groq Console](https://console.groq.com/))
- **Tavily API**: For web search (get from [Tavily](https://tavily.com/))

### Environment Variables:
```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

## 📋 Dependencies

```txt
langchain-community
langchain-groq
langchain-core
langgraph
streamlit
python-dotenv
typing-extensions
```

## 🎯 Usage

1. **Enter Topic**: Provide a blog topic (e.g., "Latest developments in AI")
2. **Review Research**: System automatically researches and creates outline
3. **Approve/Revise**: Review the generated outline and approve or request changes
4. **Get Blog**: Receive comprehensive, well-researched blog post

### Example Topics:
- "NVIDIA stock market performance 2024"
- "Latest trends in renewable energy"
- "Impact of AI on healthcare industry"
- "Cryptocurrency market analysis"

## 🛠️ Technical Details

### LangGraph Workflow:
- **State Management**: TypedDict with message history and content fields
- **Interrupt Mechanism**: Human review with resume capability
- **Error Handling**: Graceful error recovery and user feedback
- **Checkpointing**: Memory saver for workflow persistence

### AI Models:
- **LLM**: Groq Gemma2-9B-IT for text generation
- **Search**: Tavily for real-time web research
- **Max Results**: 3 search results per query

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Troubleshooting

### Common Issues:

**API Key Errors**:
- Ensure `.env` file exists with correct API keys
- Verify API keys are valid and have sufficient quota

**Import Errors**:
- Install all dependencies: `pip install -r requirements.txt`
- Ensure Python version is 3.8+

**Streamlit Issues**:
- Clear browser cache
- Restart Streamlit server: `Ctrl+C` then `streamlit run app.py`

**Graph Execution Errors**:
- Check internet connection for web search
- Verify LLM model availability in Groq

## 🙏 Acknowledgments

- [LangGraph](https://github.com/langchain-ai/langgraph) for workflow orchestration
- [Groq](https://groq.com/) for fast LLM inference
- [Tavily](https://tavily.com/) for web search capabilities
- [Streamlit](https://streamlit.io/) for beautiful web interface

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Search existing issues in the repository
3. Create a new issue with detailed description

---

⭐ Star this repository if you find it helpful!