"use client";

import Link from "next/link";

import { LoginForm } from "@/components/forms/LoginForm";
import { AuthProvider } from "@/contexts/AuthContext";

export default function LoginPage() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gradient-radial noise relative overflow-hidden flex items-center justify-center p-6">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-gradient-glow rounded-full blur-3xl animate-pulse-slow" />
          <div className="absolute bottom-1/4 left-1/3 w-80 h-80 bg-gradient-glow rounded-full blur-3xl animate-pulse-slow delay-200" />
        </div>

        {/* Back to Home */}
        <Link
          href="/"
          className="absolute top-6 left-6 flex items-center gap-2 text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors z-20"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          <span className="text-sm font-medium">Back</span>
        </Link>

        {/* Card */}
        <div className="relative z-10 w-full max-w-md animate-scale-in">
          <div className="card-elevated rounded-2xl p-8">
            {/* Logo */}
            <div className="flex justify-center mb-8">
              <Link href="/" className="flex items-center gap-3 group">
                <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-[var(--accent-secondary)] to-[var(--accent-muted)] flex items-center justify-center transition-transform group-hover:scale-110">
                  <svg className="w-6 h-6 text-[var(--bg-primary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                  </svg>
                </div>
              </Link>
            </div>

            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold mb-2">Welcome back</h1>
              <p className="text-[var(--text-secondary)]">
                Sign in to continue to Taskflow
              </p>
            </div>

            {/* Form */}
            <LoginForm />

            {/* Divider */}
            <div className="relative my-8">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-[var(--glass-border)]" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-[var(--bg-secondary)] text-[var(--text-muted)]">
                  New to Taskflow?
                </span>
              </div>
            </div>

            {/* Register Link */}
            <Link
              href="/register"
              className="btn-ghost w-full text-center block"
            >
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </AuthProvider>
  );
}
