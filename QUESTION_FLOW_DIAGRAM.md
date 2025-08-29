# 🔄 FinalRound Question Generation Flow Diagram

## 📋 Complete Interview Flow Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTERVIEW SESSION START                     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│              DOCUMENT ANALYSIS PHASE                           │
│  ┌─────────────────┐         ┌─────────────────┐               │
│  │  Job Description│         │     Resume      │               │
│  │   Parsing       │         │    Parsing      │               │
│  │                 │         │                 │               │
│  │ • Title & Company│         │• Name & Title   │               │
│  │ • Requirements  │         │• Skills List    │               │
│  │ • Responsibilities│        │• Experience     │               │
│  │ • Preferences   │         │• Education      │               │
│  └─────────┬───────┘         └───────┬─────────┘               │
│            │                         │                         │
│            └─────────┬───────────────┘                         │
│                      ▼                                         │
│            ┌─────────────────────┐                             │
│            │   SKILL MATCHING    │                             │
│            │                     │                             │
│            │ • Gap Analysis      │                             │
│            │ • Strength Areas    │                             │
│            │ • Priority Topics   │                             │
│            └─────────┬───────────┘                             │
└──────────────────────┼─────────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────────┐
│                 SHARED STATE SETUP                             │
│                                                                │
│  shared_state = {                                              │
│    "job_description": parsed_job,                              │
│    "resume": parsed_resume,                                    │
│    "skill_matching": analysis_result,                          │
│    "current_focus_areas": [priority_skills],                   │
│    "completed_topics": [],                                     │
│    "next_topic": first_priority_skill                          │
│  }                                                             │
└──────────────────────┬─────────────────────────────────────────┘
                       │
┌──────────────────────▼─────────────────────────────────────────┐
│               INTERVIEW CONVERSATION LOOP                      │
└──────────────────────┬─────────────────────────────────────────┘
                       │
            ┌──────────▼──────────┐
            │   USER RESPONSE     │
            │    INPUT            │
            └──────────┬──────────┘
                       │
            ┌──────────▼──────────┐
            │  COMMAND CHECK      │
            │                    │
            │ help → Show commands│
            │ status → Progress   │
            │ save → Persist      │
            │ exit → End session  │
            └──────────┬──────────┘
                       │ (Not a command)
                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                 RESPONSE ANALYSIS                               │
│                                                                │
│  ┌─────────────────────┐  ┌─────────────────────┐              │
│  │  Response Length    │  │  Content Analysis   │              │
│  │  Assessment         │  │                     │              │
│  │                     │  │ • Technical keywords│              │
│  │ • < 20 words:       │  │ • Experience depth  │              │
│  │   Needs elaboration │  │ • Confidence level  │              │
│  │ • 20-50 words:      │  │ • Knowledge gaps    │              │
│  │   Ask challenges    │  │ • Follow-up needs   │              │
│  │ • > 50 words:       │  │                     │              │
│  │   Probe deeper      │  │                     │              │
│  └─────────────────────┘  └─────────────────────┘              │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│               QUESTION STRATEGY DECISION                        │
│                                                                │
│              ┌─────────────────────────┐                       │
│              │    PHASE ANALYSIS       │                       │
│              │                         │                       │
│              │ Current Phase:          │                       │
│              │ ├─ Introduction         │                       │
│              │ ├─ Technical            │                       │
│              │ ├─ Behavioral           │                       │
│              │ └─ Situational          │                       │
│              └─────────┬───────────────┘                       │
│                        │                                       │
│    ┌───────────────────┼───────────────────┐                   │
│    ▼                   ▼                   ▼                   │
│ ┌──────────┐    ┌──────────────┐    ┌─────────────┐            │
│ │FOLLOW-UP │    │  NEW TOPIC   │    │ TRANSITION  │            │
│ │ QUESTION │    │   QUESTION   │    │  QUESTION   │            │
│ │          │    │              │    │             │            │
│ │Based on  │    │Based on      │    │Move to next │            │
│ │previous  │    │uncovered     │    │interview    │            │
│ │response  │    │focus areas   │    │phase        │            │
│ └──────────┘    └──────────────┘    └─────────────┘            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│              STREAMING QUESTION GENERATION                      │
│                                                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │            CONTEXT COMPILATION STAGE                        │ │
│  │                                                             │ │
│  │  prompt_parts = [                                           │ │
│  │    "You are an experienced technical interviewer",          │ │
│  │    f"Job Role: {job_desc.title}",                          │ │
│  │    f"Key Requirements: {requirements[:3]}",                 │ │
│  │    f"Candidate: {resume.name}",                            │ │
│  │    f"Key Skills: {candidate_skills[:5]}",                  │ │
│  │    f"Focus Topic: {current_topic}",                        │ │
│  │    f"Additional Context: {user_response}",                 │ │
│  │    f"Question Style: {type_instructions}",                 │ │
│  │    "Generate only the question - no extra text"            │ │
│  │  ]                                                          │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                │                                │
│  ┌─────────────────────────────▼───────────────────────────────┐ │
│  │              OPENAI STREAMING API CALL                     │ │
│  │                                                             │ │
│  │  for chunk in streaming_llm.stream_complete(prompt):        │ │
│  │      chunk_text = chunk.delta                               │ │
│  │      full_question += chunk_text                            │ │
│  │      callback(chunk_text)  # Real-time display             │ │
│  └─────────────────────────────┬───────────────────────────────┘ │
│                                │                                │
│  ┌─────────────────────────────▼───────────────────────────────┐ │
│  │                UI DISPLAY                                   │ │
│  │                                                             │ │
│  │  Option 1: "🤔 Generating question..." → Complete panel     │ │
│  │  Option 2: "Interviewer: " + real-time typewriter effect   │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────┐
│            SESSION STATE UPDATE                                │
│                                                                │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ session.questions_asked.append(generated_question)          │ │
│  │ session.responses.append(user_response)                     │ │
│  │ session.update_activity_timestamp()                         │ │
│  │ shared_state["completed_topics"].append(current_topic)      │ │
│  │ shared_state["next_topic"] = determine_next_focus()         │ │
│  └─────────────────────────────────────────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
          ┌───────────▼───────────┐
          │    TIMEOUT CHECK      │
          │                       │
          │ • 15 min session limit│
          │ • Warning at 5,2,1 min│
          │ • Auto-save every 30s │
          └───────────┬───────────┘
                      │
                      ▼
              ┌───────────────┐     ┌─────────────────┐
              │   CONTINUE    │────▶│  BACK TO LOOP   │
              │   INTERVIEW   │     │   (USER INPUT)  │
              └───────────────┘     └─────────────────┘
                      │
                  (On exit)
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  END INTERVIEW                                  │
│                                                                │
│  • Generate transcript file (data/transcripts/)                │
│  • Generate evaluation report (data/evaluations/)              │
│  • Save final session state (data/sessions/)                   │
│  • Display completion summary                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Question Type Decision Matrix

```
┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐
│  INTERVIEW      │    QUESTION     │     TRIGGER     │    AI FOCUS     │
│    PHASE        │     TYPE        │   CONDITIONS    │   STRATEGY      │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│  Introduction   │  Opening        │ • First question│ • Build rapport │
│                 │  Icebreaker     │ • Session start │ • Set tone      │
│                 │                 │                 │ • Gather basics │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│   Technical     │  Skill-based    │ • Job req match │ • Test depth    │
│                 │  Implementation │ • Candidate exp │ • Verify claims │
│                 │  Problem-solving│ • Gap analysis  │ • Assess ability│
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│  Behavioral     │  STAR format    │ • Team skills   │ • Past behavior │
│                 │  Experience     │ • Leadership req│ • Soft skills   │
│                 │  Situational    │ • Culture fit   │ • Work style    │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│  Situational    │  Hypothetical   │ • Role scenarios│ • Decision logic│
│                 │  Problem-based  │ • Critical think│ • Problem solve │
│                 │  Design         │ • Architecture  │ • Trade-offs    │
├─────────────────┼─────────────────┼─────────────────┼─────────────────┤
│   Follow-up     │  Clarification  │ • Shallow resp  │ • Dig deeper    │
│                 │  Deep-dive      │ • Technical hint│ • Verify depth  │
│                 │  Expansion      │ • Interesting pt│ • Explore more  │
└─────────────────┴─────────────────┴─────────────────┴─────────────────┘
```

## 🧠 AI Reasoning Decision Tree

```
                    ┌─────────────────────┐
                    │   USER RESPONSE     │
                    │     RECEIVED        │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  ANALYZE RESPONSE   │
                    │                     │
                    │ • Length check      │
                    │ • Technical depth   │
                    │ • Confidence level  │
                    │ • Completeness      │
                    └──────────┬──────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │   SHALLOW   │    │   MEDIUM    │    │    DEEP     │
    │  RESPONSE   │    │  RESPONSE   │    │  RESPONSE   │
    │             │    │             │    │             │
    │ < 20 words  │    │ 20-50 words │    │ > 50 words  │
    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
           │                  │                  │
           ▼                  ▼                  ▼
    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
    │ ENCOURAGE   │    │  ASK ABOUT  │    │  PROBE FOR │
    │ELABORATION  │    │ CHALLENGES  │    │  INSIGHTS   │
    │             │    │             │    │             │
    │"Can you     │    │"What were   │    │"What lessons│
    │elaborate?"  │    │the          │    │did you      │
    │             │    │challenges?" │    │learn?"      │
    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
           │                  │                  │
           └──────────────────┼──────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │  CHECK COVERAGE   │
                    │                   │
                    │ • Topics covered  │
                    │ • Skills assessed │
                    │ • Time remaining  │
                    │ • Phase progress  │
                    └─────────┬─────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌─────────────┐   ┌─────────────┐   ┌─────────────┐
    │  CONTINUE   │   │ TRANSITION  │   │ FOLLOW-UP   │
    │ SAME TOPIC  │   │  TO NEW     │   │   DEEPER    │
    │             │   │   TOPIC     │   │             │
    │ More depth  │   │ Next skill  │   │ Clarify/    │
    │ needed      │   │ area        │   │ Expand      │
    └──────┬──────┘   └──────┬──────┘   └──────┬──────┘
           │                 │                 │
           └─────────────────┼─────────────────┘
                             │
                  ┌──────────▼──────────┐
                  │  GENERATE QUESTION  │
                  │                     │
                  │ • Context aware     │
                  │ • Skill targeted    │
                  │ • Difficulty tuned  │
                  │ • Conversation flow │
                  └──────────┬──────────┘
                             │
                  ┌──────────▼──────────┐
                  │   STREAM TO USER    │
                  │                     │
                  │ Real-time display   │
                  │ Professional format │
                  └─────────────────────┘
```

This comprehensive flow diagram shows how the FinalRound system intelligently generates contextual questions through multi-agent coordination, real-time analysis, and adaptive AI reasoning patterns.