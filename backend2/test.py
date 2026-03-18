import sounddevice as sd
import numpy as np
import soundfile as sf
from transformers import WhisperProcessor, WhisperForConditionalGeneration

# -----------------------------
# Record audio from microphone
# -----------------------------
def record_audio(duration=5, sample_rate=16000, filename=None):
    """
    Records audio from the microphone.
    Args:
        duration: seconds to record
        sample_rate: recording sample rate
        filename: optional, if provided saves the audio
    Returns:
        audio_data: numpy array of recorded audio
    """
    print(f"🎙️ Recording for {duration} seconds... Please speak now.")
    audio_data = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()  # Wait until recording is finished
    audio_data = audio_data.squeeze()  # Convert to 1D array

    if filename:
        sf.write(filename, audio_data, sample_rate)
        print(f"✅ Audio saved to {filename}")

    return audio_data, sample_rate

# -----------------------------
# Transcribe audio using Whisper
# -----------------------------
def transcribe_audio(audio_data, sample_rate=16000):
    """
    Transcribes audio using Hugging Face Whisper model.
    Automatically detects language.
    """
    model_name = "openai/whisper-large"
    processor = WhisperProcessor.from_pretrained(model_name)
    model = WhisperForConditionalGeneration.from_pretrained(model_name)

    # Process audio
    inputs = processor(audio_data, sampling_rate=sample_rate, return_tensors="pt")

    # Generate transcription
    generated_ids = model.generate(inputs["input_features"])
    transcription = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]

    return transcription

# -----------------------------
# Main function
# -----------------------------
def main():
    # Record audio (5 seconds)
    audio_data, sample_rate = record_audio(duration=5)

    print("\n⏳ Transcribing audio...")
    text = transcribe_audio(audio_data, sample_rate)

    print("\n✅ Transcription Result:")
    print(f"🗣️ You said: {text}")

if __name__ == "__main__":
    main()
