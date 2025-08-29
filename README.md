# 🎯 FinalRound - Multi-Agent Interview System

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)](https://www.python.org/)
[![LlamaIndex](https://img.shields.io/badge/LlamaIndex-0.11.0-green)](https://llamaindex.ai/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange)](https://openai.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

> **AI-powered technical interview system with real-time streaming question generation, multi-agent coordination, and comprehensive candidate assessment.**

## 🚀 Overview

FinalRound is a sophisticated multi-agent interview system that conducts automated technical interviews with intelligent question generation, natural conversation flow, and detailed candidate evaluation. The system uses LlamaIndex framework with OpenAI GPT-4 to create engaging, contextual interviews that adapt in real-time based on candidate responses.

## ✨ Key Features

- 🤖 **Multi-Agent Architecture**: Orchestrator and Interviewer agents working in coordination
- ⚡ **Real-time Streaming**: Questions generated and displayed with streaming typewriter effects
- 📋 **Document Analysis**: Automatic parsing of job descriptions and resumes with skill matching
- 💾 **Session Persistence**: Auto-save with 15-minute timeout and recovery capabilities
- 🎨 **Rich CLI Interface**: Professional terminal interface with progress indicators
- 📊 **Comprehensive Reporting**: Detailed transcripts and evaluation reports
- 🔄 **Adaptive Intelligence**: Dynamic question difficulty and contextual follow-ups
- 🎯 **Context-Aware Questions**: Intelligent question generation based on role requirements

## 🏗️ Multi-Agent Architecture

### Agent Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        FINALROUND MULTI-AGENT SYSTEM                   │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────┐
│                           CLI INTERFACE                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │  User Commands  │  │ Streaming UI    │  │ Progress Track  │         │
│  │ • help, status  │  │ • Real-time gen │  │ • Timeout warn  │         │
│  │ • save, exit    │  │ • Typewriter    │  │ • Auto-save     │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
            ┌─────────────────────┼─────────────────────┐
            ▼                     ▼                     ▼
┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐
│ ORCHESTRATOR      │   │   INTERVIEWER     │   │ SESSION MANAGER   │
│     AGENT         │◄──┤      AGENT        │   │                   │
│                   │   │                   │   │ • State tracking  │
│ • Document parse  │   │ • Question gen    │   │ • Persistence     │
│ • Skill matching  │   │ • Streaming LLM   │   │ • Report creation │
│ • State coord     │   │ • Follow-up logic │   │ • Timeout mgmt    │
│ • Topic planning  │   │ • Conversation    │   │ • Auto-save       │
│ • Agent sync      │   │   flow mgmt       │   │                   │
└─────────┬─────────┘   └─────────┬─────────┘   └─────────┬─────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  │
                    ┌─────────────▼─────────────┐
                    │      SHARED STATE         │
                    │                           │
                    │ • job_description         │
                    │ • resume                  │
                    │ • skill_matching          │
                    │ • current_focus_areas     │
                    │ • completed_topics        │
                    │ • next_topic              │
                    │ • interview_context       │
                    └───────────────────────────┘
```

### Agent Responsibilities

#### 🎯 **Orchestrator Agent**
- **Document Analysis**: Parses job descriptions and resumes
- **Skill Matching**: Identifies gaps and strengths
- **State Management**: Maintains shared context across agents
- **Interview Coordination**: Manages phases and topic progression
- **Strategic Planning**: Determines optimal interview flow

#### 🎙️ **Interviewer Agent** 
- **Question Generation**: Creates contextual, role-specific questions
- **Streaming Response**: Real-time question delivery with OpenAI streaming
- **Follow-up Logic**: Analyzes responses for depth and follow-up needs
- **Conversation Flow**: Maintains natural dialogue progression
- **Adaptive Difficulty**: Adjusts question complexity based on candidate performance

#### 💾 **Session Manager**
- **Persistence**: Saves interview state every 30 seconds
- **Timeout Management**: 15-minute inactivity warnings
- **Report Generation**: Creates transcripts and evaluation files
- **Recovery**: Enables resume from previous sessions

## 🧠 Intelligent Question Generation

### AI Reasoning Process

```
User Response → Context Analysis → Strategic Decision → Question Generation → Streaming Display
      │              │                    │                   │                │
      ▼              ▼                    ▼                   ▼                ▼
┌──────────┐  ┌─────────────┐  ┌─────────────────┐  ┌─────────────┐  ┌─────────────┐
│Response  │  │• Length     │  │• Phase check    │  │• LLM prompt │  │• Typewriter │
│Processing│  │• Technical  │  │• Topic select   │  │• Context    │  │• Panel view │
│          │  │  depth      │  │• Difficulty     │  │• Streaming  │  │• Professional│
│          │  │• Confidence │  │• Follow-up vs   │  │• Callback   │  │  formatting │
│          │  │• Engagement │  │  new topic      │  │             │  │             │
└──────────┘  └─────────────┘  └─────────────────┘  └─────────────┘  └─────────────┘
```

### Question Types & Intelligence

- **📋 Technical**: Implementation details, problem-solving, hands-on experience
- **🤝 Behavioral**: STAR format, teamwork, leadership, past experiences  
- **🧩 Situational**: Role scenarios, decision-making, hypothetical challenges
- **🏗️ System Design**: Architecture, scalability, trade-offs, high-level thinking
- **🔄 Follow-up**: Adaptive depth probing based on response quality

## 📁 Project Structure

```
FinalRound/
├── 📚 Documentation
│   ├── README.md                           # This comprehensive guide
│   ├── CLAUDE.md                          # Project instructions & setup
│   ├── Plan.md                            # 3-phase implementation plan
│   ├── QUESTION_GENERATION_ANALYSIS.md    # AI thought process analysis
│   ├── QUESTION_FLOW_DIAGRAM.md           # Visual decision flow diagrams
│   ├── AI_REASONING_PATTERNS.md           # Cognitive strategies & patterns
│   └── cli_test.md                        # CLI testing documentation
│
├── 🤖 Multi-Agent System
│   ├── agents/
│   │   ├── orchestrator_agent.py          # Central coordinator agent
│   │   └── interviewer_agent.py           # Question generation agent
│   │
│   ├── core/
│   │   ├── cli.py                         # Rich terminal interface
│   │   ├── document_parser.py             # Resume & job description parser
│   │   └── session_manager.py             # Session persistence & management
│   │
│   └── main.py                            # CLI application entry point
│
├── 🧪 Testing Suite  
│   ├── tests/
│   │   ├── README.md                      # Test documentation
│   │   ├── run_all_tests.py               # Complete test suite runner
│   │   ├── test_core_logic.py             # Core functionality tests
│   │   ├── test_simplified.py             # OpenAI-free testing
│   │   └── fixtures/                      # Test data files
│   │
│   └── test_streaming.py                  # Streaming functionality tests
│
├── 📊 Data Storage
│   ├── data/sessions/                     # Interview session files
│   ├── data/transcripts/                  # Complete interview transcripts
│   └── data/evaluations/                  # Candidate assessment reports
│
└── 📋 Sample Data
    ├── sample_job_description.txt         # Example job posting
    ├── sample_resume.txt                  # Example candidate resume
    └── requirements.txt                   # Python dependencies
```

## 🛠️ Technology Stack

- **🧠 AI Framework**: LlamaIndex 0.11.0 (Multi-agent orchestration)
- **🤖 LLM Provider**: OpenAI GPT-4 (Question generation & analysis)
- **🎨 CLI Framework**: Rich (Professional terminal interface)
- **💾 Persistence**: JSON-based session storage
- **🐍 Runtime**: Python 3.8+
- **🔧 Environment**: python-dotenv for configuration

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Installation Steps

```bash
# 1. Clone the repository
git clone <repository-url>
cd FinalRound

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_api_key_here" > .env

# 4. Run the system
python main.py
```

### Quick Start
```bash
# Run complete test suite
python tests/run_all_tests.py

# Test streaming functionality  
python test_streaming.py

# Start interview system
python main.py
```

## 🎮 Usage Guide

### Starting an Interview
1. **Launch**: `python main.py`
2. **Select**: "1. Start New Interview" 
3. **Provide Files**: Job description and resume paths
4. **Begin**: Answer questions naturally as they stream in real-time

### Available Commands
- `help` - Show available commands
- `status` - Display interview progress
- `save` - Manually save session
- `exit` - End interview and generate reports

### Session Management
- **Auto-save**: Every 30 seconds
- **Timeout**: 15 minutes with warnings at 5, 2, and 1 minute
- **Resume**: Continue previous sessions
- **Reports**: Automatic transcript and evaluation generation

## 📊 Sample Interview Flow

```
Welcome to FinalRound! 
🎯 Starting interview for John Doe - Senior Backend Engineer position

[Streaming] 🤔 Generating your next question...

┌─────────────────────────────────────────────────────────────────┐
│                          Interviewer                           │
├─────────────────────────────────────────────────────────────────┤
│ Let's start with your experience with Python. Can you walk me  │
│ through a recent project where you used Python for backend     │
│ development, particularly focusing on any challenges you       │
│ encountered with scalability or performance optimization?       │
└─────────────────────────────────────────────────────────────────┘

Your response: [Detailed technical response about microservices...]

[Streaming] 🤔 Generating your next question...

┌─────────────────────────────────────────────────────────────────┐
│                          Interviewer                           │
├─────────────────────────────────────────────────────────────────┤
│ That's great insight into microservices architecture. You      │
│ mentioned handling communication between services - how did you │
│ approach service discovery and what trade-offs did you         │
│ consider between synchronous and asynchronous communication?    │
└─────────────────────────────────────────────────────────────────┘
```

## 📚 Documentation Links

### 📖 **Core Documentation**
- **[Project Setup & Instructions](CLAUDE.md)** - Comprehensive project overview and setup
- **[Implementation Plan](Plan.md)** - 3-phase development roadmap with detailed milestones
- **[CLI Testing Guide](cli_test.md)** - Step-by-step testing instructions

### 🧠 **AI & Intelligence Analysis** 
- **[Question Generation Analysis](QUESTION_GENERATION_ANALYSIS.md)** - Deep dive into AI thought processes
- **[Flow Diagrams](QUESTION_FLOW_DIAGRAM.md)** - Visual decision trees and process flows
- **[AI Reasoning Patterns](AI_REASONING_PATTERNS.md)** - Cognitive strategies and adaptive intelligence

### 🧪 **Testing Documentation**
- **[Test Suite Guide](tests/README.md)** - Complete testing framework documentation
- **[Test Results & Coverage](tests/)** - Unit, integration, and system tests

## 🔬 Advanced Features

### Streaming Question Generation
- **Real-time Display**: Questions appear as they're generated
- **Professional UI**: Clean panels with typewriter effects
- **Fallback Support**: Graceful degradation if streaming fails
- **Context Awareness**: Each question builds on previous responses

### Adaptive Intelligence
- **Response Analysis**: Length, depth, and confidence assessment
- **Dynamic Difficulty**: Adjusts complexity based on candidate performance
- **Follow-up Logic**: Intelligent probing for deeper insights
- **Topic Management**: Strategic coverage of all critical areas

### Session Management
- **Persistence**: Automatic state saving and recovery
- **Timeout Handling**: Professional warning system
- **Report Generation**: Comprehensive transcripts and evaluations
- **Multi-session Support**: Resume interrupted interviews

## 🎯 Phase 1 Status: ✅ COMPLETED

All Phase 1 deliverables have been successfully implemented:

- ✅ **Core Infrastructure**: Project structure, dependencies, environment setup
- ✅ **Document Processing**: Job description and resume parsing with skill matching
- ✅ **Multi-Agent System**: Orchestrator and Interviewer agents with coordination
- ✅ **Session Management**: Persistence, timeout, auto-save, and recovery
- ✅ **Rich CLI Interface**: Professional terminal experience with streaming
- ✅ **Streaming Questions**: Real-time generation with OpenAI streaming API
- ✅ **Comprehensive Testing**: Full test suite with documentation
- ✅ **Advanced Analysis**: AI reasoning documentation and flow diagrams

## 🚀 Next Development Phases

### **Phase 2: Advanced Agent Logic** (Planned)
- TopicManager Agent for intelligent topic transitions
- Evaluator Agent for real-time candidate assessment
- Advanced question sequencing and difficulty scaling
- Enhanced behavioral and situational question generation

### **Phase 3: System Optimization** (Planned)
- Enhanced evaluation reports with scoring algorithms
- System performance optimization and caching
- Advanced analytics and candidate insights
- Integration capabilities and API development

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **LlamaIndex** for the powerful multi-agent framework
- **OpenAI** for GPT-4 and streaming API capabilities
- **Rich** library for beautiful terminal interfaces
- **Python Community** for excellent tooling and libraries

---

<div align="center">

**🎯 FinalRound - Intelligent Technical Interviews Powered by AI**

*Built with ❤️ using LlamaIndex, OpenAI GPT-4, and Python*

</div>