
import React, { useState, useCallback, useEffect } from 'react';
import { WebRTCService } from '../services/WebRTCService';

interface MobileControllerProps {
  webrtc: WebRTCService;
  roomId: string;
  connected: boolean;
  onExit: () => void;
}

const MobileController: React.FC<MobileControllerProps> = ({ webrtc, roomId, connected, onExit }) => {
  const [fretStates, setFretStates] = useState<number[]>([0, 0, 0, 0, 0, 0]);
  const stringNames = ['E', 'A', 'D', 'G', 'B', 'E'];
  const totalFrets = 4;

  const handleTouch = useCallback((stringIdx: number, fret: number) => {
    // 振動フィードバック (対応ブラウザのみ)
    if (window.navigator.vibrate) {
      window.navigator.vibrate(10);
    }
    
    setFretStates(prev => {
      const next = [...prev];
      next[stringIdx] = fret;
      return next;
    });
  }, []);

  useEffect(() => {
    // データ送信
    webrtc.send({ type: 'FRET_UPDATE', payload: fretStates });
  }, [fretStates, webrtc]);

  return (
    <div className="flex-1 flex flex-col h-screen w-full bg-slate-950 overflow-hidden select-none touch-none font-sans">
      {/* Status Bar */}
      <div className="flex items-center justify-between px-6 py-4 bg-slate-900 border-b border-white/5">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500 shadow-[0_0_12px_rgba(34,197,94,0.6)]' : 'bg-red-500 animate-pulse'}`}></div>
          <span className="text-[10px] font-black tracking-[0.2em] text-white uppercase opacity-70">
            {connected ? 'LINKED TO PC' : 'LINKING...'}
          </span>
        </div>
        <div className="text-right">
           <div className="text-[8px] font-bold text-slate-500 uppercase">Room Code</div>
           <div className="font-mono text-sm font-black text-orange-500 leading-none">{roomId}</div>
        </div>
        <button onClick={onExit} className="ml-4 p-2 px-4 bg-white/5 hover:bg-white/10 rounded-xl text-[10px] font-bold border border-white/5">EXIT</button>
      </div>

      {/* Fretboard Area */}
      <div className="flex-1 flex fret-board relative">
        {/* String Names Rail */}
        <div className="w-14 flex flex-col justify-around py-4 bg-black/40 border-r border-white/10 z-20">
          {stringNames.map((name, i) => (
            <div key={i} className="text-center font-black text-slate-600 text-xs italic">{name}</div>
          ))}
        </div>

        {/* Frets Grid */}
        <div className="flex-1 flex relative bg-[#0f172a]">
          {/* Fret Vertical Lines (Visual) */}
          {Array.from({ length: totalFrets }).map((_, i) => (
            <div 
              key={i} 
              className="absolute h-full w-[2px] bg-gradient-to-b from-slate-700 via-slate-500 to-slate-700 shadow-[2px_0_5px_rgba(0,0,0,0.5)] z-10" 
              style={{ left: `${(i + 1) * (100 / totalFrets)}%` }} 
            />
          ))}

          {/* Strings and Interaction Layers */}
          <div className="flex-1 flex flex-col py-4">
            {stringNames.map((_, sIdx) => (
              <div key={sIdx} className="flex-1 flex relative items-center group">
                {/* The Physical String Visual */}
                <div 
                  className={`absolute w-full left-0 transition-all duration-75 ${
                    fretStates[sIdx] > 0 
                    ? 'h-[4px] bg-orange-400 shadow-[0_0_15px_rgba(251,146,60,0.8)] string-vibrate' 
                    : 'h-[2px] bg-slate-700 shadow-inner'
                  }`}
                  style={{ top: '50%' }}
                />
                
                {/* Touch Zones (Invisible but large) */}
                <div className="flex w-full h-full relative z-20">
                  {/* Open string zone (Left-most) */}
                  <div 
                    className={`flex-1 flex items-center justify-center transition-all ${fretStates[sIdx] === 0 ? 'bg-orange-500/10' : ''}`}
                    onTouchStart={() => handleTouch(sIdx, 0)}
                  >
                    <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-[10px] font-black transition-all ${fretStates[sIdx] === 0 ? 'bg-orange-500 border-orange-400 text-white scale-110 shadow-lg' : 'border-slate-800 text-slate-800'}`}>O</div>
                  </div>

                  {/* Fret zones */}
                  {Array.from({ length: totalFrets }).map((_, fIdx) => (
                    <div 
                      key={fIdx}
                      className={`flex-[2] flex items-center justify-center transition-all active:bg-white/5`}
                      onTouchStart={() => handleTouch(sIdx, fIdx + 1)}
                    >
                      <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-[12px] font-black transition-all ${
                        fretStates[sIdx] === fIdx + 1 
                        ? 'bg-orange-500 border-orange-300 text-white scale-125 shadow-[0_0_20px_rgba(249,115,22,0.5)] z-30' 
                        : 'border-slate-800/50 bg-slate-900/30 text-slate-700'
                      }`}>
                        {fIdx + 1}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Chord Shortcuts */}
      <div className="h-28 bg-slate-900/80 border-t border-white/5 p-4 grid grid-cols-4 gap-3 backdrop-blur-xl">
         <ChordButton label="C" pattern={[0, 1, 0, 2, 3, 0]} current={fretStates} onClick={setFretStates} />
         <ChordButton label="G" pattern={[3, 0, 0, 0, 2, 3]} current={fretStates} onClick={setFretStates} />
         <ChordButton label="D" pattern={[2, 3, 2, 0, 0, 0]} current={fretStates} onClick={setFretStates} />
         <ChordButton label="Am" pattern={[0, 1, 2, 2, 0, 0]} current={fretStates} onClick={setFretStates} />
      </div>

      <div className="bg-orange-600 h-1 w-full opacity-50"></div>
    </div>
  );
};

interface ChordBtnProps {
  label: string;
  pattern: number[];
  current: number[];
  onClick: (p: number[]) => void;
}

const ChordButton: React.FC<ChordBtnProps> = ({ label, pattern, current, onClick }) => {
  const isActive = pattern.every((v, i) => v === current[i]);
  const handleClick = () => {
    if (window.navigator.vibrate) window.navigator.vibrate([15, 10, 15]);
    onClick(pattern);
  };

  return (
    <button 
      className={`rounded-2xl border-2 font-black text-lg transition-all active:scale-95 shadow-lg ${
        isActive 
        ? 'bg-orange-500 border-orange-300 text-white shadow-orange-500/20' 
        : 'bg-slate-800 border-white/5 text-slate-400'
      }`}
      onTouchStart={handleClick}
    >
      {label}
    </button>
  );
};

export default MobileController;
