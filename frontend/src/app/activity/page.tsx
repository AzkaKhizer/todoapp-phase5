"use client";

import { Header } from "@/components/layout/Header";
import { ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { ActivityLog } from "@/components/ActivityLog";
import { AuthProvider } from "@/contexts/AuthContext";

function ActivityContent() {
  return (
    <div className="min-h-screen bg-gradient-radial noise">
      <Header />

      <main className="max-w-4xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div className="mb-8 animate-slide-up">
          <h1 className="text-2xl font-bold text-gradient mb-2">Activity & Productivity</h1>
          <p className="text-[var(--text-muted)]">
            Track your task completion history and productivity metrics
          </p>
        </div>

        <div className="animate-slide-up delay-100">
          <ActivityLog showProductivity={true} limit={50} />
        </div>
      </main>
    </div>
  );
}

export default function ActivityPage() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <ActivityContent />
      </ProtectedRoute>
    </AuthProvider>
  );
}
