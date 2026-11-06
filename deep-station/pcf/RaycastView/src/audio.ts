// Original sound effects synthesized with Web Audio. Power Fx raises events by id in Frame.events;
// the view plays each id once per new tick. The AudioContext starts on the first user gesture.

export const SND = {
    shot: 1, enemyHit: 2, enemyDeath: 3, door: 4, hurt: 5, pickup: 6, wake: 7, enemyAttack: 8, empty: 9, playerDeath: 10,
} as const;

type AC = AudioContext;

export class Sound {
    private ac: AC | null = null;
    private noise: AudioBuffer | null = null;
    muted = false;

    unlock() {
        if (this.ac) { if (this.ac.state === "suspended") void this.ac.resume(); return; }
        const Ctor = (globalThis as unknown as { AudioContext?: typeof AudioContext; webkitAudioContext?: typeof AudioContext });
        const C = Ctor.AudioContext ?? Ctor.webkitAudioContext;
        if (!C) return;
        this.ac = new C();
        const len = this.ac.sampleRate * 0.5;
        this.noise = this.ac.createBuffer(1, len, this.ac.sampleRate);
        const d = this.noise.getChannelData(0);
        let s = 12345;
        for (let i = 0; i < len; i++) { s = (s * 1103515245 + 12345) & 0x7fffffff; d[i] = s / 0x3fffffff - 1; }
    }

    destroy() { void this.ac?.close(); this.ac = null; }

    play(id: number) {
        const ac = this.ac;
        if (!ac || this.muted) return;
        if (ac.state === "suspended") void ac.resume(); // mobile webviews suspend the context between gestures
        const t = ac.currentTime;
        switch (id) {
            case SND.shot: this.burst(t, 0.12, 1800, 0.5); this.tone(t, "square", 140, 60, 0.08, 0.25); break;
            case SND.enemyHit: this.tone(t, "square", 520, 260, 0.06, 0.2); break;
            case SND.enemyDeath: this.burst(t, 0.35, 700, 0.5); this.tone(t, "sawtooth", 300, 40, 0.4, 0.25); break;
            case SND.door: this.tone(t, "sawtooth", 70, 50, 0.5, 0.18); this.burst(t, 0.5, 300, 0.15); break;
            case SND.hurt: this.tone(t, "sawtooth", 260, 110, 0.18, 0.3); break;
            case SND.pickup: this.tone(t, "square", 660, 660, 0.06, 0.2); this.tone(t + 0.07, "square", 990, 990, 0.08, 0.2); break;
            case SND.wake: this.tone(t, "triangle", 300, 700, 0.15, 0.25); this.tone(t + 0.15, "triangle", 700, 500, 0.1, 0.2); break;
            case SND.enemyAttack: this.tone(t, "square", 900, 400, 0.08, 0.15); break;
            case SND.empty: this.tone(t, "square", 1200, 1200, 0.02, 0.15); break;
            case SND.playerDeath: this.tone(t, "sawtooth", 300, 30, 1.0, 0.35); break;
        }
    }

    private tone(t: number, type: OscillatorType, f0: number, f1: number, dur: number, vol: number) {
        const ac = this.ac!;
        const o = ac.createOscillator(), g = ac.createGain();
        o.type = type;
        o.frequency.setValueAtTime(f0, t);
        o.frequency.exponentialRampToValueAtTime(Math.max(20, f1), t + dur);
        g.gain.setValueAtTime(vol, t);
        g.gain.exponentialRampToValueAtTime(0.001, t + dur);
        o.connect(g).connect(ac.destination);
        o.start(t);
        o.stop(t + dur + 0.02);
    }

    private burst(t: number, dur: number, cutoff: number, vol: number) {
        const ac = this.ac!;
        const src = ac.createBufferSource(), f = ac.createBiquadFilter(), g = ac.createGain();
        src.buffer = this.noise;
        f.type = "lowpass";
        f.frequency.value = cutoff;
        g.gain.setValueAtTime(vol, t);
        g.gain.exponentialRampToValueAtTime(0.001, t + dur);
        src.connect(f).connect(g).connect(ac.destination);
        src.start(t);
        src.stop(t + dur + 0.02);
    }
}
