import { motion, useInView, useMotionValue, useSpring, useTransform } from "framer-motion";
import { useEffect, useRef } from "react";
import {
  KeyRound, Fish, UserX, Fingerprint, Atom, Lock, Cpu, Bot, Shield, Activity, Cloud,
  Landmark, HeartPulse, ShieldAlert, Zap, Building2, GraduationCap,
  Apple, MonitorDown, TerminalSquare, Github, Linkedin, Globe,
} from "lucide-react";

function SectionHeader({ eyebrow, title, sub }: { eyebrow?: string; title: string; sub?: string }) {
  return (
    <div className="mx-auto max-w-2xl text-center">
      {eyebrow && (
        <div className="mb-3 text-xs font-mono uppercase tracking-[0.2em] text-cyan">{eyebrow}</div>
      )}
      <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-5xl">
        <span className="text-gradient">{title}</span>
      </h2>
      {sub && <p className="mt-4 text-muted-foreground">{sub}</p>}
    </div>
  );
}

function Reveal({ children, delay = 0 }: { children: React.ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.6, delay, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}

/* ----------------- PROBLEM ----------------- */
const problems = [
  { icon: KeyRound, title: "Password Theft", desc: "Millions of credentials are compromised every year." },
  { icon: Fish, title: "Phishing Attacks", desc: "Users are tricked into revealing sensitive information." },
  { icon: UserX, title: "Session Hijacking", desc: "Attackers take over active authenticated sessions." },
  { icon: Fingerprint, title: "Biometric Spoofing", desc: "Traditional biometrics can be replicated." },
  { icon: Atom, title: "Quantum Threats", desc: "Quantum computers may break current encryption standards." },
];

export function ProblemSection() {
  return (
    <section id="problem" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
          eyebrow="The Problem"
          title="Why Traditional Authentication Fails"
          sub="Passwords, OTPs, and static biometrics were not built for the threats of 2026 — let alone the post-quantum era."
        />
        <div className="mt-14 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
          {problems.map((p, i) => (
            <Reveal key={p.title} delay={i * 0.05}>
              <div className="hover-lift group relative h-full overflow-hidden rounded-2xl glass p-6">
                <div
                  aria-hidden
                  className="pointer-events-none absolute -right-12 -top-12 h-40 w-40 rounded-full opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                  style={{ background: "radial-gradient(circle, rgba(34,211,238,0.3), transparent 70%)" }}
                />
                <div className="mb-5 inline-flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-cyan/20 to-blue/10 ring-1 ring-cyan/30">
                  <p.icon className="h-6 w-6 text-cyan" />
                </div>
                <h3 className="font-display text-lg font-semibold">{p.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{p.desc}</p>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ----------------- METRICS COUNT-UP ----------------- */
function CountUp({ to, decimals = 0, suffix = "" }: { to: number; decimals?: number; suffix?: string }) {
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-50px" });
  const mv = useMotionValue(0);
  const sp = useSpring(mv, { duration: 1.8, bounce: 0 });
  const text = useTransform(sp, (v) => v.toFixed(decimals) + suffix);
  useEffect(() => {
    if (inView) mv.set(to);
  }, [inView, to, mv]);
  return <motion.span ref={ref}>{text}</motion.span>;
}

const metrics = [
  { label: "ROC-AUC Score", value: 0.999, decimals: 3 },
  { label: "Equal Error Rate", value: 1.06, decimals: 2, suffix: "%" },
  { label: "Research Participants", value: 51 },
  { label: "Authentication Accuracy", value: 95, suffix: "%+" },
];

export function MetricsSection() {
  return (
    <section className="relative py-20">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader eyebrow="Validated" title="Research Highlights" />
        <div className="mt-12 grid grid-cols-2 gap-4 sm:gap-5 lg:grid-cols-4">
          {metrics.map((m, i) => (
            <Reveal key={m.label} delay={i * 0.07}>
              <div className="relative overflow-hidden rounded-2xl glass-strong p-6 text-center">
                <div
                  aria-hidden
                  className="absolute inset-x-0 -top-px mx-auto h-px w-2/3 bg-gradient-to-r from-transparent via-cyan to-transparent"
                />
                <div className="font-display text-4xl font-semibold tracking-tight text-gradient sm:text-5xl">
                  <CountUp to={m.value} decimals={m.decimals ?? 0} suffix={m.suffix ?? ""} />
                </div>
                <div className="mt-2 text-xs font-mono uppercase tracking-widest text-muted-foreground">
                  {m.label}
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ----------------- FEATURES ----------------- */
const features = [
  { icon: Lock, title: "Continuous Authentication", desc: "Continuously verifies user identity throughout the entire session." },
  { icon: Atom, title: "Quantum Identity Modeling", desc: "Generates secure quantum-inspired identity signatures per user." },
  { icon: Bot, title: "AI Threat Detection", desc: "Detects anomalies and suspicious behavior in real time using ML." },
  { icon: Shield, title: "Post-Quantum Security", desc: "Designed to remain secure even in the post-quantum era." },
  { icon: Activity, title: "Risk Monitoring", desc: "Monitors sessions and identifies high-risk activity instantly." },
  { icon: Cloud, title: "Enterprise Ready", desc: "Built to scale to large enterprise deployments with full SSO." },
];

export function FeaturesSection() {
  return (
    <section id="features" className="relative py-24 sm:py-32">
      <div
        aria-hidden
        className="absolute inset-0 -z-10 opacity-50"
        style={{ background: "radial-gradient(ellipse at center, rgba(59,130,246,0.12), transparent 70%)" }}
      />
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
          eyebrow="Platform"
          title="Why Q-SHIELD?"
          sub="Six core capabilities engineered to render today's attacks — and tomorrow's — obsolete."
        />
        <div className="mt-14 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <Reveal key={f.title} delay={i * 0.05}>
              <div className="hover-lift group relative h-full overflow-hidden rounded-2xl glass p-7">
                <div className="relative mb-5 inline-flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan to-blue text-background shadow-[0_0_30px_rgba(34,211,238,0.35)]">
                  <f.icon className="h-7 w-7" />
                </div>
                <h3 className="font-display text-xl font-semibold">{f.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{f.desc}</p>
                <div
                  aria-hidden
                  className="pointer-events-none absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                  style={{ background: "linear-gradient(135deg, rgba(34,211,238,0.06), transparent 60%)" }}
                />
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ----------------- TECHNOLOGY FLOW ----------------- */
const flow = [
  { icon: Activity, label: "User Behavior" },
  { icon: Cpu, label: "Feature Extraction" },
  { icon: Atom, label: "Quantum Identity" },
  { icon: Bot, label: "AI Analysis" },
  { icon: Shield, label: "Authentication" },
];

export function TechnologySection() {
  return (
    <section id="technology" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
          eyebrow="How It Works"
          title="The Q-SHIELD Pipeline"
          sub="From keystroke to cryptographic proof — five synchronized stages, sub-second latency."
        />

        <div className="mt-16 hidden lg:block">
          <div className="relative">
            <div className="absolute left-[6%] right-[6%] top-1/2 h-px -translate-y-1/2 bg-gradient-to-r from-transparent via-cyan to-transparent">
              <div
                className="absolute inset-0 bg-gradient-to-r from-cyan via-blue to-cyan opacity-60"
                style={{ backgroundSize: "200% 100%", animation: "shimmer 4s linear infinite" }}
              />
            </div>
            <ol className="relative grid grid-cols-5 gap-4">
              {flow.map((s, i) => (
                <Reveal key={s.label} delay={i * 0.1}>
                  <li className="relative flex flex-col items-center text-center">
                    <div className="relative grid h-20 w-20 place-items-center rounded-2xl glass-strong ring-1 ring-cyan/30 glow-cyan">
                      <s.icon className="h-8 w-8 text-cyan" />
                      <span className="absolute -top-2 -right-2 grid h-6 w-6 place-items-center rounded-full bg-gradient-to-br from-cyan to-blue text-[10px] font-bold text-background">
                        {i + 1}
                      </span>
                    </div>
                    <div className="mt-4 font-display text-sm font-medium">{s.label}</div>
                  </li>
                </Reveal>
              ))}
            </ol>
          </div>
        </div>

        {/* mobile vertical flow */}
        <ol className="mt-14 grid gap-4 lg:hidden">
          {flow.map((s, i) => (
            <Reveal key={s.label} delay={i * 0.06}>
              <li className="flex items-center gap-4 rounded-2xl glass p-4">
                <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-gradient-to-br from-cyan/20 to-blue/10 ring-1 ring-cyan/30">
                  <s.icon className="h-5 w-5 text-cyan" />
                </div>
                <div>
                  <div className="text-xs font-mono uppercase tracking-widest text-muted-foreground">
                    Step {i + 1}
                  </div>
                  <div className="font-display text-base font-medium">{s.label}</div>
                </div>
              </li>
            </Reveal>
          ))}
        </ol>
      </div>
    </section>
  );
}

/* ----------------- INDUSTRIES ----------------- */
const industries = [
  { icon: Landmark, label: "Banking" },
  { icon: HeartPulse, label: "Healthcare" },
  { icon: ShieldAlert, label: "Defense" },
  { icon: Zap, label: "Critical Infrastructure" },
  { icon: Building2, label: "Enterprises" },
  { icon: GraduationCap, label: "Education" },
];

export function IndustriesSection() {
  return (
    <section id="industries" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader eyebrow="Reach" title="Industries We Protect" />
        <div className="mt-14 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
          {industries.map((it, i) => (
            <Reveal key={it.label} delay={i * 0.04}>
              <div className="hover-lift group flex flex-col items-center gap-3 rounded-2xl glass p-6 text-center">
                <div className="grid h-14 w-14 place-items-center rounded-2xl bg-gradient-to-br from-cyan/15 to-blue/10 ring-1 ring-white/10 transition-transform duration-500 group-hover:scale-110 group-hover:ring-cyan/40">
                  <it.icon className="h-6 w-6 text-cyan transition-colors group-hover:text-foreground" />
                </div>
                <div className="text-sm font-medium">{it.label}</div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ----------------- TEAM ----------------- */
const team = [
  { name: "Yasmin Khatun Sekh", role: "Research · Behavioral ML", initials: "YK" },
  { name: "Kruparani Tomar", role: "Research · Quantum Identity", initials: "KT" },
  { name: "Zeel Gajjar", role: "Research · Systems & Crypto", initials: "ZG" },
];

export function TeamSection() {
  return (
    <section id="team" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-7xl px-6">
        <SectionHeader
          eyebrow="People"
          title="Research Team"
          sub="MBIT, CVM University, India"
        />
        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {team.map((m, i) => (
            <Reveal key={m.name} delay={i * 0.08}>
              <div className="hover-lift group relative overflow-hidden rounded-2xl glass-strong p-6 text-center">
                <div
                  aria-hidden
                  className="absolute inset-0 rounded-2xl opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                  style={{
                    background:
                      "radial-gradient(ellipse at top, rgba(34,211,238,0.18), transparent 60%)",
                  }}
                />
                <div className="relative mx-auto grid h-24 w-24 place-items-center rounded-full bg-gradient-to-br from-cyan to-blue p-[2px]">
                  <div className="grid h-full w-full place-items-center rounded-full bg-card font-display text-2xl font-semibold text-gradient">
                    {m.initials}
                  </div>
                </div>
                <h3 className="relative mt-5 font-display text-lg font-semibold">{m.name}</h3>
                <p className="relative mt-1 text-xs font-mono uppercase tracking-widest text-cyan">
                  {m.role}
                </p>
                <p className="relative mt-2 text-sm text-muted-foreground">
                  MBIT, CVM University, India
                </p>
                <div className="relative mt-4 flex justify-center gap-2">
                  {[Github, Linkedin, Globe].map((Icon, k) => (
                    <a
                      key={k}
                      href="#"
                      className="grid h-9 w-9 place-items-center rounded-lg glass text-muted-foreground transition-colors hover:text-cyan"
                    >
                      <Icon className="h-4 w-4" />
                    </a>
                  ))}
                </div>
              </div>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  );
}

/* ----------------- DOWNLOAD ----------------- */
const downloads = [
  { icon: MonitorDown, label: "Download for Windows", sub: "Windows 10/11 · 64-bit" },
  { icon: TerminalSquare, label: "Download for Linux", sub: "Ubuntu · Debian · Fedora" },
  { icon: Apple, label: "Download for macOS", sub: "Apple Silicon · Intel" },
];

export function DownloadSection() {
  return (
    <section id="download" className="relative py-24 sm:py-32">
      <div className="mx-auto max-w-5xl px-6">
        <Reveal>
          <div className="relative overflow-hidden rounded-3xl glass-strong p-10 text-center sm:p-16">
            <div
              aria-hidden
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "radial-gradient(ellipse at top, rgba(34,211,238,0.25), transparent 60%), radial-gradient(ellipse at bottom, rgba(59,130,246,0.2), transparent 60%)",
              }}
            />
            <div className="relative">
              <div className="mb-3 text-xs font-mono uppercase tracking-[0.22em] text-cyan">
                Ship Today
              </div>
              <h2 className="font-display text-4xl font-semibold tracking-tight sm:text-5xl">
                <span className="text-gradient">Ready for the Future?</span>
              </h2>
              <p className="mx-auto mt-4 max-w-2xl text-muted-foreground">
                Download Q-Shield and experience next-generation authentication powered by AI,
                Behavioral Biometrics, and Post-Quantum Security.
              </p>

              <div className="mt-10 grid gap-4 sm:grid-cols-3">
                {downloads.map((d, i) => (
                  <motion.a
                    key={d.label}
                    href="#"
                    initial={{ opacity: 0, y: 16 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ delay: i * 0.08 }}
                    whileHover={{ y: -4 }}
                    className="group relative flex flex-col items-center gap-3 overflow-hidden rounded-2xl glass p-5 transition-colors hover:border-cyan/40"
                  >
                    <div className="grid h-12 w-12 place-items-center rounded-xl bg-gradient-to-br from-cyan to-blue text-background shadow-[0_0_25px_rgba(34,211,238,0.4)]">
                      <d.icon className="h-6 w-6" />
                    </div>
                    <div className="font-display text-sm font-semibold">{d.label}</div>
                    <div className="text-xs text-muted-foreground">{d.sub}</div>
                    <span
                      aria-hidden
                      className="absolute inset-x-6 bottom-0 h-px bg-gradient-to-r from-transparent via-cyan to-transparent opacity-0 transition-opacity duration-500 group-hover:opacity-100"
                    />
                  </motion.a>
                ))}
              </div>
            </div>
          </div>
        </Reveal>
      </div>
    </section>
  );
}

/* ----------------- FOOTER ----------------- */
export function Footer() {
  return (
    <footer className="relative border-t border-white/5 py-12">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-6 px-6 sm:flex-row">
        <div className="flex items-center gap-2 font-display font-semibold">
          <span className="grid h-8 w-8 place-items-center rounded-lg bg-gradient-to-br from-cyan to-blue">
            <Shield className="h-4 w-4 text-background" />
          </span>
          <span>
            Q<span className="text-cyan">-</span>SHIELD
          </span>
          <span className="ml-3 text-xs font-mono uppercase tracking-widest text-muted-foreground">
            Behavior · Intelligence · Security
          </span>
        </div>
        <div className="text-center text-xs text-muted-foreground sm:text-right">
          © 2026 Q-SHIELD Research Project<br />
          MBIT, CVM University, India
        </div>
      </div>
    </footer>
  );
}
