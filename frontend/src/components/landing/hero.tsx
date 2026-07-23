"use client";

import { motion } from "framer-motion";
import { ArrowRight, Circle, PlayCircle } from "lucide-react";

import { Button } from "@/components/ui/button";

const FILMSTRIP_FRAMES = [0, 1, 2, 3];

const DOC_LINES = [
  { width: "w-4/5", delay: 0 },
  { width: "w-full", delay: 0.08 },
  { width: "w-3/5", delay: 0.16 },
  { width: "w-2/3", delay: 0.24 },
];

/**
 * Signature element: a filmstrip (the raw recording, indigo) resolves into a
 * structured document (the generated output, teal) along a connecting beam.
 * This is the one motif the whole page is built around — it literally is the
 * product's core transformation, not a decorative flourish.
 */
function RecordingToDocVisual() {
  return (
    <div className="relative flex items-center gap-6">
      {/* Filmstrip — raw input */}
      <div className="flex flex-col gap-2">
        {FILMSTRIP_FRAMES.map((frame) => (
          <motion.div
            key={frame}
            initial={{ opacity: 0, x: -16 }}
            animate={{ opacity: [0.5, 1, 0.5], x: 0 }}
            transition={{
              opacity: { duration: 2.4, repeat: Infinity, delay: frame * 0.3 },
              x: { duration: 0.5, delay: frame * 0.1 },
            }}
            className="relative flex h-12 w-16 items-center justify-center rounded-md border border-indigo/25 bg-indigo/[0.07]"
          >
            <PlayCircle className="h-4 w-4 text-indigo/70" strokeWidth={1.75} />
            <span className="absolute -left-1 top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-background ring-1 ring-indigo/40" />
          </motion.div>
        ))}
      </div>

      {/* Connecting beam */}
      <div className="relative h-40 w-16 shrink-0 md:w-24">
        <svg viewBox="0 0 100 160" className="h-full w-full" preserveAspectRatio="none">
          <defs>
            <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="hsl(var(--accent-indigo))" />
              <stop offset="100%" stopColor="hsl(var(--accent-teal))" />
            </linearGradient>
          </defs>
          <path
            d="M0 80 C 40 80, 60 80, 100 80"
            stroke="url(#beam)"
            strokeWidth="2"
            strokeDasharray="6 6"
            fill="none"
            opacity={0.6}
          />
        </svg>
        <motion.span
          className="glow-dot absolute top-1/2 h-2 w-2 -translate-y-1/2 rounded-full bg-teal text-teal"
          animate={{ left: ["0%", "92%"] }}
          transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
        />
      </div>

      {/* Generated document — structured output */}
      <div className="flex w-48 flex-col gap-2.5 rounded-xl border border-teal/25 bg-teal/[0.06] p-4">
        <div className="mb-1 flex items-center gap-1.5">
          <Circle className="h-2 w-2 fill-teal text-teal" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-teal/80">
            Doc generated
          </span>
        </div>
        {DOC_LINES.map((line, i) => (
          <motion.div
            key={i}
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.6, delay: 0.4 + line.delay, ease: "easeOut" }}
            style={{ transformOrigin: "left" }}
            className={`h-2 ${line.width} rounded-full bg-teal/25`}
          />
        ))}
      </div>
    </div>
  );
}

export function Hero() {
  return (
    <section className="relative overflow-hidden pb-28 pt-40 md:pt-48">
      <div className="grid-overlay bg-mesh-glow absolute inset-0 -z-10 [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,black,transparent)]" />

      <div className="container flex flex-col items-center text-center">
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="glass-panel mb-8 inline-flex items-center gap-2 rounded-full px-4 py-1.5"
        >
          <span className="h-1.5 w-1.5 animate-pulse-slow rounded-full bg-teal" />
          <span className="text-xs font-medium text-muted">
            Now onboarding early design-partner teams
          </span>
        </motion.div>

        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="max-w-3xl font-display text-4xl font-semibold leading-[1.1] tracking-tight md:text-6xl"
        >
          Every screen recording is <span className="text-gradient">undocumented knowledge.</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-6 max-w-xl text-balance text-base text-muted md:text-lg"
        >
          FlowMind watches how your product actually gets used and turns that footage into
          documentation, FAQs, onboarding guides, and a knowledge base your team can ask questions
          against.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-10 flex flex-col gap-3 sm:flex-row"
        >
          <Button size="lg">
            Get early access <ArrowRight className="h-4 w-4" />
          </Button>
          <Button size="lg" variant="outline">
            Watch a 90s demo
          </Button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7, delay: 0.4, ease: "easeOut" }}
          className="glass-panel mt-20 hidden rounded-2xl p-8 md:block"
        >
          <RecordingToDocVisual />
        </motion.div>
      </div>
    </section>
  );
}
