import os
import sys
import time
import threading
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.layout import Layout
from rich.text import Text

from core.session_manager import SessionManager
from agents.orchestrator_agent import OrchestratorAgent
from agents.interviewer_agent import InterviewerAgent


class InterviewCLI:
    def __init__(self):
        self.console = Console()
        self.session_manager = SessionManager()
        self.orchestrator = None
        self.interviewer = None
        self.is_interview_active = False
        self.warning_thread = None
        self.warning_active = False
        
    def display_welcome(self):
        """Display welcome screen and system overview."""
        welcome_panel = Panel(
            """
🎯 [bold blue]FinalRound - Multi-Agent Interview System[/bold blue]

[yellow]Features:[/yellow]
• AI-powered technical interviews
• Real-time candidate evaluation
• Session persistence with 15-minute timeout
• Comprehensive interview transcripts
• Detailed evaluation reports

[green]Ready to conduct professional technical interviews![/green]
            """,
            title="Welcome",
            border_style="blue"
        )
        
        self.console.print(welcome_panel)
        self.console.print()
    
    def display_menu(self):
        """Display main menu options."""
        table = Table(title="Main Menu", show_header=True)
        table.add_column("Option", style="cyan", width=10)
        table.add_column("Description", style="white")
        
        table.add_row("1", "Start New Interview")
        table.add_row("2", "Resume Interview Session")
        table.add_row("3", "View Session Status")
        table.add_row("4", "End Current Session")
        table.add_row("5", "Exit")
        
        self.console.print(table)
        self.console.print()
    
    def get_file_paths(self):
        """Get job description and resume file paths from user."""
        self.console.print("[yellow]Please provide the following files:[/yellow]")
        
        # Get job description path
        while True:
            job_desc_path = Prompt.ask("📄 Job Description file path", default="sample_job_description.txt")
            if os.path.exists(job_desc_path):
                break
            self.console.print(f"[red]File not found: {job_desc_path}[/red]")
        
        # Get resume path  
        while True:
            resume_path = Prompt.ask("📋 Resume file path", default="sample_resume.txt")
            if os.path.exists(resume_path):
                break
            self.console.print(f"[red]File not found: {resume_path}[/red]")
        
        return job_desc_path, resume_path
    
    def initialize_agents(self):
        """Initialize the multi-agent system."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            
            task = progress.add_task("Initializing multi-agent system...", total=None)
            
            # Initialize orchestrator
            progress.update(task, description="Setting up Orchestrator Agent...")
            self.orchestrator = OrchestratorAgent(self.session_manager)
            time.sleep(1)
            
            # Initialize interviewer with shared state
            progress.update(task, description="Setting up Interviewer Agent...")
            shared_state = self.orchestrator.get_shared_state()
            self.interviewer = InterviewerAgent(self.session_manager, shared_state)
            time.sleep(1)
            
            progress.update(task, description="Multi-agent system ready!")
            time.sleep(0.5)
    
    def start_new_interview(self):
        """Start a new interview session."""
        self.console.print("\n[bold green]🚀 Starting New Interview[/bold green]\n")
        
        # Get file paths
        job_desc_path, resume_path = self.get_file_paths()
        
        # Get candidate name
        candidate_name = Prompt.ask("👤 Candidate Name (optional)", default="")
        
        # Initialize agents if not already done
        if not self.orchestrator:
            self.initialize_agents()
        
        # Initialize interview
        with self.console.status("Analyzing documents and setting up interview..."):
            result = self.orchestrator.initialize_interview(job_desc_path, resume_path, candidate_name)
        
        self.console.print(Panel(result, title="Interview Initialization", border_style="green"))
        
        # Start interview conversation
        self.is_interview_active = True
        self.start_timeout_warnings()
        self.conduct_interview()
    
    def conduct_interview(self):
        """Main interview conversation loop."""
        self.console.print("\n[bold blue]🎙️  Interview Started[/bold blue]")
        self.console.print("[yellow]Type 'help' for commands, 'exit' to end interview[/yellow]\n")
        
        # Start with opening question
        opening_question = self.interviewer.start_interview()
        self.display_question(opening_question)
        
        while self.is_interview_active:
            try:
                # Check for timeout
                if self.session_manager.check_timeout():
                    self.console.print("\n[red]⏰ Session timed out after 15 minutes of inactivity.[/red]")
                    self.end_interview()
                    break
                
                # Get user input
                user_input = Prompt.ask("\n[cyan]Your response[/cyan]")
                
                if user_input.lower() in ['exit', 'quit', 'end']:
                    self.end_interview()
                    break
                elif user_input.lower() == 'help':
                    self.display_help()
                    continue
                elif user_input.lower() == 'status':
                    self.display_session_status()
                    continue
                elif user_input.lower() == 'save':
                    self.session_manager.save_session()
                    self.console.print("[green]✅ Session saved[/green]")
                    continue
                
                # Process response
                self.process_response(user_input)
                
                # Generate next question with streaming
                self.console.print()  # Add spacing
                
                # Determine question type and topic based on interview phase
                current_phase = self.session_manager.current_session.interview_phase if self.session_manager.current_session else "technical"
                current_topic = self.orchestrator.get_shared_state().get("next_topic", "") if self.orchestrator else ""
                
                question_type = current_phase if current_phase in ["technical", "behavioral", "situational"] else "technical"
                
                # Use streaming question generation
                next_question = self.display_streaming_question(
                    question_type=question_type,
                    topic=current_topic,
                    context=user_input
                )
                
                if not next_question:
                    # Fallback to regular generation if streaming fails
                    next_question = self.generate_next_question(user_input)
                    if next_question:
                        self.display_question(next_question)
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Interview interrupted. Saving session...[/yellow]")
                self.session_manager.save_session()
                break
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")
    
    def process_response(self, response: str):
        """Process candidate response and update session."""
        # Record response
        self.session_manager.add_response(response)
        
        # Update activity timestamp
        self.session_manager.update_activity()
        
        # Simple response acknowledgment
        acknowledgments = [
            "Thank you for that response.",
            "I see, that's helpful.",
            "Interesting perspective.",
            "Good, let me ask you about something else."
        ]
        
        # Show brief acknowledgment (optional)
        # self.console.print(f"[dim]{random.choice(acknowledgments)}[/dim]")
    
    def generate_next_question(self, previous_response: str) -> Optional[str]:
        """Generate the next interview question."""
        try:
            # Update shared state with orchestrator
            self.interviewer.shared_state = self.orchestrator.get_shared_state()
            
            # Generate next question based on context
            next_question = self.interviewer.generate_next_question(previous_response)
            
            return next_question
        except Exception as e:
            self.console.print(f"[red]Error generating question: {str(e)}[/red]")
            return None
    
    def display_question(self, question: str):
        """Display interview question in a formatted panel."""
        question_panel = Panel(
            question,
            title="[bold blue]Interviewer[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(question_panel)
    
    def display_streaming_question(self, question_type: str = "technical", topic: str = "", context: str = "", show_realtime: bool = False):
        """Display a streaming interview question as it's being generated."""
        
        if show_realtime:
            # Show real-time streaming (typewriter effect)
            self.console.print("\n[bold blue]Interviewer:[/bold blue]", end=" ")
            question_text = ""
            
            def stream_callback(chunk):
                nonlocal question_text
                question_text += chunk
                self.console.print(chunk, end="", style="white")
                time.sleep(0.02)  # Small delay for typewriter effect
        else:
            # Show thinking indicator then complete question
            self.console.print("\n[dim]🤔 Generating your next question...[/dim]")
            question_text = ""
            
            def stream_callback(chunk):
                nonlocal question_text
                question_text += chunk
        
        try:
            # Use the streaming question generation
            if hasattr(self.interviewer, 'generate_streaming_question'):
                complete_question = self.interviewer.generate_streaming_question(
                    question_type=question_type,
                    topic=topic,
                    context=context,
                    callback=stream_callback
                )
            else:
                # Fallback to non-streaming
                complete_question = self.interviewer.generate_next_question(context)
            
            if show_realtime:
                # Just add a newline since we already showed the text
                self.console.print("\n")
            else:
                # Clear the generation indicator and show final question in a panel
                self.console.print("\r" + " " * 50 + "\r", end="")  # Clear the generating line
                
                # Display the complete question in a nice panel
                question_panel = Panel(
                    complete_question,
                    title="[bold blue]Interviewer[/bold blue]",
                    border_style="blue",
                    padding=(1, 2)
                )
                self.console.print(question_panel)
            
            return complete_question
            
        except Exception as e:
            self.console.print(f"[red]Error generating streaming question: {str(e)}[/red]")
            return None
    
    def display_help(self):
        """Display help commands."""
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        
        help_table.add_row("help", "Show this help menu")
        help_table.add_row("status", "Show current interview status")
        help_table.add_row("save", "Save current session")
        help_table.add_row("exit", "End interview and generate reports")
        
        self.console.print(help_table)
    
    def display_session_status(self):
        """Display current session status."""
        if not self.session_manager.current_session:
            self.console.print("[red]No active session[/red]")
            return
        
        summary = self.session_manager.get_session_summary()
        
        status_table = Table(title="Session Status")
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("Session ID", summary.get("session_id", "N/A"))
        status_table.add_row("Candidate", summary.get("candidate_name", "N/A"))
        status_table.add_row("Position", summary.get("job_title", "N/A"))
        status_table.add_row("Current Phase", summary.get("current_phase", "N/A"))
        status_table.add_row("Questions Asked", str(summary.get("questions_asked", 0)))
        status_table.add_row("Time Remaining", f"{summary.get('time_remaining', 0)} seconds")
        
        self.console.print(status_table)
    
    def start_timeout_warnings(self):
        """Start timeout warning system."""
        def warning_timer():
            while self.warning_active and self.is_interview_active:
                time_remaining = self.session_manager.get_time_remaining()
                
                if time_remaining <= 300 and time_remaining > 240:  # 5 minutes warning
                    self.console.print("\n[yellow]⚠️  Warning: 5 minutes remaining in session[/yellow]")
                    time.sleep(60)  # Wait 1 minute before next check
                elif time_remaining <= 120 and time_remaining > 60:  # 2 minutes warning
                    self.console.print("\n[orange1]⚠️  Warning: 2 minutes remaining in session[/orange1]")
                    time.sleep(30)  # Check every 30 seconds
                elif time_remaining <= 60:  # 1 minute warning
                    self.console.print("\n[red]🚨 Warning: 1 minute remaining in session![/red]")
                    time.sleep(10)  # Check every 10 seconds
                else:
                    time.sleep(60)  # Check every minute
        
        self.warning_active = True
        self.warning_thread = threading.Thread(target=warning_timer, daemon=True)
        self.warning_thread.start()
    
    def end_interview(self):
        """End the current interview and generate reports."""
        self.is_interview_active = False
        self.warning_active = False
        
        self.console.print("\n[bold green]📝 Ending Interview & Generating Reports[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
        ) as progress:
            
            task = progress.add_task("Finalizing interview session...", total=None)
            
            progress.update(task, description="Saving final session data...")
            time.sleep(1)
            
            progress.update(task, description="Generating transcript...")
            self.session_manager.end_session()
            time.sleep(1)
            
            progress.update(task, description="Creating evaluation report...")
            time.sleep(1)
            
            progress.update(task, description="Interview completed!")
            time.sleep(0.5)
        
        if self.session_manager.current_session:
            session_id = self.session_manager.current_session.session_id
            self.console.print(f"\n[green]✅ Interview completed successfully![/green]")
            self.console.print(f"📄 Transcript: data/transcripts/{session_id}_transcript.json")
            self.console.print(f"📊 Evaluation: data/evaluations/{session_id}_evaluation.json")
        
        self.console.print("\n[yellow]Thank you for using FinalRound![/yellow]")
    
    def resume_session(self):
        """Resume a previous interview session."""
        self.console.print("\n[bold yellow]🔄 Resume Interview Session[/bold yellow]")
        
        # List available sessions
        session_files = [f for f in os.listdir("data/sessions") if f.endswith('.json')]
        
        if not session_files:
            self.console.print("[red]No saved sessions found.[/red]")
            return
        
        self.console.print("Available sessions:")
        for i, session_file in enumerate(session_files, 1):
            session_id = session_file.replace('.json', '')
            self.console.print(f"  {i}. {session_id}")
        
        try:
            choice = int(Prompt.ask("Select session number")) - 1
            if 0 <= choice < len(session_files):
                session_id = session_files[choice].replace('.json', '')
                
                if self.session_manager.load_session(session_id):
                    self.console.print(f"[green]✅ Loaded session: {session_id}[/green]")
                    
                    # Initialize agents if needed
                    if not self.orchestrator:
                        self.initialize_agents()
                    
                    # Continue interview
                    self.is_interview_active = True
                    self.start_timeout_warnings()
                    self.conduct_interview()
                else:
                    self.console.print(f"[red]Failed to load session: {session_id}[/red]")
            else:
                self.console.print("[red]Invalid selection[/red]")
        except ValueError:
            self.console.print("[red]Please enter a valid number[/red]")
    
    def run(self):
        """Main CLI loop."""
        self.display_welcome()
        
        while True:
            try:
                self.display_menu()
                choice = Prompt.ask("Select an option", choices=["1", "2", "3", "4", "5"])
                
                if choice == "1":
                    self.start_new_interview()
                elif choice == "2":
                    self.resume_session()
                elif choice == "3":
                    self.display_session_status()
                elif choice == "4":
                    if self.is_interview_active:
                        if Confirm.ask("Are you sure you want to end the current interview?"):
                            self.end_interview()
                    else:
                        self.console.print("[yellow]No active interview session[/yellow]")
                elif choice == "5":
                    if self.is_interview_active:
                        if Confirm.ask("You have an active interview. Save before exiting?"):
                            self.session_manager.save_session()
                    self.console.print("[green]Goodbye![/green]")
                    sys.exit(0)
                
                self.console.print("\n" + "="*50 + "\n")
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Exiting FinalRound...[/yellow]")
                if self.is_interview_active:
                    self.session_manager.save_session()
                sys.exit(0)
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/red]")


if __name__ == "__main__":
    cli = InterviewCLI()
    cli.run()