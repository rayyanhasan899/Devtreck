"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { api, type Profile } from "@/services/api";

export function AppShell({
  profile,
  children,
}: {
  profile: Profile;
  children: React.ReactNode;
}) {
  const router = useRouter();
  const path = usePathname();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    document.documentElement.dataset.theme = profile.theme;
    const leave = () => {
      document.documentElement.removeAttribute("data-theme");
      router.replace("/login?reason=expired");
      router.refresh();
    };
    const check = () => {
      void api<Profile>("/users/me").catch(() => {});
    };
    window.addEventListener("auth-expired", leave);
    window.addEventListener("focus", check);
    const timer = setInterval(check, 60000);
    check();
    return () => {
      window.removeEventListener("auth-expired", leave);
      window.removeEventListener("focus", check);
      clearInterval(timer);
    };
  }, [profile.theme, router, path]);
  async function logout() {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      await api("/auth/logout", { method: "POST" });
      document.documentElement.removeAttribute("data-theme");
      router.replace("/login");
      router.refresh();
    } catch {
      setError("Could not sign out. Please try again.");
      setBusy(false);
    }
  }
  return (
    <div className="workspace">
      <aside className="sidebar">
        <Link href="/app" className="brand">
          <span className="brand-mark" aria-hidden="true">
            d.
          </span>
          devtreck
        </Link>
        <p className="nav-caption">YOUR WORKSPACE</p>
        <nav aria-label="Main navigation">
          <Link href="/app" aria-current={path === "/app" ? "page" : undefined}>
            Today
          </Link>
          <Link
            href="/app/tasks"
            aria-current={path === "/app/tasks" ? "page" : undefined}
          >
            All tasks
          </Link>
          <Link
            href="/app/daily"
            aria-current={path === "/app/daily" ? "page" : undefined}
          >
            Daily habits
          </Link>
          <Link
            href="/app/settings"
            aria-current={path === "/app/settings" ? "page" : undefined}
          >
            Settings
          </Link>
        </nav>
        <div className="sidebar-bottom">
          <p>{profile.name}</p>
          <button className="secondary" onClick={logout} disabled={busy}>
            {busy ? "Signing out…" : "Sign out"}
          </button>
          {error && <p role="alert">{error}</p>}
        </div>
      </aside>
      <div className="workspace-body">
        <header className="workspace-header">
          <span>YOUR PERSONAL SPACE</span>
          <span>{profile.time_zone}</span>
        </header>
        {children}
      </div>
    </div>
  );
}
