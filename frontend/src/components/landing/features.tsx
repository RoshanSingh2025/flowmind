"use client";

import { motion } from "framer-motion";
import { BookOpen, Layers, MessagesSquare, ScanSearch, Sparkles, Workflow } from "lucide-react";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const FEATURES = [
  {
    icon: ScanSearch,
    accent: "indigo" as const,
    title: "Scene-aware understanding",
    description:
      "FlowMind segments a recording into meaningful steps — clicks, navigation, form fills — instead of treating it as one long undifferentiated clip.",
  },
  {
    icon: BookOpen,
    accent: "teal" as const,
    title: "Docs that write themselves",
    description:
      "Every walkthrough becomes a structured how-to guide, complete with numbered steps and the screenshots that matter.",
  },
  {
    icon: MessagesSquare,
    accent: "indigo" as const,
    title: "FAQs, extracted not guessed",
    description:
      "Common questions are pulled from what people actually struggled with on screen, not invented from a template.",
  },
  {
    icon: Layers,
    accent: "teal" as const,
    title: "Onboarding, assembled automatically",
    description:
      "Stitch multiple recordings into a single onboarding path new hires can follow at their own pace.",
  },
  {
    icon: Sparkles,
    accent: "indigo" as const,
    title: "An interactive knowledge base",
    description:
      "Every generated doc is indexed, so your team can ask a question in plain language and get the exact step back.",
  },
  {
    icon: Workflow,
    accent: "teal" as const,
    title: "Fits your existing workflow",
    description:
      "Drop in a recording from any tool you already use. No new recorder to install, no workflow to relearn.",
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

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-80px" }}
              transition={{ duration: 0.5, delay: (index % 3) * 0.08 }}
            >
              <Card className="h-full">
                <CardHeader>
                  <div
                    className={`mb-2 flex h-10 w-10 items-center justify-center rounded-lg ${
                      feature.accent === "indigo"
                        ? "bg-indigo/10 text-indigo"
                        : "bg-teal/10 text-teal"
                    }`}
                  >
                    <feature.icon className="h-5 w-5" strokeWidth={1.75} />
                  </div>
                  <CardTitle>{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <CardDescription>{feature.description}</CardDescription>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
