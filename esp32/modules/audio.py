"""I2S playback of 16-bit PCM mono .wav files stored on the SD card."""
import struct
from machine import I2S, Pin

import pins

SAMPLE_RATE = 16000
CHUNK_BYTES = 4096


class Audio(object):
    def __init__(self):
        self._i2s = None
        self._volume = 70  # percent, 0-100

    def set_volume(self, percent):
        self._volume = max(0, min(100, percent))

    def _open_i2s(self, sample_rate):
        if self._i2s is not None:
            self._i2s.deinit()
        self._i2s = I2S(
            pins.I2S_ID,
            sck=Pin(pins.I2S_SCK),
            ws=Pin(pins.I2S_WS),
            sd=Pin(pins.I2S_SD),
            mode=I2S.TX,
            bits=16,
            format=I2S.MONO,
            rate=sample_rate,
            ibuf=CHUNK_BYTES * 2,
        )

    def _read_wav_header(self, f):
        riff, _, wave = struct.unpack("<4sI4s", f.read(12))
        if riff != b"RIFF" or wave != b"WAVE":
            raise ValueError("not a RIFF/WAVE file")

        sample_rate = SAMPLE_RATE
        data_size = 0
        while True:
            chunk_id, chunk_size = struct.unpack("<4sI", f.read(8))
            if chunk_id == b"fmt ":
                fmt = f.read(chunk_size)
                sample_rate = struct.unpack("<H H I I H H", fmt[:16])[3]
            elif chunk_id == b"data":
                data_size = chunk_size
                break
            else:
                f.read(chunk_size)
        return sample_rate, data_size

    def _apply_volume(self, buf):
        if self._volume >= 100:
            return buf
        scale = self._volume / 100.0
        out = bytearray(len(buf))
        for i in range(0, len(buf) - 1, 2):
            sample = struct.unpack_from("<h", buf, i)[0]
            struct.pack_into("<h", out, i, int(sample * scale))
        return out

    def play_wav(self, path, stop_flag=None):
        """Play a wav file; stop_flag is a callable polled between chunks
        that returns True to abort playback early (e.g. button pressed)."""
        with open(path, "rb") as f:
            sample_rate, data_size = self._read_wav_header(f)
            self._open_i2s(sample_rate)

            remaining = data_size
            while remaining > 0:
                if stop_flag is not None and stop_flag():
                    break
                chunk = f.read(min(CHUNK_BYTES, remaining))
                if not chunk:
                    break
                self._i2s.write(self._apply_volume(chunk))
                remaining -= len(chunk)
