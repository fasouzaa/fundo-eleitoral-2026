import type { Metadata } from "next";
import { DM_Sans, Fraunces } from "next/font/google";
import { SiteHeader } from "@/components/SiteHeader";
import "./globals.css";

const sans = DM_Sans({
  variable: "--font-sans",
  subsets: ["latin"],
});

const display = Fraunces({
  variable: "--font-display",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Fundo Eleitoral 2026",
  description:
    "Distribuição pública do FEFC nas Eleições 2026 — por partido, cargo e UF. Dados do TSE.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="pt-BR"
      className={`${sans.variable} ${display.variable} h-full antialiased`}
    >
      <body className="flex min-h-full flex-col">
        <SiteHeader />
        <main className="mx-auto w-full max-w-6xl flex-1 px-4 py-8 sm:px-6 sm:py-10">
          {children}
        </main>
        <footer className="border-t border-[var(--line)] bg-[var(--surface)]/80">
          <div className="mx-auto max-w-6xl px-4 py-6 text-xs text-[var(--muted)] sm:px-6">
            Fonte: Tribunal Superior Eleitoral (dados abertos). Projeto
            independente, sem vínculo oficial com o TSE. Valores de
            candidato/UF/cargo refletem a prestação de contas na data de
            corte.
          </div>
        </footer>
      </body>
    </html>
  );
}
