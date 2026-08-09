"""Export utilities: render a completed upload's generated documents as a
Markdown bundle or a PDF. Self-contained (no FastAPI/SQLAlchemy imports),
consistent with the rest of `app.utils`.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExportableResults:
    original_filename: str
    summary: str | None
    documentation: str | None
    sop: str | None
    faq: str | None
    transcript: str | None


def build_markdown_bundle(results: ExportableResults) -> str:
    """Combine all generated sections into a single Markdown document."""
    sections = [f"# {results.original_filename}\n"]

    if results.summary:
        sections.append(f"## Summary\n\n{results.summary}\n")
    if results.documentation:
        sections.append(f"## Documentation\n\n{results.documentation}\n")
    if results.sop:
        sections.append(f"## Standard Operating Procedure\n\n{results.sop}\n")
    if results.faq:
        sections.append(f"## FAQ\n\n{results.faq}\n")
    if results.transcript:
        sections.append(f"## Full Transcript\n\n{results.transcript}\n")

    return "\n".join(sections)


def build_pdf_bundle(results: ExportableResults) -> bytes:
    """Render the same content as a simple PDF using fpdf2 (pure-Python, no
    system dependencies — chosen specifically to keep this free/lightweight
    per project constraints)."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 16)
    pdf.multi_cell(0, 10, results.original_filename)
    pdf.ln(4)

    def _section(title: str, body: str | None) -> None:
        if not body:
            return
        pdf.set_font("Helvetica", "B", 13)
        pdf.multi_cell(0, 8, title)
        pdf.ln(1)
        pdf.set_font("Helvetica", "", 11)
        safe_body = body.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 6, safe_body)
        pdf.ln(4)

    _section("Summary", results.summary)
    _section("Documentation", results.documentation)
    _section("Standard Operating Procedure", results.sop)
    _section("FAQ", results.faq)
    _section("Full Transcript", results.transcript)

    return bytes(pdf.output())
