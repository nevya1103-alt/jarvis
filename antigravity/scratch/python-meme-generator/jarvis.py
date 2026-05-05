
import os
import pygame
try:
    import pyaudio
except ImportError:
    pyaudio = None
try:
    import sounddevice as sd
except ImportError:
    sd = None
import speech_recognition as sr
from gtts import gTTS
import tkinter as tk
from tkinter import scrolledtext
import threading
import time
from datetime import datetime

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None
try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
except ImportError:
    AudioUtilities = None
    IAudioEndpointVolume = None
    CLSCTX_ALL = None

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv()
load_dotenv(os.path.join(PROJECT_DIR, ".env"))

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
last_microphone_level = ""
selected_microphone_index = None
ai_client = None
AI_MODEL = os.getenv("JARVIS_AI_MODEL", "gpt-5.4-mini")
AI_SYSTEM_PROMPT = (
    "You are Jarvis, a warm robot-cat desktop assistant. "
    "Answer clearly, briefly, and helpfully. Keep replies friendly and easy to speak aloud. "
    "When the user asks for code, steps, facts, or ideas, answer directly without saying you are still learning."
)
AI_HISTORY = []
AI_HISTORY_LIMIT = 8
last_microphone_volume_fix = ""

def ensure_default_microphone_volume():
    """Unmute and raise the default Windows microphone endpoint when pycaw is available."""
    global last_microphone_volume_fix
    last_microphone_volume_fix = ""
    if AudioUtilities is None or IAudioEndpointVolume is None:
        return False

    try:
        microphone = AudioUtilities.GetMicrophone()
        endpoint = microphone.Activate(
            IAudioEndpointVolume._iid_,
            CLSCTX_ALL,
            None,
        ).QueryInterface(IAudioEndpointVolume)

        was_muted = bool(endpoint.GetMute())
        old_volume = float(endpoint.GetMasterVolumeLevelScalar())
        changed = False
        if was_muted:
            endpoint.SetMute(0, None)
            changed = True
        if old_volume < 0.8:
            endpoint.SetMasterVolumeLevelScalar(1.0, None)
            changed = True

        new_volume = float(endpoint.GetMasterVolumeLevelScalar())
        is_muted = bool(endpoint.GetMute())
        last_microphone_volume_fix = (
            f"default mic volume {old_volume:.0%}->{new_volume:.0%}, "
            f"mute {was_muted}->{is_muted}"
        )
        return changed
    except Exception as e:
        last_microphone_volume_fix = f"Could not adjust default microphone volume: {e}"
        return False

def get_microphone_devices():
    """Return usable input devices from PyAudio when available, otherwise sounddevice."""
    if pyaudio is not None:
        audio = pyaudio.PyAudio()
        try:
            devices = []
            for idx in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(idx)
                input_channels = int(info.get("maxInputChannels", 0))
                devices.append((idx, info.get("name", f"Device {idx}"), input_channels))
            return devices
        finally:
            audio.terminate()

    if sd is not None:
        return [
            (idx, device["name"], int(device["max_input_channels"]))
            for idx, device in enumerate(sd.query_devices())
        ]

    raise RuntimeError("No microphone backend available. Install sounddevice or PyAudio.")

def is_real_microphone_name(name):
    """Filter out loopback and output-like devices that report input channels."""
    name_lower = name.lower()
    blocked = ["output", "speaker", "headphone", "pc speaker", "sound mapper - output", "stereo mix"]
    return not any(keyword in name_lower for keyword in blocked)

def get_sounddevice_hostapi_name(device_info):
    """Return the host API name for a sounddevice device info dict."""
    if sd is None:
        return ""
    try:
        return sd.query_hostapis(int(device_info["hostapi"]))["name"]
    except Exception:
        return ""

def is_preferred_sounddevice_input(device_info):
    """Prefer normal Windows shared inputs over raw WDM-KS pins."""
    return get_sounddevice_hostapi_name(device_info) != "Windows WDM-KS"

def get_sounddevice_input_candidates(device_index=None, device_name=None):
    """Build an ordered list of sounddevice input devices to try."""
    if sd is None:
        return []

    devices = list(enumerate(sd.query_devices()))
    candidates = []

    def add_if_input(idx, allow_wdmks=False):
        try:
            info = sd.query_devices(idx)
        except Exception:
            return
        if int(info["max_input_channels"]) <= 0:
            return
        if not allow_wdmks and not is_preferred_sounddevice_input(info):
            return
        item = (idx, info)
        if item not in candidates:
            candidates.append(item)

    for hostapi in sd.query_hostapis():
        host_name = hostapi.get("name", "")
        if host_name == "Windows WDM-KS":
            continue
        default_idx = int(hostapi.get("default_input_device", -1))
        if default_idx >= 0:
            add_if_input(default_idx)

    if device_name:
        target = " ".join(device_name.lower().split())
        for idx, info in devices:
            name = " ".join(info["name"].lower().split())
            if target and (target in name or name in target):
                add_if_input(idx)

    if device_index is not None:
        add_if_input(device_index)

    for idx, info in devices:
        if int(info["max_input_channels"]) > 0 and is_real_microphone_name(info["name"]) and is_preferred_sounddevice_input(info):
            add_if_input(idx)

    if device_index is not None:
        add_if_input(device_index, allow_wdmks=True)

    return candidates

def get_supported_sounddevice_settings(device_index):
    """Find recording settings accepted by the current Windows audio driver."""
    info = sd.query_devices(device_index)
    default_rate = int(info.get("default_samplerate") or 0)
    sample_rates = []
    for rate in (default_rate, 48000, 44100, 16000, 8000):
        if rate > 0 and rate not in sample_rates:
            sample_rates.append(rate)

    max_channels = int(info["max_input_channels"])
    channels_to_try = [1]
    if max_channels >= 2:
        channels_to_try.append(2)

    errors = []
    for samplerate in sample_rates:
        for channels in channels_to_try:
            try:
                sd.check_input_settings(
                    device=device_index,
                    channels=channels,
                    samplerate=samplerate,
                    dtype="int16",
                )
                return samplerate, channels
            except Exception as e:
                errors.append(f"{samplerate}Hz/{channels}ch: {e}")

    raise RuntimeError("; ".join(errors[-4:]))

def get_recognition_language():
    """Map Jarvis UI language to Google speech-recognition locale."""
    return {
        "en": "en-IN",
        "hi": "hi-IN",
        "gu": "gu-IN",
    }.get(current_language, "en-IN")

def describe_recorded_level(frames):
    """Return simple signal numbers for the recorded int16 audio."""
    peak = int(abs(frames).max())
    rms = float((frames.astype("float64") ** 2).mean() ** 0.5)
    return peak, rms

def normalize_recorded_audio(frames, peak):
    """Boost quiet non-silent input before speech recognition."""
    if peak <= 0:
        return frames
    target_peak = 18000
    if peak >= target_peak:
        return frames
    scale = min(target_peak / peak, 50)
    boosted = frames.astype("float64") * scale
    return boosted.clip(-32768, 32767).astype("int16")

def get_text(key):
    """Get localized text for given key."""
    return LANGUAGE_PACK.get(current_language, LANGUAGE_PACK['en']).get(key, "")

def get_ai_client():
    """Create the OpenAI client only when an API key is available."""
    global ai_client
    if OpenAI is None:
        return None
    if not os.getenv("OPENAI_API_KEY"):
        return None
    if ai_client is None:
        ai_client = OpenAI()
    return ai_client

def ask_ai(user_input):
    """Ask the AI model for a Jarvis response."""
    global AI_HISTORY
    if OpenAI is None:
        return "AI is connected in the code, but the OpenAI package is not installed yet."

    client = get_ai_client()
    if client is None:
        return "AI is ready, but OPENAI_API_KEY is not set. Add your API key, restart Jarvis, and ask me again."

    try:
        conversation = [{"role": "system", "content": AI_SYSTEM_PROMPT}]
        conversation.extend(AI_HISTORY[-AI_HISTORY_LIMIT:])
        conversation.append({"role": "user", "content": user_input})

        response = client.responses.create(
            model=AI_MODEL,
            input=conversation,
            max_output_tokens=220,
        )
        answer = response.output_text.strip()
        AI_HISTORY.extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": answer},
        ])
        AI_HISTORY = AI_HISTORY[-AI_HISTORY_LIMIT:]
        return answer
    except Exception as e:
        error_text = str(e)
        if "insufficient_quota" in error_text or "exceeded your current quota" in error_text:
            return (
                "AI is connected, but this OpenAI API key has no available quota. "
                "Check billing/quota on the OpenAI platform or use another API key."
            )
        if "Connection error" in error_text:
            return "AI is connected in Jarvis, but the network request failed. Check your internet connection and try again."
        return f"AI error: {e}"

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

def listen(device_index=None, device_name="Windows default input"):
    """Captures voice input from the microphone and returns it as text."""
    global last_microphone_error, last_microphone_level
    last_microphone_error = ""
    last_microphone_level = ""
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300
    recognizer.pause_threshold = 0.8

    def listen_from_source(source, device_name):
        print(f"[INFO] Using microphone: {device_name}")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("[INFO] Listening for speech (12 seconds timeout)...")
        print("[TIP] Speak clearly and wait for processing...")
        audio = recognizer.listen(source, timeout=12, phrase_time_limit=10)
        print("[INFO] Processing audio...")
        text = recognizer.recognize_google(audio, language=get_recognition_language())
        print(f"[SUCCESS] Recognized: {text}")
        return text

    def listen_with_sounddevice(device_index, device_name):
        global last_microphone_error, last_microphone_level
        if sd is None:
            raise RuntimeError("Sounddevice is not installed")
        ensure_default_microphone_volume()
        errors = []
        for candidate_index, info in get_sounddevice_input_candidates(device_index, device_name):
            candidate_name = info["name"]
            try:
                samplerate, channels = get_supported_sounddevice_settings(candidate_index)
                print(f"[INFO] Using sounddevice microphone {candidate_index}: {candidate_name}")
                print(f"[INFO] Recording at {samplerate} Hz, {channels} channel(s)")
                frames = sd.rec(
                    int(12 * samplerate),
                    samplerate=samplerate,
                    channels=channels,
                    dtype='int16',
                    device=candidate_index,
                )
                sd.wait()
                peak, rms = describe_recorded_level(frames)
                last_microphone_level = f"{candidate_name}: peak {peak}, rms {rms:.1f}"
                print(f"[INFO] Mic signal level: {last_microphone_level}")
                if peak <= 3 and rms < 1:
                    message = (
                        f"{candidate_index} ({candidate_name}): very low input "
                        f"(peak {peak}, rms {rms:.1f})"
                    )
                    errors.append(message)
                    print(f"[WARN] Skipping silent input: {message}")
                    try:
                        sd.stop()
                    except Exception:
                        pass
                    time.sleep(0.2)
                    continue

                frames = normalize_recorded_audio(frames, peak)
                raw_data = frames.tobytes()
                audio_data = sr.AudioData(raw_data, samplerate, 2)
                text = recognizer.recognize_google(audio_data, language=get_recognition_language())
                print(f"[SUCCESS] Recognized: {text}")
                return text
            except (sr.UnknownValueError, sr.RequestError):
                raise
            except Exception as e:
                message = f"{candidate_index} ({candidate_name}): {e}"
                errors.append(message)
                print(f"[WARN] Sounddevice input failed: {message}")
                try:
                    sd.stop()
                except Exception:
                    pass
                time.sleep(0.2)

        if errors:
            last_microphone_error = "Tried sounddevice inputs:\n" + "\n".join(errors[-6:])
            if any("very low input" in error for error in errors):
                return "SILENCE"
            raise RuntimeError("Tried sounddevice inputs:\n" + "\n".join(errors[-6:]))
        raise RuntimeError("No sounddevice input microphones are available")

    def listen_from_device(device_index, device_name):
        if pyaudio is None:
            return listen_with_sounddevice(device_index, device_name)

        mic = None
        audio = None
        try:
            mic = sr.Microphone(device_index=device_index)
            if device_index is not None:
                probe = pyaudio.PyAudio()
                try:
                    info = probe.get_device_info_by_index(device_index)
                    if int(info.get("maxInputChannels", 0)) <= 0:
                        raise OSError(f"{device_name} is not an input microphone")
                finally:
                    probe.terminate()

            audio = mic.pyaudio_module.PyAudio()
            stream = audio.open(
                input_device_index=mic.device_index,
                channels=1,
                format=mic.format,
                rate=mic.SAMPLE_RATE,
                frames_per_buffer=mic.CHUNK,
                input=True,
            )
            mic.audio = audio
            mic.stream = sr.Microphone.MicrophoneStream(stream)
            return listen_from_source(mic, device_name)
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
            elif audio is not None:
                audio.terminate()

    if device_index is not None:
        try:
            return listen_from_device(device_index, device_name)
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
            last_microphone_error = f"{device_name}: {e}"
            print(f"[ERROR] Selected microphone failed: {e}")
            return "MIC_ERROR"

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
        devices = get_microphone_devices()
        print(f"[INFO] Found {len(devices)} audio devices")

        if not devices:
            last_microphone_error = "No audio devices were returned by the microphone backend."
            print("[ERROR] No audio devices found!")
            return "MIC_ERROR"

        for idx, name, input_channels in devices:
            print(f"[INFO] Audio Device {idx}: {name} ({input_channels} input channels)")

        priority_keywords = ["microphone", "mic", "array", "input", "realtek", "headset", "webcam", "camera"]

        priority_devices = []
        fallback_devices = []
        for idx, name, input_channels in devices:
            if input_channels <= 0:
                continue
            name_lower = name.lower()
            if not is_real_microphone_name(name):
                continue
            if any(keyword in name_lower for keyword in priority_keywords):
                priority_devices.append((idx, name))
            else:
                fallback_devices.append((idx, name))

        devices_to_try = priority_devices + fallback_devices
        if not devices_to_try:
            devices_to_try = [(idx, name) for idx, name, input_channels in devices if input_channels > 0]

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
def is_simple_greeting(user_input):
    """Detect greetings that should stay as quick local replies."""
    cleaned = user_input.strip().lower().replace(",", "").replace("!", "").replace(".", "")
    return cleaned in {"hello", "hi", "hey", "hello jarvis", "hi jarvis", "hey jarvis"}

def handle_command(user_input):
    """Handle specific commands from user input."""
    global is_sleeping, current_language
    original_input = user_input.strip()
    user_input = original_input.lower()
    
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
    if is_simple_greeting(original_input):
        return get_text('hello'), False
    elif "how are you" in user_input:
        return get_text('how_are_you'), False
    elif "your name" in user_input:
        return get_text('name'), False
    elif "bye" in user_input or "exit" in user_input or "quit" in user_input:
        return get_text('goodbye'), True
    else:
        return ask_ai(original_input), False

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
        
        self.is_listening = False
        self.voice_btn = tk.Button(
            button_frame,
            text="Voice Input",
            command=self.on_voice_input,
            bg='#ffc46b',
            fg='#101112',
            font=("Helvetica", 10, "bold")
        )
        self.voice_btn.pack(side=tk.LEFT, padx=5)

        self.microphone_choices = {"Default microphone": (None, "Windows default input")}
        self.microphone_var = tk.StringVar(value="Default microphone")
        self.microphone_menu = tk.OptionMenu(button_frame, self.microphone_var, "Default microphone")
        self.microphone_menu.configure(
            bg='#161515',
            fg='#e8f7fb',
            activebackground='#2a2827',
            activeforeground='#8ee8ff',
            highlightthickness=0,
            font=("Helvetica", 9)
        )
        self.microphone_menu.pack(side=tk.LEFT, padx=5)

        refresh_mic_btn = tk.Button(
            button_frame,
            text="Refresh Mics",
            command=self.refresh_microphone_list,
            bg='#2a2827',
            fg='#8ee8ff',
            font=("Helvetica", 10, "bold")
        )
        refresh_mic_btn.pack(side=tk.LEFT, padx=5)
        
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
        if ensure_default_microphone_volume() and last_microphone_volume_fix:
            self.add_to_display(f"[FIX] Microphone was muted/low. Adjusted {last_microphone_volume_fix}.")
        self.add_to_display("[INFO] Refreshing microphone list on startup...")
        self.refresh_microphone_list(show_messages=True)
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
        if self.is_listening:
            self.add_to_display("[INFO] Already listening. Wait for the current voice input to finish.")
            return

        self.is_listening = True
        self.voice_btn.configure(state=tk.DISABLED, text="Listening...")
        self.add_to_display("[LISTENING] Speak now... (12 seconds timeout)")
        self.add_to_display("[INFO] Keep speaking while Jarvis checks available microphone inputs.")
        threading.Thread(target=self._process_voice, daemon=True).start()
    
    def _process_voice(self):
        """Process voice input in background thread."""
        try:
            selected_mic = self.microphone_choices.get(self.microphone_var.get(), (None, "Windows default input"))
            user_input = listen(*selected_mic)
            
            # Handle error codes
            if user_input == "TIMEOUT":
                self.add_to_display("[ERROR] No speech detected. Please try again and speak clearly.")
                return
            elif user_input == "UNKNOWN":
                self.add_to_display("[ERROR] Could not understand audio. Please speak clearly and try again.")
                if last_microphone_level:
                    self.add_to_display(f"[DETAIL] Mic signal: {last_microphone_level}")
                self.add_to_display("[TIP] Say a short phrase like 'hello Jarvis' while the button says Listening.")
                return
            elif user_input == "SILENCE":
                self.add_to_display("[ERROR] Jarvis recorded silence or very low microphone volume.")
                if last_microphone_error:
                    self.add_to_display(f"[DETAIL] {last_microphone_error}")
                self.add_to_display("[FIX] Windows is not exposing a working recording endpoint. Enable a Microphone in Sound > Recording, set it as Default, and raise its Levels volume.")
                return
            elif user_input == "API_ERROR":
                self.add_to_display("[ERROR] Google API error. Check your internet connection.")
                return
            elif user_input == "MIC_ERROR":
                self.add_to_display("[ERROR] Microphone not found or not working. Check your audio device.")
                if last_microphone_error:
                    self.add_to_display(f"[DETAIL] {last_microphone_error}")
                    if "-9999" in last_microphone_error or "Unanticipated host error" in last_microphone_error:
                        self.add_to_display("[FIX] Windows is blocking or failing to open the mic stream.")
                        self.add_to_display("[FIX] Enable microphone access for desktop apps, close other mic apps, then try mic 7 or 5.")
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
        finally:
            self.root.after(0, self._finish_voice_input)

    def _finish_voice_input(self):
        """Re-enable voice controls after the recorder finishes."""
        self.is_listening = False
        self.voice_btn.configure(state=tk.NORMAL, text="Voice Input")

    def refresh_microphone_list(self, show_messages=True):
        """Refresh available microphone devices in the dropdown."""
        try:
            devices = get_microphone_devices()
        except Exception as e:
            if show_messages:
                self.add_to_display(f"[ERROR] Could not list microphones: {e}")
            return

        self.microphone_choices = {"Default microphone": (None, "Windows default input")}
        input_count = 0
        for idx, name, input_channels in devices:
            if input_channels <= 0:
                continue

            if not is_real_microphone_name(name):
                continue

            if sd is not None and pyaudio is None:
                try:
                    device_info = sd.query_devices(idx)
                    if not is_preferred_sounddevice_input(device_info):
                        continue
                    hostapi_name = get_sounddevice_hostapi_name(device_info)
                except Exception:
                    hostapi_name = ""
            else:
                hostapi_name = ""

            backend_label = f", {hostapi_name}" if hostapi_name else ""
            label = f"{idx}: {name} ({input_channels} input channel{'s' if input_channels != 1 else ''}{backend_label})"
            self.microphone_choices[label] = (idx, name)
            input_count += 1

        menu = self.microphone_menu["menu"]
        menu.delete(0, "end")
        for label in self.microphone_choices:
            menu.add_command(label=label, command=lambda value=label: self.microphone_var.set(value))

        current = self.microphone_var.get()
        if current not in self.microphone_choices:
            preferred = next(
                (label for label in self.microphone_choices if "Microphone Array" in label),
                next((label for label in self.microphone_choices if "Microphone" in label), "Default microphone")
            )
            self.microphone_var.set(preferred)

        if show_messages:
            backend = "PyAudio" if pyaudio is not None else "sounddevice"
            self.add_to_display(f"[INFO] Found {len(devices)} audio devices via {backend}, {input_count} usable microphone inputs.")
            if input_count > 0:
                self.add_to_display("[INFO] Available microphones:")
                for label in self.microphone_choices:
                    self.add_to_display(f"  {label}")
            self.add_to_display(f"[INFO] Selected mic: {self.microphone_var.get()}")
    
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
