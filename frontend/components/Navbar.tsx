"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken, getUser } from "@/lib/api";

const links = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/analyze", label: "Analyze" },
  { href: "/history", label: "History" },
];

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const user = getUser();

  function logout() {
    clearToken();
    router.push("/login");
  }

  return (
    <nav className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-5xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link href="/dashboard" className="font-bold text-lg text-emerald-400">
          PumpShield AI
        </Link>
        <div className="flex items-center gap-6">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className={`text-sm ${pathname === l.href ? "text-white font-medium" : "text-gray-400 hover:text-white"}`}
            >
              {l.label}
            </Link>
          ))}
          {user && (
            <span className="text-sm text-gray-500 hidden sm:inline">{user.name}</span>
          )}
          <button onClick={logout} className="text-sm text-gray-400 hover:text-red-400">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
