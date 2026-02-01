
import * as Tone from 'tone';

export class AudioEngine {
  private dist: Tone.Distortion;
  private synth: Tone.PolySynth;
  private strings: string[] = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4'];
  private isStarted: boolean = false;
  private mainGain: Tone.Gain;

  constructor() {
    this.mainGain = new Tone.Gain(2.0).toDestination();
    this.dist = new Tone.Distortion(0.8).connect(this.mainGain);
    
    const verb = new Tone.Reverb({ decay: 1.5, wet: 0.35 }).connect(this.dist);
    const filter = new Tone.Filter(2500, "lowpass").connect(verb);
    
    this.synth = new Tone.PolySynth(Tone.FMSynth, {
      harmonicity: 3,
      modulationIndex: 10,
      oscillator: { type: 'sawtooth' },
      envelope: {
        attack: 0.002, // 鋭いピッキング
        decay: 0.2,
        sustain: 0.2,
        release: 1.2
      }
    }).connect(filter);
  }

  async start() {
    if (this.isStarted) return;
    try {
      await Tone.start();
      await Tone.context.resume();
      this.isStarted = true;
      console.log("🎸 Audio Engine: Ready for Rock");
    } catch (e) {
      console.error("Audio Engine failed to start:", e);
    }
  }

  playMuted() {
    if (!this.isStarted) return;
    this.synth.triggerAttackRelease('E1', '32n', Tone.now(), 0.3);
  }

  playStrum(fretStates: (number | null)[], direction: 'up' | 'down') {
    if (!this.isStarted) return;
    const now = Tone.now();
    const indices = direction === 'down' ? [0, 1, 2, 3, 4, 5] : [5, 4, 3, 2, 1, 0];

    indices.forEach((stringIdx, i) => {
      const fret = fretStates[stringIdx];
      // nullの弦は音を出さない（コードに含まれない弦）
      if (fret === null || fret === -1) return;

      const baseNote = this.strings[stringIdx];
      const note = Tone.Frequency(baseNote).transpose(fret).toNote();
      const strumDelay = i * 0.015; // 指で弾く時間差
      this.synth.triggerAttackRelease(note, '1n', now + strumDelay, 0.85);
    });
  }
}
