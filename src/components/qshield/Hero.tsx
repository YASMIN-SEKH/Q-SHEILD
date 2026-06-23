import { motion } from "framer-motion";
import { ArrowRight, Download, BookOpen, Sparkles } from "lucide-react";
import { CyberGrid, Particles } from "./BackgroundFX";

export function Hero() {
  return (
    <section id="top" className="relative isolate overflow-hidden pt-36 pb-24 sm:pt-44 sm:pb-32">
      {/* gradient layers */}
      <div
        aria-hidden
        className="absolute inset-0 -z-10"
        style={{
          background:
            "radial-gradient(ellipse 80% 50% at 50% 0%, rgba(59,130,246,0.25), transparent 60%), radial-gradient(ellipse 60% 50% at 50% 100%, rgba(34,211,238,0.18), transparent 60%)",
        }}
      />
      <CyberGrid />
      <Particles count={50} />

      {/* orbiting nodes */}
      <div
        aria-hidden
        className="pointer-events-none absolute left-1/2 top-[55%] -z-10 hidden h-[400px] w-[400px] -translate-x-1/2 -translate-y-1/2 md:block"
      >
        <div className="absolute inset-0 rounded-full border border-cyan/20" />
        <div className="absolute inset-8 rounded-full border border-blue/15" />
        <div className="absolute inset-16 rounded-full border border-cyan/10" />
        {[0, 1, 2, 3].map((i) => (
          <span
            key={i}
            className="absolute left-1/2 top-1/2 h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-cyan shadow-[0_0_20px_#22D3EE]"
            style={{ animation: `orbit 18s linear ${i * -4.5}s infinite` }}
          />
        ))}
      </div>

      <div className="relative mx-auto max-w-5xl px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7 }}
          className="mx-auto inline-flex items-center gap-2 rounded-full glass px-4 py-1.5 text-xs font-medium uppercase tracking-[0.18em] text-cyan"
        >
          <Sparkles className="h-3.5 w-3.5" />
          Next Generation Cybersecurity
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.1 }}
          className="mt-6 font-display text-6xl font-semibold tracking-tight sm:text-7xl md:text-8xl"
        >
          <span className="text-gradient">Q-SHIELD</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.25 }}
          className="mt-5 font-display text-xl text-foreground/90 sm:text-2xl"
        >
          Quantum-Inspired Behavioral Authentication
        </motion.p>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.35 }}
          className="mx-auto mt-6 max-w-2xl text-base leading-relaxed text-muted-foreground sm:text-lg"
        >
          A next-generation authentication framework combining Behavioral Biometrics, Artificial
          Intelligence, Continuous Authentication, and Post-Quantum Cryptography to protect digital
          identities against modern cyber threats and future quantum attacks.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.45 }}
          className="mt-10 flex flex-wrap items-center justify-center gap-3"
        >
          <a
            href="#download"
            className="group relative inline-flex items-center gap-2 overflow-hidden rounded-xl bg-gradient-to-r from-cyan to-blue px-6 py-3 text-sm font-semibold text-background shadow-[0_0_30px_rgba(34,211,238,0.4)] transition-all hover:shadow-[0_0_50px_rgba(34,211,238,0.7)]"
          >
            <Download className="h-4 w-4" />
            Download Q-Shield
            <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/40 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
          </a>
          <a
            href="#technology"
            className="inline-flex items-center gap-2 rounded-xl glass-strong px-6 py-3 text-sm font-semibold text-foreground transition-all hover:border-cyan/40 hover:text-cyan"
          >
            <BookOpen className="h-4 w-4" />
            Read Research
            <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
          </a>
        </motion.div>

        {/* trust strip */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.7 }}
          className="mt-16 flex flex-wrap items-center justify-center gap-x-10 gap-y-3 text-xs font-mono uppercase tracking-widest text-muted-foreground/70"
        >
          <span>ROC-AUC · 0.999</span>
          <span className="hidden h-1 w-1 rounded-full bg-cyan sm:block" />
          <span>EER · 1.06%</span>
          <span className="hidden h-1 w-1 rounded-full bg-cyan sm:block" />
          <span>Accuracy · 95%+</span>
          <span className="hidden h-1 w-1 rounded-full bg-cyan sm:block" />
          <span>Post-Quantum Ready</span>
        </motion.div>
      </div>
    </section>
  );
}
