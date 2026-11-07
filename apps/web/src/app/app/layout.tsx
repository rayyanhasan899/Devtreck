import { AppShell } from "@/components/app-shell";
import { requireProfile } from "@/services/server-profile";
export default async function Layout({
  children,
}: {
  children: React.ReactNode;
}) {
  const profile = await requireProfile();
  return <AppShell profile={profile}>{children}</AppShell>;
}
