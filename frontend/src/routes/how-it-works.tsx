import { createFileRoute } from "@tanstack/react-router";
import { ArrowRight, BrainCircuit, Cpu, Database, Gauge, Layers, MessageSquareText, Network, Route as RouteIcon, ShieldCheck, Sparkles, Zap } from "lucide-react";
import { Card } from "@/components/ui/card";

export const Route = createFileRoute("/how-it-works")({
  head: () => ({
    meta: [
      { title: "How it works — Helix Support" },
      { name: "description", content: "The architecture, models, and stack behind the Helix customer support AI agent." },
      { property: "og:title", content: "How it works — Helix Support" },
      { property: "og:description", content: "Architecture, models, and tech stack behind Helix." },
    ],
  }),
  component: HowItWorks,
});

const STEPS = [
  { icon: MessageSquareText, title: "Ingest", body: "Customer message arrives via web chat, email, or API. Helix normalizes language, redacts PII, and prepares the payload for classification." },
  { icon: BrainCircuit, title: "Classify", body: "A fine-tuned DistilBERT model assigns one of 7 intent classes. A calibrated SVM ensemble produces a confidence score." },
  { icon: RouteIcon, title: "Resolve or route", body: "Above the 70% confidence threshold, Helix generates a grounded reply and updates the ticket. Otherwise it hands off with full context to a human agent." },
];

const STACK = [
  { icon: BrainCircuit, label: "DistilBERT", sub: "Intent model" },
  { icon: Gauge, label: "SVM ensemble", sub: "Confidence" },
  { icon: Network, label: "FastAPI", sub: "Inference API" },
  { icon: Layers, label: "React + TanStack", sub: "Dashboard" },
  { icon: Database, label: "Postgres", sub: "Tickets & orders" },
  { icon: Cpu, label: "ONNX Runtime", sub: "Edge inference" },
  { icon: ShieldCheck, label: "PII Guard", sub: "Privacy layer" },
  { icon: Zap, label: "Redis", sub: "Cache & queue" },
];

function HowItWorks() {
  return (
    <div className="space-y-12">
      <section className="relative overflow-hidden rounded-3xl border border-border/60 surface-card p-8 sm:p-12">
        <div className="absolute -top-20 right-0 h-72 w-72 rounded-full bg-primary/20 blur-3xl" aria-hidden />
        <div className="relative max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-background/40 px-3 py-1 text-xs text-muted-foreground">
            <Sparkles className="h-3.5 w-3.5 text-primary-glow" />
            Inside Helix
          </div>
          <h1 className="gradient-text mt-5 text-4xl font-semibold tracking-tight sm:text-5xl">How it works</h1>
          <p className="mt-4 text-base text-muted-foreground">
            Helix is a lightweight, production-grade pipeline that turns raw customer messages into resolved tickets — or into a clean hand-off to a human when it isn't confident enough.
          </p>
        </div>
      </section>

      <section>
        <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">The pipeline</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          {STEPS.map((s, i) => (
            <Card key={s.title} className="surface-card group relative border-border/60 p-6 transition-transform duration-300 hover:-translate-y-1">
              <div className="flex items-center justify-between">
                <div className="grid h-11 w-11 place-items-center rounded-xl gradient-primary glow-shadow">
                  <s.icon className="h-5 w-5 text-white" />
                </div>
                <span className="text-xs font-mono text-muted-foreground">0{i + 1}</span>
              </div>
              <div className="mt-5 text-lg font-semibold">{s.title}</div>
              <p className="mt-2 text-sm text-muted-foreground">{s.body}</p>
              {i < STEPS.length - 1 && (
                <ArrowRight className="absolute -right-3 top-1/2 hidden h-5 w-5 -translate-y-1/2 text-primary-glow md:block" />
              )}
            </Card>
          ))}
        </div>
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <AccuracyCard name="DistilBERT" desc="Fine-tuned intent classifier" value={99.75} hue="primary" />
        <AccuracyCard name="SVM ensemble" desc="Calibrated confidence scoring" value={98.93} hue="cyan" />
      </section>

      <section>
        <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">Tech stack</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {STACK.map((s) => (
            <Card key={s.label} className="surface-card group flex items-center gap-3 border-border/60 p-4 transition-colors hover:border-primary/40">
              <div className="grid h-10 w-10 place-items-center rounded-lg bg-primary/15 text-primary-glow transition-transform group-hover:scale-110">
                <s.icon className="h-5 w-5" />
              </div>
              <div>
                <div className="text-sm font-medium">{s.label}</div>
                <div className="text-xs text-muted-foreground">{s.sub}</div>
              </div>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
}

function AccuracyCard({ name, desc, value, hue }: { name: string; desc: string; value: number; hue: "primary" | "cyan" }) {
  const pct = `${value}%`;
  return (
    <Card className="surface-card relative overflow-hidden border-border/60 p-6">
      <div className={`absolute -right-12 -top-12 h-40 w-40 rounded-full blur-3xl ${hue === "primary" ? "bg-primary/30" : "bg-cyan-500/30"}`} aria-hidden />
      <div className="relative">
        <div className="text-xs uppercase tracking-wide text-muted-foreground">Model accuracy</div>
        <div className="mt-3 flex items-baseline gap-2">
          <span className="gradient-text text-5xl font-semibold tabular-nums">{pct}</span>
        </div>
        <div className="mt-2 text-base font-medium">{name}</div>
        <p className="text-sm text-muted-foreground">{desc}</p>
        <div className="mt-5 h-1.5 overflow-hidden rounded-full bg-background/60">
          <div className="h-full rounded-full gradient-primary" style={{ width: pct }} />
        </div>
      </div>
    </Card>
  );
}