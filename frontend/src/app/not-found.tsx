import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gradient-radial noise flex items-center justify-center p-6">
      <div className="glass-card p-8 rounded-2xl max-w-md w-full text-center animate-slide-up">
        <h1 className="text-6xl font-bold text-[var(--accent-primary)] mb-4">
          404
        </h1>
        <h2 className="text-xl font-semibold mb-2">Page Not Found</h2>
        <p className="text-[var(--text-muted)] mb-6">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
        </p>
        <Link
          href="/"
          className="inline-block px-6 py-3 bg-[var(--accent-primary)] text-white rounded-lg font-medium hover:bg-[var(--accent-primary)]/90 transition-colors"
        >
          Go Home
        </Link>
      </div>
    </div>
  );
}
