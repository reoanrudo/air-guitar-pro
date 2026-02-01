
export enum AppRole {
  LOBBY = 'LOBBY',
  PC_PLAYER = 'PC_PLAYER',
  MOBILE_CONTROLLER = 'MOBILE_CONTROLLER'
}

export interface FretState {
  stringIndex: number; // 0-5
  fretIndex: number;   // 0 (open), 1, 2, 3...
  active: boolean;
}

export interface Message {
  type: 'FRET_UPDATE' | 'STRUM_EVENT' | 'READY';
  payload: any;
}

export interface HandData {
  y: number;
  timestamp: number;
}
