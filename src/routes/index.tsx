import { createFileRoute } from "@tanstack/react-router";
import { Navbar } from "@/components/qshield/Navbar";
import { Hero } from "@/components/qshield/Hero";
import { MouseGlow } from "@/components/qshield/BackgroundFX";
import {
  ProblemSection,
  MetricsSection,
  FeaturesSection,
  TechnologySection,
  IndustriesSection,
  TeamSection,
  DownloadSection,
  Footer,
} from "@/components/qshield/Sections";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Q-SHIELD — Quantum-Inspired Behavioral Authentication" },
      {
        name: "description",
        content:
          "Q-SHIELD is a next-generation authentication framework combining behavioral biometrics, AI, continuous authentication, and post-quantum cryptography.",
      },
      { property: "og:title", content: "Q-SHIELD — Quantum-Inspired Behavioral Authentication" },
      {
        property: "og:description",
        content:
          "Protect digital identities against modern cyber threats and future quantum attacks.",
      },
    ],
  }),
  component: Index,
});

function Index() {
  return (
    <main className="relative min-h-screen overflow-hidden bg-[#050816]">
      <MouseGlow />
      <Navbar />
      <Hero />
      <ProblemSection />
      <MetricsSection />
      <FeaturesSection />
      <TechnologySection />
      <IndustriesSection />
      <TeamSection />
      <DownloadSection />
      <Footer />
    </main>
  );
}
