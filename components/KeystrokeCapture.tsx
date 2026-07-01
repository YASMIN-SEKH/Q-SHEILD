'use client'

import React, { useState, useCallback, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'

interface KeystrokeEvent {
  key: string
  dwellTime: number
  flightTime: number
  latency: number
  holdTime: number
  timestamp: number
}

interface KeystrokeMetrics {
  dwellTime: number // Time key is held
  flightTime: number // Time between keystrokes
  latency: number // Response time
  holdTime: number // Average hold per key
}

interface KeystrokeCaptureProps {
  onCapture: (keystrokes: KeystrokeEvent[], metrics: KeystrokeMetrics) => void
  placeholder?: string
  label?: string
  readOnly?: boolean
  disabled?: boolean
  minKeystrokes?: number
}

export function KeystrokeCapture({
  onCapture,
  placeholder = 'Enter your authentication pattern...',
  label = 'Keystroke Pattern',
  readOnly = false,
  disabled = false,
  minKeystrokes = 10,
}: KeystrokeCaptureProps) {
  const [keystrokes, setKeystrokes] = useState<KeystrokeEvent[]>([])
  const keystrokesRef = useRef<KeystrokeEvent[]>([])
  const [displayText, setDisplayText] = useState('')
  const [isCapturing, setIsCapturing] = useState(false)
  const [metrics, setMetrics] = useState<KeystrokeMetrics>({
    dwellTime: 0,
    flightTime: 0,
    latency: 0,
    holdTime: 0,
  })
  const inputRef = useRef<HTMLInputElement>(null)
  const keyPressTimesRef = useRef<Map<string, number>>(new Map())

  const calculateMetrics = useCallback((events: KeystrokeEvent[]): KeystrokeMetrics => {
    if (events.length === 0) {
      return { dwellTime: 0, flightTime: 0, latency: 0, holdTime: 0 }
    }

    let totalDwellTime = 0
    let totalFlightTime = 0
    let dwellCount = 0

    for (let i = 0; i < events.length; i++) {
      const event = events[i]
      if (event.dwellTime) {
        totalDwellTime += event.dwellTime
        dwellCount++
      }

      if (i > 0) {
        const flightTime = event.timestamp - events[i - 1].timestamp
        totalFlightTime += flightTime
      }
    }

    const avgDwellTime = dwellCount > 0 ? totalDwellTime / dwellCount : 0
    const avgFlightTime = events.length > 1 ? totalFlightTime / (events.length - 1) : 0
    const latency = events.length > 0 ? events[0].timestamp : 0

    return {
      dwellTime: Math.round(avgDwellTime),
      flightTime: Math.round(avgFlightTime),
      latency: Math.round(latency),
      holdTime: Math.round(avgDwellTime),
    }
  }, [])

  const handleKeyDown = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (disabled || readOnly) return

    const key = e.key
    const timestamp = performance.now()

    keyPressTimesRef.current.set(key, timestamp)
    setIsCapturing(true)

    if (!readOnly) {
      setDisplayText((prev) => prev + '*')
    }
  }, [disabled, readOnly])

  const handleKeyUp = useCallback((e: React.KeyboardEvent<HTMLInputElement>) => {
    if (disabled) return

    const key = e.key
    const currentTime = performance.now()
    const pressTime = keyPressTimesRef.current.get(key) || currentTime

    const previousEvent = keystrokesRef.current[keystrokesRef.current.length - 1]
    const dwellTime = currentTime - pressTime
    const flightTime = previousEvent ? currentTime - previousEvent.timestamp : 0
    const latency = previousEvent ? currentTime - previousEvent.timestamp : 0

    const keystrokeEvent: KeystrokeEvent = {
      key: key === ' ' ? 'Space' : key.length === 1 ? key : key.substring(0, 10),
      dwellTime: Math.round(dwellTime),
      flightTime: Math.round(flightTime),
      latency: Math.round(latency),
      holdTime: Math.round(dwellTime),
      timestamp: currentTime,
    }

    setKeystrokes((prev) => {
      const updated = [...prev, keystrokeEvent]
      keystrokesRef.current = updated
      const newMetrics = calculateMetrics(updated)
      setMetrics(newMetrics)

      if (updated.length >= minKeystrokes) {
        setIsCapturing(false)
        onCapture(updated, newMetrics)
      }

      return updated
    })

    keyPressTimesRef.current.delete(key)
  }, [minKeystrokes, onCapture, calculateMetrics, disabled])

  const reset = useCallback(() => {
    setKeystrokes([])
    setDisplayText('')
    setIsCapturing(false)
    setMetrics({ dwellTime: 0, flightTime: 0, latency: 0, holdTime: 0 })
    keystrokesRef.current = []
    keyPressTimesRef.current.clear()
  }, [])

  const progress = (keystrokes.length / minKeystrokes) * 100

  return (
    <div className="w-full space-y-6">
      <div>
        <label className="block text-sm font-medium text-foreground mb-3">
          {label}
        </label>
        <div className="relative">
          <input
            ref={inputRef}
            type="password"
            placeholder={placeholder}
            onKeyDown={handleKeyDown}
            onKeyUp={handleKeyUp}
            disabled={disabled}
            readOnly={readOnly}
            className="w-full px-4 py-3 rounded-lg glassmorphic text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
          />
          {isCapturing && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="absolute right-3 top-1/2 -translate-y-1/2"
            >
              <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
            </motion.div>
          )}
        </div>
      </div>

      {/* Progress bar */}
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-xs font-medium text-muted-foreground">
            Keystrokes captured
          </span>
          <span className="text-xs font-medium text-primary">
            {keystrokes.length}/{minKeystrokes}
          </span>
        </div>
        <motion.div className="w-full h-1 rounded-full glassmorphic overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-primary to-secondary"
            initial={{ width: 0 }}
            animate={{ width: `${Math.min(progress, 100)}%` }}
            transition={{ duration: 0.3 }}
          />
        </motion.div>
      </div>

      {/* Metrics display */}
      {keystrokes.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="grid grid-cols-2 gap-3"
        >
          <div className="p-3 rounded-lg glassmorphic">
            <div className="text-xs text-muted-foreground">Dwell Time</div>
            <div className="text-sm font-semibold text-primary">
              {metrics.dwellTime}ms
            </div>
          </div>
          <div className="p-3 rounded-lg glassmorphic">
            <div className="text-xs text-muted-foreground">Flight Time</div>
            <div className="text-sm font-semibold text-primary">
              {metrics.flightTime}ms
            </div>
          </div>
          <div className="p-3 rounded-lg glassmorphic">
            <div className="text-xs text-muted-foreground">Latency</div>
            <div className="text-sm font-semibold text-primary">
              {metrics.latency}ms
            </div>
          </div>
          <div className="p-3 rounded-lg glassmorphic">
            <div className="text-xs text-muted-foreground">Hold Time</div>
            <div className="text-sm font-semibold text-primary">
              {metrics.holdTime}ms
            </div>
          </div>
        </motion.div>
      )}

      {/* Actions */}
      {keystrokes.length > 0 && (
        <motion.button
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          onClick={reset}
          className="w-full py-2 px-3 text-xs font-medium text-muted-foreground hover:text-foreground transition-colors"
        >
          Clear and retry
        </motion.button>
      )}
    </div>
  )
}
