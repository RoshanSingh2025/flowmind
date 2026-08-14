"use client";

import { motion } from "framer-motion";
import { BookOpen, Layers, MessagesSquare, ScanSearch, Sparkles, Workflow } from "lucide-react";

const FEATURES = [
  {
    icon: ScanSearch,
    accent: "indigo" as const,
    title: "Scene-aware understanding",
    description:
      "FlowMind segments a recording into meaningful steps — clicks, navigation, form fills — instead of treating it as one long undifferentiated clip.",
    span: "md:col-span-2 md:row-span-1",
  },
  {
    icon: Sparkles,
    accent: "indigo" as const,
    title: "An interactive knowledge base",
    description:
      "Every generated doc is indexed, so your team can ask a question in plain language and get the exact step back — the payoff of the whole pipeline.",
    span: "md:col-span-2 md:row-span-2",
    featured: true,
  },
  {
    icon: BookOpen,
    accent: "teal" as const,
    title: "Docs that write themselves",
    description:
      "Every walkthrough becomes a structured how-to guide, complete with numbered steps and the screenshots that matter.",
    span: "md:col-span-1 md:row-span-1",
  },
  {
    icon: MessagesSquare,
    accent: "indigo" as const,
    title: "FAQs, extracted not guessed",
    description:
      "Common questions are pulled from what people actually struggled with on screen, not invented from a template.",
    span: "md:col-span-1 md:row-span-1",
  },
  {
    icon: Layers,
    accent: "teal" as const,
    title: "Onboarding, assembled automatically",
    description:
      "Stitch multiple recordings into a single onboarding path new hires can follow at their own pace.",
    span: "md:col-span-1 md:row-span-1",
  },
  {
    icon: Workflow,
    accent: "teal" as const,
    title: "Fits your existing workflow",
    description:
      "Drop in a recording from any tool you already use. No new recorder to install, no workflow to relearn.",
    span: "md:col-span-3 md:row-span-1",
  },
];

export function Features() {
  return (
    <section id="features" className="relative py-28">
      <div className="container">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <span className="font-mono text-xs uppercase tracking-[0.2em] text-indigo/70">
            What it does
          </span>
          <h2 className="mt-4 font-display text-3xl font-semibold tracking-tight md:text-4xl">
            From raw footage to a knowledge base people actually use
          </h2>
        </div>

        {/* Bento Grid — deliberately uneven cell sizes to establish
            hierarchy: the knowledge-base feature (the actual payoff)
            gets the largest, tallest cell. */}
        <div className="grid auto-rows-[minmax(0,1fr)] gap-5 md:grid-cols-4">
          {FEATURES.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: (index % 3) * 0.08 }}
              className={feature.span}
            >
              <div
                className={`bento-cell glass-panel-hover flex h-full flex-col p-6 ${
                  feature.featured ? "justify-between" : ""
                }`}
              >
                <div
                  className={`mb-4 flex items-center justify-center rounded-xl ${
                    feature.featured ? "h-12 w-12" : "h-10 w-10"
                  } ${
                    feature.accent === "indigo"
                      ? "bg-indigo/10 text-indigo"
                      : "bg-teal/10 text-teal"
                  }`}
                >
                  <feature.icon
                    className={feature.featured ? "h-6 w-6" : "h-5 w-5"}
                    strokeWidth={1.75}
                  />
                </div>
                <h3
                  className={`font-display font-semibold text-foreground ${
                    feature.featured ? "text-2xl" : "text-lg"
                  }`}
                >
                  {feature.title}
                </h3>
                <p
                  className={`mt-2 leading-relaxed text-muted ${
                    feature.featured ? "text-sm md:text-base" : "text-sm"
                  }`}
                >
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}