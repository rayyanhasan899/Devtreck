export type Streak = {
  current_streak: number;
  best_streak: number;
  today_completed: boolean;
  last_qualified_day: string | null;
  total_completions: number;
  current_day: string;
  time_zone: string;
};
export type Task = {
  id: string;
  title: string;
  description: string | null;
  status: "pending" | "in-progress" | "completed";
  task_type: "one-time" | "daily";
  priority: "low" | "medium" | "high";
  category_id: string | null;
  due_date: string | null;
  due_at: string | null;
  estimated_minutes: number | null;
  created_at: string;
  updated_at: string;
  streak: Streak | null;
};
export type Category = { id: string; name: string };
export type TaskPage = {
  items: Task[];
  total: number;
  limit: number;
  offset: number;
};
export type Summary = {
  today_actionable: number;
  outstanding: number;
  completions_today: number;
  daily_total: number;
  daily_done: number;
};
export type History = {
  id: string;
  completed_at: string;
  completion_day?: string;
  time_zone?: string;
};
export type View =
  "all" | "today" | "upcoming" | "overdue" | "daily" | "completed";
export function dateLabel(task: Task, zone: string) {
  return task.due_date
    ? new Intl.DateTimeFormat("en", {
        dateStyle: "medium",
        timeZone: "UTC",
      }).format(new Date(task.due_date + "T12:00:00Z"))
    : task.due_at
      ? new Intl.DateTimeFormat("en", {
          dateStyle: "medium",
          timeStyle: "short",
          timeZone: zone,
        }).format(new Date(task.due_at))
      : "No deadline";
}
