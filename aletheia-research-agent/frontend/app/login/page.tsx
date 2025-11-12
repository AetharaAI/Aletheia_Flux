"use client";

import { useState } from "react";
import { supabase } from "@/lib/supabase";
import { useRouter } from "next/navigation";
import { LogIn, UserPlus } from "lucide-react";

export default function LoginPage() {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      if (isLogin) {
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });
        if (error) throw error;
      } else {
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
        });
        if (error) throw error;
      }
      router.push("/chat");
    } catch (error: any) {
      // Handle specific Supabase errors
      if (error.message?.includes("Email not confirmed")) {
        setError("Please check your email and click the confirmation link before logging in.");
      } else if (error.message?.includes("Invalid login credentials")) {
        setError("Invalid email or password. Please check your credentials and try again.");
      } else {
        setError(error.message || "An error occurred. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-bg-near-black flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-text-white mb-2">Aletheia</h1>
          <p className="text-text-tertiary">Truth-Seeking Research Agent</p>
        </div>

        {/* Auth Form */}
        <div className="bg-bg-pure-black border border-border-subtle rounded-lg p-8">
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setIsLogin(true)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md transition-colors ${
                isLogin
                  ? "bg-accent-primary text-white"
                  : "bg-bg-pure-black border border-border-subtle text-text-secondary hover:text-text-white"
              }`}
            >
              <LogIn size={18} />
              Login
            </button>
            <button
              onClick={() => setIsLogin(false)}
              className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md transition-colors ${
                !isLogin
                  ? "bg-accent-primary text-white"
                  : "bg-bg-pure-black border border-border-subtle text-text-secondary hover:text-text-white"
              }`}
            >
              <UserPlus size={18} />
              Sign Up
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 bg-bg-near-black border border-border-subtle rounded-md text-text-white focus:outline-none focus:ring-2 focus:ring-accent-primary"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 bg-bg-near-black border border-border-subtle rounded-md text-text-white focus:outline-none focus:ring-2 focus:ring-accent-primary"
                placeholder="••••••••"
                required
                minLength={6}
              />
            </div>

            {error && (
              <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-md">
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-accent-primary hover:bg-accent-hover disabled:opacity-50 text-white font-medium py-2 px-4 rounded-md transition-colors"
            >
              {loading ? "Please wait..." : isLogin ? "Login" : "Create Account"}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
