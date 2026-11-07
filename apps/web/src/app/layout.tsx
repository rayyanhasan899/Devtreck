import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Devtreck — Make room for meaningful work",
  description: "A calmer place for tasks, daily habits, and focused work. Devtreck is in development.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><a className="skip-link" href="#main">Skip to content</a>{children}</body></html>;
}
