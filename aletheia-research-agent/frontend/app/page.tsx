"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { supabase } from "@/lib/supabase";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is logged in
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user) {
        router.push("/chat");
      } else {
        router.push("/login");
      }
    });
  }, [router]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-bg-near-black">
      <div className="text-text-white">Redirecting...</div>
    </div>
  );
}
