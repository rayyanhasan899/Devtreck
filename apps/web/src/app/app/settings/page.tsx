import { Settings } from "@/components/settings";
import { requireProfile } from "@/services/server-profile";
export default async function Page() {
  return <Settings profile={await requireProfile()} />;
}
