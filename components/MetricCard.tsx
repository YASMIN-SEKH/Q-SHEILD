'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { LucideIcon } from 'lucide-react'

interface MetricCardProps {
  label: string
  value: string | number
  unit?: string
  icon?: LucideIcon
  color?: 'cyan' | 'purple' | 'emerald' | 'blue' | 'pink'
  trend?: 'up' | 'down' | 'neutral'
  trendValue?: string
  delay?: number
}

export function MetricCard({
  label,
  value,
  unit = '',
  icon: Icon,
  color = 'cyan',
  trend,
  trendValue,
  delay = 0,
}: MetricCardProps) {
  const colorMap = {
    cyan: 'from-cyan-500 to-cyan-600',
    purple: 'from-purple-500 to-purple-600',
    emerald: 'from-emerald-500 to-emerald-600',
    blue: 'from-blue-500 to-blue-600',
    pink: 'from-pink-500 to-pink-600',
  }

  const trendColorMap = {
    up: 'text-emerald-400',
    down: 'text-red-400',
    neutral: 'text-yellow-400',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay }}
      className="p-6 rounded-2xl glassmorphic-glow border border-primary/20 group hover:border-primary/40 transition-all"
    >
      <div className="flex items-start justify-between mb-4">
        {Icon && (
          <div className={`p-3 rounded-lg bg-gradient-to-br ${colorMap[color]}`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
        )}
        {trend && trendValue && (
          <div className={`text-sm font-semibold ${trendColorMap[trend]}`}>
            {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {trendValue}
          </div>
        )}
      </div>
      <div>
        <div className="text-3xl font-bold mb-1">
          {value}
          {unit && <span className="text-lg text-muted-foreground ml-1">{unit}</span>}
        </div>
        <div className="text-sm text-muted-foreground">{label}</div>
      </div>
    </motion.div>
  )
}
