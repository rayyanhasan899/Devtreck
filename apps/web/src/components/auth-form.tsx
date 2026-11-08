"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef, useState } from "react";
import { api, ApiError } from "@/services/api";

export function AuthForm({ register = false }: { register?: boolean }) {
  const router = useRouter();
  const guard = useRef(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const invalid = (name: string) =>
    error?.fields.some((field) => field.split(".").includes(name)) || false;
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (guard.current) return;
    guard.current = true;
    setBusy(true);
    setError(null);
    const form = new FormData(event.currentTarget);
    try {
      const body = {
        email: String(form.get("email")).trim(),
        password: String(form.get("password")),
        ...(register ? { name: String(form.get("name")).trim() } : {}),
      };
      await api(
        register ? "/auth/register" : "/auth/login",
        { method: "POST", body: JSON.stringify(body) },
        false,
      );
      router.replace(register ? "/login?registered=true" : "/app");
      router.refresh();
    } catch (e) {
      setError(e as ApiError);
    } finally {
      guard.current = false;
      setBusy(false);
    }
  }
  return (
    <main id="main" className="auth-page">
      <div className="auth-aside">
        <Link href="/" className="brand">
          <span className="brand-mark" aria-hidden="true">
            d.
          </span>
          devtreck
        </Link>
        <p className="eyebrow">YOUR SPACE TO MOVE FORWARD</p>
        <h2 className="brand-pitch">
          Small steps.
          <br />
          <span>Steady progress.</span>
        </h2>
        <p>
          A calmer home for meaningful work. Start with a little clarity, one
          day at a time.
        </p>
      </div>
      <section className="auth-card" aria-labelledby="auth-title">
        <p className="eyebrow">
          {register ? "A FRESH START" : "GOOD TO SEE YOU"}
        </p>
        <h1 id="auth-title">
          {register ? "Create your account" : "Welcome back"}
        </h1>
        <p className="muted">
          {register
            ? "A personal space, built around your day."
            : "Sign in to your personal workspace."}
        </p>
        <form onSubmit={submit} aria-busy={busy}>
          {register && (
            <label>
              Your name
              <input
                name="name"
                aria-label="Your name"
                autoComplete="name"
                required
                maxLength={120}
                aria-invalid={invalid("name")}
              />
              {invalid("name") && (
                <small>Enter a name with 1–120 characters.</small>
              )}
            </label>
          )}
          <label>
            Email address
            <input
              type="email"
              name="email"
              aria-label="Email address"
              autoComplete="email"
              required
              maxLength={320}
              aria-invalid={invalid("email")}
            />
            {invalid("email") && <small>Enter a valid email address.</small>}
          </label>
          <label>
            Password
            <input
              type="password"
              name="password"
              aria-label="Password"
              autoComplete={register ? "new-password" : "current-password"}
              minLength={register ? 8 : undefined}
              maxLength={128}
              required
              aria-invalid={invalid("password")}
              aria-describedby={register ? "password-hint" : undefined}
            />
            {register && (
              <small id="password-hint">
                Use 8–128 characters. A memorable passphrase works well.
              </small>
            )}
          </label>
          {error && (
            <p className="notice error" role="alert">
              {error.message}
            </p>
          )}
          <button className="primary" disabled={busy}>
            {busy ? "Please wait…" : register ? "Create account" : "Sign in"}
          </button>
        </form>
        <p className="auth-switch">
          {register ? "Already have an account? " : "New to Devtreck? "}
          <Link href={register ? "/login" : "/signup"}>
            {register ? "Sign in" : "Create account"}
          </Link>
        </p>
        <Link href="/" className="muted">
          Back to home
        </Link>
      </section>
    </main>
  );
}
