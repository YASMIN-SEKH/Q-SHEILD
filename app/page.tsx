'use client'

import React from 'react'
import Link from 'next/link'
import { motion } from 'framer-motion'
import { Zap, Lock, Brain, BarChart3, ArrowRight } from 'lucide-react'

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
}

const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0 },
}

export default function Home() {
  return (
    <main className="min-h-screen bg-background overflow-hidden">
      {/* Animated background elements */}
      <div className="fixed inset-0 -z-10">
        <motion.div
          animate={{ opacity: [0.3, 0.6, 0.3] }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute top-20 right-20 w-72 h-72 rounded-full blur-3xl bg-primary/20"
        />
        <motion.div
          animate={{ opacity: [0.2, 0.5, 0.2] }}
          transition={{ duration: 10, repeat: Infinity, delay: 2 }}
          className="absolute bottom-40 left-20 w-96 h-96 rounded-full blur-3xl bg-secondary/20"
        />
      </div>

      <div className="relative z-10">
        {/* Navigation */}
        <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-background/40">
          <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="font-bold text-lg">
              <span className="gradient-text">Q-Shield v2</span>
            </motion.div>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="flex gap-6"
            >
              <Link href="/login" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Sign In
              </Link>
              <Link
                href="/register"
                className="px-4 py-2 text-sm font-medium rounded-lg bg-primary text-primary-foreground hover:shadow-lg hover:shadow-primary/50 transition-all"
              >
                Get Started
              </Link>
            </motion.div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="min-h-screen flex items-center justify-center px-6 pt-20">
          <div className="max-w-4xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="space-y-6 mb-12"
            >
              <h1 className="text-6xl md:text-7xl font-bold leading-tight">
                <span className="gradient-text">Quantum-Resistant</span>
                <br />
                Biometric Authentication
              </h1>
              <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                Enterprise-grade keystroke biometrics with quantum-resistant encryption, advanced anomaly detection, and
                real-time threat analysis powered by cutting-edge ML algorithms.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3, duration: 0.8 }}
              className="flex flex-col sm:flex-row gap-4 justify-center mb-20"
            >
              <Link
                href="/register"
                className="px-8 py-4 rounded-lg bg-primary text-primary-foreground font-semibold hover:shadow-lg hover:shadow-primary/50 transition-all flex items-center justify-center gap-2 group"
              >
                Start Enrollment
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="/login"
                className="px-8 py-4 rounded-lg glassmorphic font-semibold hover:border-primary/50 transition-all flex items-center justify-center gap-2"
              >
                Learn More
              </Link>
            </motion.div>

            {/* Stats */}
            <motion.div
              variants={container}
              initial="hidden"
              animate="show"
              className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-2xl mx-auto"
            >
              <motion.div variants={item} className="space-y-2">
                <div className="text-3xl font-bold text-primary">99.9%</div>
                <div className="text-sm text-muted-foreground">Authentication Accuracy</div>
              </motion.div>
              <motion.div variants={item} className="space-y-2">
                <div className="text-3xl font-bold text-primary">Quantum</div>
                <div className="text-sm text-muted-foreground">Resistant</div>
              </motion.div>
              <motion.div variants={item} className="space-y-2">
                <div className="text-3xl font-bold text-primary">Real-time</div>
                <div className="text-sm text-muted-foreground">Threat Detection</div>
              </motion.div>
            </motion.div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-20 px-6 max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <motion.h2
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              className="text-4xl font-bold mb-4"
            >
              Advanced Security Features
            </motion.h2>
            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              transition={{ delay: 0.1 }}
              className="text-muted-foreground max-w-2xl mx-auto"
            >
              Multi-layered authentication with advanced biometric analysis
            </motion.p>
          </div>

          <motion.div
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="grid grid-cols-1 md:grid-cols-2 gap-8"
          >
            {[
              {
                icon: Lock,
                title: 'Keystroke Biometrics',
                description: 'Unique typing patterns analyzed for dwell time, flight time, and pressure dynamics',
              },
              {
                icon: Zap,
                title: 'Real-time Processing',
                description: 'Instant authentication with sub-100ms response time for seamless UX',
              },
              {
                icon: Brain,
                title: 'ML-Powered Analysis',
                description: 'Quantum-resistant algorithms with advanced anomaly detection',
              },
              {
                icon: BarChart3,
                title: 'Comprehensive Metrics',
                description: 'EER, ROC curves, and detailed analytics for security insights',
              },
            ].map((feature, i) => (
              <motion.div
                key={i}
                variants={item}
                className="p-6 rounded-2xl glassmorphic-glow hover:border-primary/50 transition-all group"
              >
                <feature.icon className="w-8 h-8 text-primary mb-4 group-hover:scale-110 transition-transform" />
                <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                <p className="text-muted-foreground text-sm">{feature.description}</p>
              </motion.div>
            ))}
          </motion.div>
        </section>

        {/* CTA Section */}
        <section className="py-20 px-6">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="max-w-2xl mx-auto text-center space-y-8 p-12 rounded-2xl glassmorphic-glow"
          >
            <h2 className="text-3xl font-bold">Ready to Secure Your Application?</h2>
            <p className="text-muted-foreground">
              Join enterprises using Q-Shield v2 for quantum-resistant biometric authentication
            </p>
            <Link
              href="/register"
              className="inline-block px-8 py-4 rounded-lg bg-primary text-primary-foreground font-semibold hover:shadow-lg hover:shadow-primary/50 transition-all"
            >
              Start Free Enrollment
            </Link>
          </motion.div>
        </section>

        {/* Footer */}
        <footer className="border-t border-border py-8 px-6 mt-20">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-muted-foreground">
            <div>&copy; 2026 Q-Shield v2. All rights reserved.</div>
            <div className="flex gap-6">
              <a href="#" className="hover:text-foreground transition-colors">
                Privacy
              </a>
              <a href="#" className="hover:text-foreground transition-colors">
                Terms
              </a>
              <a href="#" className="hover:text-foreground transition-colors">
                Docs
              </a>
            </div>
          </div>
        </footer>
      </div>
    </main>
  )
}
