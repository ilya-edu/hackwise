import { defineStore } from 'pinia'
import { connect } from './useSocket'

export interface Message {
  created_at: string;
  id: number;
  room_id: number;
  text: string;
  updated_at: string;
  user_id: number;
  references: string[] | null
  user: {
    id: number,
    name: string
}
}

export const useMessageStore = defineStore('messages', {
  state: () => ({
    messages: [] as Message[],
    currentRoomId: -1 as null | number,
    socket: null as WebSocket | null
  }),
  actions: {
    connect () {
      if (this.socket == null) {
        this.socket = connect()
      }
    },
    disconnect () {
      if (this.socket != null) {
        this.socket.onclose = null
        this.socket.close()
        this.socket = null
        this.currentRoomId = -1
        this.messages = []
      }
    },
    changeRoom (id: number) {
      this.messages = []
      this.currentRoomId = id
    }
  },
  getters: {
    getRoomId (state) {
      return state.currentRoomId
    }
  }
})
