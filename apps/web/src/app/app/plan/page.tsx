import { DailyPlan } from "@/features/tasks/plan";
export default function Page() {
  return (
    <main id="main" className="workspace-main">
      <p className="eyebrow">A LITTLE INTENTION GOES A LONG WAY</p>
      <h1>Plan your day</h1>
      <DailyPlan />
    </main>
  );
}
