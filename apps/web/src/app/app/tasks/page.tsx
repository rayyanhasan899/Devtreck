import { TaskBoard } from "@/features/tasks/board";
import { requireProfile } from "@/services/server-profile";
export default async function Page() {
  const profile = await requireProfile();
  return (
    <TaskBoard initialView="all" zone={profile.time_zone} name={profile.name} />
  );
}
