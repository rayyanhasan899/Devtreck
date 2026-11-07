import "server-only";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import type { Profile } from "./api";

export async function requireProfile(): Promise<Profile> {
  const token = (await cookies()).get("devtreck_session")?.value;
  if (!token) redirect("/login?reason=protected");
  const response = await fetch(
    `${process.env.API_ORIGIN ?? "http://127.0.0.1:8002"}/api/users/me`,
    { headers: { Cookie: `devtreck_session=${token}` }, cache: "no-store" },
  );
  if (response.status === 401) redirect("/login?reason=expired");
  if (!response.ok) throw new Error("Account service unavailable");
  return response.json() as Promise<Profile>;
}
