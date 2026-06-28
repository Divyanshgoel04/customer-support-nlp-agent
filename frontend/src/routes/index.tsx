import { createFileRoute } from "@tanstack/react-router";
import { useRef, useState } from "react";
import { ArrowRight, BrainCircuit, CheckCircle2, Loader2, ShieldAlert, UserCog, Zap, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { analyzeTicket } from "@/lib/api";
import { INTENT_META, type Intent } from "@/lib/mock-agent";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Helix Support — AI Customer Support Agent" },
      { name: "description", content: "Live demo of an AI agent that classifies, routes, and resolves customer support tickets in real time." },
      { property: "og:title", content: "Helix Support — AI Customer Support Agent" },
      { property: "og:description", content: "Live demo of an AI agent that classifies, routes, and resolves customer support tickets." },
    ],
  }),
  component: Index,
});

interface AnalyzeResult {
  intent: string;
  confidence: number;
  escalated: boolean;
  response: string;
  latencyMs?: number;
}

function Index() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const resultRef = useRef<HTMLDivElement | null>(null);

  const samples = [
    "Where is my order #45128? It's been a week.",
    "I'd like a refund for the headphones I received.",
    "I can't log into my account, password reset isn't working.",
    "I was charged twice for my monthly subscription.",
  ];

  const handleSubmit = async () => {
    if (!text.trim() || loading) return;
    setLoading(true);
    setResult(null);
    setError(null);
    const start = performance.now();
    try {
      const data = await analyzeTicket(text);
      setResult({ ...data, latencyMs: Math.round(performance.now() - start) });
    } catch {
      setError("Unable to connect to agent. Please try again.");
    } finally {
      setLoading(false);
      requestAnimationFrame(() => resultRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }));
    }
  };

  return (
    <div className="space-y-10">
      <section className="relative overflow-hidden rounded-3xl border border-border/60 surface-card p-8 sm:p-12">
        <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full bg-primary/20 blur-3xl" aria-hidden />
        <div className="absolute -bottom-32 -left-20 h-72 w-72 rounded-full bg-primary-glow/20 blur-3xl" aria-hidden />
        <div className="relative max-w-2xl">
          <div className="inline-flex items-center gap-2 rounded-full border border-border/60 bg-background/40 px-3 py-1 text-xs text-muted-foreground">
            <Zap className="h-3.5 w-3.5 text-primary-glow" />
            Real-time intent classification + routing
          </div>
          <h1 className="mt-5 text-4xl font-semibold tracking-tight sm:text-5xl">
            <span className="gradient-text">Customer Support</span>
            <br />
            AI Agent
          </h1>
          <p className="mt-4 max-w-xl text-base text-muted-foreground">
            Drop in any customer message. Helix detects the intent, scores its confidence, decides whether to auto-resolve or escalate, and drafts the reply — in milliseconds.
          </p>
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <Card className="surface-card border-border/60 p-6">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BrainCircuit className="h-5 w-5 text-primary-glow" />
              <h2 className="text-sm font-medium tracking-wide uppercase text-muted-foreground">New ticket</h2>
            </div>
            <span className="text-xs text-muted-foreground">{text.length} chars</span>
          </div>
          <div className="input-glow">
            <Textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Type your customer support ticket here..."
              className="min-h-[180px] w-full resize-none rounded-[11px] border-0 bg-background/70 text-base focus-visible:ring-0 focus-visible:ring-offset-0"
            />
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {samples.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => setText(s)}
                className="rounded-full border border-border/60 bg-background/40 px-3 py-1 text-xs text-muted-foreground transition-colors hover:border-primary/40 hover:text-foreground"
              >
                {s.slice(0, 38)}…
              </button>
            ))}
          </div>
          <div className="mt-5 flex items-center justify-between">
            <p className="text-xs text-muted-foreground">Press ⌘ + Enter to submit</p>
            <Button
              onClick={handleSubmit}
              disabled={loading || !text.trim()}
              className="gradient-primary text-white shadow-lg shadow-primary/30 hover:opacity-95"
            >
              {loading ? (
                <><Loader2 className="mr-2 h-4 w-4 animate-spin" /> Analyzing…</>
              ) : (
                <>Analyze ticket <ArrowRight className="ml-2 h-4 w-4" /></>
              )}
            </Button>
          </div>
        </Card>

        <Card className="surface-card border-border/60 p-6">
          <h3 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">How Helix decides</h3>
          <ol className="mt-4 space-y-4 text-sm">
            {[
              { t: "Classify intent", d: "DistilBERT routes the message into one of 7 intent buckets." },
              { t: "Score confidence", d: "An SVM ensemble assigns a calibrated probability." },
              { t: "Auto-resolve or escalate", d: "≥ 0.70 confidence → agent reply. Otherwise hand off to a human." },
            ].map((step, i) => (
              <li key={step.t} className="flex gap-3">
                <span className="grid h-7 w-7 shrink-0 place-items-center rounded-full bg-primary/15 text-xs font-semibold text-primary-glow">{i + 1}</span>
                <div>
                  <div className="font-medium text-foreground">{step.t}</div>
                  <div className="text-muted-foreground">{step.d}</div>
                </div>
              </li>
            ))}
          </ol>
        </Card>
      </section>

      <section ref={resultRef} className="min-h-[60px] space-y-6">
        {loading && (
          <div className="grid gap-6 lg:grid-cols-3 animate-in fade-in duration-300">
            <div className="shimmer h-48 rounded-xl border border-white/10" />
            <div className="shimmer h-48 rounded-xl border border-white/10" />
            <div className="shimmer h-48 rounded-xl border border-white/10" />
          </div>
        )}
        {error && (
          <Card className="surface-card border-red-500/30 p-6 animate-in fade-in slide-in-from-bottom-2 duration-500">
            <div className="flex items-center gap-3 text-red-300">
              <AlertCircle className="h-5 w-5 shrink-0" />
              <p className="text-sm font-medium">{error}</p>
            </div>
          </Card>
        )}
        {result && !loading && <ResultPanel result={result} ticket={text} />}
      </section>
    </div>
  );
}

function ResultPanel({ result, ticket }: { result: AnalyzeResult; ticket: string }) {
  const intentKey = (result.intent?.toUpperCase() as Intent) || "GENERAL";
  const meta = INTENT_META[intentKey] || INTENT_META["GENERAL"];
  const pct = Math.round(result.confidence * 100);
  return (
    <div className="grid gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500 lg:grid-cols-3">
      <Card className="surface-card border-border/60 p-6">
        <div className="text-xs uppercase tracking-wide text-muted-foreground">Detected intent</div>
        <div className={`mt-3 inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-sm font-medium ring-1 ${meta.bg} ${meta.color} ${meta.ring}`}>
          <span className="h-1.5 w-1.5 rounded-full bg-current" />
          {result.intent}
        </div>
        <div className="mt-6">
          <div className="flex items-baseline justify-between">
            <span className="text-xs uppercase tracking-wide text-muted-foreground">Confidence</span>
            <span className="text-2xl font-semibold tabular-nums">{pct}%</span>
          </div>
          <Progress value={pct} className="progress-glow mt-2 h-2" />
          <p className="mt-2 text-xs text-muted-foreground">Threshold for auto-resolve: 70%</p>
        </div>
        <div className="mt-6 flex items-center justify-between border-t border-border/60 pt-4 text-xs text-muted-foreground">
          <span>Latency</span>
          <span className="font-mono text-foreground">{result.latencyMs ?? "—"} ms</span>
        </div>
      </Card>

      <Card className={`surface-card border-border/60 p-6 ${result.escalated ? "ring-1 ring-amber-400/30" : "ring-1 ring-emerald-400/30"}`}>
        <div className="text-xs uppercase tracking-wide text-muted-foreground">Routing decision</div>
        <div className="mt-3 flex items-center gap-3">
          {result.escalated ? (
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-amber-500/15 text-amber-300">
              <UserCog className="h-6 w-6" />
            </div>
          ) : (
            <div className="grid h-12 w-12 place-items-center rounded-2xl bg-emerald-500/15 text-emerald-300">
              <CheckCircle2 className="h-6 w-6" />
            </div>
          )}
          <div>
            <div className="text-lg font-semibold">{result.escalated ? "Escalated to Human" : "AI Agent Handled"}</div>
            <div className="text-xs text-muted-foreground">
              {result.escalated ? "Confidence below threshold." : "Confidence cleared the bar."}
            </div>
          </div>
        </div>
        <div className="mt-6 grid grid-cols-2 gap-3 text-center">
          <Stat label="SLA" value={result.escalated ? "1h" : "Instant"} />
          <Stat label="Priority" value={result.escalated ? "High" : "Normal"} />
        </div>
        {result.escalated && (
          <div className="mt-4 flex items-center gap-2 rounded-lg bg-amber-500/10 px-3 py-2 text-xs text-amber-200">
            <ShieldAlert className="h-3.5 w-3.5" />
            Routed to a specialist queue.
          </div>
        )}
      </Card>

      <Card className="surface-card border-border/60 p-6 lg:col-span-1">
        <div className="text-xs uppercase tracking-wide text-muted-foreground">Agent response</div>
        <div className="mt-4 space-y-3">
          <div className="ml-auto max-w-[90%] rounded-2xl rounded-tr-sm bg-background/60 px-4 py-3 text-sm text-muted-foreground">
            <div className="mb-1 text-[10px] uppercase tracking-wide text-muted-foreground/70">Customer</div>
            {ticket}
          </div>
          <div className="max-w-[95%] rounded-2xl rounded-tl-sm gradient-primary px-4 py-3 text-sm text-white shadow-lg shadow-primary/30">
            <div className="mb-1 flex items-center gap-1.5 text-[10px] uppercase tracking-wide text-white/80">
              <BrainCircuit className="h-3 w-3" /> Helix
            </div>
            {result.response}
          </div>
        </div>
      </Card>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border/60 bg-background/40 px-3 py-2">
      <div className="text-[10px] uppercase tracking-wide text-muted-foreground">{label}</div>
      <div className="mt-0.5 text-sm font-semibold">{value}</div>
    </div>
  );
}
