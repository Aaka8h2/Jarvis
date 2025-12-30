"""
J.A.R.V.I.S. MARK 110 - DUAL INPUT EDITION
Features:
1. Voice + Text Input Support
2. Proper Command Queue System
3. Sequential Processing (One command at a time)
4. Enhanced Response System
5. Manual Text Input Panel
"""

import threading
import subprocess
import speech_recognition as sr
from gtts import gTTS
import sounddevice as sd
import soundfile as sf
import os
import tempfile
import customtkinter as ctk
import ollama
import pyautogui
import pywhatkit
import psutil
import time
import math
import numpy as np
from datetime import datetime
import queue
import json
import re
import webbrowser
from collections import deque
import tkinter as tk
from tkinter import scrolledtext
import sys

# Advanced Configuration
THEME_COLOR = "#00f2ff"
ACCENT_COLOR = "#ff0055"
SECONDARY_COLOR = "#00ff88"
BG_COLOR = "#0a0a12"
DARK_BG = "#050510"
TEXT_COLOR = "#e0e0ff"
INPUT_COLOR = "#222233"

class VoiceEngine:
    """Enhanced Voice Engine with gTTS and sounddevice"""
    def __init__(self):
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        self.start_speech_worker()
        self.temp_audio_file = None

    def start_speech_worker(self):
        """Background thread for speech synthesis"""
        def worker():
            while True:
                try:
                    text = self.speech_queue.get(timeout=0.1)
                    if text:
                        self._speak(text)
                    self.speech_queue.task_done()
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Speech worker error: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def _speak(self, text):
        """Synchronous speech synthesis using gTTS and sounddevice"""
        self.is_speaking = True
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                self.temp_audio_file = fp.name
                tts.save(self.temp_audio_file)

            # Load the audio file and play it
            data, fs = sf.read(self.temp_audio_file, dtype='float32')
            sd.play(data, fs)
            sd.wait()  # Wait for the sound to finish playing

        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            if self.temp_audio_file:
                try:
                    os.remove(self.temp_audio_file)
                    self.temp_audio_file = None
                except OSError as e:
                    print(f"Error removing temporary file: {e}")
            self.is_speaking = False

    def speak(self, text):
        """Queue text for speech (non-blocking)"""
        if text and not self.is_speaking:
            self.speech_queue.put(text)

    def stop(self):
        """Stop all speech"""
        sd.stop()

class CommandProcessor:
    """Handles all command processing with queue system"""
    def __init__(self, ui_ref):
        self.ui = ui_ref
        self.command_queue = queue.Queue()
        self.processing = False
        self.current_command = None
        self.model = "qwen2.5:7b"
        
        # Command patterns
        self.command_patterns = {
            "greeting": r"(hi|hello|hey).*jarvis",
            "time": r"(what.*time|current.*time|time.*now)",
            "date": r"(what.*date|today.*date|current.*date)",
            "open_app": r"open.*(chrome|notepad|calculator|file explorer)",
            "youtube": r"play.*(youtube|song).*",
            "search": r"search.*google.*",
            "write": r"write.*notepad.*",
            "system": r"(cpu|ram|memory|system).*usage",
            "shutdown": r"(shutdown|turn off).*computer",
            "weather": r"weather.*in.*"
        }
        
        # Start command processor thread
        threading.Thread(target=self.process_queue, daemon=True).start()
    
    def add_command(self, command_text, source="voice"):
        """Add command to processing queue"""
        self.command_queue.put((command_text, source))
        self.ui.update_status("📥 COMMAND QUEUED", SECONDARY_COLOR)
    
    def process_queue(self):
        """Process commands from queue one at a time"""
        while True:
            try:
                command_text, source = self.command_queue.get(timeout=0.1)
                self.current_command = command_text
                self.processing = True
                
                # Update UI
                self.ui.update_status("⚡ PROCESSING", ACCENT_COLOR)
                self.ui.update_reactor_state("BUSY")
                self.ui.log_event(f"Processing command from {source}: {command_text}")
                
                # Process command
                response = self._process_command(command_text)
                
                # Update UI with response
                self.ui.update_response(response)
                self.ui.log_event(f"Response: {response[:50]}...")
                
                # Speak response
                self.ui.voice.speak(response)
                
                # Wait for speech to complete
                while self.ui.voice.is_speaking:
                    time.sleep(0.1)
                
                # Reset state
                self.current_command = None
                self.processing = False
                
                # Return to standby
                self.ui.update_status("✅ READY", THEME_COLOR)
                self.ui.update_reactor_state("IDLE")
                
                self.command_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Queue processing error: {e}")
                self.processing = False
    
    def _process_command(self, text):
        """Process individual command"""
        text_lower = text.lower()
        
        # System commands (fast response)
        for cmd_type, pattern in self.command_patterns.items():
            if re.search(pattern, text_lower):
                return self._execute_system_command(cmd_type, text_lower)
        
        # AI commands
        return self._execute_ai_command(text)
    
    def _execute_system_command(self, cmd_type, text):
        """Execute system-level commands"""
        if cmd_type == "greeting":
            return "Hello, I'm here. How can I assist you?"
        
        elif cmd_type == "time":
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}"
        
        elif cmd_type == "date":
            current_date = datetime.now().strftime("%B %d, %Y")
            return f"Today is {current_date}"
        
        elif cmd_type == "open_app":
            app_match = re.search(r"open.*(chrome|notepad|calculator|file explorer)", text)
            if app_match:
                app = app_match.group(1)
                self._open_application(app)
                return f"Opening {app}"
        
        elif cmd_type == "youtube":
            query = re.sub(r"play.*(youtube|song)\s*", "", text).strip()
            if query:
                threading.Thread(target=self._play_youtube, args=(query,), daemon=True).start()
                return f"Playing {query} on YouTube"
        
        elif cmd_type == "write":
            content_match = re.search(r"write.*notepad.*", text)
            if content_match:
                content = text.replace("write", "").replace("notepad", "").strip()
                threading.Thread(target=self._write_notepad, args=(content,), daemon=True).start()
                return f"Writing to Notepad: {content[:30]}..."
        
        elif cmd_type == "system":
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            return f"System Status - CPU: {cpu}%, RAM: {ram}%"
        
        elif cmd_type == "shutdown":
            return "Shutdown protocol requires confirmation."
        
        elif cmd_type == "weather":
            location = text.replace("weather in", "").replace("weather", "").strip()
            return f"Checking weather for {location}..."
        
        return None
    
    def _execute_ai_command(self, text):
        """Execute command using Ollama AI"""
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are JARVIS. Be concise and helpful."},
                    {"role": "user", "content": text}
                ]
            )
            return response['message']['content']
        except Exception as e:
            print(f"AI error: {e}")
            return "I'm having trouble accessing my neural network."
    
    def _open_application(self, app_name):
        """Open system applications"""
        apps = {
            "chrome": ["start", "chrome"],
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "file explorer": ["explorer.exe"]
        }
        
        if app_name in apps:
            subprocess.Popen(apps[app_name])
    
    def _play_youtube(self, query):
        """Play video on YouTube"""
        try:
            pywhatkit.playonyt(query)
        except:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)
    
    def _write_notepad(self, text):
        """Write text to Notepad"""
        subprocess.Popen("notepad.exe")
        time.sleep(0.8)
        pyautogui.write(text, interval=0.02)

class VoiceListener:
    """Handles voice input with proper state management"""
    def __init__(self, processor_ref):
        self.processor = processor_ref
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.listening = False
        
        # Configure recognizer
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.5
        
        # Calibrate for noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
    
    def start_listening(self):
        """Start continuous voice listening"""
        self.listening = True
        threading.Thread(target=self._listen_loop, daemon=True).start()
    
    def stop_listening(self):
        """Stop voice listening"""
        self.listening = False
    
    def _listen_loop(self):
        """Main listening loop"""
        while self.listening:
            # Skip if currently processing or speaking
            if (self.processor.processing or 
                self.processor.ui.voice.is_speaking):
                time.sleep(0.1)
                continue
            
            try:
                with self.microphone as source:
                    # Quick ambient adjustment
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.1)
                    
                    # Update UI to listening state
                    self.processor.ui.update_status("🎤 LISTENING...", SECONDARY_COLOR)
                    self.processor.ui.update_reactor_state("LISTENING")
                    
                    # Listen for audio
                    audio = self.recognizer.listen(
                        source, 
                        timeout=None,
                        phrase_time_limit=5
                    )
                    
                    # Convert to text
                    text = self.recognizer.recognize_google(audio)
                    
                    if text and len(text.strip()) > 1:
                        print(f"🎤 Recognized: {text}")
                        self.processor.ui.log_event(f"Voice input: {text}")
                        
                        # Add to command queue
                        self.processor.add_command(text, "voice")
                        
                        # Brief pause to prevent double-trigger
                        time.sleep(0.5)
                        
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                continue
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
            except Exception as e:
                print(f"Listening error: {e}")
            
            # Small delay between listening attempts
            time.sleep(0.1)

class ReactorDisplay(ctk.CTkCanvas):
    """Visual reactor display with state animation"""
    def __init__(self, master, size=300):
        super().__init__(master, width=size, height=size, bg=BG_COLOR, highlightthickness=0)
        self.size = size
        self.center = size // 2
        self.state = "IDLE"
        self.angle = 0
        self.pulse = 0
        self.pulse_dir = 1
        
        self.animate()
    
    def set_state(self, state):
        """Change reactor state"""
        self.state = state
    
    def animate(self):
        """Animation loop"""
        self.delete("all")
        
        # Color based on state
        if self.state == "IDLE":
            color = THEME_COLOR
            speed = 2
        elif self.state == "LISTENING":
            color = SECONDARY_COLOR
            speed = 4
        elif self.state == "BUSY":
            color = ACCENT_COLOR
            speed = 6
        else:
            color = THEME_COLOR
            speed = 2
        
        # Animation progression
        self.angle = (self.angle + speed) % 360
        self.pulse += 0.5 * self.pulse_dir
        if self.pulse > 5 or self.pulse < -5:
            self.pulse_dir *= -1
        
        # Outer ring
        outer_radius = self.size // 2 - 10
        self.create_oval(
            self.center - outer_radius, self.center - outer_radius,
            self.center + outer_radius, self.center + outer_radius,
            outline=color, width=2
        )
        
        # Spinning segments
        segment_count = 8
        for i in range(segment_count):
            seg_angle = self.angle + (i * 360/segment_count)
            start_angle = seg_angle
            extent = 30
            
            self.create_arc(
                self.center - outer_radius + 15, self.center - outer_radius + 15,
                self.center + outer_radius - 15, self.center + outer_radius - 15,
                start=start_angle, extent=extent,
                outline=color, width=4, style="arc"
            )
        
        # Pulsing core
        core_radius = 40 + self.pulse
        self.create_oval(
            self.center - core_radius, self.center - core_radius,
            self.center + core_radius, self.center + core_radius,
            fill=color, outline=""
        )
        
        # Inner core
        inner_radius = 15
        self.create_oval(
            self.center - inner_radius, self.center - inner_radius,
            self.center + inner_radius, self.center + inner_radius,
            fill="#ffffff", outline=""
        )
        
        self.after(30, self.animate)

class JarvisInterface(ctk.CTk):
    """Main JARVIS interface with dual input support"""
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("J.A.R.V.I.S. - DUAL INPUT EDITION")
        self.geometry("1300x850")
        self.configure(fg_color=BG_COLOR)
        ctk.set_appearance_mode("dark")
        
        # Initialize systems
        self.voice = VoiceEngine()
        self.processor = CommandProcessor(self)
        self.listener = VoiceListener(self.processor)
        
        # State variables
        self.is_running = True
        self.voice_enabled = True
        
        # Setup GUI
        self.setup_interface()
        
        # Start systems
        self.start_systems()
        
        # Initial greeting
        self.after(1000, lambda: self.voice.speak("Systems online. Voice and text input active."))
    
    def setup_interface(self):
        """Setup the user interface"""
        # Configure grid
        self.grid_columnconfigure(0, weight=2)  # Left panel
        self.grid_columnconfigure(1, weight=1)  # Right panel
        self.grid_rowconfigure(0, weight=1)
        
        # --- LEFT PANEL: Main Display ---
        self.left_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.left_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        # Title
        title_label = ctk.CTkLabel(
            self.left_frame,
            text="J.A.R.V.I.S.",
            font=("Arial", 36, "bold"),
            text_color=THEME_COLOR
        )
        title_label.pack(pady=(20, 5))
        
        subtitle_label = ctk.CTkLabel(
            self.left_frame,
            text="Just A Rather Very Intelligent System",
            font=("Consolas", 14),
            text_color=TEXT_COLOR
        )
        subtitle_label.pack(pady=(0, 30))
        
        # Reactor Display
        self.reactor = ReactorDisplay(self.left_frame, size=350)
        self.reactor.pack(pady=20)
        
        # Status Display
        self.status_label = ctk.CTkLabel(
            self.left_frame,
            text="✅ SYSTEMS ONLINE",
            font=("Arial", 20, "bold"),
            text_color=SECONDARY_COLOR
        )
        self.status_label.pack(pady=(20, 10))
        
        # Response Display
        response_frame = ctk.CTkFrame(self.left_frame, fg_color="#111122", corner_radius=10)
        response_frame.pack(fill="both", expand=True, pady=20, padx=20)
        
        response_title = ctk.CTkLabel(
            response_frame,
            text="RESPONSE",
            font=("Arial", 16, "bold"),
            text_color=THEME_COLOR
        )
        response_title.pack(pady=(15, 10))
        
        self.response_text = ctk.CTkTextbox(
            response_frame,
            fg_color="transparent",
            text_color=TEXT_COLOR,
            font=("Consolas", 16),
            height=120,
            wrap="word"
        )
        self.response_text.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.response_text.insert("1.0", "> Awaiting your command...")
        self.response_text.configure(state="disabled")
        
        # --- RIGHT PANEL: Controls & Input ---
        self.right_frame = ctk.CTkFrame(self, fg_color="#111122", corner_radius=15)
        self.right_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        # Voice Controls
        voice_title = ctk.CTkLabel(
            self.right_frame,
            text="VOICE CONTROLS",
            font=("Arial", 18, "bold"),
            text_color=SECONDARY_COLOR
        )
        voice_title.pack(pady=(20, 15))
        
        # Voice toggle button
        self.voice_toggle = ctk.CTkSwitch(
            self.right_frame,
            text="Voice Input",
            font=("Arial", 14),
            command=self.toggle_voice,
            switch_width=50,
            switch_height=25,
            fg_color="#333",
            progress_color=SECONDARY_COLOR
        )
        self.voice_toggle.pack(pady=(0, 10))
        self.voice_toggle.select()  # Voice on by default
        
        # Voice status indicator
        self.voice_status = ctk.CTkLabel(
            self.right_frame,
            text="🎤 Voice: ACTIVE",
            font=("Consolas", 12),
            text_color=SECONDARY_COLOR
        )
        self.voice_status.pack(pady=(0, 30))
        
        # Manual Input Section
        input_title = ctk.CTkLabel(
            self.right_frame,
            text="MANUAL INPUT",
            font=("Arial", 18, "bold"),
            text_color=THEME_COLOR
        )
        input_title.pack(pady=(10, 15))
        
        # Text input area
        self.input_text = ctk.CTkTextbox(
            self.right_frame,
            height=150,
            font=("Consolas", 14),
            fg_color=INPUT_COLOR,
            text_color=TEXT_COLOR,
            wrap="word"
        )
        self.input_text.pack(fill="x", padx=20, pady=(0, 15))
        self.input_text.insert("1.0", "Type your command here...")
        
        # Input buttons frame
        button_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        button_frame.pack(pady=(0, 20))
        
        # Send button
        self.send_button = ctk.CTkButton(
            button_frame,
            text="📤 SEND COMMAND",
            font=("Arial", 14, "bold"),
            height=40,
            width=150,
            fg_color=THEME_COLOR,
            hover_color=ACCENT_COLOR,
            command=self.send_text_command
        )
        self.send_button.grid(row=0, column=0, padx=5)
        
        # Clear button
        self.clear_button = ctk.CTkButton(
            button_frame,
            text="🗑️ CLEAR",
            font=("Arial", 14),
            height=40,
            width=100,
            fg_color="#333333",
            hover_color="#555555",
            command=self.clear_input
        )
        self.clear_button.grid(row=0, column=1, padx=5)
        
        # Quick Commands
        quick_title = ctk.CTkLabel(
            self.right_frame,
            text="QUICK COMMANDS",
            font=("Arial", 16, "bold"),
            text_color=SECONDARY_COLOR
        )
        quick_title.pack(pady=(20, 10))
        
        # Quick command buttons
        quick_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        quick_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        quick_commands = [
            ("⏰ Time", "What time is it?"),
            ("📅 Date", "What's today's date?"),
            ("💻 System", "System status"),
            ("🌐 Browser", "Open Chrome"),
            ("📝 Notepad", "Open Notepad")
        ]
        
        for i, (label, command) in enumerate(quick_commands):
            btn = ctk.CTkButton(
                quick_frame,
                text=label,
                font=("Arial", 12),
                height=35,
                command=lambda cmd=command: self.quick_command(cmd)
            )
            btn.grid(row=i//2, column=i%2, padx=5, pady=5, sticky="ew")
        
        quick_frame.grid_columnconfigure(0, weight=1)
        quick_frame.grid_columnconfigure(1, weight=1)
        
        # Activity Log
        log_title = ctk.CTkLabel(
            self.right_frame,
            text="ACTIVITY LOG",
            font=("Arial", 16, "bold"),
            text_color=THEME_COLOR
        )
        log_title.pack(pady=(10, 10))
        
        # Log display
        self.log_display = ctk.CTkTextbox(
            self.right_frame,
            height=150,
            font=("Consolas", 11),
            fg_color="#0a0a1a",
            text_color="#8888ff"
        )
        self.log_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.log_display.insert("1.0", "=== SYSTEM LOG ===\n")
        self.log_display.configure(state="disabled")
    
    def start_systems(self):
        """Start all background systems"""
        # Start voice listening
        self.listener.start_listening()
        
        # Start system monitoring
        threading.Thread(target=self.monitor_system, daemon=True).start()
        
        # Log startup
        self.log_event("System initialized")
        self.log_event("Voice input: ACTIVE")
        self.log_event("Text input: READY")
    
    def update_status(self, text, color):
        """Update status display"""
        self.status_label.configure(text=text, text_color=color)
    
    def update_reactor_state(self, state):
        """Update reactor animation state"""
        self.reactor.set_state(state)
    
    def update_response(self, text):
        """Update response display"""
        self.response_text.configure(state="normal")
        self.response_text.delete("1.0", "end")
        self.response_text.insert("1.0", f"> {text}")
        self.response_text.see("end")
        self.response_text.configure(state="disabled")
    
    def log_event(self, text):
        """Log event to activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_display.configure(state="normal")
        
        # Insert at beginning to show latest first
        log_entry = f"[{timestamp}] {text}\n"
        self.log_display.insert("1.0", log_entry)
        
        # Limit log size
        lines = self.log_display.get("1.0", "end").split('\n')
        if len(lines) > 100:
            self.log_display.delete("100.0", "end")
        
        self.log_display.configure(state="disabled")
        self.log_display.see("1.0")
    
    def toggle_voice(self):
        """Toggle voice input on/off"""
        if self.voice_toggle.get():
            self.voice_enabled = True
            self.listener.listening = True
            self.voice_status.configure(text="🎤 Voice: ACTIVE", text_color=SECONDARY_COLOR)
            self.log_event("Voice input: ENABLED")
        else:
            self.voice_enabled = False
            self.listener.listening = False
            self.voice_status.configure(text="🎤 Voice: INACTIVE", text_color="#666666")
            self.log_event("Voice input: DISABLED")
    
    def send_text_command(self):
        """Send text command from input box"""
        command = self.input_text.get("1.0", "end-1c").strip()
        
        if command and command != "Type your command here...":
            # Clear input
            self.input_text.delete("1.0", "end")
            
            # Log command
            self.log_event(f"Text command: {command}")
            
            # Add to processing queue
            self.processor.add_command(command, "text")
            
            # Visual feedback
            self.update_status("📝 PROCESSING TEXT...", THEME_COLOR)
            
            # Reset input placeholder
            self.after(1000, lambda: self.input_text.insert("1.0", "Type your command here..."))
    
    def clear_input(self):
        """Clear the input text box"""
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", "Type your command here...")
    
    def quick_command(self, command):
        """Execute a quick command"""
        self.input_text.delete("1.0", "end")
        self.input_text.insert("1.0", command)
        self.send_text_command()
    
    def monitor_system(self):
        """Monitor system resources"""
        while self.is_running:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                
                # Update status with system info periodically
                if random.random() < 0.1:  # 10% chance to update
                    status_msg = f"✅ READY | CPU: {cpu}% | RAM: {ram}%"
                    self.status_label.configure(text=status_msg)
                    
            except Exception as e:
                print(f"Monitor error: {e}")
            
            time.sleep(5)
    
    def on_closing(self):
        """Clean shutdown"""
        self.is_running = False
        self.listener.stop_listening()
        self.voice.stop()
        self.destroy()

# For random system updates
import random

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║        J.A.R.V.I.S. MARK 110 - DUAL INPUT EDITION        ║
    ║             Voice + Text Input System - Online           ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    app = JarvisInterface()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()