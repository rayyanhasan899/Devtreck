import Link from "next/link";
import { requireProfile } from "@/services/server-profile";
export default async function Overview() {
  const profile = await requireProfile();
  return (
    <main id="main" className="workspace-main">
      <p className="eyebrow">A LITTLE CLARITY. EVERY DAY.</p>
      <h1>Welcome, {profile.name.split(" ")[0]}.</h1>
      <p className="intro">
        Your personal workspace is taking shape. Make yourself at home.
      </p>
      <section className="settings-card">
        <h2>Your account, your rhythm.</h2>
        <p>
          Keep your details up to date, choose your time zone, and make this
          space feel like yours.
        </p>
        <Link href="/app/settings" className="button">
          Manage your settings ↗
        </Link>
        <dl className="account-facts">
          <div>
            <dt>Email address</dt>
            <dd>{profile.email}</dd>
          </div>
          <div>
            <dt>Time zone</dt>
            <dd>{profile.time_zone}</dd>
          </div>
          <div>
            <dt>Member since</dt>
            <dd>
              {new Intl.DateTimeFormat("en", {
                dateStyle: "medium",
                timeZone: profile.time_zone,
              }).format(new Date(profile.created_at))}
            </dd>
          </div>
        </dl>
      </section>
      <section className="development-note">
        <h2>More room to focus, soon.</h2>
        <p>
          Task lists, daily habits, and progress screens will arrive in the next
          stages. Your account settings are ready to use now.
        </p>
      </section>
    </main>
  );
}
