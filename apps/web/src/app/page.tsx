import Link from "next/link";

const pillars = [
  {
    number: "01",
    title: "Choose what matters",
    copy: "A clear home for your tasks, with a daily plan that leaves room to breathe.",
  },
  {
    number: "02",
    title: "Build a steady rhythm",
    copy: "Daily habits and honest streaks, built around your time zone and your day.",
  },
  {
    number: "03",
    title: "Give work your attention",
    copy: "Focused sessions and thoughtful progress insights to help you keep moving.",
  },
];

export default function Home() {
  return (
    <>
      <header className="site-header">
        <Link href="/" className="brand" aria-label="Devtreck home">
          <span className="brand-mark" aria-hidden="true">
            d.
          </span>
          devtreck
        </Link>
        <nav className="landing-nav" aria-label="Account navigation">
          <Link href="/login">Sign in</Link>
          <Link className="primary compact" href="/signup">
            Create account
          </Link>
        </nav>
      </header>
      <main id="main">
        <section className="hero" aria-labelledby="hero-title">
          <div>
            <p className="eyebrow">A LITTLE CLARITY. EVERY DAY.</p>
            <h1 id="hero-title">
              Make room for
              <br />
              <span>meaningful work.</span>
            </h1>
            <p className="intro">
              Less scattered. More intentional. A calmer place for your tasks,
              daily habits, and focused work.
            </p>
            <a className="button" href="#approach">
              Explore the approach <span aria-hidden="true">↗</span>
            </a>
            <p className="availability">
              We’re building the foundations. Your account is ready. Task
              screens are coming next.
            </p>
          </div>
          <aside className="manifesto" aria-label="Our guiding principle">
            <span className="card-kicker">THE DEVTRECK WAY</span>
            <div className="orbit" aria-hidden="true">
              <span>✓</span>
            </div>
            <h2>
              Small steps.
              <br />A steady direction.
            </h2>
            <p>
              You don’t need to do everything today.
              <br />
              Just make space for what matters.
            </p>
            <div className="card-footer">
              <span className="dot" aria-hidden="true" /> Progress, at your pace
            </div>
          </aside>
        </section>
        <section
          id="approach"
          className="approach"
          aria-labelledby="approach-title"
        >
          <div className="section-heading">
            <p className="eyebrow">DESIGNED FOR REAL DAYS</p>
            <h2 id="approach-title">Find your rhythm.</h2>
          </div>
          <div className="pillars">
            {pillars.map((item) => (
              <article key={item.number}>
                <span className="item-number">{item.number}</span>
                <h3>{item.title}</h3>
                <p>{item.copy}</p>
                <span className="planned">Planned capability</span>
              </article>
            ))}
          </div>
        </section>
      </main>
      <footer>
        <span>devtreck</span>
        <p>A thoughtful start. Built one phase at a time.</p>
        <a href="#main">Back to top ↑</a>
      </footer>
    </>
  );
}
