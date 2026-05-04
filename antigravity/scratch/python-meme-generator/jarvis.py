import os
import pygame
import speech_recognition as sr
from gtts import gTTS
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from datetime import datetime

# Initialize pygame mixer for playing audio
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Warning: Audio mixer failed to initialize. {e}")

# ============================================================================
# PHASE 4: MULTI-LANGUAGE SUPPORT
# ============================================================================
LANGUAGE_PACK = {
    'en': {
        'hello': "Hello! I am Jarvis. How can I help you today?",
        'how_are_you': "I am just a computer program, but I'm doing great! How about you?",
        'name': "My name is Jarvis, your virtual assistant.",
        'goodbye': "Goodbye! Have a great day!",
        'unknown': "I'm sorry, I don't understand that yet. I am still learning.",
        'sleeping': "Going to sleep now. Good night!",
        'waking': "I'm awake now!",
        'dancing': "Let's dance! I'm performing my dance moves!",
        'title': "Jarvis Assistant"
    },
    'hi': {  # Hindi
        'hello': "नमस्ते! मैं जार्विस हूँ। मैं आपकी कैसे मदद कर सकता हूँ?",
        'how_are_you': "मैं एक कंप्यूटर प्रोग्राम हूँ, लेकिन मैं बहुत अच्छा हूँ। आप कैसे हैं?",
        'name': "मेरा नाम जार्विस है, आपका वर्चुअल असिस्टेंट।",
        'goodbye': "अलविदा! आपका दिन शुभ हो!",
        'unknown': "मुझे माफ करें, मैं अभी तक यह नहीं समझ सकता। मैं अभी सीख रहा हूँ।",
        'sleeping': "अब सो जाता हूँ। शुभरात्रि!",
        'waking': "मैं अब जाग गया हूँ!",
        'dancing': "चलिए नाचते हैं! मैं अपने नृत्य चाल कर रहा हूँ!",
        'title': "जार्विस असिस्टेंट"
    },
    'gu': {  # Gujarati
        'hello': "નમસ્તે! હું જાર્વિસ છું. હું તમને કેવી રીતે મદદ કરી શકું?",
        'how_are_you': "હું એક કોમ્પ્યુટર પ્રોગ્રામ છું, પણ હું સારો છું! તમે કેમ છો?",
        'name': "મારું નામ જાર્વિસ છે, તમારો વર્ચ્યુઅલ સહાયક.",
        'goodbye': "આલવિદા! તમારો દિવસ શુભ હોય!",
        'unknown': "મને માફ કરો, હું હજી તે સમજી શકું નથી. હું હજી શીખી રહ્યો છું.",
        'sleeping': "હવે સૂઈ જાઉં છું. શુભરાત્રી!",
        'waking': "હું હવે જાગી ગયો છું!",
        'dancing': "ચાલો નાચીએ! હું મારી નૃત્ય ચાલો કરી રહ્યો છું!",
        'title': "જાર્વિસ સહાયક"
    }
}

LANGUAGE_PACK['hi'] = {
    'hello': "नमस्ते! मैं जार्विस हूं। मैं आपकी कैसे मदद कर सकता हूं?",
    'how_are_you': "मैं एक कंप्यूटर प्रोग्राम हूं, लेकिन मैं बहुत अच्छा हूं। आप कैसे हैं?",
    'name': "मेरा नाम जार्विस है, आपका वर्चुअल असिस्टेंट।",
    'goodbye': "अलविदा! आपका दिन शुभ हो!",
    'unknown': "मुझे माफ करें, मैं अभी तक यह नहीं समझ सकता। मैं अभी सीख रहा हूं।",
    'sleeping': "अब सो जाता हूं। शुभरात्रि!",
    'waking': "मैं अब जाग गया हूं!",
    'dancing': "चलिए नाचते हैं! मैं अपनी डांस मूव्स दिखा रहा हूं!",
    'title': "जार्विस असिस्टेंट"
}

LANGUAGE_PACK['gu'] = {
    'hello': "નમસ્તે! હું જાર્વિસ છું. હું તમને કેવી રીતે મદદ કરી શકું?",
    'how_are_you': "હું એક કમ્પ્યુટર પ્રોગ્રામ છું, પણ હું સારો છું! તમે કેમ છો?",
    'name': "મારું નામ જાર્વિસ છે, તમારો વર્ચ્યુઅલ સહાયક.",
    'goodbye': "આવજો! તમારો દિવસ શુભ હોય!",
    'unknown': "મને માફ કરો, હું હજી તે સમજી શકતો નથી. હું હજી શીખી રહ્યો છું.",
    'sleeping': "હવે સૂઈ જાઉં છું. શુભરાત્રી!",
    'waking': "હું હવે જાગી ગયો છું!",
    'dancing': "ચાલો નાચીએ! હું મારી ડાન્સ મૂવ્સ બતાવી રહ્યો છું!",
    'title': "જાર્વિસ સહાયક"
}

current_language = 'en'
is_sleeping = False
last_microphone_error = ""

def get_text(key):
    """Get localized text for given key."""
    return LANGUAGE_PACK.get(current_language, LANGUAGE_PACK['en']).get(key, "")

def speak(text, lang=None):
    """Converts text to speech using Google TTS and plays it."""
    global current_language
    language_code = lang if lang else current_language
    
    try:
        tts = gTTS(text=text, lang=language_code)
        filename = f"response_{threading.get_ident()}_{int(time.time() * 1000)}.mp3"
        tts.save(filename)
        
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.unload()
        
        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        print(f"(Audio error: {e})")

def listen():
    """Captures voice input from the microphone and returns it as text."""
    global last_microphone_error
    last_microphone_error = ""
    recognizer = sr.Recognizer()

    def listen_from_source(source, device_name):
        print(f"[INFO] Using microphone: {device_name}")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("[INFO] Listening for speech (7 seconds timeout)...")
        print("[TIP] Speak clearly and wait for processing...")
        audio = recognizer.listen(source, timeout=7, phrase_time_limit=10)
        print("[INFO] Processing audio...")
        text = recognizer.recognize_google(audio)
        print(f"[SUCCESS] Recognized: {text}")
        return text

    def listen_from_device(device_index, device_name):
        mic = None
        try:
            mic = sr.Microphone(device_index=device_index)
            source = mic.__enter__()
            return listen_from_source(source, device_name)
        finally:
            if mic is not None:
                try:
                    stream = getattr(mic, "stream", None)
                    if stream is not None:
                        stream.close()
                    mic.stream = None

                    audio = getattr(mic, "audio", None)
                    if audio is not None:
                        audio.terminate()
                    mic.audio = None
                except Exception as cleanup_error:
                    print(f"[WARN] Microphone cleanup skipped: {cleanup_error}")

    try:
        print("[INFO] Trying Windows default microphone...")
        return listen_from_device(None, "Windows default input")
    except sr.WaitTimeoutError:
        print("[ERROR] No speech detected within timeout period")
        return "TIMEOUT"
    except sr.UnknownValueError:
        print("[ERROR] Could not understand the audio")
        return "UNKNOWN"
    except sr.RequestError as e:
        print(f"[ERROR] Google API request failed: {e}")
        return "API_ERROR"
    except Exception as e:
        print(f"[WARN] Default microphone failed: {e}")
        last_microphone_error = f"Default input failed: {e}"

    try:
        print("[INFO] Scanning for available microphones...")
        mic_names = sr.Microphone.list_microphone_names()
        print(f"[INFO] Found {len(mic_names)} audio devices")

        if not mic_names:
            last_microphone_error = "No audio input devices were returned by PyAudio."
            print("[ERROR] No audio devices found!")
            return "MIC_ERROR"

        for idx, name in enumerate(mic_names):
            print(f"[INFO] Audio Device {idx}: {name}")

        exclude_keywords = ["output", "speaker", "headphone", "sound mapper - output"]
        priority_keywords = ["microphone", "mic", "array", "input", "realtek", "headset", "webcam", "camera"]

        priority_devices = []
        fallback_devices = []
        for idx, name in enumerate(mic_names):
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in exclude_keywords):
                continue
            if any(keyword in name_lower for keyword in priority_keywords):
                priority_devices.append((idx, name))
            else:
                fallback_devices.append((idx, name))

        devices_to_try = priority_devices + fallback_devices
        if not devices_to_try:
            devices_to_try = list(enumerate(mic_names))

        errors = []
        for device_idx, device_name in devices_to_try:
            try:
                return listen_from_device(device_idx, device_name)
            except sr.WaitTimeoutError:
                print("[ERROR] No speech detected within timeout period")
                return "TIMEOUT"
            except sr.UnknownValueError:
                print("[ERROR] Could not understand the audio")
                return "UNKNOWN"
            except sr.RequestError as e:
                print(f"[ERROR] Google API request failed: {e}")
                return "API_ERROR"
            except Exception as e:
                message = f"{device_idx} ({device_name}): {e}"
                errors.append(message)
                print(f"[WARN] Skipping audio device {message}")

        last_microphone_error = "Tried devices:\n" + "\n".join(errors[-6:])
        return "MIC_ERROR"
    except Exception as e:
        last_microphone_error = str(e)
        print(f"[ERROR] Microphone error: {e}")
        return "MIC_ERROR"

# ============================================================================
# PHASE 5: COMMAND HANDLING
# ============================================================================
def handle_command(user_input):
    """Handle specific commands from user input."""
    global is_sleeping, current_language
    user_input = user_input.lower()
    
    # Sleep command
    if "sleep" in user_input:
        is_sleeping = True
        return get_text('sleeping'), True
    
    # Wake command
    if "wake" in user_input or "wake up" in user_input:
        is_sleeping = False
        return get_text('waking'), False
    
    # Dance command
    if "dance" in user_input:
        return get_text('dancing'), False
    
    # Language commands
    if "hindi" in user_input:
        current_language = 'hi'
        return "Language changed to Hindi.", False
    if "gujarati" in user_input:
        current_language = 'gu'
        return "Language changed to Gujarati.", False
    if "english" in user_input:
        current_language = 'en'
        return "Language changed to English.", False
    
    # Standard responses
    if "hello" in user_input or "hi" in user_input:
        return get_text('hello'), False
    elif "how are you" in user_input:
        return get_text('how_are_you'), False
    elif "your name" in user_input:
        return get_text('name'), False
    elif "bye" in user_input or "exit" in user_input or "quit" in user_input:
        return get_text('goodbye'), True
    else:
        return get_text('unknown'), False

# ============================================================================
# PHASE 6: GUI DEVELOPMENT
# ============================================================================
class JarvisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Jarvis Assistant")
        self.root.geometry("860x700")
        self.root.configure(bg='#3b3634')
        
        # Title
        title_label = tk.Label(
            root, 
            text="JARVIS", 
            font=("Helvetica", 24, "bold"),
            bg='#3b3634',
            fg='#f5eee7'
        )
        title_label.pack(pady=10)
        
        # Display area for responses
        self.display = scrolledtext.ScrolledText(
            root,
            height=15,
            width=90,
            bg='#161515',
            fg='#e8f7fb',
            font=("Courier", 10),
            wrap=tk.WORD
        )
        self.display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Animation area
        self.animation_canvas = tk.Canvas(
            root,
            height=220,
            bg='#3b3634',
            highlightthickness=0
        )
        self.animation_canvas.pack(padx=10, pady=5, fill=tk.X)
        
        # Input frame
        input_frame = tk.Frame(root, bg='#3b3634')
        input_frame.pack(padx=10, pady=10, fill=tk.X)
        
        tk.Label(input_frame, text="You: ", bg='#3b3634', fg='#8ee8ff').pack(side=tk.LEFT)
        
        self.input_field = tk.Entry(
            input_frame,
            bg='#161515',
            fg='#e8f7fb',
            insertbackground='#8ee8ff',
            font=("Courier", 10)
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_field.bind('<Return>', self.on_send)
        
        # Buttons
        button_frame = tk.Frame(root, bg='#3b3634')
        button_frame.pack(padx=10, pady=5, fill=tk.X)
        
        send_btn = tk.Button(
            button_frame,
            text="Send",
            command=self.on_send,
            bg='#8ee8ff',
            fg='#101112',
            font=("Helvetica", 10, "bold")
        )
        send_btn.pack(side=tk.LEFT, padx=5)
        
        voice_btn = tk.Button(
            button_frame,
            text="Voice Input",
            command=self.on_voice_input,
            bg='#ffc46b',
            fg='#101112',
            font=("Helvetica", 10, "bold")
        )
        voice_btn.pack(side=tk.LEFT, padx=5)
        
        language_btn = tk.Button(
            button_frame,
            text="Change Language",
            command=self.show_language_menu,
            bg='#f5eee7',
            fg='#101112',
            font=("Helvetica", 10, "bold")
        )
        language_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="Clear",
            command=self.on_clear,
            bg='#6f4a2c',
            fg='#f5eee7',
            font=("Helvetica", 10, "bold")
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.animation_frame = 0
        self.add_to_display("[SYSTEM] Jarvis Assistant initialized. All phases active!")
        self.show_idle_face()
    
    def add_to_display(self, message):
        """Add message to display area."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.display.insert(tk.END, f"[{timestamp}] {message}\n")
        self.display.see(tk.END)
        self.root.update()
    
    def on_send(self, event=None):
        """Handle send button click."""
        user_input = self.input_field.get().strip()
        if not user_input:
            return
        
        self.input_field.delete(0, tk.END)
        self.add_to_display(f"You: {user_input}")
        
        # Process command
        response, should_exit = handle_command(user_input)
        self.add_to_display(f"Jarvis: {response}")
        
        # Play audio
        threading.Thread(target=lambda: speak(response), daemon=True).start()
        
        # Play animation
        if "dance" in user_input.lower():
            self.play_animation("dance")
        elif "sleep" in user_input.lower():
            self.play_animation("sleep")
        elif "wake" in user_input.lower():
            self.play_animation("wake")
        else:
            self.play_animation("talk")
        
        if should_exit:
            self.root.quit()
    
    def on_voice_input(self):
        """Handle voice input."""
        self.add_to_display("[LISTENING] Speak now... (7 seconds timeout)")
        self.add_to_display("[INFO] Make sure your microphone is connected and working!")
        threading.Thread(target=self._process_voice, daemon=True).start()
    
    def _process_voice(self):
        """Process voice input in background thread."""
        try:
            user_input = listen()
            
            # Handle error codes
            if user_input == "TIMEOUT":
                self.add_to_display("[ERROR] No speech detected. Please try again and speak clearly.")
                return
            elif user_input == "UNKNOWN":
                self.add_to_display("[ERROR] Could not understand audio. Please speak clearly and try again.")
                return
            elif user_input == "API_ERROR":
                self.add_to_display("[ERROR] Google API error. Check your internet connection.")
                return
            elif user_input == "MIC_ERROR":
                self.add_to_display("[ERROR] Microphone not found or not working. Check your audio device.")
                if last_microphone_error:
                    self.add_to_display(f"[DETAIL] {last_microphone_error}")
                return
            elif not user_input:
                self.add_to_display("[ERROR] Voice input failed. Try typing instead.")
                return
            
            self.add_to_display(f"You (Voice): {user_input}")
            response, should_exit = handle_command(user_input)
            self.add_to_display(f"Jarvis: {response}")
            speak(response)
            
            if should_exit:
                self.root.after(1000, self.root.quit)
        except Exception as e:
            self.add_to_display(f"[ERROR] Unexpected error: {e}")
    
    def show_language_menu(self):
        """Show language selection menu."""
        window = tk.Toplevel(self.root)
        window.title("Select Language")
        window.geometry("300x150")
        window.configure(bg='#3b3634')
        
        tk.Label(window, text="Choose Language:", bg='#3b3634', fg='#8ee8ff').pack(pady=10)
        
        def set_language(lang):
            global current_language
            current_language = lang
            lang_names = {'en': 'English', 'hi': 'Hindi', 'gu': 'Gujarati'}
            self.add_to_display(f"Language changed to {lang_names[lang]}")
            window.destroy()
        
        tk.Button(window, text="English", command=lambda: set_language('en'),
                 bg='#8ee8ff', fg='#101112').pack(padx=5, pady=5, fill=tk.X)
        tk.Button(window, text="Hindi", command=lambda: set_language('hi'),
                 bg='#ffc46b', fg='#101112').pack(padx=5, pady=5, fill=tk.X)
        tk.Button(window, text="Gujarati", command=lambda: set_language('gu'),
                 bg='#f5eee7', fg='#101112').pack(padx=5, pady=5, fill=tk.X)
    
    # ========================================================================
    # PHASE 7: ANIMATION SYSTEM
    # ========================================================================
    def draw_jarvis_model(self, mouth="smile", eye_scale=1.0, body_x=210, body_y=18, tilt=0, label=""):
        """Draw the robot-cat Jarvis model inspired by the user's reference."""
        c = self.animation_canvas
        x = body_x + tilt
        y = body_y

        white = '#f5eee7'
        shell_shadow = '#d8cec5'
        black = '#101112'
        blue = '#8ee8ff'
        amber = '#ffc46b'
        gold = '#c38a39'

        c.create_oval(x + 40, y + 160, x + 160, y + 184, fill='#2b2928', outline='')
        c.create_oval(x + 44, y + 161, x + 156, y + 177, fill='#46403d', outline='')

        c.create_line(x + 130, y + 105, x + 175, y + 92, x + 175, y + 55,
                      fill=black, width=16, smooth=True, capstyle=tk.ROUND)
        c.create_line(x + 168, y + 58, x + 178, y + 52, fill=gold, width=5, capstyle=tk.ROUND)

        c.create_polygon(x + 22, y + 38, x + 44, y - 10, x + 66, y + 38,
                         fill=white, outline=shell_shadow, width=3)
        c.create_polygon(x + 132, y + 38, x + 154, y - 10, x + 176, y + 38,
                         fill=white, outline=shell_shadow, width=3)
        c.create_polygon(x + 40, y + 30, x + 46, y + 6, x + 57, y + 30,
                         fill=amber, outline='#6f4a2c', width=2)
        c.create_polygon(x + 141, y + 30, x + 152, y + 6, x + 158, y + 30,
                         fill=amber, outline='#6f4a2c', width=2)

        c.create_oval(x + 12, y + 10, x + 188, y + 118, fill=white, outline=shell_shadow, width=4)
        c.create_arc(x + 26, y + 20, x + 122, y + 88, start=90, extent=75, outline='#fffaf3', width=3, style=tk.ARC)
        c.create_oval(x + 30, y + 32, x + 170, y + 105, fill=black, outline='#050505', width=3)
        c.create_arc(x + 42, y + 40, x + 120, y + 82, start=105, extent=55, outline='#303436', width=2, style=tk.ARC)
        c.create_polygon(x + 90, y + 18, x + 110, y + 18, x + 100, y + 30,
                         fill='#ffe2a4', outline=gold, width=1)

        c.create_oval(x + 2, y + 52, x + 28, y + 84, fill='#2a2827', outline=shell_shadow, width=2)
        c.create_oval(x + 172, y + 52, x + 198, y + 84, fill='#2a2827', outline=shell_shadow, width=2)
        c.create_oval(x + 178, y + 58, x + 192, y + 78, outline=amber, width=3)
        c.create_oval(x + 183, y + 65, x + 187, y + 69, fill=amber, outline=amber)

        eye_r = 13 * eye_scale
        c.create_oval(x + 63 - eye_r, y + 65 - eye_r, x + 63 + eye_r, y + 65 + eye_r,
                      outline=blue, width=5)
        c.create_oval(x + 137 - eye_r, y + 65 - eye_r, x + 137 + eye_r, y + 65 + eye_r,
                      outline=blue, width=5)
        if eye_r > 7:
            c.create_oval(x + 63 - eye_r + 5, y + 65 - eye_r + 5, x + 63 + eye_r - 5, y + 65 + eye_r - 5,
                          outline='#dff8ff', width=1)
            c.create_oval(x + 137 - eye_r + 5, y + 65 - eye_r + 5, x + 137 + eye_r - 5, y + 65 + eye_r - 5,
                          outline='#dff8ff', width=1)
        c.create_line(x + 43, y + 72, x + 52, y + 72, fill=blue, width=2)
        c.create_line(x + 148, y + 72, x + 157, y + 72, fill=blue, width=2)

        if mouth == "sleep":
            c.create_line(x + 88, y + 83, x + 96, y + 83, fill=blue, width=3)
            c.create_line(x + 104, y + 83, x + 112, y + 83, fill=blue, width=3)
        elif mouth == "open":
            c.create_oval(x + 94, y + 78, x + 106, y + 91, outline=blue, width=3)
        else:
            c.create_arc(x + 86, y + 74, x + 101, y + 92, start=200, extent=130, outline=blue, width=3, style=tk.ARC)
            c.create_arc(x + 99, y + 74, x + 114, y + 92, start=210, extent=130, outline=blue, width=3, style=tk.ARC)

        c.create_oval(x + 55, y + 108, x + 145, y + 174, fill=white, outline=shell_shadow, width=3)
        c.create_line(x + 65, y + 116, x + 135, y + 116, fill=black, width=8)
        c.create_oval(x + 93, y + 110, x + 107, y + 126, fill=gold, outline='#7a511f', width=2)
        c.create_line(x + 100, y + 118, x + 100, y + 124, fill=black, width=1)

        c.create_line(x + 57, y + 128, x + 33, y + 154, fill=white, width=18, capstyle=tk.ROUND)
        c.create_line(x + 143, y + 128, x + 167, y + 154, fill=white, width=18, capstyle=tk.ROUND)
        c.create_oval(x + 23, y + 146, x + 45, y + 168, fill=black, outline='#2b2b2b')
        c.create_oval(x + 155, y + 146, x + 177, y + 168, fill=black, outline='#2b2b2b')
        c.create_oval(x + 66, y + 160, x + 92, y + 178, fill=black, outline='#2b2b2b')
        c.create_oval(x + 108, y + 160, x + 134, y + 178, fill=black, outline='#2b2b2b')

        c.create_oval(x + 92, y + 139, x + 108, y + 155, fill='#fff1bc', outline=amber, width=1)
        for px, py in [(86, 137), (95, 130), (105, 130), (114, 137)]:
            c.create_oval(x + px, y + py, x + px + 7, y + py + 9, fill='#fff1bc', outline=amber, width=1)

        if label:
            c.create_text(x + 245, y + 82, text=label, fill=blue, font=("Helvetica", 16, "bold"))

    def show_idle_face(self):
        """Show Jarvis immediately when the app opens."""
        self.animation_canvas.delete("all")
        self.draw_jarvis_model(label="Ready")
        self.animation_canvas.update()

    def play_animation(self, animation_type):
        """Play visual animation."""
        self.animation_canvas.delete("all")
        
        if animation_type == "talk":
            self.animate_talking()
        elif animation_type == "dance":
            self.animate_dancing()
        elif animation_type == "sleep":
            self.animate_sleeping()
        elif animation_type == "wake":
            self.animate_waking()
    
    def animate_talking(self):
        """Animate talking with mouth movement."""
        for i in range(3):
            self.animation_canvas.delete("all")
            self.draw_jarvis_model(mouth="open" if i % 2 == 0 else "smile", eye_scale=1.0, label="Listening")
            self.animation_canvas.update()
            time.sleep(0.3)
    
    def animate_dancing(self):
        """Animate dancing."""
        dance_positions = [100, 200, 100, 50, 100]
        for pos in dance_positions:
            self.animation_canvas.delete("all")
            self.draw_jarvis_model(mouth="smile", eye_scale=1.08, body_x=pos, tilt=(pos - 100) // 8, label="Dancing!")
            self.animation_canvas.update()
            time.sleep(0.2)
    
    def animate_sleeping(self):
        """Animate sleeping."""
        self.animation_canvas.delete("all")
        self.draw_jarvis_model(mouth="sleep", eye_scale=0.25, label="Z z z")
        self.animation_canvas.update()
    
    def animate_waking(self):
        """Animate waking up."""
        for i in range(3):
            self.animation_canvas.delete("all")
            self.draw_jarvis_model(mouth="smile", eye_scale=0.45 + (i * 0.28), label="Wake!")
            self.animation_canvas.update()
            time.sleep(0.3)
    
    def on_clear(self):
        """Clear display."""
        self.display.delete(1.0, tk.END)
        self.add_to_display("[CLEARED] Display cleared")

# ============================================================================
# PHASE 8: AUDIO + ANIMATION SYNC
# ============================================================================
def main():
    root = tk.Tk()
    gui = JarvisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
