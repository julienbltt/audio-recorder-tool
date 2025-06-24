# audio-recorder-tool
This tool allows you to record a voice message and stop after a certain period of silence.

## Installation

### Prerequisites
- Python 3.11 (recommended version)
- Required modules: `numpy`, `pyaudio`

### Virtual environment (recommended)

**Windows:**
```bash
python -m venv audio_recorder_env
audio_recorder_env\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv audio_recorder_env
source audio_recorder_env/bin/activate
```

### Installing dependencies
```bash
pip install numpy pyaudio
```

## Simple usage of the recorder.py module

### Basic example

```python
from recorder import AudioRecorder
import time

# Create the recorder
recorder = AudioRecorder()

# List available microphones
mics = recorder.mic_selector.get_microphones()
for i, (index, name) in enumerate(mics):
    print(f"{i}: {name}")

# Select the first microphone (optional)
if mics:
    recorder.set_microphone(mics[0][0])

# Start recording
print("Starting recording...")
recorder.start_recording()

# Wait for recording to finish automatically
while recorder.is_recording:
    time.sleep(0.1)

print("Recording finished!")

# Save the file
recorder.save_recording("my_recording.wav")

# Clean up resources
recorder.cleanup()
```

### Example with custom callbacks

```python
from recorder import AudioRecorder

def on_start():
    print("🎤 Recording started!")

def on_stop():
    print("⏹️ Recording stopped!")

def on_volume(volume):
    print(f"🔊 Volume: {volume:.0f}")

# Create recorder with callbacks
recorder = AudioRecorder()
recorder.on_recording_start = on_start
recorder.on_recording_stop = on_stop
recorder.on_volume_update = on_volume

# Custom silence detector configuration
recorder.set_silence_settings(
    threshold=800,    # Silence threshold (lower = more sensitive)
    duration=3.0      # Silence duration before stopping (in seconds)
)

# Start recording
recorder.start_recording()

# Rest of the code...
```

### Example with error handling

```python
from recorder import AudioRecorder
import time

def record_message(filename="recording.wav"):
    """Complete recording function with error handling"""
    recorder = None
    try:
        # Initialization
        recorder = AudioRecorder()
        
        # Check available microphones
        mics = recorder.mic_selector.get_microphones()
        if not mics:
            print("❌ No microphone detected!")
            return False
        
        print(f"🎤 Selected microphone: {mics[0][1]}")
        recorder.set_microphone(mics[0][0])
        
        # Callbacks for feedback
        recorder.on_recording_start = lambda: print("🔴 Recording in progress...")
        recorder.on_recording_stop = lambda: print("⏹️ Recording finished!")
        
        # Start recording
        recorder.start_recording()
        
        # Wait for automatic completion
        while recorder.is_recording:
            time.sleep(0.1)
        
        # Check that we have audio data
        if not recorder.audio_data:
            print("❌ No audio data recorded!")
            return False
        
        # Save
        if recorder.save_recording(filename):
            duration = recorder.get_recording_duration()
            print(f"✅ File saved: {filename} ({duration:.1f}s)")
            return True
        else:
            print("❌ Error during save!")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        # Mandatory cleanup
        if recorder:
            recorder.cleanup()

# Usage
if __name__ == "__main__":
    record_message("test.wav")
```

## Advanced configuration

### Recording parameters

```python
recorder = AudioRecorder()

# Modify audio parameters (optional)
recorder.chunk_size = 2048        # Chunk size (default: 1024)
recorder.sample_rate = 48000      # Sample rate (default: 44100)
recorder.channels = 1             # Mono (default: 1)

# Silence detector configuration
recorder.set_silence_settings(
    threshold=500,    # Detection threshold (default: 1000)
    duration=2.5      # Silence duration in seconds (default: 2.0)
)
```

### Specific microphone selection

```python
recorder = AudioRecorder()

# List all microphones
mics = recorder.mic_selector.get_microphones()
for i, (index, name) in enumerate(mics):
    print(f"{i}: {name}")

# Select a specific microphone by name
for index, name in mics:
    if "USB" in name or "Headset" in name:
        recorder.set_microphone(index)
        print(f"Selected microphone: {name}")
        break
```

## Main classes

### AudioRecorder
Main class for audio recording with automatic silence detection.

**Main methods:**
- `start_recording()`: Starts recording
- `stop_recording()`: Manually stops recording
- `save_recording(filename)`: Saves to WAV file
- `set_microphone(index)`: Selects microphone
- `set_silence_settings(threshold, duration)`: Configures silence detection
- `get_recording_duration()`: Returns recording duration
- `cleanup()`: Releases resources

**Available callbacks:**
- `on_recording_start`: Called at recording start
- `on_recording_stop`: Called at recording end
- `on_volume_update`: Called on each volume update

### SilenceDetector
Automatically detects periods of silence to stop recording.

### MicrophoneSelector
Manages selection and configuration of available microphones.

## Graphical interface

The project also includes a complete graphical interface in `recorder_app.py`:

```bash
python recorder_app.py
```

## Usage tips

1. **Silence threshold**: Adjust according to your environment
   - Quiet environment: 300-500
   - Normal environment: 800-1200
   - Noisy environment: 1500-2000

2. **Silence duration**: 
   - Quick conversations: 1.5-2.0 seconds
   - Dictation/reflection: 3.0-4.0 seconds

3. **Error handling**: Always call `cleanup()` at the end of script

4. **Threading**: Recording happens in a separate thread, your main script remains responsive

## Troubleshooting

### Common issues

**"No module named 'pyaudio'"**
```bash
# Windows
pip install pyaudio

# Linux
sudo apt-get install portaudio19-dev python3-pyaudio

# macOS
brew install portaudio && pip install pyaudio
```

**"No microphone detected"**
- Check that your microphone is plugged in and recognized by the system
- Test with other audio applications
- Restart the script with administrator rights if necessary

**Poor recording quality**
- Increase the `sample_rate` (44100 → 48000)
- Check your microphone gain levels
- Use a better quality microphone

## License

GNU General Public License v3.0