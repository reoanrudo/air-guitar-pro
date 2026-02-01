
import React, { useState } from 'react';
import { AppRole } from '../types';

interface LobbyProps {
  onSelect: (role: AppRole, roomId: string) => void;
  initialRoomId?: string;
}

const Lobby: React.FC<LobbyProps> = ({ onSelect, initialRoomId }) => {
  const displayRoomId = (initialRoomId || 'TEST').toUpperCase();

  const handlePCSession = () => {
    onSelect(AppRole.PC_PLAYER, displayRoomId);
  };

  const handleMobileSession = () => {
    if (displayRoomId.length === 4) {
      onSelect(AppRole.MOBILE_CONTROLLER, displayRoomId);
    } else {
      alert('Invalid Room ID');
    }
  };

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-6 space-y-8 max-w-lg mx-auto">
      <div className="text-center">
        <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-yellow-400 mb-2 italic">
          AIR GUITAR PRO
        </h1>
        <p className="text-slate-400 text-lg">The Ultimate Two-Device Rock Simulator</p>
      </div>

      {/* Room ID Display */}
      <div className="w-full bg-gradient-to-br from-slate-900/80 to-slate-800/80 p-10 rounded-3xl border-2 border-orange-500/30 shadow-2xl backdrop-blur-xl text-center">
        <label className="text-xs font-bold text-orange-400 uppercase tracking-widest px-1 block mb-6">Room Code (モバイル側に入力)</label>
        <div className="text-8xl font-black text-white tracking-widest mb-4 drop-shadow-lg">{displayRoomId}</div>
        <p className="text-slate-400 text-base">モバイル側（左手）の設定画面で</p>
        <p className="text-slate-400 text-base">このRoom IDを入力して接続してください</p>
      </div>

      <div className="grid grid-cols-1 gap-4 w-full">
        <button
          onClick={handlePCSession}
          className="group relative bg-white text-slate-950 px-8 py-5 rounded-xl font-bold text-lg hover:scale-[1.02] active:scale-95 transition-all shadow-lg overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-500"></div>
          <i className="fa-solid fa-desktop mr-2"></i> PC MODE (Right Hand)
        </button>
      </div>

      <div className="text-slate-500 text-sm text-center px-4 leading-relaxed">
        <p>カメラを使用して右手のストロークを検出します</p>
      </div>
    </div>
  );
};

export default Lobby;
