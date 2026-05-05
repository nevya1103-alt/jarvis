import os
import pygame
import speech_recognition as sr
from gtts import gTTS
import time
try:
    import pyaudio
except ImportError:
    pyaudio = None
try:
    import sounddevice as sd
except ImportError:
    sd = None

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
    }
}

current_language = 'en'
is_sleeping = False

def get_microphone_devices():
    """Return usable input devices from PyAudio when available, otherwise sounddevice."""
    if pyaudio is not None:
        audio = pyaudio.PyAudio()
        try:
            devices = []
            for idx in range(audio.get_device_count()):
                info = audio.get_device_info_by_index(idx)
                devices.append((idx, info.get("name", f"Device {idx}"), int(info.get("maxInputChannels", 0))))
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
    blocked = ["output", "speaker", "speakers", "headphone", "pc speaker", "sound mapper", "stereo mix"]
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

def get_text(key):
    """Get localized text for given key."""
    return LANGUAGE_PACK.get(current_language, LANGUAGE_PACK['en']).get(key, "")

def speak(text, lang=None):
    """Converts text to speech using Google TTS and plays it."""
    global current_language
    language_code = lang if lang else current_language
    
    try:
        tts = gTTS(text=text, lang=language_code)
        filename = "response.mp3"
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
    recognizer = sr.Recognizer()

    def listen_with_sounddevice(device_idx, device_name):
        if sd is None:
            raise RuntimeError("sounddevice is not installed")
        errors = []
        for candidate_idx, info in get_sounddevice_input_candidates(device_idx, device_name):
            candidate_name = info["name"]
            try:
                samplerate, channels = get_supported_sounddevice_settings(candidate_idx)
                print(f"[INFO] Using sounddevice microphone {candidate_idx}: {candidate_name}")
                print(f"[LISTENING] Recording for 7 seconds at {samplerate} Hz")
                frames = sd.rec(
                    int(7 * samplerate),
                    samplerate=samplerate,
                    channels=channels,
                    dtype="int16",
                    device=candidate_idx,
                )
                sd.wait()
                peak = int(abs(frames).max())
                rms = float((frames.astype("float64") ** 2).mean() ** 0.5)
                if peak <= 3 and rms < 1:
                    message = f"{candidate_idx} ({candidate_name}): very low input (peak {peak}, rms {rms:.1f})"
                    errors.append(message)
                    print(f"[WARN] Skipping silent input: {message}")
                    try:
                        sd.stop()
                    except Exception:
                        pass
                    time.sleep(0.2)
                    continue

                if 0 < peak < 18000:
                    scale = min(18000 / peak, 50)
                    frames = (frames.astype("float64") * scale).clip(-32768, 32767).astype("int16")

                audio = sr.AudioData(frames.tobytes(), samplerate, 2)
                print("[INFO] Processing audio...")
                return recognizer.recognize_google(audio)
            except (sr.UnknownValueError, sr.RequestError):
                raise
            except Exception as e:
                message = f"{candidate_idx} ({candidate_name}): {e}"
                errors.append(message)
                print(f"[WARN] Sounddevice input failed: {message}")
                try:
                    sd.stop()
                except Exception:
                    pass
                time.sleep(0.2)

        if errors:
            raise RuntimeError("Tried sounddevice inputs:\n" + "\n".join(errors[-6:]))
        raise RuntimeError("No sounddevice input microphones are available")

    try:
        print("\n🎤 [INFO] Scanning for available microphones...")
        
        # Find available input microphones
        devices = get_microphone_devices()
        print(f"🎤 [INFO] Found {len(devices)} audio devices")
        
        # Look for input devices
        input_devices = []
        for idx, name, input_channels in devices:
            if input_channels <= 0:
                continue
            name_lower = name.lower()
            if "microphone" in name_lower or "mic" in name_lower:
                # Exclude output devices
                if is_real_microphone_name(name):
                    input_devices.append((idx, name))
                    print(f"🎤 [INFO] Input Device {idx}: {name}")
        
        if not input_devices:
            print("❌ [ERROR] No microphone devices found!")
            print("💡 [TIP] Falling back to text input...")
            return "TEXT_FALLBACK"
        
        # Use the first microphone found
        device_idx, device_name = input_devices[0]
        print(f"🎤 [INFO] Using: {device_name}")
        print("🎤 [INFO] Microphone ready. Adjusting for ambient noise...")
        
        try:
            if pyaudio is None:
                return listen_with_sounddevice(device_idx, device_name)

            with sr.Microphone(device_index=device_idx) as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                print("🎤 [LISTENING] Speak now... (7 seconds timeout)")
                print("🎤 [TIP] Speak clearly and wait for processing...\n")
                audio = recognizer.listen(source, timeout=7, phrase_time_limit=10)
                print("🎤 [INFO] Processing audio...")
                text = recognizer.recognize_google(audio)
                return text
        except OSError as os_err:
            print(f"❌ [ERROR] Microphone hardware issue: {os_err}")
            print("💡 [TIP] Falling back to text input...")
            return "TEXT_FALLBACK"
            
    except sr.WaitTimeoutError:
        print("❌ [ERROR] No speech detected within timeout. Please try again.")
        return ""
    except sr.UnknownValueError:
        print("❌ [ERROR] Could not understand audio. Please speak clearly.")
        return ""
    except sr.RequestError as e:
        print(f"❌ [ERROR] Google API error: {e}")
        print("💡 [TIP] Check your internet connection.")
        return ""
    except Exception as e:
        print(f"❌ [ERROR] Unexpected error: {e}")
        print("💡 [TIP] Falling back to text input...")
        return "TEXT_FALLBACK"

# ============================================================================
# PHASE 5: COMMAND HANDLING
# ============================================================================
def handle_command(user_input):
    """Handle specific commands from user input."""
    global is_sleeping, current_language
    user_input_lower = user_input.lower()
    
    # Sleep command
    if "sleep" in user_input_lower:
        is_sleeping = True
        return get_text('sleeping'), True
    
    # Wake command
    if "wake" in user_input_lower or "wake up" in user_input_lower:
        is_sleeping = False
        return get_text('waking'), False
    
    # Dance command
    if "dance" in user_input_lower:
        return get_text('dancing'), False
    
    # Language commands
    if "hindi" in user_input_lower:
        current_language = 'hi'
        return "Language changed to Hindi.", False
    if "gujarati" in user_input_lower:
        current_language = 'gu'
        return "Language changed to Gujarati.", False
    if "english" in user_input_lower:
        current_language = 'en'
        return "Language changed to English.", False
    
    # Standard responses
    if "hello" in user_input_lower or "hi" in user_input_lower:
        return get_text('hello'), False
    elif "how are you" in user_input_lower:
        return get_text('how_are_you'), False
    elif "your name" in user_input_lower:
        return get_text('name'), False
    elif "bye" in user_input_lower or "exit" in user_input_lower or "quit" in user_input_lower:
        return get_text('goodbye'), True
    else:
        return get_text('unknown'), False

def show_help():
    """Display help menu."""
    print("\n" + "="*60)
    print("📚 JARVIS ASSISTANT - HELP MENU")
    print("="*60)
    print("\n✨ COMMANDS:")
    print("  • 'hello' / 'hi' - Greet Jarvis")
    print("  • 'how are you' - Ask how Jarvis is doing")
    print("  • 'your name' - Ask Jarvis's name")
    print("  • 'dance' - Jarvis will dance")
    print("  • 'sleep' - Put Jarvis to sleep")
    print("  • 'wake up' - Wake Jarvis")
    print("  • 'english' - Switch to English")
    print("  • 'hindi' - Switch to Hindi (हिंदी)")
    print("  • 'gujarati' - Switch to Gujarati (ગુજરાતી)")
    print("  • 'help' - Show this menu")
    print("  • 'bye' / 'exit' / 'quit' - End conversation")
    print("\n💡 MODES:")
    print("  • Type text input manually")
    print("  • Say 'voice' to use voice input")
    print("="*60 + "\n")

def main():
    print("\n" + "="*60)
    print("🤖 JARVIS ASSISTANT - TERMINAL VERSION")
    print("="*60)
    print("\n✨ FEATURES:")
    print("  ✓ Phase 1: Basic Chatbot")
    print("  ✓ Phase 2: Text-to-Speech")
    print("  ✓ Phase 3: Speech Recognition")
    print("  ✓ Phase 4: Multi-language Support (EN/HI/GU)")
    print("  ✓ Phase 5: Command Handling")
    print("\n💬 Type 'help' for commands or 'voice' for voice input")
    print("="*60 + "\n")
    
    while True:
        try:
            current_lang_name = {'en': 'English', 'hi': 'Hindi', 'gu': 'Gujarati'}.get(current_language, 'Unknown')
            print(f"\n[{current_lang_name}] You: ", end="", flush=True)
            user_input = input().strip()
            
            # Skip empty inputs
            if not user_input:
                print("⚠️  [NOTICE] Please type something or say 'help'")
                continue
            
            # Handle help command
            if user_input.lower() == 'help':
                show_help()
                continue
            
            # Handle voice input request
            if user_input.lower() == 'voice':
                print("\n🎤 [VOICE INPUT MODE]")
                user_input = listen()
                if user_input == "TEXT_FALLBACK":
                    print("📝 Type your message instead: ", end="", flush=True)
                    user_input = input().strip()
                if not user_input or user_input == "TEXT_FALLBACK":
                    print("⚠️  [NOTICE] Voice input failed. Please try again or type manually.")
                    continue
                if user_input != "TEXT_FALLBACK":
                    print(f"🎤 You (Voice): {user_input}")
            
            # Get response
            response, should_exit = handle_command(user_input)
            print(f"\n✨ Jarvis: {response}")
            
            # Play audio response
            speak(response)
            
            # Exit if needed
            if should_exit:
                print("\n👋 Thank you for using Jarvis Assistant!")
                break
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Jarvis is shutting down...")
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ [ERROR] {e}")
            print("⚠️  [NOTICE] An error occurred. Please try again.")

if __name__ == "__main__":
    main()
