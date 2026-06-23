import { useEffect, useRef } from "react";

export function MouseGlow() {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!ref.current) return;
      ref.current.style.transform = `translate(${e.clientX - 300}px, ${e.clientY - 300}px)`;
    };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, []);
  return (
    <div
      ref={ref}
      aria-hidden
      className="pointer-events-none fixed left-0 top-0 z-0 h-[600px] w-[600px] rounded-full opacity-40 transition-transform duration-300 ease-out"
      style={{
        background: "radial-gradient(circle, rgba(34,211,238,0.18), transparent 60%)",
        filter: "blur(40px)",
      }}
    />
  );
}

export function Particles({ count = 40 }: { count?: number }) {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      {Array.from({ length: count }).map((_, i) => {
        const size = 1 + Math.random() * 3;
        const left = Math.random() * 100;
        const top = Math.random() * 100;
        const delay = Math.random() * 8;
        const duration = 6 + Math.random() * 10;
        return (
          <span
            key={i}
            className="absolute rounded-full"
            style={{
              left: `${left}%`,
              top: `${top}%`,
              width: size,
              height: size,
              background: i % 3 === 0 ? "#22D3EE" : i % 3 === 1 ? "#3B82F6" : "#67e8f9",
              boxShadow: `0 0 ${size * 4}px currentColor`,
              color: i % 3 === 0 ? "#22D3EE" : "#3B82F6",
              animation: `float ${duration}s ease-in-out ${delay}s infinite`,
              opacity: 0.5 + Math.random() * 0.4,
            }}
          />
        );
      })}
    </div>
  );
}

export function CyberGrid() {
  return (
    <div
      aria-hidden
      className="pointer-events-none absolute inset-0 cyber-grid opacity-40"
      style={{ animation: "grid-shift 30s linear infinite", maskImage: "radial-gradient(ellipse at center, black 30%, transparent 80%)" }}
    />
  );
}
