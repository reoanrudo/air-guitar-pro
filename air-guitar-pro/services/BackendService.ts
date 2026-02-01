const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ScoreData {
  player_id: string;
  score: number;
  max_combo: number;
  perfect_count: number;
  great_count: number;
  miss_count: number;
}

export interface PlayHistoryData {
  player_id: string;
  score: number;
  max_combo: number;
  duration_seconds: number;
}

export interface LeaderboardEntry {
  rank: number;
  player_id: string;
  score: number;
  max_combo: number;
  played_at: string;
}

export interface PlayerStats {
  total_plays: number;
  total_score: number;
  average_score: number;
  best_score: number;
  best_combo: number;
  perfect_rate: number;
}

export class BackendService {
  private static async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  static async submitScore(data: ScoreData): Promise<void> {
    return this.request('/api/scores', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async submitPlayHistory(data: PlayHistoryData): Promise<void> {
    return this.request('/api/history', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static async getLeaderboard(limit: number = 10): Promise<LeaderboardEntry[]> {
    return this.request(`/api/leaderboard?limit=${limit}`);
  }

  static async getPlayerHistory(playerId: string, limit: number = 20): Promise<any[]> {
    return this.request(`/api/history/${playerId}?limit=${limit}`);
  }

  static async getPlayerStats(playerId: string): Promise<PlayerStats> {
    return this.request(`/api/stats/${playerId}`);
  }
}
