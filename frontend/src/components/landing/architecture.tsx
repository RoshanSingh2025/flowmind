"use client";

import { motion } from "framer-motion";
import { Bot, Database, FileStack, MonitorPlay, Search } from "lucide-react";

import { Badge } from "@/components/ui/badge";

const PIPELINE = [
  {
    step: "01",
    icon: MonitorPlay,
    title: "Ingest",
    description: "A screen recording is uploaded and stored, metadata captured immediately.",
  },
  {
    step: "02",
    icon: Bot,
    title: "Agents",
    description:
      "A pipeline of agents transcribes, segments, and interprets what happened on screen.",
  },
  {
    step: "03",
    icon: FileStack,
    title: "Generate",
    description: "Structured docs, FAQs, and onboarding guides are drafted from that understanding.",
  },
  {
    step: "04",
    icon: Database,
    title: "Embed",
    description: "Every generated doc is chunked and embedded into the vector store.",
  },
  {
    step: "05",
    icon: Search,
    title: "Retrieve",
    description: "Your team asks a question; the knowledge base answers with the exact source.",
  },
];

export function Architecture() {
  return (
    <section id="architecture" className="relative py-28">
      <div className="container">
        <div className="mx-auto mb-16 max-w-2xl text-center">
          <span className="font-mono text-xs uppercase tracking-[0.2em] text-teal/70">
            How it works
          </span>
          <h2 className="mt-4 font-display text-3xl font-semibold tracking-tight md:text-4xl">
            A real pipeline, not a black box
          </h2>
          <p className="mt-4 text-muted">
            Each recording moves through five concrete stages on its way from raw footage to an
            answer your team can query.
          </p>
        </div>

        <div className="relative">
          {/* connecting line, desktop only */}
          <div className="absolute left-0 right-0 top-9 hidden h-px bg-gradient-to-r from-indigo/40 via-teal/40 to-indigo/40 lg:block" />

          <div className="grid gap-6 lg:grid-cols-5">
            {PIPELINE.map((stage, index) => (
              <motion.div
                key={stage.step}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: "-80px" }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="relative flex flex-col items-start gap-4"
              >
                <div className="glass-panel relative z-10 flex h-[72px] w-[72px] items-center justify-center rounded-2xl">
                  <stage.icon className="h-6 w-6 text-foreground" strokeWidth={1.5} />
                  <span className="absolute -right-2 -top-2 font-mono text-[10px] text-muted">
                    {stage.step}
                  </span>
                </div>
                <div>
                  <h3 className="font-display text-lg font-semibold">{stage.title}</h3>
                  <p className="mt-1.5 text-sm leading-relaxed text-muted">{stage.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="glass-panel mt-16 flex flex-col gap-6 rounded-2xl p-8 md:flex-row md:items-center md:justify-between">
          <div>
            <Badge variant="outline">Today&apos;s foundation</Badge>
            <p className="mt-3 max-w-md text-sm text-muted">
              This delivery ships stages 01 and the surrounding infrastructure — API, database,
              queues, and vector store are wired and ready. Stages 02–05 are the next phase.
            </p>
          </div>
          <div className="flex flex-wrap gap-2">
            {["FastAPI", "PostgreSQL", "Redis", "Qdrant", "Next.js 15"].map((tech) => (
              <span
                key={tech}
                className="rounded-full border border-border/15 bg-white/[0.03] px-3 py-1 font-mono text-xs text-muted"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}