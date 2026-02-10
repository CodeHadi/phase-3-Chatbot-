import Link from "next/link";

export default function Home() {
  const features = [
    {
      icon: "🎯",
      title: "Smart Task Management",
      description: "Create, organize, and prioritize your tasks with ease"
    },
    {
      icon: "🤖",
      title: "AI-Powered Assistant",
      description: "Get intelligent suggestions and task automation"
    },
    {
      icon: "⚡",
      title: "Lightning Fast",
      description: "Optimized for speed with real-time updates"
    },
    {
      icon: "🔐",
      title: "Secure & Private",
      description: "Your data is encrypted and secure"
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-black via-slate-900 to-black flex flex-col items-center justify-center p-4 relative overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-96 h-96 bg-cyan-500 opacity-10 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute -bottom-40 -left-40 w-96 h-96 bg-purple-500 opacity-10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1.5s' }}></div>
        <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-pink-500 opacity-10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '3s' }}></div>
      </div>

      {/* Content */}
      <div className="relative z-10 max-w-5xl mx-auto text-center space-y-12 animate-in fade-in slide-in-from-bottom-8 duration-1000">
        {/* Icon */}
        <div className="flex justify-center">
          <div className="inline-flex items-center justify-center w-32 h-32 bg-gradient-to-br from-cyan-500 via-purple-500 to-pink-500 rounded-full border-3 border-cyan-400 shadow-2xl shadow-cyan-500/30 animate-bounce">
            <span className="text-7xl">📝</span>
          </div>
        </div>

        {/* Headline */}
        <div className="space-y-6">
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-black leading-tight">
            <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Task Master Pro
            </span>
          </h1>
          <p className="text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto leading-relaxed font-light">
            🚀 Stay organized, boost productivity, and achieve your goals with intelligent task management
          </p>
          <p className="text-base text-gray-400 max-w-xl mx-auto">
            A modern, AI-powered task management platform designed for your success. Works seamlessly across all your devices.
          </p>
        </div>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center pt-6">
          <Link
            href="/todos"
            className="px-12 py-4 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-black font-bold text-lg rounded-xl transition duration-300 transform hover:scale-105 active:scale-95 flex items-center justify-center gap-3 shadow-2xl shadow-purple-500/40"
          >
            <span>🚀</span>
            Get Started
          </Link>
          <Link
            href="/login"
            className="px-12 py-4 bg-gray-800 hover:bg-gray-700 text-white font-bold text-lg rounded-xl transition duration-300 transform hover:scale-105 active:scale-95 flex items-center justify-center gap-3 border-2 border-gray-600 hover:border-cyan-400"
          >
            <span>🔐</span>
            Sign In
          </Link>
        </div>

        {/* Features Grid */}
        <div className="pt-20 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full">
          {[
            { icon: "🎯", title: "Smart Tasks", desc: "Create and organize with AI assistance" },
            { icon: "⚡", title: "Real-time Sync", desc: "Stay updated across all devices" },
            { icon: "🤖", title: "AI Assistant", desc: "Get smart suggestions & automation" },
            { icon: "🔐", title: "Secure & Private", desc: "Enterprise-grade encryption" }
          ].map((feature, i) => (
            <div key={i} className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700 hover:border-cyan-500/50 hover:from-slate-700 transition duration-300 group">
              <div className="text-5xl mb-4 group-hover:scale-110 transition duration-300">{feature.icon}</div>
              <h3 className="text-white font-bold text-lg mb-2">{feature.title}</h3>
              <p className="text-gray-400 text-sm">{feature.desc}</p>
            </div>
          ))}
        </div>

        {/* Why Choose Us */}
        <div className="pt-20 w-full max-w-3xl mx-auto">
          <h2 className="text-4xl font-bold mb-12 bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
            Why Task Master Pro?
          </h2>
          <div className="space-y-4">
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 hover:border-cyan-500/30 transition">
              <div className="flex gap-4">
                <span className="text-2xl">✓</span>
                <div className="text-left">
                  <h4 className="text-white font-semibold mb-1">Effortless Organization</h4>
                  <p className="text-gray-400 text-sm">Categorize tasks, set priorities, and meet deadlines</p>
                </div>
              </div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 hover:border-cyan-500/30 transition">
              <div className="flex gap-4">
                <span className="text-2xl">✓</span>
                <div className="text-left">
                  <h4 className="text-white font-semibold mb-1">AI-Powered Insights</h4>
                  <p className="text-gray-400 text-sm">Get smart reminders and task recommendations</p>
                </div>
              </div>
            </div>
            <div className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 hover:border-cyan-500/30 transition">
              <div className="flex gap-4">
                <span className="text-2xl">✓</span>
                <div className="text-left">
                  <h4 className="text-white font-semibold mb-1">Collaborate & Share</h4>
                  <p className="text-gray-400 text-sm">Work with your team and delegate tasks easily</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer CTA */}
        <div className="pt-20 text-center pb-10">
          <p className="text-gray-400 mb-6">Join thousands of productive users</p>
          <Link
            href="/todos"
            className="inline-block px-10 py-3 bg-gradient-to-r from-cyan-500 to-purple-500 hover:from-cyan-400 hover:to-purple-400 text-black font-bold rounded-xl transition duration-300 shadow-xl shadow-purple-500/20 hover:shadow-purple-500/40"
          >
            Start Free Today →
          </Link>
        </div>
      </div>
    </div>
  );
}
