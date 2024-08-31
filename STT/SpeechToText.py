import pyaudio
import wave
import threading
from faster_whisper import WhisperModel

class MicrophoneRecorder:
    def __init__(self, output_filename="output.wav", channels=1, rate=44100, chunk=1024, input_device_index=None, model_size="base"):
        self.output_filename = output_filename
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.frames = []
        self.stream = None
        self.p = None  # Initialize PyAudio in start_recording
        self.recording = False
        self.input_device_index = input_device_index
        self.model = WhisperModel(model_size)

    def start_recording(self):
        if self.recording:
            return "Already recording!"

        self.frames = []
        self.p = pyaudio.PyAudio()  # Reinitialize PyAudio here
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=self.channels,
                                  rate=self.rate,
                                  input=True,
                                  input_device_index=self.input_device_index,
                                  frames_per_buffer=self.chunk)
        self.recording = True
        threading.Thread(target=self._record).start()
        return "Started recording..."

    def _record(self):
        while self.recording:
            data = self.stream.read(self.chunk)
            self.frames.append(data)

    def stop_recording(self):
        if not self.recording:
            return "Not recording!"

        self.recording = False
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()  # Terminate PyAudio here

        wf = wave.open(self.output_filename, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        return self.transcribe_audio()

    def transcribe_audio(self):
        segments, info = self.model.transcribe(self.output_filename)
        text = " ".join([segment.text for segment in segments])
        return f"Transcription: {text}" if text else "No speech detected."
