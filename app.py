"""
J.A.R.V.I.S. MARK 90 - QUANTUM EDITION
Features:
1. Real-time Arc Reactor Visualization (Canvas Animation)
2. Always-Listening Background Thread (Non-blocking)
3. Direct System Control (Notepad, YouTube, Apps)
4. Hardware Monitoring (CPU/RAM/Battery)
5. DeepSeek-R1 Integration via Ollama
6. Advanced Voice Activity Detection
7. 3D-like Interface with Multiple Layers
8. Faster Response System with Pre-processing
"""

import threading
import subprocess
import speech_recognition as sr
import pyttsx3
import customtkinter as ctk
import ollama
import pyautogui
import pywhatkit
import psutil
import time
import math
import numpy as np
from datetime import datetime
import sys
import os
import queue
import json
from PIL import Image, ImageDraw
import webbrowser
import requests
from vosk import Model, KaldiRecognizer
import pyaudio
import wave
import sounddevice as sd
import soundfile as sf
from scipy import signal
import asyncio
import concurrent.futures

# --- ADVANCED CONFIGURATION ---
THEME_COLOR = "#00f2ff"    # Cyan (Arc Reactor Core)
ACCENT_COLOR = "#ff0055"   # Red (Processing/Thinking)
SECONDARY_COLOR = "#ffaa00" # Orange (Warning/Alert)
BG_COLOR = "#0a0a0a"       # Deep Black with slight blue tint
TEXT_COLOR = "#ffffff"
NEON_PURPLE = "#9d00ff"
NEON_GREEN = "#00ff9d"

class AdvancedVoiceEngine:
    """Ultra-Fast Speech Engine with Multiple Voice Profiles"""
    def __init__(self):
        self.engine = pyttsx3.init()
        self.voice_queue = queue.Queue()
        self.is_speaking = False
        self.current_voice = "male"
        self.speech_rate = 280  # Increased for faster speech
        self.configure_engine()
        self.start_speech_worker()

    def configure_engine(self):
        """Advanced Voice Configuration"""
        try:
            voices = self.engine.getProperty('voices')
            self.engine.setProperty('rate', self.speech_rate)
            self.engine.setProperty('volume', 1.0)
            
            # Voice selection based on availability
            preferred_voices = ["david", "zira", "hazel", "mark", "microsoft david"]
            for v in voices:
                voice_name = v.name.lower()
                if any(pref in voice_name for pref in preferred_voices):
                    self.engine.setProperty('voice', v.id)
                    print(f"✓ Voice selected: {v.name}")
                    break
            
            # Additional voice properties for clarity
            self.engine.setProperty('pitch', 110)  # Slightly higher pitch for clarity
        except Exception as e:
            print(f"Voice Config Error: {e}")

    def set_voice_profile(self, profile="jarvis"):
        """Change voice characteristics"""
        profiles = {
            "jarvis": {"rate": 280, "volume": 1.0},
            "assistant": {"rate": 250, "volume": 0.9},
            "alert": {"rate": 320, "volume": 1.0}
        }
        if profile in profiles:
            config = profiles[profile]
            self.engine.setProperty('rate', config["rate"])
            self.engine.setProperty('volume', config["volume"])

    def speak(self, text, priority=1, profile="jarvis"):
        """Threaded speech with priority queue"""
        if not text: 
            return
        
        def _speak():
            self.is_speaking = True
            try:
                self.set_voice_profile(profile)
                self.engine.say(text)
                self.engine.runAndWait()
            except Exception as e:
                print(f"Speech error: {e}")
            finally:
                self.is_speaking = False

        self.voice_queue.put((priority, text, _speak))
        self.process_queue()

    def start_speech_worker(self):
        """Background worker for speech processing"""
        def worker():
            while True:
                try:
                    priority, text, speech_func = self.voice_queue.get(timeout=0.1)
                    if not self.is_speaking:
                        speech_func()
                    time.sleep(0.05)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Speech worker error: {e}")

        threading.Thread(target=worker, daemon=True).start()

    def process_queue(self):
        """Process speech queue based on priority"""
        pass  # Already handled in worker

class QuantumBrain:
    """Advanced Intelligence & Automation Core with VAD"""
    def __init__(self, ui_ref):
        self.ui = ui_ref
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Advanced VAD Configuration
        self.recognizer.energy_threshold = 400
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.pause_threshold = 0.5  # Reduced for faster response
        self.recognizer.phrase_threshold = 0.1
        self.recognizer.non_speaking_duration = 0.3
        
        # Noise calibration
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        
        # Command cache for faster responses
        self.command_cache = {}
        self.last_command = None
        
        # Ollama model configuration
        self.model_name = "deepseek-r1:1.5b"
        self.system_prompt = """You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), 
        Tony Stark's AI assistant. Be concise, witty, and helpful. 
        Maximum 2 sentences. Always sound confident and efficient."""
        
        # Thread pool for parallel processing
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=4)

    def listen_with_vad(self):
        """Advanced listening with Voice Activity Detection"""
        with self.microphone as source:
            try:
                # Dynamic adjustment for noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                
                print("🎤 Listening...")
                self.ui.update_reactor_state("LISTENING")
                
                # Listen with optimized parameters
                audio = self.recognizer.listen(
                    source, 
                    timeout=1.0,
                    phrase_time_limit=4,  # Reduced for faster capture
                    snowboy_configuration=None
                )
                
                # Convert speech to text
                text = self.recognizer.recognize_google(
                    audio, 
                    language="en-US",
                    show_all=False
                ).lower()
                
                print(f"Recognized: {text}")
                return text
                
            except sr.WaitTimeoutError:
                return None
            except sr.UnknownValueError:
                return None
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
                return None
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

    def preprocess_command(self, text):
        """Pre-process command for faster execution"""
        text = text.lower().strip()
        
        # Check cache first
        if text in self.command_cache:
            cache_data = self.command_cache[text]
            if time.time() - cache_data['timestamp'] < 300:  # 5 minute cache
                return cache_data['response']
        
        return None

    def execute_command(self, text):
        """Execute commands with parallel processing"""
        if not text:
            return "I didn't catch that. Please try again."
        
        # Update UI
        self.ui.update_status("⚡ PROCESSING", ACCENT_COLOR)
        self.ui.update_reactor_state("BUSY")
        
        # Check for pre-processed response
        cached = self.preprocess_command(text)
        if cached:
            return cached
        
        # System commands (processed locally - fastest)
        response = self.process_system_command(text)
        if response:
            return response
        
        # AI commands (processed by Ollama)
        return self.process_ai_command(text)

    def process_system_command(self, text):
        """Process system-level commands"""
        text_lower = text.lower()
        
        # 1. NOTEPAD COMMANDS
        if "notepad" in text_lower and ("write" in text_lower or "type" in text_lower):
            if "write" in text_lower:
                content = text.split("write", 1)[1].strip()
            elif "type" in text_lower:
                content = text.split("type", 1)[1].strip()
            else:
                content = text_lower.replace("notepad", "").strip()
            
            # Start notepad and write
            self.thread_pool.submit(self.write_to_notepad, content)
            return f"Writing '{content[:30]}...' in Notepad"
        
        # 2. YOUTUBE PLAYBACK
        elif "play" in text_lower and ("youtube" in text_lower or "song" in text_lower):
            song = text_lower.replace("play", "").replace("on youtube", "").replace("song", "").strip()
            self.thread_pool.submit(self.play_youtube, song)
            return f"Playing {song} on YouTube"
        
        # 3. APPLICATION LAUNCH
        elif any(cmd in text_lower for cmd in ["open chrome", "open browser", "launch browser"]):
            self.thread_pool.submit(self.open_application, "chrome")
            return "Launching Chrome browser"
        
        elif "open calculator" in text_lower:
            self.thread_pool.submit(self.open_application, "calc")
            return "Opening Calculator"
        
        elif "open file explorer" in text_lower:
            self.thread_pool.submit(self.open_application, "explorer")
            return "Opening File Explorer"
        
        # 4. SYSTEM CONTROL
        elif "shutdown" in text_lower and "system" in text_lower:
            return "Security protocol prevents unauthorized shutdown. Use override code."
        
        elif "force shutdown" in text_lower:
            return "Initiating emergency shutdown sequence in 5...4..."
        
        # 5. INFORMATION QUERIES
        elif "time" in text_lower:
            current_time = datetime.now().strftime("%I:%M %p")
            return f"The current time is {current_time}"
        
        elif "date" in text_lower:
            current_date = datetime.now().strftime("%B %d, %Y")
            return f"Today is {current_date}"
        
        elif "cpu" in text_lower or "memory" in text_lower or "ram" in text_lower:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            return f"CPU: {cpu}% | RAM: {ram}%"
        
        return None  # Not a system command

    def process_ai_command(self, text):
        """Process with Ollama AI"""
        try:
            # Use streaming for faster response perception
            stream = ollama.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": text}
                ],
                stream=True,
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 50  # Limit response length
                }
            )
            
            # Stream response for perceived speed
            full_response = ""
            for chunk in stream:
                if 'message' in chunk and 'content' in chunk['message']:
                    content = chunk['message']['content']
                    full_response += content
                    # Update UI in real-time
                    self.ui.update_response(content, incremental=True)
            
            # Cache the response
            self.command_cache[text.lower()] = {
                'response': full_response,
                'timestamp': time.time()
            }
            
            return full_response
            
        except Exception as e:
            print(f"Ollama error: {e}")
            return "Neural network connection unstable. Please try again."

    def write_to_notepad(self, content):
        """Write text to Notepad"""
        subprocess.Popen("notepad.exe")
        time.sleep(0.8)  # Reduced wait time
        pyautogui.write(content, interval=0.02)  # Faster typing

    def play_youtube(self, query):
        """Play on YouTube"""
        try:
            pywhatkit.playonyt(query, open_video=True)
        except:
            url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            webbrowser.open(url)

    def open_application(self, app_name):
        """Open system applications"""
        apps = {
            "chrome": ["start", "chrome"],
            "calc": ["calc.exe"],
            "explorer": ["explorer.exe"],
            "notepad": ["notepad.exe"]
        }
        
        if app_name in apps:
            subprocess.Popen(apps[app_name])

class QuantumReactor(ctk.CTkCanvas):
    """3D-like Arc Reactor with Multiple Animation Layers"""
    def __init__(self, master, size=350):
        super().__init__(master, width=size, height=size, bg=BG_COLOR, highlightthickness=0)
        self.size = size
        self.center = size // 2
        self.state = "IDLE"
        self.angle = 0
        self.pulse_phase = 0
        self.inner_glow = 0
        self.particles = []
        self.init_particles(50)
        
        # Colors for different states
        self.state_colors = {
            "IDLE": {"core": "#0055ff", "ring": "#0088ff", "glow": "#0022aa"},
            "LISTENING": {"core": "#00ff00", "ring": "#00cc00", "glow": "#004400"},
            "BUSY": {"core": "#ff0055", "ring": "#ff4444", "glow": "#880022"},
            "PROCESSING": {"core": "#ffaa00", "ring": "#ff8800", "glow": "#884400"}
        }
        
        self.animate()

    def init_particles(self, count):
        """Initialize particle system for 3D effect"""
        for _ in range(count):
            angle = np.random.uniform(0, 2 * math.pi)
            distance = np.random.uniform(0.3, 0.9)
            speed = np.random.uniform(0.01, 0.05)
            size = np.random.uniform(1, 3)
            self.particles.append({
                'angle': angle,
                'distance': distance,
                'speed': speed,
                'size': size,
                'phase': np.random.uniform(0, 2 * math.pi)
            })

    def set_state(self, state):
        self.state = state

    def draw_3d_circle(self, x, y, radius, color, glow=False):
        """Draw a circle with 3D effect"""
        if glow:
            # Create glow effect with multiple circles
            for i in range(5, 0, -1):
                alpha = int(50 * (i/5))
                glow_radius = radius + i * 3
                self.create_oval(
                    x - glow_radius, y - glow_radius,
                    x + glow_radius, y + glow_radius,
                    outline=color,
                    fill="",
                    width=1,
                    stipple="gray50"
                )
        
        # Main circle
        self.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=color,
            outline="",
            width=0
        )

    def animate(self):
        """Advanced 3D animation loop"""
        self.delete("all")
        state_colors = self.state_colors[self.state]
        
        # Animation progression
        self.angle = (self.angle + 8) % 360
        self.pulse_phase += 0.1
        self.inner_glow = 5 * math.sin(self.pulse_phase)
        
        # 1. Outer Glow (background)
        glow_radius = 140 + math.sin(self.pulse_phase * 2) * 10
        self.draw_3d_circle(self.center, self.center, glow_radius, state_colors["glow"], glow=True)
        
        # 2. Main Reactor Ring
        ring_radius = 120
        segments = 12
        
        for i in range(segments):
            segment_angle = self.angle + (i * 360/segments)
            rad_angle = math.radians(segment_angle)
            
            x1 = self.center + ring_radius * math.cos(rad_angle)
            y1 = self.center + ring_radius * math.sin(rad_angle)
            x2 = self.center + (ring_radius - 20) * math.cos(rad_angle)
            y2 = self.center + (ring_radius - 20) * math.sin(rad_angle)
            
            # Gradient color based on position
            color_intensity = 0.5 + 0.5 * math.sin(rad_angle + self.pulse_phase)
            color = self.mix_colors(state_colors["ring"], "#ffffff", color_intensity)
            
            self.create_line(x1, y1, x2, y2, fill=color, width=3, capstyle="round")
        
        # 3. Spinning Energy Orbs
        orb_count = 8
        orb_radius = 80
        
        for i in range(orb_count):
            orb_angle = self.angle * 2 + (i * 360/orb_count)
            rad_angle = math.radians(orb_angle)
            
            x = self.center + orb_radius * math.cos(rad_angle)
            y = self.center + orb_radius * math.sin(rad_angle)
            
            # Pulsing effect
            pulse = 3 + 2 * math.sin(self.pulse_phase + i)
            
            self.draw_3d_circle(x, y, pulse, state_colors["core"])
        
        # 4. Core Reactor
        core_radius = 40 + self.inner_glow
        self.draw_3d_circle(self.center, self.center, core_radius, state_colors["core"])
        
        # Inner core details
        inner_details = 6
        for i in range(inner_details):
            detail_angle = (self.angle * 3) + (i * 360/inner_details)
            rad_angle = math.radians(detail_angle)
            
            start_x = self.center + 15 * math.cos(rad_angle)
            start_y = self.center + 15 * math.sin(rad_angle)
            end_x = self.center + 25 * math.cos(rad_angle)
            end_y = self.center + 25 * math.sin(rad_angle)
            
            self.create_line(start_x, start_y, end_x, end_y, 
                           fill="#ffffff", width=2, capstyle="round")
        
        # 5. Particle System
        for particle in self.particles:
            particle['angle'] += particle['speed']
            particle['phase'] += 0.02
            
            radius = 100 * particle['distance']
            pulse = 0.5 + 0.5 * math.sin(particle['phase'])
            radius *= (0.9 + 0.1 * pulse)
            
            x = self.center + radius * math.cos(particle['angle'])
            y = self.center + radius * math.sin(particle['angle'])
            
            particle_size = particle['size'] * pulse
            
            self.draw_3d_circle(x, y, particle_size, NEON_PURPLE)
        
        # 6. Data Stream Lines
        if self.state in ["BUSY", "PROCESSING"]:
            for i in range(8):
                stream_angle = (self.angle * 4) + (i * 45)
                rad_angle = math.radians(stream_angle)
                
                start_radius = 60
                end_radius = 180
                
                x1 = self.center + start_radius * math.cos(rad_angle)
                y1 = self.center + start_radius * math.sin(rad_angle)
                x2 = self.center + end_radius * math.cos(rad_angle)
                y2 = self.center + end_radius * math.sin(rad_angle)
                
                # Animated dash pattern
                dash_offset = int(self.angle) % 20
                
                self.create_line(x1, y1, x2, y2, 
                               fill=NEON_GREEN, 
                               width=1,
                               dash=(10, 5),
                               dashoffset=dash_offset)
        
        self.after(20, self.animate)  # ~50 FPS

    def mix_colors(self, color1, color2, ratio):
        """Mix two hex colors"""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        
        r = int(r1 * (1 - ratio) + r2 * ratio)
        g = int(g1 * (1 - ratio) + g2 * ratio)
        b = int(b1 * (1 - ratio) + b2 * ratio)
        
        return f"#{r:02x}{g:02x}{b:02x}"

class QuantumInterface(ctk.CTk):
    """Advanced 3D-like JARVIS Interface"""
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title("J.A.R.V.I.S. QUANTUM INTERFACE")
        self.geometry("1400x900")
        self.configure(fg_color=BG_COLOR)
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Make window semi-transparent for modern look
        self.attributes('-alpha', 0.98)
        
        # Modules
        self.voice = AdvancedVoiceEngine()
        self.brain = QuantumBrain(self)
        self.is_running = True
        
        # Response buffer for incremental display
        self.response_buffer = ""
        self.last_response_time = 0
        
        # Setup GUI
        self.setup_quantum_gui()
        self.start_quantum_threads()
        
        # Initial greeting
        self.after(500, lambda: self.voice.speak("Quantum systems online. Ready for commands.", profile="jarvis"))

    def setup_quantum_gui(self):
        """Setup advanced 3D-like interface"""
        # Configure grid
        self.grid_columnconfigure(0, weight=2)  # Main display
        self.grid_columnconfigure(1, weight=1)  # Side panels
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # --- MAIN DISPLAY AREA ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.grid(row=0, column=0, rowspan=2, padx=40, pady=40, sticky="nsew")
        
        # Title
        title_font = ("Arial", 36, "bold")
        self.lbl_title = ctk.CTkLabel(
            self.main_frame, 
            text="J.A.R.V.I.S. QUANTUM",
            font=title_font,
            text_color=THEME_COLOR,
            textvariable=None
        )
        self.lbl_title.pack(pady=(20, 10))
        
        # Subtitle
        subtitle_font = ("Consolas", 14)
        self.lbl_subtitle = ctk.CTkLabel(
            self.main_frame,
            text="Just A Rather Very Intelligent System",
            font=subtitle_font,
            text_color=TEXT_COLOR
        )
        self.lbl_subtitle.pack(pady=(0, 30))
        
        # Quantum Reactor
        self.reactor = QuantumReactor(self.main_frame, size=400)
        self.reactor.pack(pady=20)
        
        # Status Display
        status_font = ("Arial", 20, "bold")
        self.lbl_status = ctk.CTkLabel(
            self.main_frame,
            text="SYSTEMS NOMINAL",
            font=status_font,
            text_color=NEON_GREEN
        )
        self.lbl_status.pack(pady=(20, 10))
        
        # Response Display with typing effect
        self.response_frame = ctk.CTkFrame(self.main_frame, fg_color="#111111", corner_radius=10)
        self.response_frame.pack(fill="both", expand=True, pady=20, padx=20)
        
        self.txt_response = ctk.CTkTextbox(
            self.response_frame,
            fg_color="transparent",
            text_color=TEXT_COLOR,
            font=("Consolas", 16),
            wrap="word",
            height=120
        )
        self.txt_response.pack(fill="both", expand=True, padx=15, pady=15)
        self.txt_response.insert("1.0", "> Awaiting vocal input...")
        self.txt_response.configure(state="disabled")
        
        # --- RIGHT SIDEBAR: SYSTEM STATS ---
        self.stats_frame = ctk.CTkFrame(self, fg_color="#111122", corner_radius=15)
        self.stats_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        
        stats_title = ctk.CTkLabel(
            self.stats_frame,
            text="SYSTEM INTEGRITY",
            font=("Arial", 18, "bold"),
            text_color=THEME_COLOR
        )
        stats_title.pack(pady=20)
        
        # Real-time stats
        self.stats_display = ctk.CTkTextbox(
            self.stats_frame,
            fg_color="transparent",
            text_color=TEXT_COLOR,
            font=("Consolas", 12),
            height=200
        )
        self.stats_display.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Progress bars for system metrics
        self.cpu_bar = self.create_metric_bar("CPU LOAD", self.stats_frame)
        self.ram_bar = self.create_metric_bar("MEMORY USAGE", self.stats_frame)
        self.disk_bar = self.create_metric_bar("STORAGE", self.stats_frame)
        self.net_bar = self.create_metric_bar("NETWORK", self.stats_frame)
        
        # --- BOTTOM PANEL: COMMAND LOG ---
        self.log_frame = ctk.CTkFrame(self, fg_color="#111111", corner_radius=15)
        self.log_frame.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        
        log_title = ctk.CTkLabel(
            self.log_frame,
            text="COMMAND LOG",
            font=("Arial", 16, "bold"),
            text_color=SECONDARY_COLOR
        )
        log_title.pack(pady=15)
        
        self.log_display = ctk.CTkTextbox(
            self.log_frame,
            fg_color="transparent",
            text_color="#888888",
            font=("Consolas", 11),
            height=150
        )
        self.log_display.pack(fill="both", expand=True, padx=15, pady=10)
        
        # Voice activity indicator
        self.voice_indicator = ctk.CTkProgressBar(
            self.log_frame,
            progress_color=NEON_GREEN,
            height=4,
            width=200
        )
        self.voice_indicator.pack(pady=10)
        self.voice_indicator.set(0)

    def create_metric_bar(self, label, parent):
        """Create a labeled metric bar"""
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", padx=20, pady=8)
        
        # Label and value
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(fill="x")
        
        ctk.CTkLabel(
            label_frame,
            text=label,
            font=("Consolas", 11, "bold"),
            text_color="#aaaaaa"
        ).pack(side="left")
        
        value_label = ctk.CTkLabel(
            label_frame,
            text="0%",
            font=("Consolas", 11),
            text_color=THEME_COLOR
        )
        value_label.pack(side="right")
        
        # Progress bar
        bar = ctk.CTkProgressBar(
            frame,
            progress_color=THEME_COLOR,
            height=8,
            corner_radius=4
        )
        bar.pack(fill="x", pady=(5, 0))
        bar.set(0)
        
        return {"bar": bar, "label": value_label}

    def update_status(self, text, color):
        """Update main status display"""
        self.lbl_status.configure(text=text, text_color=color)
        
    def update_reactor_state(self, state):
        """Update reactor animation state"""
        self.reactor.set_state(state)
        
    def update_response(self, text, incremental=False):
        """Update response display with typing effect"""
        self.txt_response.configure(state="normal")
        
        if incremental:
            self.response_buffer += text
            self.txt_response.delete("1.0", "end")
            self.txt_response.insert("1.0", self.response_buffer)
        else:
            self.response_buffer = text
            self.txt_response.delete("1.0", "end")
            self.txt_response.insert("1.0", f"> {text}")
        
        self.txt_response.see("end")
        self.txt_response.configure(state="disabled")
        self.last_response_time = time.time()

    def log_command(self, text, sender="USER"):
        """Log commands to display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Color code based on sender
        colors = {
            "USER": THEME_COLOR,
            "JARVIS": NEON_GREEN,
            "SYSTEM": SECONDARY_COLOR,
            "ERROR": "#ff3333"
        }
        
        color = colors.get(sender, TEXT_COLOR)
        
        # Insert formatted log
        log_text = f"[{timestamp}] [{sender}]: {text}\n"
        self.log_display.insert("1.0", log_text)
        self.log_display.see("1.0")
        
        # Keep log manageable
        lines = self.log_display.get("1.0", "end").split('\n')
        if len(lines) > 50:
            self.log_display.delete("50.0", "end")

    def update_system_stats(self):
        """Update real-time system statistics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            ram_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Network
            net_io = psutil.net_io_counters()
            net_percent = min(100, (net_io.bytes_sent + net_io.bytes_recv) / 1000000)
            
            # Update progress bars
            metrics = [
                (self.cpu_bar, cpu_percent, f"{cpu_percent:.1f}%"),
                (self.ram_bar, ram_percent, f"{ram_percent:.1f}%"),
                (self.disk_bar, disk_percent, f"{disk_percent:.1f}%"),
                (self.net_bar, net_percent, f"{net_percent:.1f} MB")
            ]
            
            for metric, value, text in metrics:
                metric["bar"].set(value / 100)
                metric["label"].configure(text=text)
                
                # Color code based on usage
                if value > 80:
                    metric["bar"].configure(progress_color="#ff3333")
                elif value > 60:
                    metric["bar"].configure(progress_color=SECONDARY_COLOR)
                else:
                    metric["bar"].configure(progress_color=THEME_COLOR)
            
            # Update stats display
            stats_text = f"""SYSTEM SNAPSHOT
Time: {datetime.now().strftime("%H:%M:%S")}
CPU Cores: {psutil.cpu_count()}
CPU Freq: {psutil.cpu_freq().current:.0f} MHz
Memory: {memory.used//(1024**3)}GB / {memory.total//(1024**3)}GB
Disk: {disk.used//(1024**3)}GB / {disk.total//(1024**3)}GB
Network: ↑{net_io.bytes_sent//1024}KB ↓{net_io.bytes_recv//1024}KB
Battery: {psutil.sensors_battery().percent if psutil.sensors_battery() else 'N/A'}%
Temperature: {self.get_cpu_temp() if hasattr(self, 'get_cpu_temp') else 'N/A'}°C"""
            
            self.stats_display.delete("1.0", "end")
            self.stats_display.insert("1.0", stats_text)
            
        except Exception as e:
            print(f"Stats update error: {e}")

    def start_quantum_threads(self):
        """Start all background processing threads"""
        # System monitoring
        threading.Thread(target=self.monitor_system, daemon=True).start()
        
        # Main AI processing loop
        threading.Thread(target=self.quantum_ai_loop, daemon=True).start()
        
        # Voice activity monitoring
        threading.Thread(target=self.monitor_voice_activity, daemon=True).start()

    def monitor_system(self):
        """Continuous system monitoring"""
        while self.is_running:
            self.update_system_stats()
            time.sleep(2)

    def monitor_voice_activity(self):
        """Monitor and visualize voice activity"""
        while self.is_running:
            # Simulate voice activity (in real app, this would read from audio stream)
            activity = np.random.random() * 0.3  # Placeholder
            self.voice_indicator.set(activity)
            time.sleep(0.1)

    def quantum_ai_loop(self):
        """Main AI processing loop with improved VAD"""
        consecutive_silence = 0
        max_silence = 3  # Seconds of silence before reset
        
        while self.is_running:
            try:
                # Don't listen while speaking
                if self.voice.is_speaking:
                    time.sleep(0.1)
                    continue
                
                # Update status to listening
                self.update_status("LISTENING", NEON_GREEN)
                self.update_reactor_state("LISTENING")
                
                # Listen for command
                user_text = self.brain.listen_with_vad()
                
                if user_text:
                    # Reset silence counter
                    consecutive_silence = 0
                    
                    # Log user input
                    self.log_command(user_text, "USER")
                    self.update_response(f"Processing: {user_text}")
                    
                    # Execute command
                    response = self.brain.execute_command(user_text)
                    
                    # Log and speak response
                    self.log_command(response, "JARVIS")
                    self.update_response(response)
                    self.voice.speak(response, profile="jarvis")
                    
                    # Wait for speech to complete
                    while self.voice.is_speaking:
                        time.sleep(0.05)
                        
                else:
                    # Increment silence counter
                    consecutive_silence += 0.5
                    
                    if consecutive_silence >= max_silence:
                        self.update_status("STANDBY", THEME_COLOR)
                        self.update_reactor_state("IDLE")
                
                # Brief pause between loops
                time.sleep(0.1)
                
            except Exception as e:
                print(f"AI loop error: {e}")
                time.sleep(1)

if __name__ == "__main__":
    # Check dependencies
    required = ["speech_recognition", "pyttsx3", "customtkinter", "ollama", 
                "pyautogui", "pywhatkit", "psutil", "numpy", "PIL"]
    
    print("Initializing J.A.R.V.I.S. Quantum Systems...")
    
    app = QuantumInterface()
    app.mainloop()