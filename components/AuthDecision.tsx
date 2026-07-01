'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

interface AuthDecisionProps {
  authenticated: boolean
  fusedScore: number
  anomalyZone: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL'
  confidence: number
  message: string
  fidelityIp?: number
  fidelityBc?: number
  llr?: number
}

export function AuthDecision({
  authenticated,
  fusedScore,
  anomalyZone,
  confidence,
  message,
  fidelityIp = 0,
  fidelityBc = 0,
  llr = 0,
}: AuthDecisionProps) {
  const isAccepted = authenticated
  const anomalyColor =
    anomalyZone === 'LOW'
      ? 'text-emerald-400'
      : anomalyZone === 'MEDIUM'
        ? 'text-yellow-400'
        : anomalyZone === 'HIGH'
          ? 'text-orange-400'
          : 'text-red-400'

  const anomalyBg =
    anomalyZone === 'LOW'
      ? 'bg-emerald-500/10'
      : anomalyZone === 'MEDIUM'
        ? 'bg-yellow-500/10'
        : anomalyZone === 'HIGH'
          ? 'bg-orange-500/10'
          : 'bg-red-500/10'

  const ScoreBar = ({
    label,
    value,
    color,
  }: {
    label: string
    value: number
    color: string
  }) => (
    <div className="space-y-2">
      <div className="flex justify-between items-center">
        <span className="text-xs font-medium text-muted-foreground">{label}</span>
        <span className="text-xs font-semibold text-foreground">
          {(value * 100).toFixed(1)}%
        </span>
      </div>
      <div className="w-full h-2 rounded-full bg-muted overflow-hidden">
        <motion.div
          className={`h-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${value * 100}%` }}
          transition={{ duration: 0.8, ease: 'easeOut' }}
        />
      </div>
    </div>
  )

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5 }}
      className={`rounded-2xl p-8 glassmorphic-glow border-2 ${
        isAccepted
          ? 'border-emerald-500/30 neon-glow-cyan'
          : 'border-red-500/30'
      }`}
    >
      <div className="space-y-6">
        {/* Decision Header */}
        <div className="flex items-start gap-4">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 200 }}
          >
            {isAccepted ? (
              <CheckCircle className="w-12 h-12 text-emerald-400" />
            ) : (
              <XCircle className="w-12 h-12 text-red-400" />
            )}
          </motion.div>
          <div className="flex-1">
            <motion.h3
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3 }}
              className={`text-2xl font-bold ${
                isAccepted ? 'text-emerald-400' : 'text-red-400'
              }`}
            >
              {isAccepted ? 'Access Granted' : 'Access Denied'}
            </motion.h3>
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="text-sm text-foreground/80 mt-1"
            >
              {message}
            </motion.p>
          </div>
        </div>

        {/* Confidence Score */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="space-y-3"
        >
          <div className="flex justify-between items-center">
            <span className="text-sm font-semibold text-foreground">
              Confidence Score
            </span>
            <span className="text-lg font-bold text-primary">
              {(confidence * 100).toFixed(1)}%
            </span>
          </div>
          <div className="w-full h-3 rounded-full bg-muted overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary via-secondary to-primary"
              initial={{ width: 0 }}
              animate={{ width: `${confidence * 100}%` }}
              transition={{ duration: 0.8, ease: 'easeOut' }}
            />
          </div>
        </motion.div>

        {/* Fused Score */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <ScoreBar
            label="Fused Likelihood Ratio"
            value={fusedScore}
            color="bg-gradient-to-r from-primary to-secondary"
          />
        </motion.div>

        {/* Fidelity Metrics */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="grid grid-cols-2 gap-4"
        >
          <div className="p-3 rounded-lg bg-muted/50">
            <div className="text-xs font-medium text-muted-foreground mb-2">
              IP Fidelity
            </div>
            <ScoreBar label="" value={fidelityIp} color="bg-blue-400" />
          </div>
          <div className="p-3 rounded-lg bg-muted/50">
            <div className="text-xs font-medium text-muted-foreground mb-2">
              Behavioral Fidelity
            </div>
            <ScoreBar label="" value={fidelityBc} color="bg-purple-400" />
          </div>
        </motion.div>

        {/* Anomaly Zone */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className={`p-4 rounded-lg flex items-center gap-3 ${anomalyBg}`}
        >
          <AlertTriangle className={`w-5 h-5 ${anomalyColor}`} />
          <div>
            <div className={`text-sm font-semibold ${anomalyColor}`}>
              Anomaly Level: {anomalyZone}
            </div>
            <div className="text-xs text-muted-foreground">
              {anomalyZone === 'LOW'
                ? 'Pattern matches training profile'
                : anomalyZone === 'MEDIUM'
                  ? 'Minor deviation from pattern'
                  : anomalyZone === 'HIGH'
                    ? 'Significant pattern deviation'
                    : 'Critical anomaly detected'}
            </div>
          </div>
        </motion.div>

        {/* LLR */}
        {llr !== 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="p-3 rounded-lg glassmorphic text-center"
          >
            <div className="text-xs font-medium text-muted-foreground mb-1">
              Log-Likelihood Ratio
            </div>
            <div className="text-lg font-bold text-primary font-mono">
              {llr.toFixed(4)}
            </div>
          </motion.div>
        )}
      </div>
    </motion.div>
  )
}
