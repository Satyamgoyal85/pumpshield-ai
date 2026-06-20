"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getUser, getToken } from "@/lib/api";

export function useAuth(requireAuth = false) {
  const router = useRouter();
  const [user, setUserState] = useState<ReturnType<typeof getUser>>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = getToken();
    const u = getUser();
    if (requireAuth && !token) {
      router.replace("/login");
    } else {
      setUserState(u);
    }
    setLoading(false);
  }, [requireAuth, router]);

  return { user, loading };
}
