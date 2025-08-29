# FinalRound Project

## Overview
FinalRound is a multi-agent interview system powered by LlamaIndex that conducts automated technical interviews with real-time evaluation and comprehensive reporting. The system uses multiple AI agents to simulate professional interviews with intelligent question generation, natural conversation flow, and detailed candidate assessment.

## Project Structure
```
FinalRound/
├── agents/                    # Multi-agent system components
│   ├── __init__.py
│   ├── orchestrator_agent.py  # Central coordinator agent
│   └── interviewer_agent.py   # Question generation agent
├── core/                      # Core system components
│   ├── __init__.py
│   ├── document_parser.py     # Resume and job description parser
│   ├── session_manager.py     # Session persistence and management
│   └── cli.py                 # Command-line interface
├── data/                      # Data storage directories
│   ├── sessions/              # Interview session data
│   ├── transcripts/           # Interview transcripts
│   └── evaluations/           # Candidate evaluation reports
├── main.py                    # CLI application entry point
├── requirements.txt           # Python dependencies
├── sample_job_description.txt # Sample job posting data
├── sample_resume.txt          # Sample resume data
├── Plan.md                    # 3-phase implementation plan
└── CLAUDE.md                  # This documentation file
```

## Technology Stack
- **AI Framework**: LlamaIndex 0.11.0
- **LLM Provider**: OpenAI GPT-4
- **CLI Framework**: Rich (terminal formatting)
- **Runtime**: Python 3.x
- **Session Storage**: JSON-based persistence

## Key Features
- **Multi-Agent Architecture**: Orchestrator and Interviewer agents working in coordination
- **Document Analysis**: Automatic parsing of job descriptions and resumes
- **Dynamic Question Generation**: Context-aware questions based on job requirements
- **Session Persistence**: Auto-save with 15-minute timeout and recovery
- **Real-time Evaluation**: Continuous assessment during interviews
- **Rich CLI Interface**: Professional terminal interface with progress indicators
- **Comprehensive Reporting**: Detailed transcripts and evaluation reports

## Key Dependencies
- `llama-index` - Multi-agent framework and LLM integration
- `llama-index-llms-openai` - OpenAI LLM integration
- `python-dotenv` - Environment configuration
- `rich` - Terminal formatting and CLI interface
- `fastapi` - Web framework (legacy, not currently used)

## Phase 1 Implementation Status ✅
**COMPLETED** - All Phase 1 deliverables have been implemented and tested:

### Core Infrastructure
- ✅ Project directory structure created
- ✅ LlamaIndex and dependencies installed
- ✅ Environment configuration (.env with OpenAI API key)
- ✅ Basic CLI framework implemented

### Document Processing
- ✅ Document parser for job descriptions and resumes
- ✅ Skill matching and requirement analysis
- ✅ Structured data extraction for agent consumption

### Session Management
- ✅ Session persistence using JSON
- ✅ Auto-save functionality (30-second intervals)
- ✅ 15-minute timeout with warning system
- ✅ Resume capability from checkpoints

### Agent Implementation
- ✅ **OrchestratorAgent**: Central coordination, shared state management, document analysis
- ✅ **InterviewerAgent**: Question generation, conversation flow, contextual responses
- ✅ Multi-agent communication and coordination

### CLI Interface
- ✅ Rich terminal interface with menus and progress indicators
- ✅ Interactive command system with help and status commands
- ✅ Session lifecycle management (create, resume, save, end)
- ✅ Timeout warnings and session monitoring

## Setup and Running
```bash
# Install dependencies
pip install -r requirements.txt

# Set up OpenAI API key (already configured in .env)
# OPENAI_API_KEY=your_api_key_here

# Run the multi-agent interview system
python main.py
```

## Usage Instructions
1. **Start New Interview**: Select option 1, provide job description and resume paths
2. **Resume Session**: Select option 2 to continue a previous interview
3. **During Interview**: 
   - Respond naturally to questions
   - Use `help` for available commands
   - Use `status` to check progress
   - Use `save` to manually save session
   - Use `exit` to end and generate reports

## Development Commands
- **Run interview system**: `python main.py`
- **Install dependencies**: `pip install -r requirements.txt`
- **Check data output**: View files in `data/` directories

## Sample Data
- `sample_job_description.txt` - Senior Backend Engineer role at TechCo
- `sample_resume.txt` - John Doe's software engineer profile

## Next Development Phases
- **Phase 2**: TopicManagerAgent, EvaluatorAgent, advanced question logic
- **Phase 3**: Enhanced evaluation reports, system optimization, advanced features

## Notes
- OpenAI API key is configured and ready for use
- Session data auto-saves every 30 seconds
- Interview timeout after 15 minutes of inactivity
- Comprehensive error handling and recovery
- Rich CLI provides professional interview experience