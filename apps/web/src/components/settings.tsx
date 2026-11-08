"use client";
import {
  Children,
  isValidElement,
  cloneElement,
  type ReactElement,
  createContext,
  useContext,
  useRef,
  useState,
} from "react";
import { useRouter } from "next/navigation";
import { api, ApiError, type Profile } from "@/services/api";

const ErrorContext = createContext<ApiError | null>(null);
function Field({
  label,
  name,
  type = "text",
  hint,
  defaultValue,
  minLength,
  children,
}: {
  label: string;
  name: string;
  type?: string;
  hint?: string;
  defaultValue?: string;
  minLength?: number;
  children?: React.ReactNode;
}) {
  const error = useContext(ErrorContext);
  const invalid = error?.fields.some((field) =>
    field.split(".").includes(name),
  );
  return (
    <label>
      {label}
      {children ? (
        Children.map(children, (child) =>
          isValidElement(child) &&
          (child.type === "input" || child.type === "select")
            ? cloneElement(child as ReactElement<Record<string, unknown>>, {
                "aria-label": label,
                "aria-invalid": !!invalid,
                "aria-describedby": `${name}-hint`,
              })
            : child,
        )
      ) : (
        <input
          aria-label={label}
          name={name}
          type={type}
          defaultValue={defaultValue}
          required
          minLength={minLength}
          maxLength={name === "name" ? 120 : name === "email" ? 320 : 128}
          autoComplete={
            type === "password"
              ? name === "new_password"
                ? "new-password"
                : "current-password"
              : name
          }
          aria-invalid={invalid}
          aria-describedby={`${name}-hint`}
        />
      )}
      <small id={`${name}-hint`}>
        {invalid ? "Please check this value. " : ""}
        {hint}
      </small>
    </label>
  );
}
function AccountForm({
  action,
  label,
  children,
}: {
  action: (data: FormData) => Promise<void>;
  label: string;
  children: React.ReactNode;
}) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<ApiError | null>(null);
  const [success, setSuccess] = useState(false);
  const guard = useRef(false);
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (guard.current) return;
    guard.current = true;
    setBusy(true);
    setError(null);
    setSuccess(false);
    try {
      await action(new FormData(event.currentTarget));
      setSuccess(true);
    } catch (e) {
      const err = e as ApiError;
      if (err.status === 401) err.fields.push("current_password");
      setError(err);
    } finally {
      guard.current = false;
      setBusy(false);
    }
  }
  return (
    <ErrorContext.Provider value={error}>
      <form onSubmit={submit} aria-busy={busy}>
        <fieldset disabled={busy}>
          {children}
          <button className="primary" disabled={busy}>
            {busy ? "Saving…" : label}
          </button>
        </fieldset>
        {error && (
          <p className="notice error" role="alert">
            {error.message}
          </p>
        )}
        {success && (
          <p className="notice success" role="status">
            Changes saved.
          </p>
        )}
      </form>
    </ErrorContext.Provider>
  );
}

export function Settings({ profile }: { profile: Profile }) {
  const router = useRouter();
  const dialog = useRef<HTMLDialogElement>(null);
  const [zone, setZone] = useState(profile.time_zone);
  const [suggestion, setSuggestion] = useState("");
  const [zones] = useState(() => [
    "UTC",
    ...Intl.supportedValuesOf("timeZone"),
  ]);
  const leave = (reason: string) => {
    document.documentElement.removeAttribute("data-theme");
    router.replace(`/login?reason=${reason}`);
    router.refresh();
  };
  return (
    <main id="main" className="workspace-main">
      <p className="eyebrow">MAKE THIS SPACE YOURS</p>
      <h1>Account settings</h1>
      <p className="intro">A few details to keep your day in rhythm.</p>
      <div className="settings-grid">
        <section className="settings-card">
          <h2>Profile & preferences</h2>
          <p className="muted">
            Choose how your account looks and how your day is counted.
          </p>
          <AccountForm
            label="Save preferences"
            action={async (data) => {
              const updated = await api<Profile>("/users/me", {
                method: "PATCH",
                body: JSON.stringify({
                  name: data.get("name"),
                  time_zone: data.get("time_zone"),
                  theme: data.get("theme"),
                }),
              });
              document.documentElement.dataset.theme = updated.theme;
              router.refresh();
            }}
          >
            <Field name="name" label="Your name" defaultValue={profile.name} />
            <Field
              name="time_zone"
              label="Time zone"
              hint="Changing your zone changes future day boundaries. Historical completion dates stay unchanged."
            >
              <input
                name="time_zone"
                list="time-zones"
                value={zone}
                onChange={(e) => setZone(e.target.value)}
                required
                maxLength={100}
                aria-describedby="time_zone-hint"
              />
              <datalist id="time-zones">
                {zones.map((zone) => (
                  <option key={zone} value={zone} />
                ))}
              </datalist>
            </Field>
            <button
              type="button"
              className="text-button"
              onClick={() => {
                const detected =
                  Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
                setZone(detected);
                setSuggestion(
                  `Suggested time zone: ${detected}. Save preferences to confirm.`,
                );
              }}
            >
              Use device time zone
            </button>
            {suggestion && <small role="status">{suggestion}</small>}
            <Field name="theme" label="Appearance">
              <select name="theme" defaultValue={profile.theme}>
                <option value="system">Match your device</option>
                <option value="light">Light</option>
                <option value="dark">Dark</option>
              </select>
            </Field>
          </AccountForm>
        </section>
        <div className="settings-stack">
          <section className="settings-card">
            <h2>Email address</h2>
            <p className="muted">
              Changing email signs you out on every device.
            </p>
            <AccountForm
              label="Update email"
              action={async (data) => {
                await api("/users/me", {
                  method: "PATCH",
                  body: JSON.stringify({
                    email: data.get("email"),
                    current_password: data.get("email_password"),
                  }),
                });
                leave("updated");
              }}
            >
              <Field
                name="email"
                type="email"
                label="Email address"
                defaultValue={profile.email}
              />
              <label>
                Current password for email change
                <input
                  name="email_password"
                  type="password"
                  required
                  maxLength={128}
                  autoComplete="current-password"
                />
              </label>
            </AccountForm>
          </section>
          <section className="settings-card">
            <h2>Password</h2>
            <p className="muted">
              Changing your password signs you out on every device.
            </p>
            <AccountForm
              label="Change password"
              action={async (data) => {
                await api("/users/me/password", {
                  method: "PATCH",
                  body: JSON.stringify({
                    current_password: data.get("current_password"),
                    new_password: data.get("new_password"),
                  }),
                });
                leave("updated");
              }}
            >
              <Field
                name="current_password"
                type="password"
                label="Current password"
              />
              <Field
                name="new_password"
                type="password"
                label="New password"
                minLength={8}
                hint="Use 8–128 characters. Spaces and passphrases are welcome."
              />
            </AccountForm>
          </section>
        </div>
      </div>
      <section className="settings-card danger-zone">
        <h2>Delete account</h2>
        <p>
          Deleting your account permanently removes your profile, tasks,
          completion history, and other account data. This cannot be undone.
        </p>
        <button className="danger" onClick={() => dialog.current?.showModal()}>
          Delete my account
        </button>
      </section>
      <dialog ref={dialog} aria-labelledby="delete-title">
        <h2 id="delete-title">Permanently delete account?</h2>
        <p>
          Your account and associated data will be removed. There is no
          recovery.
        </p>
        <AccountForm
          label="Permanently delete account"
          action={async (data) => {
            await api("/users/me", {
              method: "DELETE",
              body: JSON.stringify({
                current_password: data.get("delete_password"),
                confirm: true,
              }),
            });
            dialog.current?.close();
            leave("deleted");
          }}
        >
          <label>
            Confirm your current password
            <input
              name="delete_password"
              type="password"
              required
              maxLength={128}
              autoComplete="current-password"
            />
          </label>
          <label className="checkbox">
            <input type="checkbox" required />I understand this permanently
            deletes my account and data.
          </label>
          <button
            className="secondary"
            type="button"
            onClick={() => dialog.current?.close()}
          >
            Keep my account
          </button>
        </AccountForm>
      </dialog>
    </main>
  );
}
