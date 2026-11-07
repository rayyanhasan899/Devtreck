"use client";
import { useEffect, useRef, useState } from "react";
import { api } from "@/services/api";

type Period = {
  start: string;
  end: string;
  completed: number;
  eligible: number;
  eligible_completed: number;
  covered_days: number;
  days: number;
  completion_rate: number | null;
  focus_seconds: number;
  focus_sessions: number;
};
type Report = {
  time_zone: string;
  xp: number;
  level: number;
  level_progress: number;
  next_level_xp: number;
  today: Period;
  week: Period;
  current_streak: number;
  best_streak: number;
  daily_completions: number;
  rules: {
    task_xp: number;
    daily_xp: number;
    focus_xp: number;
    focus_min_seconds: number;
    focus_daily_cap: number;
  };
  badges: {
    key: string;
    name: string;
    reason: string;
    earned_at: string | null;
  }[];
  trends: { day: string; completed: number; focus_seconds: number }[];
  categories: { name: string; completed: number }[];
};
const minutes = (seconds: number) => `${Math.floor(seconds / 60)} min`;

function Summary({ label, period }: { label: string; period: Period }) {
  return (
    <section className="progress-card" aria-label={label}>
      <h2>{label}</h2>
      <p>
        {period.start} through {period.end}, inclusive
      </p>
      <dl className="progress-numbers">
        <div>
          <dt>Task occurrences completed</dt>
          <dd>{period.completed}</dd>
        </div>
        <div>
          <dt>Completion rate</dt>
          <dd>
            {period.completion_rate === null
              ? "Unavailable"
              : `${Math.round(period.completion_rate * 100)}%`}
          </dd>
        </div>
        <div>
          <dt>Recorded focus time</dt>
          <dd>{minutes(period.focus_seconds)}</dd>
        </div>
        <div>
          <dt>Focus sessions started</dt>
          <dd>{period.focus_sessions}</dd>
        </div>
      </dl>
      <p>
        {period.eligible_completed} completed eligible occurrences /{" "}
        {period.eligible} eligible occurrences. Tracking covers{" "}
        {period.covered_days} of {period.days} dates.
      </p>
    </section>
  );
}

export function Progress() {
  const [data, setData] = useState<Report | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const sequence = useRef(0);
  async function load() {
    const current = ++sequence.current;
    setLoading(true);
    try {
      const report = await api<Report>("/progress");
      if (current === sequence.current) {
        setData(report);
        setError("");
      }
    } catch {
      if (current === sequence.current)
        setError("Could not load progress. Please retry.");
    } finally {
      if (current === sequence.current) setLoading(false);
    }
  }
  useEffect(() => {
    const requests = sequence;
    const initial = setTimeout(() => void load(), 0);
    const refresh = () => {
      void load();
    };
    window.addEventListener("focus", refresh);
    const timer = setInterval(refresh, 60000);
    return () => {
      ++requests.current;
      clearTimeout(initial);
      clearInterval(timer);
      window.removeEventListener("focus", refresh);
    };
  }, []);
  return (
    <main id="main" tabIndex={-1} className="workspace-main progress-page">
      <header className="dialog-heading">
        <div>
          <p className="eyebrow">YOUR MOMENTUM</p>
          <h1>Progress</h1>
          <p>Small steps, recorded honestly.</p>
        </div>
        <button
          className="secondary"
          disabled={loading}
          onClick={() => void load()}
        >
          Refresh progress
        </button>
      </header>
      {loading && <p role="status">Loading progress…</p>}
      {error && <p role="alert">{error}</p>}
      {data && (
        <>
          <p>
            Calendar dates use {data.time_zone}. Daily check-ins retain their
            original qualifying date.
          </p>
          <section
            className="progress-card level-card"
            aria-label="Experience and level"
          >
            <div>
              <p className="eyebrow">EXPERIENCE</p>
              <h2>Level {data.level}</h2>
              <p>
                <strong>{data.xp} XP</strong> earned ·{" "}
                {data.next_level_xp - data.xp} XP to level {data.level + 1}
              </p>
            </div>
            <progress
              aria-label="Progress to next level"
              max={100}
              value={data.level_progress}
            />
            <p>{data.level_progress} of 100 XP toward your next level</p>
          </section>
          <div className="progress-grid">
            <Summary label="Today" period={data.today} />
            <Summary label="Last 7 local dates" period={data.week} />
          </div>
          <details className="progress-card">
            <summary>How rewards and completion rates work</summary>
            <p>
              First-ever one-time completion: {data.rules.task_xp} XP. Qualified
              daily date: {data.rules.daily_xp} XP. Completed focus session with
              at least {data.rules.focus_min_seconds / 60} active minutes:{" "}
              {data.rules.focus_xp} XP, up to {data.rules.focus_daily_cap}{" "}
              rewards per local completion date. Level = 1 + whole hundreds of
              XP.
            </p>
            <p>
              Repeating requests or reopening a task never grants another reward
              for the same completion. Existing valid history is credited
              automatically. Rewards are personal feedback; prioritize
              meaningful work over point totals.
            </p>
            <p>
              Eligible occurrences are due one-time tasks and active daily
              dates. A one-time due occurrence is frozen when first observed
              due; daily dates are saved before schedule changes. Subtasks do
              not count. Rates require a nonzero denominator and every date
              tracked in the current time zone; earlier missing schedules are
              unavailable. Overdue work belongs to its due date, while
              completion activity belongs to its recorded date.
            </p>
            <p>
              Deleted task history is excluded from insights, including
              associated focus sessions. Earned XP and badges remain until
              account deletion. Category totals use current categories. Focus
              time excludes pauses and breaks; session counts include active,
              stopped and completed focus sessions started in the period.
              Minutes round down; daily table values preserve seconds.
            </p>
          </details>
          <section className="progress-card">
            <h2>Habit consistency</h2>
            <dl className="progress-numbers">
              <div>
                <dt>Current streak</dt>
                <dd>{data.current_streak} days</dd>
              </div>
              <div>
                <dt>Best streak</dt>
                <dd>{data.best_streak} days</dd>
              </div>
              <div>
                <dt>Daily completions</dt>
                <dd>{data.daily_completions}</dd>
              </div>
            </dl>
            <p>
              Longest streak among your current daily tasks; prior activation
              epochs cannot bridge a streak.
            </p>
          </section>
          <section aria-label="Achievements">
            <h2>Achievements</h2>
            <div className="progress-grid">
              {data.badges.map((badge) => (
                <article className="progress-card" key={badge.key}>
                  <h3>{badge.name}</h3>
                  <p>{badge.reason}</p>
                  <p>
                    {badge.earned_at
                      ? `Earned ${new Intl.DateTimeFormat("en", { dateStyle: "medium", timeStyle: "short", timeZone: data.time_zone }).format(new Date(badge.earned_at))}`
                      : "Not earned yet"}
                  </p>
                </article>
              ))}
            </div>
            <p>
              Backfilled badges show the date the server first verified the
              milestone.
            </p>
          </section>
          <section className="progress-card">
            <h2>Daily recorded activity</h2>
            <p>
              {data.week.completed === 0
                ? "No task completions recorded in this period."
                : "Recorded counts only; seven dates alone do not establish a long-term trend."}
            </p>
            <div className="progress-table-wrap">
              <table>
                <caption>Last seven dates · actual recorded activity</caption>
                <thead>
                  <tr>
                    <th scope="col">Local date</th>
                    <th scope="col">Completions</th>
                    <th scope="col">Focus seconds</th>
                  </tr>
                </thead>
                <tbody>
                  {data.trends.map((day) => (
                    <tr key={day.day}>
                      <th scope="row">{day.day}</th>
                      <td>
                        <span
                          className="activity-bar"
                          aria-hidden="true"
                          style={{
                            width: `${Math.min(100, day.completed * 10)}%`,
                          }}
                        />
                        {day.completed}
                      </td>
                      <td>{day.focus_seconds}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>
          <section className="progress-card">
            <h2>Completions by current category</h2>
            {data.categories.length ? (
              <ul>
                {data.categories.map((category) => (
                  <li key={category.name}>
                    {category.name}: <strong>{category.completed}</strong>
                  </li>
                ))}
              </ul>
            ) : (
              <p>No category activity recorded in the last seven dates.</p>
            )}
          </section>
        </>
      )}
    </main>
  );
}
