"use client";

import { AnimatePresence, motion } from "framer-motion";
import { Menu, Workflow, X } from "lucide-react";
import Link from "next/link";
import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { useAppStore } from "@/store/use-app-store";

const NAV_LINKS = [
  { label: "Features", href: "#features" },
  { label: "Architecture", href: "#architecture" },
  { label: "Demo", href: "#demo" },
];

const mobileMenuVariants = {
  hidden: {
    opacity: 0,
    y: -8,
    height: 0,
  },
  show: {
    opacity: 1,
    y: 0,
    height: "auto",
    transition: {
      duration: 0.25,
      ease: "easeOut" as const,
      staggerChildren: 0.05,
    },
  },
  exit: {
    opacity: 0,
    y: -8,
    height: 0,
    transition: {
      duration: 0.2,
      ease: "easeIn" as const,
    },
  },
};

const mobileLinkVariants = {
  hidden: {
    opacity: 0,
    x: -8,
  },
  show: {
    opacity: 1,
    x: 0,
  },
};

export function Navbar() {
  const isMobileNavOpen = useAppStore((state) => state.isMobileNavOpen);
  const toggleMobileNav = useAppStore((state) => state.toggleMobileNav);
  const closeMobileNav = useAppStore((state) => state.closeMobileNav);

  const [isScrolled, setIsScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 8);
    };

    handleScroll();

    window.addEventListener("scroll", handleScroll, { passive: true });

    return () => {
      window.removeEventListener("scroll", handleScroll);
    };
  }, []);

  useEffect(() => {
    if (!isMobileNavOpen) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        closeMobileNav();
      }
    };

    window.addEventListener("keydown", handleKeyDown);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [isMobileNavOpen, closeMobileNav]);

  return (
    <motion.header
      initial={{ y: -24, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      className="fixed inset-x-0 top-4 z-50 mx-auto w-[92%] max-w-5xl"
    >
      <nav
        className={`liquid-glass flex items-center justify-between rounded-2xl px-5 py-3 transition-[box-shadow,border-color] duration-300 ${
          isScrolled
            ? "border-border/20 shadow-[0_8px_40px_-16px_hsl(222_60%_3%/0.7)]"
            : ""
        }`}
      >
        <a
          href="#"
          className="flex items-center gap-2 font-display text-lg font-semibold"
        >
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
    className="group relative text-sm text-muted transition-colors hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-teal focus-visible:ring-offset-2"
  >
    {link.label}
    <span className="absolute -bottom-1 left-0 h-px w-0 bg-gradient-to-r from-indigo to-teal transition-all duration-300 group-hover:w-full" />
  </a>
))}
        </div>

        <div className="hidden items-center gap-3 md:flex">
          <Button
            variant="ghost"
            size="sm"
            disabled
            title="Sign in is coming soon"
            aria-disabled="true"
          >
            Sign in
          </Button>

          {/* If "primary" gives a TypeScript error,
              replace variant="primary" with variant="default". */}
          <Button variant="primary" size="sm" asChild>
            <Link href="/upload">Get early access</Link>
          </Button>
        </div>

        <button
          type="button"
          onClick={toggleMobileNav}
          aria-label="Toggle navigation menu"
          aria-expanded={isMobileNavOpen}
          aria-controls="mobile-nav-panel"
          className="-m-2 p-2 text-foreground md:hidden"
        >
          {isMobileNavOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </button>
      </nav>

      <AnimatePresence>
        {isMobileNavOpen && (
          <motion.div
            id="mobile-nav-panel"
            initial="hidden"
            animate="show"
            exit="exit"
            variants={mobileMenuVariants}
            className="liquid-glass mt-2 overflow-hidden rounded-2xl md:hidden"
          >
            <div className="flex flex-col gap-1 p-4">
              {NAV_LINKS.map((link) => (
                <motion.a
                  key={link.href}
                  variants={mobileLinkVariants}
                  href={link.href}
                  onClick={closeMobileNav}
                  className="rounded-lg px-3 py-2 text-sm text-muted transition-colors hover:bg-white/5 hover:text-foreground"
                >
                  {link.label}
                </motion.a>
              ))}

              <motion.div variants={mobileLinkVariants}>
                {/* If "primary" gives a TypeScript error,
                    replace variant="primary" with variant="default". */}
                <Button
                  variant="primary"
                  size="sm"
                  className="mt-2 w-full"
                  asChild
                >
                  <Link href="/upload" onClick={closeMobileNav}>
                    Get early access
                  </Link>
                </Button>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.header>
  );
}