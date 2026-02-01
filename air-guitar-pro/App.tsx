import React, { useState, useEffect, useCallback } from 'react';
import { AppRole } from './types';
import Lobby from './components/Lobby';
import PCPlayer from './components/PCPlayer';

const App: React.FC = () => {
  const [role, setRole] = useState<AppRole>(AppRole.LOBBY);
  const [roomId, setRoomId] = useState<string>('');

  useEffect(() => {
    // PCモードのみ: URLパラメータから部屋IDを取得
    const params = new URLSearchParams(window.location.search);
    const roomParam = params.get('room') || params.get('r');
    const hash = window.location.hash.replace('#', '');

    const defaultRoom = (roomParam || hash || 'TEST').toUpperCase().substring(0, 4);
    setRoomId(defaultRoom);
  }, []);

  const startPCMode = useCallback((id: string) => {
    setRole(AppRole.PC_PLAYER);
    setRoomId(id);
  }, []);

  const handleRoleSelect = useCallback(async (selectedRole: AppRole, id: string) => {
    // PCモードのみ
    if (selectedRole === AppRole.PC_PLAYER) {
      startPCMode(id);
    }
  }, [startPCMode]);

  const handleExit = useCallback(() => {
    setRole(AppRole.LOBBY);
  }, []);

  return (
    <div className="min-h-screen w-full flex flex-col bg-slate-950 text-white overflow-hidden">
      {role === AppRole.LOBBY && (
        <Lobby onSelect={handleRoleSelect} initialRoomId={roomId} />
      )}

      {role === AppRole.PC_PLAYER && (
        <PCPlayer
          roomId={roomId}
          onExit={handleExit}
        />
      )}
    </div>
  );
};

export default App;
