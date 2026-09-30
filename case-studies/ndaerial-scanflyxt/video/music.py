"""Procedural 30s soundtrack, 120 BPM, F minor. Cuts on bars at 4/10/18/26s (same as index.html).
usage: python3 music.py out/music.wav
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR, DUR, BPM = 44100, 30.0, 120
BEAT = 60 / BPM
BAR = 4 * BEAT
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = {k: np.zeros((N, 2)) for k in ("drums", "bass", "music", "fx")}


def hz(m):
    return 440 * 2 ** ((m - 69) / 12)


def place(bus, sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N:
        return
    sig = sig[: N - i]
    if sig.ndim == 1:
        sig = np.stack([sig * np.sqrt((1 - pan) / 2), sig * np.sqrt((1 + pan) / 2)], 1) * np.sqrt(2)
    L[bus][i : i + len(sig)] += sig * gain


def filt(x, kind, f, order=2):
    sos = butter(order, f, btype=kind, fs=SR, output="sos")
    return sosfilt(sos, x, axis=0)


def tt(d):
    return np.arange(int(d * SR)) / SR


# ---------- instruments ----------
def kick(d=0.45):
    t = tt(d)
    f = 45 + 110 * np.exp(-t * 32)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-t * 7.5)
    click = filt(rng.standard_normal(len(t)), "highpass", 2500) * np.exp(-t * 300) * 0.25
    return np.tanh((s + click) * 1.8) * 0.9


def clap(d=0.35):
    t = tt(d)
    n = rng.standard_normal(len(t))
    env = sum(np.where(t >= o, np.exp(-(t - o) * 90), 0) for o in (0, 0.011, 0.022)) + 0.5 * np.exp(-t * 14) * (t > 0.03)
    return filt(n * env, "bandpass", [900, 3200]) * 0.9


def hat(d=0.06, open_=False):
    t = tt(0.35 if open_ else d)
    return filt(rng.standard_normal(len(t)), "highpass", 7000) * np.exp(-t * (11 if open_ else 70)) * 0.5


def additive(freq, d, nh, decay_base, decay_k, amp_k=1.0, detune=0.0):
    t = tt(d)
    out = np.zeros(len(t))
    for k in range(1, nh + 1):
        if freq * k > SR / 2.2:
            break
        out += (1 / k ** amp_k) * np.sin(2 * np.pi * freq * (1 + detune) * k * t) * np.exp(-t * (decay_base + decay_k * k))
    return out


def pluck(m, d=0.5):
    return additive(hz(m), d, 18, 6, 2.2) * 0.35


def bass(m, d):
    t = tt(d)
    s = additive(hz(m), d, 14, 0.5, 0.35) + 0.6 * np.sin(2 * np.pi * hz(m) * t)
    a = np.minimum(1, t / 0.005) * np.minimum(1, (d - t) / 0.02)
    return np.tanh(s * a * 1.4) * 0.45


def pad(notes, d):
    t = tt(d)
    s = np.zeros((len(t), 2))
    for m in notes:
        for j, dt in enumerate((-0.006, -0.002, 0.002, 0.006)):
            v = additive(hz(m), d, 10, 0.0, 0.0, amp_k=1.0, detune=dt)
            s[:, j % 2] += v
    s = filt(s, "lowpass", 2400)
    env = np.minimum(1, t / 0.35) * np.minimum(1, (d - t) / 0.4)
    return s * env[:, None] * 0.05


def impact(d=2.5):
    t = tt(d)
    f = 30 + 60 * np.exp(-t * 6)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.2)
    n = filt(rng.standard_normal(len(t)), "lowpass", 1800) * np.exp(-t * 5) * 0.5
    return np.tanh((boom + n) * 1.5) * 0.8


def whoosh(d=0.9):
    t = tt(d)
    n = rng.standard_normal(len(t))
    # time-varying one-pole lowpass: cutoff rises through the whoosh
    fc = 300 + 9000 * (t / d) ** 2
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.zeros(len(t))
    acc = 0.0
    for i in range(len(t)):
        acc = (1 - a[i]) * n[i] + a[i] * acc
        y[i] = acc
    env = (t / d) ** 2.2
    return y * env * 0.9


def riser(d):
    t = tt(d)
    f = 220 * 2 ** (2.2 * t / d)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.15 + filt(rng.standard_normal(len(t)), "highpass", 3000) * 0.2
    return s * (t / d) ** 2


# ---------- arrangement ----------
CH = [  # bar chords (pad voicings) + bass root, F minor: Fm Db Ab Eb
    ([65, 68, 72], 41), ([61, 65, 68], 37), ([60, 63, 68], 44), ([58, 63, 67], 39)]
ARP = [[77, 80, 84, 80], [77, 80, 85, 80], [75, 80, 84, 80], [75, 79, 82, 79]]
bars = int(DUR / BAR)
kicks = []

for b in range(bars):
    t0 = b * BAR
    notes, root = CH[b % 4]
    sec = "intro" if t0 < 4 else "A" if t0 < 10 else "B" if t0 < 18 else "C" if t0 < 26 else "out"
    if sec != "out":
        place("music", pad(notes, BAR + 0.3), t0, 1.0 if sec != "intro" else 0.7)
    # drums
    for q in range(4):
        tb = t0 + q * BEAT
        if sec in ("A", "B", "C"):
            place("drums", kick(), tb, 1.0); kicks.append(tb)
        elif sec == "intro" and q in (0, 2) and t0 > 0:
            place("drums", kick(), tb, 0.8); kicks.append(tb)
        if sec in ("A", "B", "C") and q in (1, 3):
            place("drums", clap(), tb, 0.55, 0.05)
        for e in range(4 if sec in ("B", "C") else 2):
            ts = tb + e * BEAT / (4 if sec in ("B", "C") else 2)
            op = sec != "intro" and e == (2 if sec in ("B", "C") else 1)
            place("drums", hat(open_=op), ts, (0.35 if op else 0.22) * (1 if e % 2 else 0.7), 0.3 if e % 2 else -0.3)
    # bass: offbeat 8ths in A, rolling 16ths in B/C
    if sec in ("A", "B", "C"):
        step = BEAT / 2 if sec == "A" else BEAT / 4
        for k in range(int(BAR / step)):
            if sec == "A" and k % 2 == 0:
                continue
            m = root + (12 if sec == "C" and k % 4 == 3 else 0)
            place("bass", bass(m, step * 0.85), t0 + k * step, 0.9 if k % 2 else 0.7)
    elif sec == "intro":
        place("bass", bass(root, BAR * 0.95) * 0.6, t0)
    # arp
    if sec in ("B", "C") or (sec == "intro" and t0 >= 2):
        pat = ARP[b % 4]
        for k in range(16):
            m = pat[k % 4] + (12 if sec == "C" and k % 8 >= 6 else 0)
            place("music", pluck(m), t0 + k * BEAT / 4, 0.55 if sec != "intro" else 0.3, pan=0.35 if k % 2 else -0.35)

# riser into first drop, whooshes into every cut, impacts on cuts
place("fx", riser(1.8), 2.2, 0.8)
place("fx", riser(1.8), 8.2, 0.9)
place("fx", riser(1.9), 16.1, 0.9)
place("fx", riser(1.8), 24.2, 0.8)
for c in (4, 10, 18, 26):
    place("fx", whoosh(0.8), c - 0.8, 0.35)
for c, g in ((0, 0.9), (10, 1.0), (18, 0.8), (26, 1.1)):
    place("fx", impact(), c, g)
# outro: logo sting + long chord
place("music", filt(pad([60, 65, 68, 72, 77], 4.0), "highpass", 160) * 1.5, 26.0)
for i, m in enumerate((77, 84, 89)):
    place("music", pluck(m, 2.5) * 1.3, 26.35 + i * 0.12, 0.8, pan=(-0.4, 0, 0.4)[i])
place("drums", kick(), 26.0, 1.0)

# ---------- mix ----------
tax = np.arange(N) / SR
duck = np.ones(N)
for k in kicks:
    m = tax >= k
    duck[m] = np.minimum(duck[m], 1 - 0.65 * np.exp(-(tax[m] - k) / 0.11))
L["bass"] *= duck[:, None]
L["music"] *= (0.35 + 0.65 * duck)[:, None]

ir_t = tt(2.6)
ir = np.stack([rng.standard_normal(len(ir_t)), rng.standard_normal(len(ir_t))], 1) * np.exp(-ir_t / 0.55)[:, None]
ir = filt(ir, "lowpass", 6000)
ir /= np.sqrt((ir ** 2).sum(0))
send = L["music"] * 0.9 + L["fx"] * 0.5 + L["drums"] * 0.08
rev = np.stack([fftconvolve(send[:, 0], ir[:, 0])[:N], fftconvolve(send[:, 1], ir[:, 1])[:N]], 1)

mix = L["drums"] * 0.9 + filt(L["bass"], "lowpass", 1800) * 1.0 + L["music"] * 0.9 + L["fx"] * 0.8 + rev * 0.45
mix = filt(mix, "highpass", 28)
mix /= np.max(np.abs(mix))
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
mix *= 0.89 / np.max(np.abs(mix))
fade = np.minimum(1, (DUR - tax) / 1.2)
mix *= fade[:, None]
mix[: int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))[:, None]

out = sys.argv[1] if len(sys.argv) > 1 else "out/music.wav"
wavfile.write(out, SR, (mix * 32767).astype(np.int16))
print("wrote", out)
