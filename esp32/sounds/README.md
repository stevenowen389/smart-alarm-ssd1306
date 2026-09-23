Put your pre-rendered 16-bit PCM `.wav` alarm sounds on the SD card at
`/sd/sounds/`, not in this folder — the device reads them from the SD card,
this directory just documents the expected format.

To generate a wake-up phrase from your PC (any TTS engine works), export as:
- WAV, PCM 16-bit
- Mono
- 16000 Hz or 22050 Hz sample rate (must match SAMPLE_RATE in modules/audio.py)

Example with `espeak` + `ffmpeg` on Linux/WSL:
    espeak "Wake up, it's seven o'clock" -w tts_raw.wav
    ffmpeg -i tts_raw.wav -ar 16000 -ac 1 -acodec pcm_s16le alarm1.wav
