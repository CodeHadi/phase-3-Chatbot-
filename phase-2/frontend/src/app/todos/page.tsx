'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { getSession, clearSession, signOut } from '@/lib/auth';

interface Task {
  id?: number;
  title: string;
  description?: string;
  completed: boolean;
  user_id?: string;
  created_at?: string;
  updated_at?: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function TodosPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [session, setSessionState] = useState<any>(null);
  const [logoutLoading, setLogoutLoading] = useState(false);
  const [toast, setToast] = useState<{ type: 'error' | 'success'; message: string } | null>(null);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 3500);
    return () => clearTimeout(t);
  }, [toast]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const currentSession = await getSession();
        
        // Redirect to login if no session
        if (!currentSession?.token) {
          router.push('/login');
          return;
        }
        
        setSessionState(currentSession);

        // Get auth headers
        const headers: any = {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${currentSession.token}`,
        };

        const response = await fetch(`${API_URL}/api/tasks`, { headers });

        if (response.status === 401) {
          await clearSession();
          router.push('/login');
          return;
        }
        
        if (!response.ok) {
          throw new Error('Failed to fetch tasks');
        }

        const data = await response.json();
        setTasks(Array.isArray(data) ? data : []);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [router]);

  const getAuthHeaders = async () => {
    const currentSession = await getSession();
    const headers: any = {
      "Content-Type": "application/json",
    };
    if (currentSession?.token) {
      headers["Authorization"] = `Bearer ${currentSession.token}`;
    }
    return headers;
  };

  const handleAddTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTaskTitle.trim()) return;

    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${API_URL}/api/tasks`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ title: newTaskTitle, description: '' }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to create task');
      }

      const newTask = await response.json();
      setTasks([...tasks, newTask]);
      setNewTaskTitle('');
      setError('');
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to add task';
      setError(message);
      console.error('Task creation error:', err);
    }
  };

  const handleToggleTask = async (id: number | undefined, completed: boolean) => {
    if (!id) return;
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${API_URL}/api/tasks/${id}`, {
        method: 'PUT',
        headers,
        body: JSON.stringify({ completed: !completed }),
      });

      if (!response.ok) {
        throw new Error('Failed to update task');
      }

      setTasks(
        tasks.map((task) =>
          task.id === id ? { ...task, completed: !completed } : task
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  const handleDeleteTask = async (id: number | undefined) => {
    if (!id) return;
    try {
      const headers = await getAuthHeaders();
      const response = await fetch(`${API_URL}/api/tasks/${id}`, {
        method: 'DELETE',
        headers,
      });

      if (!response.ok) {
        throw new Error('Failed to delete task');
      }

      setTasks(tasks.filter((task) => task.id !== id));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  const handleLogout = async () => {
    setLogoutLoading(true);
    try {
      await signOut();
      setToast({ type: 'success', message: 'Signed out' });
    } catch (err) {
      console.error('Logout error:', err);
      await clearSession();
      setToast({ type: 'error', message: err instanceof Error ? err.message : 'Logout failed' });
    } finally {
      setLogoutLoading(false);
      router.push('/login');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-4">
              <div className="text-5xl">📝</div>
              <div>
                <h1 className="text-5xl font-black bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
                  Task Master Pro
                </h1>
                <p className="text-slate-400">Organize, prioritize, and achieve</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right bg-slate-800 rounded-lg p-3 border border-slate-700">
                <p className="text-sm font-semibold text-white">{session?.user?.email || 'User'}</p>
                <p className="text-xs text-gray-400">🟢 Online</p>
              </div>
              <button
                onClick={handleLogout}
                disabled={logoutLoading}
                className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600 disabled:from-red-400 disabled:to-red-500 text-white px-6 py-3 rounded-lg transition font-semibold text-sm shadow-lg"
              >
                {logoutLoading ? '⏳ Signing out...' : '🚪 Logout'}
              </button>
            </div>
          </div>

          {/* Stats Dashboard */}
          {tasks.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-600 to-blue-700 rounded-xl p-4 border border-blue-500/30 shadow-lg">
                <p className="text-blue-100 text-sm font-medium mb-1">Total Tasks</p>
                <p className="text-3xl font-bold text-white">{tasks.length}</p>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-700 rounded-xl p-4 border border-green-500/30 shadow-lg">
                <p className="text-green-100 text-sm font-medium mb-1">Completed</p>
                <p className="text-3xl font-bold text-white">{tasks.filter(t => t.completed).length}</p>
              </div>
              <div className="bg-gradient-to-br from-purple-600 to-purple-700 rounded-xl p-4 border border-purple-500/30 shadow-lg">
                <p className="text-purple-100 text-sm font-medium mb-1">Progress</p>
                <p className="text-3xl font-bold text-white">{tasks.length > 0 ? Math.round((tasks.filter(t => t.completed).length / tasks.length) * 100) : 0}%</p>
              </div>
            </div>
          )}

          {/* Progress Bar */}
          {tasks.length > 0 && (
            <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 shadow-lg">
              <div className="flex items-center justify-between mb-3">
                <span className="text-slate-300 text-sm font-semibold">Overall Progress</span>
                <span className="text-cyan-400 font-bold">{tasks.filter(t => t.completed).length} / {tasks.length}</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-gradient-to-r from-cyan-500 via-purple-500 to-pink-500 h-full transition-all duration-700 ease-out shadow-lg shadow-purple-500/30"
                  style={{ width: `${(tasks.filter(t => t.completed).length / tasks.length) * 100}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-500/20 border border-red-500/50 rounded-xl p-4 mb-6 backdrop-blur">
            <p className="text-red-300 text-sm font-medium">❌ {error}</p>
          </div>
        )}

        {/* Add Task Form */}
        <form onSubmit={handleAddTask} className="mb-8">
          <div className="flex gap-3">
            <input
              type="text"
              value={newTaskTitle}
              onChange={(e) => setNewTaskTitle(e.target.value)}
              placeholder="✍️ Add a new task..."
              className="flex-1 px-5 py-4 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition shadow-lg"
            />
            <button
              type="submit"
              className="bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-black px-8 py-4 rounded-xl font-bold transition text-base shadow-lg shadow-purple-500/30 active:scale-95"
            >
              🚀 Add Task
            </button>
          </div>
        </form>

        {/* Loading */}
        {loading && (
          <div className="text-center py-16">
            <div className="text-6xl mb-4 animate-bounce">⏳</div>
            <p className="text-slate-300 font-semibold text-lg">Loading your tasks...</p>
            <p className="text-slate-500 text-sm mt-2">This shouldn't take long</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && tasks.length === 0 && (
          <div className="text-center py-20 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-slate-700 border-dashed">
            <div className="text-7xl mb-6 animate-bounce">📭</div>
            <p className="text-slate-200 font-bold text-2xl mb-2">No tasks yet</p>
            <p className="text-slate-400 text-base mb-6">Let's get started! Add your first task above</p>
            <div className="text-slate-500 text-sm max-w-md mx-auto">
              <p>💡 Tip: Use clear, actionable task names like "Complete project report" or "Call the dentist"</p>
            </div>
          </div>
        )}

        {/* Task List */}
        {!loading && tasks.length > 0 && (
          <div className="space-y-3">
            <h2 className="text-lg font-bold text-slate-300 mb-4">Your Tasks</h2>
            {tasks.map((task) => (
              <div
                key={`task-${task.id}`}
                className={`groups rounded-xl p-4 border-2 transition-all duration-300 shadow-lg ${
                  task.completed
                    ? 'bg-gradient-to-r from-green-900/40 to-green-800/40 border-green-600/30 hover:border-green-500/50'
                    : 'bg-gradient-to-r from-slate-800 to-slate-700 border-slate-600 hover:border-cyan-500/50 hover:shadow-cyan-500/20'
                }`}
              >
                <div className="flex items-center gap-4">
                  <input
                    type="checkbox"
                    checked={task.completed || false}
                    onChange={() => handleToggleTask(task.id, task.completed || false)}
                    className="w-6 h-6 accent-cyan-500 rounded cursor-pointer transition-transform"
                  />
                  <div className="flex-1 min-w-0">
                    <span
                      className={`block text-lg transition-all ${
                        task.completed 
                          ? 'line-through text-slate-500' 
                          : 'text-white font-medium'
                      }`}
                    >
                      {task.title}
                    </span>
                    {task.description && (
                      <p className="text-slate-400 text-sm mt-1">{task.description}</p>
                    )}
                  </div>
                  {task.completed && (
                    <span className="text-2xl animate-bounce">✅</span>
                  )}
                  <button
                    onClick={() => handleDeleteTask(task.id)}
                    className="text-slate-400 hover:text-red-400 opacity-0 groups-hover:opacity-100 transition-all text-xl p-2 hover:bg-red-500/20 rounded-lg"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Footer Tips */}
        {!loading && (
          <div className="mt-12 pt-8 border-t border-slate-700">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-4">
                <p className="text-sm text-slate-400">💡 <span className="font-semibold text-slate-200">Pro Tip:</span> Break big tasks into smaller ones</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4">
                <p className="text-sm text-slate-400">🎯 <span className="font-semibold text-slate-200">Focus:</span> Complete one task at a time</p>
              </div>
              <div className="bg-slate-800/50 rounded-lg p-4">
                <p className="text-sm text-slate-400">🏆 <span className="font-semibold text-slate-200">Celebrate:</span> Every task counts!</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
