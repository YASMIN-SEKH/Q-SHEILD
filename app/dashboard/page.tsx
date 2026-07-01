'use client'

import React, { useState, useEffect, Suspense } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { LogOut, BarChart3, Lock, TrendingUp, User } from 'lucide-react'
import { useSearchParams } from 'next/navigation'
import { apiFetch } from '@/lib/api'

interface AuthRecord {
  timestamp: string
  user_id: string
  authenticated: boolean
  fused_score: number
  anomaly_zone: string
  session_id: string
}

function DashboardContent() {
  const searchParams = useSearchParams()
  const userId = searchParams.get('userId')
  
  const [authHistory, setAuthHistory] = useState<AuthRecord[]>([])
  const [analytics, setAnalytics] = useState<any>(null)
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!userId) {
      window.location.href = '/login'
      return
    }

    const fetchData = async () => {
      try {
        const [historyData, analyticsData, metricsData] = await Promise.all([
          apiFetch('/auth/history'),
          apiFetch('/analytics/summary'),
          apiFetch('/metrics/eer'),
        ])

        setAuthHistory(Array.isArray(historyData?.records) ? historyData.records : [])
        setAnalytics(analyticsData)
        setMetrics(metricsData)
      } catch (err) {
        console.error('Failed to fetch dashboard data', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [userId])

  const handleLogout = () => {
    window.location.href = '/'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 mx-auto border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const recentAuth = authHistory.slice(-5).reverse()
  const successRate = analytics?.average_eer != null ? Math.max(0, 100 - analytics.average_eer * 100) : 0
  const totalUsers = analytics?.total_subjects ?? 0
  const totalAuth = analytics?.total_authentications ?? 0

  // Prepare chart data
  const scoreDistribution = metrics?.distribution ? Object.entries(metrics.distribution).map(([range, count]: any) => ({
    range,
    count,
  })) : []

  return (
    <main className="min-h-screen bg-background">
      {/* Header */}
      <motion.nav
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="border-b border-border backdrop-blur-xl bg-background/40 sticky top-0 z-50"
      >
        <div className="max-w-7xl mx-auto px-6 py-4 flex justify-between items-center">
          <div className="font-bold text-lg">
            <span className="bg-gradient-to-r from-primary via-secondary to-primary bg-clip-text text-transparent">
              Q-Shield v2
            </span>
          </div>
          <div className="flex items-center gap-6">
            <span className="text-sm text-muted-foreground">
              User: <span className="text-foreground font-semibold">{userId}</span>
            </span>
            <button
              onClick={handleLogout}
              className="p-2 rounded-lg hover:bg-muted transition-colors text-muted-foreground hover:text-foreground"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </motion.nav>

      <div className="max-w-7xl mx-auto px-6 py-12">
        {/* Page title */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-12">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-muted-foreground">Authentication analytics and security metrics</p>
        </motion.div>

        {/* Stats Grid */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ staggerChildren: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8"
        >
          {[
            {
              label: 'Success Rate',
              value: `${successRate.toFixed(1)}%`,
              icon: TrendingUp,
              color: 'from-emerald-500 to-emerald-600',
            },
            {
              label: 'Total Users',
              value: totalUsers,
              icon: User,
              color: 'from-blue-500 to-blue-600',
            },
            {
              label: 'Authentications',
              value: totalAuth,
              icon: Lock,
              color: 'from-purple-500 to-purple-600',
            },
            {
              label: 'Mean Score',
              value: `${(metrics?.mean * 100).toFixed(1)}%` || '0%',
              icon: BarChart3,
              color: 'from-pink-500 to-pink-600',
            },
          ].map((stat, i) => {
            const Icon = stat.icon
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="p-6 rounded-2xl glassmorphic-glow border border-primary/20 group hover:border-primary/40 transition-all"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-lg bg-gradient-to-br ${stat.color}`}>
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-bold mb-1">{stat.value}</div>
                  <div className="text-sm text-muted-foreground">{stat.label}</div>
                </div>
              </motion.div>
            )
          })}
        </motion.div>

        {/* Charts */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8"
        >
          {/* Score Distribution */}
          <div className="p-6 rounded-2xl glassmorphic-glow border border-primary/20">
            <h3 className="font-semibold mb-4">Score Distribution</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={scoreDistribution}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(0,217,255,0.1)" />
                <XAxis dataKey="range" stroke="rgba(232, 240, 255, 0.5)" />
                <YAxis stroke="rgba(232, 240, 255, 0.5)" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(15, 20, 38, 0.8)',
                    border: '1px solid rgba(0, 217, 255, 0.3)',
                    borderRadius: '8px',
                  }}
                />
                <Bar dataKey="count" fill="#00d9ff" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Anomaly Distribution */}
          {analytics?.anomaly_distribution && (
            <div className="p-6 rounded-2xl glassmorphic-glow border border-primary/20">
              <h3 className="font-semibold mb-4">Anomaly Levels</h3>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={Object.entries(analytics.anomaly_distribution).map(([name, value]: any) => ({
                      name,
                      value,
                    }))}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].map((level, index) => (
                      <Cell key={`cell-${index}`} fill={
                        level === 'LOW'
                          ? '#10b981'
                          : level === 'MEDIUM'
                            ? '#f59e0b'
                            : level === 'HIGH'
                              ? '#f97316'
                              : '#ef4444'
                      } />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(15, 20, 38, 0.8)',
                      border: '1px solid rgba(0, 217, 255, 0.3)',
                      borderRadius: '8px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          )}
        </motion.div>

        {/* Recent Authentications */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="p-6 rounded-2xl glassmorphic-glow border border-primary/20"
        >
          <h3 className="font-semibold mb-4">Recent Authentications</h3>
          <div className="space-y-3">
            {recentAuth.length > 0 ? (
              recentAuth.map((record, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="p-4 rounded-lg bg-muted/30 flex items-center justify-between"
                >
                  <div className="flex-1">
                    <div className="text-sm font-medium">
                      {new Date(record.timestamp).toLocaleString()}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Score: {(record.fused_score * 100).toFixed(1)}% • Zone: {record.anomaly_zone}
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded text-xs font-semibold ${
                    record.authenticated
                      ? 'bg-emerald-500/20 text-emerald-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}>
                    {record.authenticated ? 'Granted' : 'Denied'}
                  </div>
                </motion.div>
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">No authentication records</div>
            )}
          </div>
        </motion.div>

        {/* Actions */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="flex gap-4 mt-8"
        >
          <Link
            href="/login"
            className="px-6 py-2.5 rounded-lg bg-primary text-primary-foreground font-semibold hover:shadow-lg hover:shadow-primary/50 transition-all"
          >
            Authenticate Again
          </Link>
          <button
            onClick={handleLogout}
            className="px-6 py-2.5 rounded-lg border border-primary/30 font-semibold hover:border-primary/50 transition-all"
          >
            Logout
          </button>
        </motion.div>
      </div>
    </main>
  )
}

export default function DashboardPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 mx-auto border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-muted-foreground">Loading dashboard...</p>
        </div>
      </div>
    }>
      <DashboardContent />
    </Suspense>
  )
}
