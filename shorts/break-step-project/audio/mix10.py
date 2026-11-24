# Sound for the 10.5 s "Break Step" short: synthesized SFX (template sfx_gen) + a short original march (template
# instruments), ducked under the voice. Times in seconds of the NEW timeline (30 fps, EDL from Break10.tsx).
import sys, numpy as np
sys.path.insert(0, sys.path[0])
from dsp import SR, ns, rng, st, place, read_wav, write_wav, integrated, true_peak, dbg, lp, hp, make_ir, convolve_st
import sfx_gen as G, instruments as I

DUR, VOFF = 10.5, 0.2
EDL = [(0, 45, 140), (45, 120, 290), (120, 165, 765), (165, 212, 1003), (212, 232, 1099), (232, 262, 1800), (262, 315, 1867)]
SNAP_T = 201 / 30            # bolt breaks on screen
SLAM_T = 221 / 30            # deck hits the river
CUTS = [a / 30 for a, _, _ in EDL[1:]]
N = ns(DUR)
sfx, mus = np.zeros((2, N)), np.zeros((2, N))
def put(buf, x, t, g_db=0.0):
    pre = 0.0
    if isinstance(x, tuple): x, pre = x
    place(buf, x, t - pre, dbg(g_db))

# marching: footfalls every 0.5 s of story time (tau = old frame / 30) in the march edits, harder as it bounces
r = rng(1)
for k, (a, b, o) in enumerate(EDL[:3]):
    t_old0 = o / 30
    for n in range(int(np.ceil(t_old0 * 2)), int((o + b - a) / 30 * 2) + 1):
        t = n / 2 - t_old0 + a / 30
        if a / 30 <= t < b / 30:
            inten = [0.6, 0.9, 1.25][k]
            put(sfx, G.column_stomp(r, inten, n % 2, boom_gain=0.6), t, [-12, -6, -3][k])
            if k == 2: put(sfx, G.deck_flex(r, 0.8), t + 0.05, -6)
put(sfx, G.chain_groan(2.3, rng(2), 0.4, 1.0), 4.0, -8)
put(sfx, G.bolt_strain(rng(3), 1.0), SNAP_T - 0.5, -10)
put(sfx, G.bolt_snap(rng(4)), SNAP_T, 0)
put(sfx, G.whoosh(0.3, rng(5), 0.24, 220, 1300, 1.0, 0.05, 0.1), SLAM_T - 0.24, -8)
put(sfx, G.splash_big(rng(6)), SLAM_T, -1)
put(sfx, G.hammer_hit(rng(7), 1.0), 242 / 30, -6)
put(sfx, G.hammer_hit(rng(8), 0.8), 256 / 30, -9)
rs = rng(9)
for i in range(9):  # tourists ambling, out of step
    put(sfx, G.stroll_step(rs, 0.5), 262 / 30 + 0.1 + i * 0.22 + rs.uniform(-0.05, 0.05), -16)
for c in CUTS:
    if abs(c - SNAP_T) > 0.2 and abs(c - SLAM_T) > 0.5:
        put(sfx, G.whoosh(0.45, rng(int(c * 100)), 0.07, 400, 2400, 0.8, 0.13, 0.2), c, -16)

# music: Bb march 120 bpm, beat = footfall (0.5 s); stops dead on the snap, short light tag at the end
m2f = I.m2f
BASS = [46, 53, 46, 53, 41, 48, 46, 53]  # Bb F Bb F | F C Bb F (oom on beats)
MEL = [(70, 1), (74, 1), (77, 2), (74, 1), (70, 1), (72, 2), (74, 1), (75, 1), (77, 2), (82, 1), (81, 1), (77, 2)]
rm = rng(10)
t0 = 0.05
for i in range(int((SNAP_T - t0) / 0.5)):
    t = t0 + i * 0.5
    put(mus, I.brass(m2f(BASS[i % 8] - 12), 0.22, 0.7, rm, "tuba"), t, -4)
    put(mus, I.brass(m2f(62 + (i % 2) * 3), 0.12, 0.45, rm, "horn"), t + 0.25, -14)
    put(mus, I.snare(0.55 + 0.25 * (i % 2 == 0) + 0.04 * i / 4, rm), t, -9)
    put(mus, I.snare(0.35, rm, 0.2), t + 0.25, -15)
tm = t0
while tm < SNAP_T - 0.1:
    for nnote, beats in MEL:
        if tm >= SNAP_T - 0.1: break
        put(mus, I.glock(m2f(nnote), 0.6, rm), tm, -10)
        tm += beats * 0.25
put(mus, I.cymbal(0.8, rm), SNAP_T, -8)
for i, nn in enumerate([70, 74, 77, 82, 77, 82]):  # casual tag, deliberately off-beat
    put(mus, I.pluck(m2f(nn), 0.6, rm), 8.75 + i * 0.29 + (0.06 if i % 2 else 0), -8)
put(mus, I.brass(m2f(34), 0.9, 0.5, rm, "soft"), 9.6, -6)
for buf, rt in ((sfx, 0.5), (mus, 0.9)):
    buf += 0.12 * convolve_st(buf, make_ir(rt, 11))[:, :N]

# voice + ducking + loudness
v, sr = read_wav(sys.argv[1]); v = st(v.mean(0) if v.shape[0] > 1 else v[0])
voice = np.zeros((2, N)); place(voice, v, VOFF)
env = np.abs(voice[0]); w = ns(0.15)
env = np.convolve(env, np.ones(w) / w, "same") > 0.01
env = np.convolve(env.astype(float), np.ones(ns(0.3)) / ns(0.3), "same")
duck = dbg(-9 * np.clip(env * 2, 0, 1))
voice *= dbg(-16 - integrated(voice))
mus *= dbg(-21 - integrated(mus) + 3) * duck   # music +3 dB (house mix rule)
sfx *= dbg(-19 - integrated(sfx) - 6)          # sfx -6 dB
mix = voice + mus + sfx
mix *= dbg(-14 - integrated(mix))
pk = np.abs(mix).max()
if pk > 0.89: mix = np.tanh(mix / pk * 1.3) / np.tanh(1.3) * 0.89
fo = ns(0.25); mix[:, -fo:] *= np.linspace(1, 0, fo)
write_wav(sys.argv[2], mix)
print("LUFS", round(integrated(mix), 1), "peak dB", round(20 * np.log10(np.abs(mix).max()), 2))
