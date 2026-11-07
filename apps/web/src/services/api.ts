export type Profile = {
  id: string;
  name: string;
  email: string;
  time_zone: string;
  theme: "light" | "dark" | "system";
  created_at: string;
};
export class ApiError extends Error {
  constructor(
    public status: number,
    message: string,
    public fields: string[] = [],
  ) {
    super(message);
  }
}
const expired = () => window.dispatchEvent(new Event("auth-expired"));
export async function api<T>(
  path: string,
  init: RequestInit = {},
  authenticated = true,
): Promise<T> {
  const headers = new Headers(init.headers);
  const mutate = init.method && !["GET", "HEAD"].includes(init.method);
  if (mutate) headers.set("Content-Type", "application/json");
  try {
    if (mutate && authenticated) {
      const csrf = await fetch("/api/auth/csrf", {
        credentials: "same-origin",
        cache: "no-store",
      });
      if (csrf.status === 401) {
        expired();
        throw new ApiError(
          401,
          "Your session has expired. Please sign in again.",
        );
      }
      if (!csrf.ok)
        throw new ApiError(
          csrf.status,
          "Unable to verify your request. Please try again.",
        );
      headers.set("X-CSRF-Token", (await csrf.json()).csrf_token);
    }
    const response = await fetch(`/api${path}`, {
      ...init,
      headers,
      credentials: "same-origin",
      cache: "no-store",
    });
    if (!response.ok) {
      const body = await response.json().catch(() => ({}));
      if (response.status === 401 && authenticated) {
        const me = await fetch("/api/users/me", {
          credentials: "same-origin",
          cache: "no-store",
        });
        if (me.status === 401) expired();
      }
      const messages: Record<number, string> = {
        401: authenticated
          ? "Your current password is incorrect, or your session has expired."
          : "Email or password is incorrect.",
        403: "This request could not be verified. Refresh and try again.",
        404: "This item is unavailable or no longer belongs to your account.",
        409: path.startsWith("/categories")
          ? "A category with this name already exists."
          : path.startsWith("/tasks")
            ? "This change conflicts with the saved task. Refresh and try again."
            : "That email is already in use. Please choose another.",
        422: "Please check the highlighted fields.",
        429: "Too many attempts. Please wait a few minutes and try again.",
      };
      throw new ApiError(
        response.status,
        messages[response.status] ??
          "The service is unavailable. Please try again.",
        body.error?.fields ?? [],
      );
    }
    return response.status === 204
      ? (undefined as T)
      : ((await response.json()) as T);
  } catch (error) {
    if (error instanceof ApiError) throw error;
    throw new ApiError(
      0,
      "Unable to connect. Check your connection and try again.",
    );
  }
}
