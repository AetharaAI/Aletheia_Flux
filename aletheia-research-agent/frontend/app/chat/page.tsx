"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useChatStore } from "@/store/chatStore";
import { supabase } from "@/lib/supabase";
import { Send, Search, Menu, X, LogOut } from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [input, setInput] = useState("");
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const {
    messages,
    isStreaming,
    searchEnabled,
    sidebarOpen,
    conversations,
    currentConversationId,
    addMessage,
    setStreaming,
    toggleSearch,
    toggleSidebar,
    setConversations,
    setMessages,
    setCurrentConversation,
  } = useChatStore();

  useEffect(() => {
    // Check current session
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        setUser(session.user);
        setLoading(false);
        loadConversations(session);
      } else {
        setLoading(false);
        router.push("/login");
      }
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(
      (_event, session) => {
        if (session?.user) {
          setUser(session.user);
          loadConversations(session);
        } else {
          router.push("/login");
        }
      }
    );

    return () => subscription.unsubscribe();
  }, [router]);

  const loadConversations = async (session: any) => {
    try {
      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.access_token}`
      };

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat/conversations`, {
        headers,
      });

      if (response.ok) {
        const data = await response.json();
        setConversations(data.conversations || []);
      }
    } catch (error) {
      console.error("Error loading conversations:", error);
    }
  };

  const loadConversation = async (conversationId: string) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (!session) return;

      const headers: Record<string, string> = {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${session.access_token}`
      };

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat/conversations/${conversationId}`, {
        headers,
      });

      if (response.ok) {
        const data = await response.json();
        // Clear current messages and load new ones
        setMessages([]);
        setCurrentConversation(conversationId);
        // Add messages to local store
        data.messages?.forEach((msg: any) => {
          addMessage({
            id: msg.id,
            conversation_id: msg.conversation_id,
            role: msg.role,
            content: msg.content,
            thinking_trace: msg.thinking_trace || [],
            sources: msg.sources || [],
            timestamp: msg.timestamp,
          });
        });
      }
    } catch (error) {
      console.error("Error loading conversation:", error);
    }
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    router.push("/login");
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isStreaming) return;

    const userMessage = {
      id: crypto.randomUUID(),
      conversation_id: "default",
      role: "user" as const,
      content: input.trim(),
      timestamp: new Date().toISOString(),
    };

    addMessage(userMessage);
    const messageText = input.trim();
    setInput("");
    setStreaming(true);

    try {
      // Get Supabase session
      const { data: { session } } = await supabase.auth.getSession();

      const headers: Record<string, string> = {
        "Content-Type": "application/json",
      };

      if (session?.access_token) {
        headers["Authorization"] = `Bearer ${session.access_token}`;
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat/send`, {
        method: "POST",
        headers,
        body: JSON.stringify({
          message: messageText,
          enable_search: searchEnabled,
          conversation_id: currentConversationId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage = {
        id: crypto.randomUUID(),
        conversation_id: "default",
        role: "assistant" as const,
        content: data.response || data.message || "No response received",
        thinking_trace: data.thinking_trace || [],
        sources: data.sources || [],
        timestamp: new Date().toISOString(),
      };
      addMessage(assistantMessage);
    } catch (error) {
      console.error("Error calling API:", error);
      const errorMessage = {
        id: crypto.randomUUID(),
        conversation_id: "default",
        role: "assistant" as const,
        content: `Error: ${error instanceof Error ? error.message : "Failed to connect to backend"}\n\nBackend is running at: ${process.env.NEXT_PUBLIC_API_URL}`,
        thinking_trace: [],
        sources: [],
        timestamp: new Date().toISOString(),
      };
      addMessage(errorMessage);
    } finally {
      setStreaming(false);
      // Refresh conversations list to show new/updated conversation
      const { data: { session } } = await supabase.auth.getSession();
      if (session) {
        loadConversations(session);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex h-screen bg-bg-near-black items-center justify-center">
        <div className="text-text-white">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="flex h-screen bg-bg-near-black">
      {sidebarOpen && (
        <div className="w-64 bg-bg-pure-black border-r border-border-subtle flex flex-col">
          <div className="p-4 border-b border-border-subtle">
            <h1 className="text-xl font-semibold text-text-white">Aletheia</h1>
            <p className="text-sm text-text-tertiary">Research Agent</p>
          </div>
          <div className="flex-1 p-4 overflow-y-auto">
            <button
              onClick={() => {
                setMessages([]);
                setCurrentConversation(null);
              }}
              className="w-full px-4 py-2 bg-accent-primary hover:bg-accent-hover text-white rounded-md transition-colors mb-4"
            >
              New Chat
            </button>
            <div className="space-y-2">
              {conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => loadConversation(conv.id)}
                  className="w-full text-left p-3 bg-bg-hover hover:bg-bg-elevated rounded-md transition-colors"
                >
                  <div className="text-sm text-text-white font-medium truncate">{conv.title}</div>
                  <div className="text-xs text-text-tertiary mt-1">
                    {new Date(conv.updated_at).toLocaleDateString()}
                  </div>
                </button>
              ))}
            </div>
          </div>
          {user && (
            <div className="p-4 border-t border-border-subtle">
              <p className="text-sm text-text-secondary truncate mb-3">{user.email}</p>
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-3 py-2 text-sm text-text-secondary hover:text-text-white hover:bg-bg-elevated rounded-md transition-colors"
              >
                <LogOut size={16} />
                Logout
              </button>
            </div>
          )}
        </div>
      )}

      <div className="flex-1 flex flex-col">
        <div className="h-16 border-b border-border-subtle flex items-center px-6 bg-bg-near-black/90 backdrop-blur">
          <button onClick={toggleSidebar} className="p-2 hover:bg-bg-elevated rounded-md transition-colors mr-4">
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <h2 className="text-lg font-medium">Research Chat</h2>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <h2 className="text-2xl font-semibold text-text-white mb-4">Welcome to Aletheia</h2>
                <p className="text-text-secondary max-w-md mx-auto">
                  Your truth-seeking research assistant. Ask me anything, and I&apos;ll provide transparent, well-researched answers.
                </p>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div className={`max-w-[85%] rounded-lg p-4 ${
                      msg.role === "user" ? "bg-accent-primary text-white" : "bg-bg-elevated border border-border-subtle"
                    }`}>
                    <div className="markdown-content whitespace-pre-wrap">{msg.content}</div>
                    {msg.thinking_trace && msg.thinking_trace.length > 0 && (
                      <details className="mt-4 p-3 bg-bg-near-black rounded border-l-2 border-semantic-info">
                        <summary className="text-sm text-semantic-info cursor-pointer font-medium">
                          Show reasoning ({msg.thinking_trace.length} steps)
                        </summary>
                        <div className="mt-2 space-y-2 text-sm">
                          {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                          {msg.thinking_trace.map((step: any, idx: number) => (
                            <div key={idx} className="flex gap-2">
                              <span className="text-text-tertiary">{idx + 1}.</span>
                              <span className="text-text-secondary">{step.description}</span>
                            </div>
                          ))}
                        </div>
                      </details>
                    )}
                  </div>
                </div>
              ))
            )}
            {isStreaming && (
              <div className="flex justify-start">
                <div className="bg-bg-elevated border border-border-subtle rounded-lg p-4">
                  <div className="flex gap-2">
                    <div className="w-2 h-2 bg-accent-primary rounded-full animate-pulse" />
                    <div className="w-2 h-2 bg-accent-primary rounded-full animate-pulse delay-100" />
                    <div className="w-2 h-2 bg-accent-primary rounded-full animate-pulse delay-200" />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="border-t border-border-subtle bg-bg-elevated p-4">
          <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
            <div className="flex gap-2 items-end">
              <button
                type="button"
                onClick={toggleSearch}
                className={`p-3 rounded-md transition-all ${
                  searchEnabled ? "bg-accent-primary text-white shadow-glow-subtle" : "bg-bg-hover text-text-secondary hover:bg-bg-tooltip"
                }`}
                title="Toggle web search"
              >
                <Search size={20} />
              </button>
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
                placeholder="Ask me anything..."
                className="flex-1 bg-bg-hover border border-border-subtle rounded-md px-4 py-3 text-text-primary placeholder:text-text-tertiary focus:outline-none focus:border-accent-primary focus:shadow-glow-subtle transition-all resize-none"
                rows={1}
                disabled={isStreaming}
              />
              <button
                type="submit"
                disabled={!input.trim() || isStreaming}
                className="px-6 py-3 bg-accent-primary hover:bg-accent-hover disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-md transition-all hover:shadow-glow-accent"
              >
                <Send size={20} />
              </button>
            </div>
            {searchEnabled && (
              <p className="text-xs text-text-tertiary mt-2 text-center">
                Web search enabled - responses will include verified sources
              </p>
            )}
          </form>
        </div>
      </div>
    </div>
  );
}
