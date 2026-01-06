"use client";

import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-radial noise relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-glow rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-gradient-glow rounded-full blur-3xl animate-pulse-slow delay-200" />

        {/* Floating geometric shapes */}
        <div className="absolute top-20 right-20 w-2 h-2 bg-[var(--accent-primary)] rounded-full animate-float opacity-60" />
        <div className="absolute top-40 left-32 w-3 h-3 bg-[var(--accent-secondary)] rounded-full animate-float delay-300 opacity-40" />
        <div className="absolute bottom-32 left-20 w-2 h-2 bg-[var(--accent-muted)] rounded-full animate-float delay-500 opacity-50" />
        <div className="absolute bottom-40 right-40 w-4 h-4 border border-[var(--accent-primary)] rotate-45 animate-float delay-100 opacity-30" />
      </div>

      {/* Navigation */}
      <nav className="relative z-10 px-6 py-6 animate-fade-in">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent-secondary)] to-[var(--accent-muted)] flex items-center justify-center transition-transform group-hover:scale-110">
              <svg className="w-5 h-5 text-[var(--bg-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <span className="text-xl font-semibold tracking-tight">Taskflow</span>
          </Link>

          <div className="flex items-center gap-4">
            <Link href="/login" className="btn-ghost text-sm">
              Sign In
            </Link>
            <Link href="/register" className="btn-primary text-sm">
              <span>Get Started</span>
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 px-6 pt-20 pb-32">
        <div className="max-w-6xl mx-auto">
          <div className="max-w-3xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-8 animate-slide-up opacity-0">
              <span className="w-2 h-2 rounded-full bg-[var(--success)] animate-pulse" />
              <span className="text-sm text-[var(--text-secondary)]">Productivity reimagined</span>
            </div>

            {/* Headline */}
            <h1 className="text-5xl md:text-7xl font-bold leading-tight mb-6 animate-slide-up opacity-0 delay-100">
              Organize your work,
              <br />
              <span className="text-gradient glow-text">amplify your life</span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl text-[var(--text-secondary)] mb-10 max-w-xl mx-auto animate-slide-up opacity-0 delay-200">
              A beautifully crafted task manager that helps you focus on what matters most. Simple, elegant, powerful.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up opacity-0 delay-300">
              <Link href="/register" className="btn-primary text-lg px-8 py-4 w-full sm:w-auto">
                <span>Start for free</span>
              </Link>
              <Link href="/login" className="btn-ghost text-lg px-8 py-4 w-full sm:w-auto">
                I have an account
              </Link>
            </div>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6 mt-32">
            {[
              {
                icon: (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
                  </svg>
                ),
                title: "Lightning Fast",
                description: "Instant sync across all your devices. Your tasks, always up to date.",
              },
              {
                icon: (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                  </svg>
                ),
                title: "Secure by Design",
                description: "Your data is encrypted and protected. Privacy is not optional.",
              },
              {
                icon: (
                  <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M21 8.25c0-2.485-2.099-4.5-4.688-4.5-1.935 0-3.597 1.126-4.312 2.733-.715-1.607-2.377-2.733-4.313-2.733C5.1 3.75 3 5.765 3 8.25c0 7.22 9 12 9 12s9-4.78 9-12z" />
                  </svg>
                ),
                title: "Made with Care",
                description: "Every detail crafted for the best experience. Because you deserve it.",
              },
            ].map((feature, index) => (
              <div
                key={feature.title}
                className={`glass-card rounded-2xl p-8 hover:border-[var(--accent-primary)]/30 transition-all duration-300 hover:-translate-y-1 animate-slide-up opacity-0`}
                style={{ animationDelay: `${400 + index * 100}ms` }}
              >
                <div className="w-12 h-12 rounded-xl bg-[var(--bg-tertiary)] flex items-center justify-center mb-5 text-[var(--accent-primary)]">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="relative z-10 px-6 py-8 border-t border-[var(--glass-border)]">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-[var(--text-muted)]">
            2026 Taskflow. Crafted with precision.
          </p>
          <div className="flex items-center gap-6">
            <a href="#" className="text-sm text-[var(--text-muted)] hover:text-[var(--accent-primary)] transition-colors">
              Privacy
            </a>
            <a href="#" className="text-sm text-[var(--text-muted)] hover:text-[var(--accent-primary)] transition-colors">
              Terms
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
