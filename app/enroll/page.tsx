'use client'

import React, { useState, useEffect } from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { KeystrokeCapture } from '@/components/KeystrokeCapture'
import { CheckCircle, Loader2, AlertCircle } from 'lucide-react'
import { apiFetch } from '@/lib/api'

interface KeystrokeMetrics {
  dwellTime: number
  flightTime: number
  latency: number
  holdTime: number
}

interface EnrollmentData {
  userId: string
  username: string
  email: string
}

export default function EnrollmentPage() {
  const [step, setStep] = useState(1)
  const [enrollment, setEnrollment] = useState<EnrollmentData | null>(null)
  const [samples, setSamples] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    // Get registration data from localStorage
    const regData = localStorage.getItem('qshield_registration')
    if (!regData) {
      window.location.href = '/register'
      return
    }

    try {
      const data = JSON.parse(regData)
      setEnrollment(data)
    } catch {
      window.location.href = '/register'
    }
  }, [])

  const handleCapture = (keystrokes: any[], metrics: KeystrokeMetrics) => {
    const newSamples = [...samples, { keystrokes, metrics }]
    setSamples(newSamples)

    if (newSamples.length < 3) {
      setStep(step + 1)
    } else {
      // Proceed to submission
      submitEnrollment(newSamples)
    }
  }

  const submitEnrollment = async (enrollmentSamples: any[]) => {
    if (!enrollment) return

    setLoading(true)
    setError('')

    try {
      const data = await apiFetch('/auth/enroll', {
        method: 'POST',
        body: JSON.stringify({
          user_id: enrollment.userId,
          username: enrollment.username,
          email: enrollment.email,
          keystroke_samples: enrollmentSamples.map((s) => s.keystrokes),
        }),
      })

      setSuccess(true)
      localStorage.removeItem('qshield_registration')

      // Redirect to dashboard after success
      setTimeout(() => {
        window.location.href = `/dashboard?userId=${enrollment.userId}`
      }, 2000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Enrollment failed')
      setLoading(false)
    }
  }

  if (!enrollment) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 text-primary animate-spin" />
      </div>
    )
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
        {/* Header */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-12">
          <h1 className="text-3xl font-bold mb-2">Biometric Enrollment</h1>
          <p className="text-muted-foreground">
            Create your unique keystroke profile for secure authentication
          </p>
        </motion.div>

        {success ? (
          // Success state
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="p-8 rounded-2xl glassmorphic-glow border-2 border-emerald-500/30 text-center space-y-4"
          >
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
            >
              <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto" />
            </motion.div>
            <h2 className="text-2xl font-bold text-emerald-400">Enrollment Complete!</h2>
            <p className="text-foreground/80">
              Your keystroke biometric profile has been successfully registered.
            </p>
            <p className="text-sm text-muted-foreground">Redirecting to dashboard...</p>
          </motion.div>
        ) : (
          <div className="space-y-8">
            {/* Progress indicator */}
            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="font-medium">Sample {step} of 3</span>
                <span className="text-muted-foreground">{Math.round((step / 3) * 100)}%</span>
              </div>
              <div className="flex gap-2">
                {[1, 2, 3].map((i) => (
                  <motion.div
                    key={i}
                    className={`h-2 rounded-full flex-1 ${
                      i <= step
                        ? 'bg-gradient-to-r from-primary to-secondary'
                        : 'bg-muted'
                    }`}
                    initial={{ scaleX: 0 }}
                    animate={{ scaleX: 1 }}
                    transition={{ delay: (i - 1) * 0.1 }}
                  />
                ))}
              </div>
            </div>

            {/* Keystroke capture */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              key={`step-${step}`}
              className="p-8 rounded-2xl glassmorphic-glow border border-primary/20"
            >
              <div className="mb-6 space-y-2">
                <h2 className="text-xl font-semibold">Sample {step}</h2>
                <p className="text-muted-foreground text-sm">
                  Type your authentication phrase naturally. Ensure consistent speed and pattern.
                </p>
              </div>

              <KeystrokeCapture
                onCapture={handleCapture}
                label={`Keystroke Sample ${step}`}
                placeholder="Type something distinctive..."
                minKeystrokes={15}
              />
            </motion.div>

            {/* Previous samples */}
            {samples.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="space-y-4"
              >
                <h3 className="font-semibold">Completed Samples</h3>
                <div className="grid gap-3">
                  {samples.map((sample, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.1 }}
                      className="p-4 rounded-lg glassmorphic flex items-center justify-between"
                    >
                      <div>
                        <div className="font-medium text-sm">Sample {i + 1}</div>
                        <div className="text-xs text-muted-foreground">
                          {sample.metrics.dwellTime}ms dwell • {sample.metrics.flightTime}ms flight
                        </div>
                      </div>
                      <CheckCircle className="w-5 h-5 text-emerald-400" />
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Error message */}
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 flex gap-3"
              >
                <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0" />
                <div>
                  <div className="font-medium text-red-400 text-sm">Enrollment Error</div>
                  <div className="text-xs text-red-400/80">{error}</div>
                </div>
              </motion.div>
            )}

            {/* Loading state */}
            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="p-4 rounded-lg glassmorphic flex items-center justify-center gap-3"
              >
                <Loader2 className="w-5 h-5 text-primary animate-spin" />
                <span className="text-sm">Processing enrollment...</span>
              </motion.div>
            )}
          </div>
        )}

        {/* Back link */}
        <div className="mt-12 text-center">
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Cancel enrollment
          </Link>
        </div>
      </div>
    </main>
  )
}
