"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface Message {
  id: string;
  conversation_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  thinking_trace?: any[];
  sources?: any[];
  timestamp: string;
}

export interface Conversation {
  id: string;
  title: string;
  updated_at: string;
}

interface ChatStore {
  conversations: Conversation[];
  currentConversationId: string | null;
  messages: Message[];
  isStreaming: boolean;
  searchEnabled: boolean;
  sidebarOpen: boolean;
  
  setConversations: (conversations: Conversation[]) => void;
  setCurrentConversation: (id: string | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setStreaming: (streaming: boolean) => void;
  toggleSearch: () => void;
  toggleSidebar: () => void;
  reset: () => void;
}

export const useChatStore = create<ChatStore>()(
  persist(
    (set) => ({
      conversations: [],
      currentConversationId: null,
      messages: [],
      isStreaming: false,
      searchEnabled: false,
      sidebarOpen: true,
      
      setConversations: (conversations) => set({ conversations }),
      setCurrentConversation: (id) => set({ currentConversationId: id, messages: [] }),
      setMessages: (messages) => set({ messages }),
      addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
      setStreaming: (streaming) => set({ isStreaming: streaming }),
      toggleSearch: () => set((state) => ({ searchEnabled: !state.searchEnabled })),
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      reset: () => set({
        conversations: [],
        currentConversationId: null,
        messages: [],
        isStreaming: false,
        searchEnabled: false,
      }),
    }),
    {
      name: "aletheia-chat-store",
      partialize: (state) => ({
        sidebarOpen: state.sidebarOpen,
        searchEnabled: state.searchEnabled,
      }),
    }
  )
);
