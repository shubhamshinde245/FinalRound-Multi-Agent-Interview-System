🧪 FinalRound CLI Testing Steps

  Here are the step-by-step instructions to test the FinalRound system in
   your CLI:

  📋 Prerequisites Check

  First, make sure you're in the project directory and everything is set
  up:

  # Navigate to project directory
  cd /Users/shubhamshinde/Desktop/Projects/FinalRound

  # Verify you're in the right place
  ls -la
  # Should see: agents/ core/ data/ tests/ main.py requirements.txt etc.

  🚀 Step 1: Run Automated Tests

  Start by running the automated test suite to verify everything works:

  # Run the complete test suite
  python tests/run_all_tests.py

  Expected Output:
  🎉 ALL TEST SUITES PASSED!
  ✅ FinalRound Phase 1 is ready for production use
  🚀 System is fully functional and tested

  If tests fail, check:
  - OpenAI API key is properly set in .env
  - All dependencies are installed: pip install -r requirements.txt

  🎯 Step 2: Test the Main CLI Application

  Launch the interactive interview system:

  # Start the FinalRound CLI
  python main.py

  You should see:
  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Welcome ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
  ┃                                                              ┃
  ┃ 🎯 FinalRound - Multi-Agent Interview System                 ┃
  ┃                                                              ┃
  ┃ Features:                                                    ┃
  ┃ • AI-powered technical interviews                            ┃
  ┃ • Real-time candidate evaluation                             ┃
  ┃ • Session persistence with 15-minute timeout                 ┃
  ┃ • Comprehensive interview transcripts                        ┃
  ┃ • Detailed evaluation reports                                ┃
  ┃                                                              ┃
  ┃ Ready to conduct professional technical interviews!          ┃
  ┃                                                              ┃
  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

                  Main Menu
  ┏━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┓
  ┃ Option     ┃ Description              ┃
  ┡━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━┩
  │ 1          │ Start New Interview      │
  │ 2          │ Resume Interview Session │
  │ 3          │ View Session Status      │
  │ 4          │ End Current Session      │
  │ 5          │ Exit                     │
  └────────────┴──────────────────────────┘

  Select an option [1/2/3/4/5]:

  🎪 Step 3: Test New Interview Flow

  Select Option 1 to test starting a new interview:

  # At the prompt, type:
  1

  3.1 File Path Testing

  You'll be prompted for file paths:

  📄 Job Description file path [sample_job_description.txt]:
  # Press ENTER to use default, or type: sample_job_description.txt

  📋 Resume file path [sample_resume.txt]:
  # Press ENTER to use default, or type: sample_resume.txt

  👤 Candidate Name (optional):
  # Type: Test Candidate (or press ENTER)

  3.2 Watch Agent Initialization

  You should see:
  🚀 Starting New Interview

  Initializing multi-agent system...
  ✓ Setting up Orchestrator Agent...
  ✓ Setting up Interviewer Agent...
  ✓ Multi-agent system ready!

  Analyzing documents and setting up interview...

  3.3 Test Interview Conversation

  The system will start the interview:

  🎙️  Interview Started
  Type 'help' for commands, 'exit' to end interview

  ┏━━━━━━━━━━━━━━━━━━━━━━ Interviewer ━━━━━━━━━━━━━━━━━━━━━━┓
  ┃                                                     ┃
  ┃ Let's start with a brief introduction. Can you      ┃
  ┃ tell me about your current role and what drew you   ┃
  ┃ to apply for this position?                         ┃
  ┃                                                     ┃
  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  Your response:

  Test responses:
  # Try these sample responses:
  I am currently a Senior Software Engineer with 5 years of Python
  experience. I'm interested in this Backend Engineer role because I want
   to work on distributed systems and lead technical initiatives.

  🔧 Step 4: Test CLI Commands

  During the interview, test these commands:

  4.1 Help Command

  Your response: help

  Should show:
  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
  ┃ Available Commands                                         ┃
  ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
  │ help        │ Show this help menu                          │
  │ status      │ Show current interview status                │
  │ save        │ Save current session                         │
  │ exit        │ End interview and generate reports           │
  └─────────────┴──────────────────────────────────────────────┘

  4.2 Status Command

  Your response: status

  Should show session details:
  ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
  ┃ Session Status                                             ┃
  ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
  │ Session ID       │ interview_20250828_214530               │
  │ Candidate        │ Test Candidate                          │
  │ Position         │ Senior Backend Engineer                 │
  │ Current Phase    │ introduction                            │
  │ Questions Asked  │ 2                                       │
  │ Time Remaining   │ 847 seconds                             │
  └──────────────────┴─────────────────────────────────────────┘

  4.3 Save Command

  Your response: save

  Should show:
  ✅ Session saved

  📊 Step 5: Test Interview Completion

  End the interview to test report generation:

  Your response: exit

  Should show:
  📝 Ending Interview & Generating Reports

  ◐ Finalizing interview session...
  ◑ Generating transcript...
  ◒ Creating evaluation report...
  ◓ Interview completed!

  ✅ Interview completed successfully!
  📄 Transcript:
  data/transcripts/interview_20250828_214530_transcript.json
  📊 Evaluation: 
  data/evaluations/interview_20250828_214530_evaluation.json

  Thank you for using FinalRound!

  📁 Step 6: Verify Generated Files

  Check that files were created:

  # Check session files
  ls -la data/sessions/
  # Should see: interview_YYYYMMDD_HHMMSS.json

  # Check transcript files  
  ls -la data/transcripts/
  # Should see: interview_YYYYMMDD_HHMMSS_transcript.json

  # Check evaluation files
  ls -la data/evaluations/
  # Should see: interview_YYYYMMDD_HHMMSS_evaluation.json

  # View a transcript (optional)
  cat data/transcripts/interview_*.json | head -20

  # View an evaluation (optional) 
  cat data/evaluations/interview_*.json | head -20

  🔄 Step 7: Test Session Resume

  Test the session resume functionality:

  # Start the CLI again
  python main.py

  # Select option 2
  2

  Should show available sessions and allow you to resume one.

  ⏰ Step 8: Test Timeout Warnings (Optional)

  If you want to test timeout warnings:

  # Start a new interview
  python main.py
  # Choose option 1, go through setup
  # Then wait ~14 minutes to see timeout warnings
  # Or modify session_manager.py temporarily to use shorter timeout for 
  testing

  🚨 Troubleshooting

  Common Issues:

  1. OpenAI API Errors:
  # Check your API key
  cat .env
  # Should show: OPENAI_API_KEY=sk-proj-...

  2. Import Errors:
  # Install dependencies
  pip install -r requirements.txt

  3. File Not Found:
  # Verify you're in the right directory
  pwd
  # Should end with: /FinalRound

  # Check files exist
  ls sample_*.txt

  4. Permission Errors:
  # Make sure data directories are writable
  chmod -R 755 data/

  ✅ Success Criteria

  Your CLI testing is successful when you can:
  - ✅ Start the application and see the welcome screen
  - ✅ Navigate the menu system
  - ✅ Start a new interview with document analysis
  - ✅ Interact with the interview conversation
  - ✅ Use help, status, and save commands
  - ✅ End the interview and see report generation
  - ✅ Find generated transcript and evaluation files
  - ✅ Resume a previous session

  🎉 If all steps work, your FinalRound Phase 1 implementation is fully 
  functional!

⏺ These steps will comprehensively test your FinalRound multi-agent
  interview system and verify that all Phase 1 functionality is working
  correctly! 🚀