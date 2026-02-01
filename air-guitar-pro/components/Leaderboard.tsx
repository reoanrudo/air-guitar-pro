import React, { useEffect, useState } from 'react';
import { BackendService, LeaderboardEntry } from '../services/BackendService';

interface LeaderboardProps {
  roomId: string;
}

const Leaderboard: React.FC<LeaderboardProps> = ({ roomId }) => {
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadLeaderboard();
  }, []);

  const loadLeaderboard = async () => {
    try {
      setLoading(true);
      const data = await BackendService.getLeaderboard(10);
      setLeaderboard(data);
    } catch (error) {
      console.error('Failed to load leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="absolute top-4 right-4 z-20 bg-slate-900/90 backdrop-blur-xl border border-white/10 rounded-2xl p-6 max-w-sm">
      <h3 className="text-lg font-black text-orange-500 mb-4 tracking-wider uppercase">Leaderboard</h3>
      {loading ? (
        <div className="text-center text-slate-400 py-8">Loading...</div>
      ) : leaderboard.length === 0 ? (
        <div className="text-center text-slate-400 py-8">No scores yet</div>
      ) : (
        <div className="space-y-2">
          {leaderboard.map((entry, index) => (
            <div
              key={entry.rank}
              className={`flex items-center gap-3 p-2 rounded-lg ${
                index === 0 ? 'bg-yellow-500/20 border border-yellow-500/30' :
                index === 1 ? 'bg-slate-400/20 border border-slate-400/30' :
                index === 2 ? 'bg-orange-600/20 border border-orange-600/30' :
                'bg-white/5 border border-white/10'
              }`}
            >
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-black text-sm ${
                index < 3 ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-white' : 'bg-white/10 text-slate-400'
              }`}>
                {entry.rank}
              </div>
              <div className="flex-1">
                <div className="text-white font-bold">{entry.player_id}</div>
                <div className="text-slate-400 text-xs">Combo: {entry.max_combo}</div>
              </div>
              <div className="text-2xl font-black text-white">
                {entry.score.toLocaleString()}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Leaderboard;
