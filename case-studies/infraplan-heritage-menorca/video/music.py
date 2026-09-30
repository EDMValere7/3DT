"""Procedural 30s soundtrack, 120 BPM, A minor with a Mediterranean E-major turn (Am F C E). 24 bars; sections start on bars 4/10/16/21 (7.5/18.75/30/39.375 s, same as index.html).
usage: python3 music.py out/music.wav
"""
import sys
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile

SR, DUR, BPM = 44100, 45.0, 128
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


def ks(m, d=0.7):
    """Karplus-Strong nylon-ish string, computed one period at a time."""
    n = max(2, int(round(SR / hz(m))))
    L_ = int(d * SR)
    y = np.zeros(L_ + 2 * n)
    y[:n] = filt(rng.uniform(-1, 1, n), "lowpass", 5000)
    for k in range(1, (L_ + n) // n + 1):
        a, b = k * n, (k + 1) * n
        prev = y[a - n : b - n]
        prev1 = y[a - n - 1 : b - n - 1] if a - n - 1 >= 0 else np.concatenate([[0], prev[:-1]])
        y[a:b] = 0.4985 * (prev + prev1)
    out = y[:L_]
    return out * np.minimum(1, (d - np.arange(L_) / SR) / 0.05) * 0.5


def rim():
    t = tt(0.06)
    return (np.sin(2 * np.pi * 1750 * t) * 0.6 + filt(rng.standard_normal(len(t)), "bandpass", [2000, 5000]) * 0.4) * np.exp(-t * 90) * 0.45


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
CH = [  # bar chords (pad voicings) + bass root: Am F C E
    ([64, 69, 72], 45), ([65, 69, 72], 41), ([64, 67, 72], 48), ([64, 68, 71], 40)]
ARP = [[69, 72, 76, 81], [69, 72, 77, 81], [67, 72, 76, 79], [68, 71, 76, 80]]
bars = int(DUR / BAR)
kicks = []

for b in range(bars):
    t0 = b * BAR
    notes, root = CH[b % 4]
    sec = "intro" if b < 4 else "A" if b < 10 else "B" if b < 16 else "C" if b < 21 else "out"
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
    if sec in ("B", "C") or (sec == "intro" and b >= 2):
        pat = ARP[b % 4]
        for k in range(16):
            m = pat[k % 4] + (12 if sec == "C" and k % 8 >= 6 else 0)
            place("music", ks(m, 0.5) + pluck(m + 12) * 0.25, t0 + k * BEAT / 4, 0.6 if sec != "intro" else 0.35, pan=0.35 if k % 2 else -0.35)
    if sec in ("B", "C"):
        for k in (0, 3, 6, 10, 12):
            place("drums", rim(), t0 + k * BEAT / 4, 0.5, pan=0.25)

# riser into first drop, whooshes into every cut, impacts on cuts
CUTS = [4 * BAR, 10 * BAR, 16 * BAR, 21 * BAR]
for c in CUTS:
    place("fx", riser(1.8), c - 1.8, 0.85)
    place("fx", whoosh(0.8), c - 0.8, 0.35)
for c, g in zip([0] + CUTS, (0.9, 0.8, 1.0, 0.9, 1.1)):
    place("fx", impact(), c, g)
OUT = CUTS[-1]
# outro: logo sting + long chord
place("music", filt(pad([64, 69, 71, 72, 76], DUR - OUT), "highpass", 160) * 1.5, OUT)
for i, m in enumerate((69, 76, 81)):
    place("music", ks(m, 3.5) * 1.6 + pluck(m + 12, 3.5) * 0.5, OUT + 0.35 + i * 0.12, 0.8, pan=(-0.4, 0, 0.4)[i])
place("drums", kick(), OUT, 1.0)

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
