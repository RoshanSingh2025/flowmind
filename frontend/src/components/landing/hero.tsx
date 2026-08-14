"use client";

import { motion } from "framer-motion";
import { ArrowRight, Bot, MessagesSquare, PlayCircle } from "lucide-react";
import Link from "next/link";

import { Button } from "@/components/ui/button";

const containerVariants = {
  hidden: {},
  show: {
    transition: { staggerChildren: 0.1, delayChildren: 0.05 },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" as const } },
};

/** Short animated connector between two pipeline stages. Rotates to vertical on mobile. */
function StageConnector() {
  return (
    <div className="relative h-10 w-8 shrink-0 rotate-90 md:h-px md:w-12 md:rotate-0 lg:w-16">
      <svg viewBox="0 0 100 20" className="h-full w-full" preserveAspectRatio="none">
        <path
          d="M0 10 L100 10"
          stroke="hsl(var(--border) / 0.25)"
          strokeWidth="2"
          strokeDasharray="5 5"
          fill="none"
        />
      </svg>
      <motion.span
        className="glow-dot absolute top-1/2 h-1.5 w-1.5 -translate-y-1/2 rounded-full bg-teal text-teal"
        animate={{ left: ["0%", "94%"] }}
        transition={{ duration: 1.6, repeat: Infinity, ease: "easeInOut" }}
      />
    </div>
  );
}

/**
 * The complete product journey, compressed into three stages: a raw
 * recording is *understood* by an agent pipeline, then resolved into an
 * answerable knowledge base. This is deliberately three stages, not two —
 * the "answer" stage is the actual payoff and was previously missing
 * entirely from the hero.
 */
function PipelineVisual() {
  return (
    <div className="flex flex-col items-center gap-3 md:flex-row md:items-start md:gap-0">
      {/* Stage 1 — Record */}
      <div className="flex flex-col items-center gap-3">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="relative flex h-16 w-16 items-center justify-center rounded-xl border border-indigo/25 bg-indigo/[0.07]"
        >
          <PlayCircle className="h-6 w-6 text-indigo/80" strokeWidth={1.75} />
          <span className="glow-dot absolute -right-1 -top-1 h-2 w-2 animate-pulse-slow rounded-full bg-indigo text-indigo" />
        </motion.div>
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted">Record</span>
      </div>

      <StageConnector />

      {/* Stage 2 — Understand */}
      <div className="flex flex-col items-center gap-3">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="relative flex h-16 w-16 items-center justify-center rounded-xl border border-border/15 bg-white/[0.03]"
        >
          <Bot className="h-6 w-6 text-foreground/70" strokeWidth={1.75} />
          <div className="absolute -bottom-1.5 flex gap-0.5">
            {[0, 1, 2].map((dot) => (
              <span
                key={dot}
                style={{ animationDelay: `${dot * 0.3}s` }}
                className="h-1 w-1 animate-pulse-slow rounded-full bg-foreground/40"
              />
            ))}
          </div>
        </motion.div>
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted">
          Understand
        </span>
      </div>

      <StageConnector />

      {/* Stage 3 — Answer: the payoff, so it gets the richest treatment */}
      <div className="flex flex-col items-center gap-3">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex w-56 flex-col gap-3 rounded-xl border border-teal/25 bg-teal/[0.06] p-4"
        >
          <div className="flex items-center gap-1.5">
            <MessagesSquare className="h-3.5 w-3.5 text-teal" strokeWidth={2} />
            <span className="font-mono text-[10px] uppercase tracking-wider text-teal/80">
              Knowledge base
            </span>
          </div>
          <div className="rounded-full bg-white/5 px-3 py-1.5 text-left text-xs text-foreground">
             &ldquo;How do I reset a password?&rdquo;
          </div>
          <div className="space-y-1.5 pl-1">
            <div className="h-1.5 w-full rounded-full bg-teal/25" />
            <div className="h-1.5 w-3/5 rounded-full bg-teal/15" />
          </div>
        </motion.div>
        <span className="font-mono text-[10px] uppercase tracking-wider text-muted">Answer</span>
      </div>
    </div>
  );
}

export function Hero() {
  return (
    <section className="relative overflow-hidden pb-24 pt-36 md:pb-32 md:pt-48">
      <div className="grid-overlay bg-mesh-glow absolute inset-0 -z-10 [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,black,transparent)]" />
      {/* Aurora UI atmosphere — drifting color fields, hero-only. */}
      <div
        aria-hidden="true"
        className="aurora-field absolute inset-[-10%] -z-10 animate-aurora [mask-image:radial-gradient(ellipse_65%_55%_at_50%_20%,black,transparent)]"
      />

      <motion.div
        initial="hidden"
        animate="show"
        variants={containerVariants}
        className="container flex flex-col items-center text-center"
      >
        <motion.div
          variants={itemVariants}
          whileHover={{ scale: 1.03 }}
          className="glass-panel mb-8 inline-flex items-center gap-2 rounded-full px-4 py-1.5 transition-shadow hover:shadow-[0_0_24px_-8px_hsl(var(--accent-teal)/0.5)]"
        >
          <span className="h-1.5 w-1.5 animate-pulse-slow rounded-full bg-teal" />
          <span className="text-xs font-medium text-muted">
            Now onboarding early design-partner teams
          </span>
        </motion.div>

        <motion.h1
          variants={itemVariants}
          className="max-w-4xl text-balance font-display text-4xl font-semibold leading-[1.08] tracking-tight md:text-6xl"
        >
          Screens recorded. Knowledge captured.{" "}
          <span className="text-gradient">Questions answered.</span>
        </motion.h1>

        <motion.p
          variants={itemVariants}
          className="mt-6 max-w-xl text-balance text-base leading-relaxed text-muted md:text-lg"
        >
          FlowMind watches how your product gets used, then turns that footage into
          documentation, FAQs, and a knowledge base your team can query directly.
        </motion.p>

        <motion.div
          variants={itemVariants}
          className="mt-10 flex flex-col items-center gap-4 sm:flex-row sm:gap-6"
        >
          <Button size="lg" className="w-full sm:w-auto" asChild>
            <Link href="/upload">
              Get early access
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>

          <a
            href="#demo"
            className="group inline-flex items-center gap-1.5 text-sm font-medium text-muted transition-colors hover:text-foreground"
          >
            <PlayCircle className="h-4 w-4 text-indigo transition-transform group-hover:scale-110" />
            Watch a 90s demo
          </a>
        </motion.div>

        <motion.p variants={itemVariants} className="mt-4 text-xs text-muted/70">
          Free during the design-partner phase · No credit card required
        </motion.p>

        <motion.div
          variants={itemVariants}
          className="glass-panel mt-16 w-full max-w-fit rounded-2xl p-6 md:mt-20 md:p-8"
        >
          <PipelineVisual />
        </motion.div>
      </motion.div>
    </section>
  );
}