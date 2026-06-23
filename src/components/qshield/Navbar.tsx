import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ShieldCheck, Menu, X } from "lucide-react";

const links = [
  { href: "#problem", label: "Problem" },
  { href: "#features", label: "Features" },
  { href: "#technology", label: "Technology" },
  { href: "#industries", label: "Industries" },
  { href: "#team", label: "Team" },
  { href: "#download", label: "Download" },
];

export function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [open, setOpen] = useState(false);
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return (
    <motion.header
      initial={{ y: -40, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className={`fixed left-0 right-0 top-0 z-50 transition-all duration-300 ${
        scrolled ? "py-2" : "py-4"
      }`}
    >
      <div className="mx-auto max-w-7xl px-4 sm:px-6">
        <div
          className={`glass-strong flex items-center justify-between rounded-2xl transition-all duration-300 ${
            scrolled ? "px-4 py-2 shadow-[0_10px_40px_-10px_rgba(34,211,238,0.25)]" : "px-5 py-3"
          }`}
        >
          <a href="#top" className="flex items-center gap-2 font-display font-semibold">
            <span className="relative grid h-9 w-9 place-items-center rounded-xl bg-gradient-to-br from-cyan to-blue glow-cyan">
              <ShieldCheck className="h-5 w-5 text-background" />
            </span>
            <span className="text-base tracking-tight">
              Q<span className="text-cyan">-</span>SHIELD
            </span>
          </a>

          <nav className="hidden items-center gap-1 md:flex">
            {links.map((l) => (
              <a
                key={l.href}
                href={l.href}
                className="rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-white/5 hover:text-foreground"
              >
                {l.label}
              </a>
            ))}
          </nav>

          <div className="hidden md:block">
            <a
              href="#download"
              className="group relative inline-flex items-center gap-2 overflow-hidden rounded-lg bg-gradient-to-r from-cyan to-blue px-4 py-2 text-sm font-medium text-background transition-all hover:shadow-[0_0_25px_rgba(34,211,238,0.5)]"
            >
              Get Q-Shield
              <span className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/30 to-transparent transition-transform duration-700 group-hover:translate-x-full" />
            </a>
          </div>

          <button
            className="rounded-lg p-2 md:hidden"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>

        {open && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="glass mt-2 rounded-2xl p-2 md:hidden"
          >
            {links.map((l) => (
              <a
                key={l.href}
                href={l.href}
                onClick={() => setOpen(false)}
                className="block rounded-lg px-3 py-2 text-sm text-muted-foreground hover:bg-white/5 hover:text-foreground"
              >
                {l.label}
              </a>
            ))}
          </motion.div>
        )}
      </div>
    </motion.header>
  );
}
