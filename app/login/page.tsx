'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { KeystrokeCapture } from '@/components/KeystrokeCapture'
import { AuthDecision } from '@/components/AuthDecision'
import { Loader2 } from 'lucide-react'
import { apiFetch } from '@/lib/api'

interface KeystrokeMetrics {
  dwellTime: number
  flightTime: number
  latency: number
  holdTime: number
}

interface AuthResult {
  authenticated: boolean
  fused_score: number
  llr: number
  fidelity_ip: number
  fidelity_bc: number
  anomaly_zone: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  confidence: number
  message: string
}

export default function LoginPage() {
  const [userId, setUserId] = useState('')
  const [showCapture, setShowCapture] = useState(false)
  const [loading, setLoading] = useState(false)
  const [authResult, setAuthResult] = useState<AuthResult | null>(null)
  const [error, setError] = useState('')

  const handleStartAuth = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!userId.trim()) {
      setError('Please enter your user ID')
      return
    }
    setShowCapture(true)
    setError('')
  }

  const handleKeystrokeCapture = async (keystrokes: any[], metrics: KeystrokeMetrics) => {
    setLoading(true)
    setError('')

    try {
      const data = await apiFetch('/auth/authenticate', {
        method: 'POST',
        body: JSON.stringify({
          user_id: userId,
          keystrokes,
          session_id: `session-${Date.now()}`,
        }),
      })

      setAuthResult(data)

      // Redirect on success
      if (data.authenticated) {
        setTimeout(() => {
          window.location.href = `/dashboard?userId=${userId}`
        }, 3000)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-background px-6 py-12">
      {/* Background animation */}
      <div className="fixed inset-0 -z-10">
        <motion.div
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute top-1/3 right-1/4 w-96 h-96 rounded-full blur-3xl bg-primary/15"
        />
        <motion.div
          animate={{ opacity: [0.2, 0.5, 0.2] }}
          transition={{ duration: 10, repeat: Infinity, delay: 2 }}
          className="absolute bottom-1/4 left-1/4 w-96 h-96 rounded-full blur-3xl bg-secondary/15"
        />
      </div>

      <div className="max-w-2xl mx-auto">
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-8">
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            ← Back to home
          </Link>
        </motion.div>

        {authResult ? (
          // Show auth decision
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
          >
            <AuthDecision
              authenticated={authResult.authenticated}
              fusedScore={authResult.fused_score}
              anomalyZone={authResult.anomaly_zone}
              confidence={authResult.confidence}
              message={authResult.message}
              fidelityIp={authResult.fidelity_ip}
              fidelityBc={authResult.fidelity_bc}
              llr={authResult.llr}
            />
          </motion.div>
        ) : showCapture ? (
          // Show keystroke capture
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-8 rounded-2xl glassmorphic-glow border border-primary/20"
          >
            <div className="mb-8">
              <h1 className="text-2xl font-bold mb-2">Authenticate</h1>
              <p className="text-muted-foreground">
                Enter your keystroke pattern to authenticate
              </p>
            </div>

            <KeystrokeCapture
              onCapture={handleKeystrokeCapture}
              label="Keystroke Authentication"
              placeholder="Type your authentication pattern..."
              disabled={loading}
              minKeystrokes={15}
            />

            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="mt-6 p-4 rounded-lg glassmorphic flex items-center justify-center gap-3"
              >
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
                <span className="text-sm">Analyzing biometric data...</span>
              </motion.div>
            )}

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm"
              >
                {error}
              </motion.div>
            )}

            <button
              onClick={() => {
                setShowCapture(false)
                setError('')
              }}
              className="w-full mt-6 py-2 px-3 text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              Back to user ID
            </button>
          </motion.div>
        ) : (
          // Show user ID form
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="p-8 rounded-2xl glassmorphic-glow border border-primary/20 max-w-md mx-auto"
          >
            <div className="mb-8">
              <h1 className="text-2xl font-bold mb-2">Sign In</h1>
              <p className="text-muted-foreground">
                Enter your user ID to proceed with biometric authentication
              </p>
            </div>

            <form onSubmit={handleStartAuth} className="space-y-5">
              <div>
                <label htmlFor="userId" className="block text-sm font-medium mb-2">
                  User ID
                </label>
                <input
                  id="userId"
                  type="text"
                  value={userId}
                  onChange={(e) => {
                    setUserId(e.target.value)
                    setError('')
                  }}
                  placeholder="Enter your user ID"
                  className="w-full px-4 py-2.5 rounded-lg glassmorphic text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                />
              </div>

              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm"
                >
                  {error}
                </motion.div>
              )}

              <button
                type="submit"
                className="w-full py-2.5 px-4 rounded-lg bg-primary text-primary-foreground font-semibold hover:shadow-lg hover:shadow-primary/50 transition-all"
              >
                Continue to Biometric Auth
              </button>

              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-2 bg-background text-muted-foreground">Don&apos;t have an account?</span>
                </div>
              </div>

              <Link
                href="/register"
                className="block w-full text-center py-2.5 px-4 rounded-lg border border-primary/30 text-foreground font-semibold hover:border-primary/50 transition-all"
              >
                Create Account
              </Link>
            </form>
          </motion.div>
        )}
      </div>
    </main>
  )
}
