import { Workflow } from "lucide-react";

// Only links with a real destination are rendered as clickable — the rest
// (no page/section exists for them yet) render as plain text so they don't
// look interactive when they aren't.
const FOOTER_LINKS: Record<string, { label: string; href: string | null }[]> = {
  Product: [
    { label: "Features", href: "#features" },
    { label: "Architecture", href: "#architecture" },
    { label: "Demo", href: "#demo" },
    { label: "Changelog", href: null },
  ],
  Company: [
    { label: "About", href: null },
    { label: "Careers", href: null },
    { label: "Blog", href: null },
  ],
  Resources: [
    { label: "Docs", href: null },
    { label: "API status", href: null },
    { label: "Support", href: null },
  ],
};

export function Footer() {
  return (
    <footer className="relative border-t border-border/10 py-16">
      <div className="container">
        <div className="grid gap-10 md:grid-cols-[1.5fr_1fr_1fr_1fr]">
          <div>
            <a href="#" className="flex items-center gap-2 font-display text-lg font-semibold">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo to-teal text-background">
                <Workflow className="h-4.5 w-4.5" strokeWidth={2.5} />
              </span>
              FlowMind
            </a>
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-muted">
              The AI Workflow Copilot that turns screen recordings into documentation, FAQs, and an
              interactive knowledge base.
            </p>
          </div>

          {Object.entries(FOOTER_LINKS).map(([heading, links]) => (
            <div key={heading}>
              <h4 className="font-display text-sm font-semibold text-foreground">{heading}</h4>
              <ul className="mt-4 space-y-2.5">
                {links.map((link) =>
                  link.href ? (
                    <li key={link.label}>
  <a
    href={link.href}
    className="text-sm text-muted transition-colors hover:text-foreground"
  >
    {link.label}
  </a>
</li>
                  ) : (
                    <li key={link.label}>
                      <span className="text-sm text-muted/50">{link.label} · coming soon</span>
                    </li>
                  )
                )}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-14 flex flex-col items-center justify-between gap-4 border-t border-border/10 pt-8 text-xs text-muted md:flex-row">
          <span>&copy; {new Date().getFullYear()} FlowMind. All rights reserved.</span>
          <div className="flex gap-6">
            <span className="text-muted/50">Privacy · coming soon</span>
            <span className="text-muted/50">Terms · coming soon</span>
          </div>
        </div>
      </div>
    </footer>
  );
}