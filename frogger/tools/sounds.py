"""Original chiptune sound effects and jingles -> WAV data-URI named formulas for the Frogger canvas app.

Everything here is synthesized (square waves, a noise burst, simple envelopes) and composed for this homage.
No melody from the arcade or the ports is reproduced. Output: 8000 Hz, 8-bit unsigned mono WAV, base64 in a
data URI, one named formula per clip (nfSnd...).

Run:  python tools/sounds.py   (prints clip sizes and the Power Fx lines)
"""
import base64, io, math, random, struct, wave

RATE = 8000


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def square(freq, n, duty=0.5):
    """n samples of a square wave in -1..1 at freq (freq may be a callable of sample index)."""
    out = []
    phase = 0.0
    for i in range(n):
        f = freq(i) if callable(freq) else freq
        phase += f / RATE
        out.append(1.0 if (phase % 1.0) < duty else -1.0)
    return out


def envelope(samples, attack=0.005, release=0.03, decay_to=1.0):
    n = len(samples)
    a = max(1, int(attack * RATE))
    r = max(1, int(release * RATE))
    out = []
    for i, s in enumerate(samples):
        g = min(1.0, i / a)
        if i > n - r:
            g *= (n - i) / r
        g *= 1.0 - (1.0 - decay_to) * (i / n)
        out.append(s * g)
    return out


def silence(seconds):
    return [0.0] * int(seconds * RATE)


def tone(midi, seconds, vol=0.5, duty=0.5, decay_to=0.6):
    return [s * vol for s in envelope(square(midi_hz(midi), int(seconds * RATE), duty), decay_to=decay_to)]


def sweep(f0, f1, seconds, vol=0.5):
    n = int(seconds * RATE)
    return [s * vol for s in envelope(square(lambda i: f0 + (f1 - f0) * i / n, n), release=0.01)]


def noise(seconds, vol=0.5, decay_to=0.0):
    rnd = random.Random(7)
    n = int(seconds * RATE)
    return [s * vol for s in envelope([rnd.uniform(-1, 1) for _ in range(n)], decay_to=decay_to)]


def mix(*tracks):
    n = max(len(t) for t in tracks)
    return [sum(t[i] if i < len(t) else 0.0 for t in tracks) for i in range(n)]


def seq(notes, step, vol=0.45, duty=0.5):
    """notes: list of midi numbers or None (rest), each lasting `step` seconds (a tuple (midi, beats) holds)."""
    out = []
    for n in notes:
        midi, beats = (n if isinstance(n, tuple) else (n, 1))
        out += tone(midi, step * beats, vol, duty) if midi is not None else silence(step * beats)
    return out


def wav_bytes(samples):
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(1)
        w.setframerate(RATE)
        w.writeframes(bytes(max(0, min(255, int(128 + 120 * max(-1.0, min(1.0, s))))) for s in samples))
    return buf.getvalue()


# ---------------------------------------------------------------- clips (all original)
C4, D4, E4, F4, G4, A4, B4 = 60, 62, 64, 65, 67, 69, 71
C5, D5, E5, F5, G5, A5, B5, C6, E6, G6 = 72, 74, 76, 77, 79, 81, 83, 84, 88, 91
C3, G3, F3, A3 = 48, 55, 53, 57

CLIPS = {
    # start jingle: a bouncy two-voice phrase, 1.6 s
    "nfSndJingle": mix(
        seq([C5, E5, G5, C6, G5, E5, C5, D5, E5, (G5, 2)], 0.145, 0.42, 0.5),
        seq([C3, None, G3, None, C3, None, G3, None, C3, (C3, 2)], 0.145, 0.25, 0.25)),
    "nfSndHop": sweep(320, 900, 0.07, 0.5),
    "nfSndSquash": mix([s * 0.5 for s in envelope(square(70, int(0.35 * RATE), 0.3), decay_to=0.0)], noise(0.2, 0.35)),
    "nfSndDrown": seq([(G5, 1), (D5, 1), (A4, 1), (E4, 2)], 0.2, 0.4, 0.5),
    "nfSndWarn": seq([C6, G5], 0.06, 0.5),
    "nfSndHome": seq([C6, E6, G6], 0.12, 0.45),
    "nfSndFanfare": mix(
        seq([C5, C5, C5, E5, G5, (C6, 3), G5, (C6, 3)], 0.17, 0.42),
        seq([C3, G3, C3, G3, C3, (G3, 3), C3, (C3, 3)], 0.17, 0.25, 0.25)),
    "nfSndPickup": tone(45, 0.18, 0.5, 0.5, 0.3),
    "nfSndBonus": seq([G5, C6, G5, C6, E6], 0.08, 0.45),
    "nfSndExtra": seq([C5, E5, G5, C6, E6, (G6, 2)], 0.09, 0.45),
    "nfSndOver": mix(
        seq([E5, C5, A4, F4, D4, (C4, 3)], 0.3, 0.4),
        seq([C3, A3, F3, D4 - 12, G3, (C3, 3)], 0.3, 0.25, 0.25)),
}


def data_uri(samples):
    return "data:audio/wav;base64," + base64.b64encode(wav_bytes(samples)).decode("ascii")


def powerfx_string(s):
    return '"' + s.replace('"', '""') + '"'


def formula_lines():
    return [f"{name} = {powerfx_string(data_uri(samples))};" for name, samples in CLIPS.items()]


def write_wavs(folder):
    import os
    os.makedirs(folder, exist_ok=True)
    for name, samples in CLIPS.items():
        with open(os.path.join(folder, name.replace("nfSnd", "").lower() + ".wav"), "wb") as f:
            f.write(wav_bytes(samples))


if __name__ == "__main__":
    total = 0
    for name, samples in CLIPS.items():
        n = len(data_uri(samples))
        total += n
        print(f"{name:14s} {len(samples) / RATE:5.2f} s  {n:6d} chars")
    print("total", total)
