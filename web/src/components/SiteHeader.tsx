import Link from "next/link";

const links = [
  { href: "/", label: "Visão geral" },
  { href: "/explorar", label: "Explorar" },
  { href: "/criterios", label: "Critérios" },
  { href: "/metodologia", label: "Metodologia" },
];

export function SiteHeader() {
  return (
    <header className="border-b border-[var(--line)] bg-[var(--surface)]/90 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <Link href="/" className="group">
          <p className="font-[family-name:var(--font-display)] text-xl tracking-tight text-[var(--ink)] sm:text-2xl">
            Fundo Eleitoral{" "}
            <span className="text-[var(--accent)]">2026</span>
          </p>
          <p className="text-xs text-[var(--muted)] group-hover:text-[var(--ink)]">
            Distribuição pública do FEFC · dados do TSE
          </p>
        </Link>
        <nav className="flex gap-1 text-sm">
          {links.map((l) => (
            <Link
              key={l.href}
              href={l.href}
              className="rounded-md px-3 py-1.5 text-[var(--muted)] transition hover:bg-[var(--wash)] hover:text-[var(--ink)]"
            >
              {l.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
