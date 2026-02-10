'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { setSession, signIn, signUp } from '@/lib/auth';

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isSignUp, isSetSignUp] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Email and password are required');
      return;
    }
    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    setLoading(true);
    setError('');

    try {
      const data = isSignUp ? await signUp(email, password) : await signIn(email, password);
      const session = data.session || { token: data.token, user: { email, id: email } };
      await setSession(session);
      setToast({ type: 'success', message: isSignUp ? 'Account created — redirecting...' : 'Signed in — redirecting...' });
      setTimeout(() => router.push('/todos'), 700);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'An error occurred';
      setError(message);
      setToast({ type: 'error', message });
      console.error('Auth error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Toast state
  const [toast, setToast] = useState<{ type: 'error' | 'success'; message: string } | null>(null);
  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 3500);
    return () => clearTimeout(t);
  }, [toast]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4 relative overflow-hidden">
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-cyan-500 opacity-10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500 opacity-10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1.5s' }}></div>
      </div>

      <div className="w-full max-w-md relative z-10">
        <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl shadow-2xl overflow-hidden border border-slate-700 backdrop-blur-sm">
          {/* Header */}
          <div className="bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 px-8 py-12 text-center">
            <h1 className="text-5xl font-black text-white mb-2">📝</h1>
            <h2 className="text-3xl font-bold text-white mb-3">Task Master Pro</h2>
            <p className="text-slate-100 text-sm">{isSignUp ? 'Join thousands of productive users' : 'Welcome back!'}</p>
          </div>

          {/* Form */}
          <div className="px-8 py-8">
            {/* Toast */}
            {toast && (
              <div className={`mb-6 p-4 rounded-lg border ${
                toast.type === 'success' 
                  ? 'bg-green-500/20 border-green-500/50 text-green-300' 
                  : 'bg-red-500/20 border-red-500/50 text-red-300'
              }`}>
                <p className="text-sm font-medium">{toast.message}</p>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="mb-6 p-4 rounded-lg bg-red-500/20 border border-red-500/50">
                <p className="text-red-300 text-sm font-medium">❌ {error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email Input */}
              <div>
                <label className="block text-slate-300 text-sm font-semibold mb-2">Email Address</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                />
              </div>

              {/* Password Input */}
              <div>
                <label className="block text-slate-300 text-sm font-semibold mb-2">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-4 py-3 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition"
                />
                <p className="text-xs text-slate-400 mt-1">Minimum 6 characters</p>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 disabled:from-slate-500 disabled:to-slate-500 text-black font-bold py-3 rounded-lg transition duration-300 mt-6 shadow-lg shadow-purple-500/30"
              >
                {loading ? '⏳ Processing...' : (isSignUp ? '🚀 Create Account' : '🔓 Sign In')}
              </button>
            </form>

            {/* Toggle Sign Up / Sign In */}
            <div className="mt-6 text-center">
              <p className="text-slate-400 text-sm">
                {isSignUp ? 'Already have an account?' : "Don't have an account?"}
                <button
                  type="button"
                  onClick={() => {
                    isSetSignUp(!isSignUp);
                    setError('');
                  }}
                  className="text-cyan-400 hover:text-cyan-300 font-semibold ml-1 transition"
                >
                  {isSignUp ? 'Sign In' : 'Sign Up'}
                </button>
              </p>
            </div>
          </div>

          {/* Footer Info */}
          <div className="bg-slate-900/50 px-8 py-6 border-t border-slate-700">
            <div className="space-y-3 text-sm text-slate-400">
              <div className="flex gap-2">
                <span>✓</span>
                <p>Zero setup required</p>
              </div>
              <div className="flex gap-2">
                <span>🔐</span>
                <p>Your data is encrypted and secure</p>
              </div>
              <div className="flex gap-2">
                <span>⚡</span>
                <p>Start organizing tasks instantly</p>
              </div>
            </div>
          </div>
        </div>

        {/* Additional Info */}
        <div className="mt-8 text-center text-slate-400 text-xs">
          <p>By signing in, you agree to our Terms of Service</p>
        </div>
      </div>
    </div>
  );
}
