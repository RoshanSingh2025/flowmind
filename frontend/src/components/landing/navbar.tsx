"use client";

import { motion } from "framer-motion";
import { Menu, Workflow, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { useAppStore } from "@/store/use-app-store";

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "Architecture", href: "#architecture" },
  { label: "Demo", href: "#demo" },
];

export function Navbar() {
  const isMobileNavOpen = useAppStore((s) => s.isMobileNavOpen);
  const toggleMobileNav = useAppStore((s) => s.toggleMobileNav);
  const closeMobileNav = useAppStore((s) => s.closeMobileNav);

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="fixed inset-x-0 top-4 z-50 mx-auto w-[92%] max-w-5xl"
    >
      <nav className="glass-panel flex items-center justify-between rounded-2xl px-5 py-3">
        <a href="#" className="flex items-center gap-2 font-display text-lg font-semibold">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo to-teal text-background">
            <Workflow className="h-4.5 w-4.5" strokeWidth={2.5} />
          </span>
          FlowMind
        </a>

        <div className="hidden items-center gap-8 md:flex">
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-sm text-muted transition-colors hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <Button variant="ghost" size="sm">
            Sign in
          </Button>
          <Button variant="primary" size="sm">
            Get early access
          </Button>
        </div>

        <button
          className="text-foreground md:hidden"
          onClick={toggleMobileNav}
          aria-label="Toggle navigation menu"
        >
          {isMobileNavOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </nav>

      {isMobileNavOpen && (
        <motion.div
          initial={{ opacity: 0, y: -8 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass-panel mt-2 flex flex-col gap-1 rounded-2xl p-4 md:hidden"
        >
          {NAV_LINKS.map((link) => (
            <a
              key={link.href}
              href={link.href}
              onClick={closeMobileNav}
              className="rounded-lg px-3 py-2 text-sm text-muted hover:bg-white/5 hover:text-foreground"
            >
              {link.label}
            </a>
          ))}
          <Button variant="primary" size="sm" className="mt-2">
            Get early access
          </Button>
        </motion.div>
      )}
    </motion.header>
  );
}
