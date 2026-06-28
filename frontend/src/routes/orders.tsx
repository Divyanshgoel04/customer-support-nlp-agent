import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { CalendarDays, CreditCard, Package, RotateCcw, Search, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { fetchOrder } from "@/lib/api";

export const Route = createFileRoute("/orders")({
  head: () => ({
    meta: [
      { title: "Order lookup — Helix Support" },
      { name: "description", content: "Look up any order by ID to see status, amount, and refund state." },
      { property: "og:title", content: "Order lookup — Helix Support" },
      { property: "og:description", content: "Look up an order by ID to see status, amount, and refund state." },
    ],
  }),
  component: Orders,
});

const STATUS_STYLES: Record<string, string> = {
  Delivered: "bg-emerald-500/15 text-emerald-300 ring-emerald-400/30",
  Shipped: "bg-blue-500/15 text-blue-300 ring-blue-400/30",
  Processing: "bg-amber-500/15 text-amber-300 ring-amber-400/30",
  Cancelled: "bg-rose-500/15 text-rose-300 ring-rose-400/30",
};

const REFUND_STYLES: Record<string, string> = {
  none: "bg-muted text-muted-foreground ring-border",
  requested: "bg-amber-500/15 text-amber-300 ring-amber-400/30",
  approved: "bg-blue-500/15 text-blue-300 ring-blue-400/30",
  completed: "bg-emerald-500/15 text-emerald-300 ring-emerald-400/30",
};

interface ApiOrder {
  product_name: string;
  order_date: string;
  status: string;
  amount: number;
  refund_status: string;
}

function Orders() {
  const [query, setQuery] = useState("");
  const [order, setOrder] = useState<ApiOrder | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(false);

  const handleSearch = async () => {
    const id = query.trim().replace(/^#/, "");
    if (!id) return;
    setLoading(true);
    setError(false);
    setOrder(null);
    try {
      const data = await fetchOrder(id);
      setOrder(data as ApiOrder);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  const formatAmount = (amount: number) => `$${amount.toFixed(2)}`;

  return (
    <div className="space-y-8">
      <div>
        <h1 className="gradient-text text-3xl font-semibold tracking-tight">Order lookup</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Search any order by its ID. Try ORD00001 to ORD00200.
        </p>
      </div>

      <Card className="surface-card border-border/60 p-6">
        <div className="flex flex-col gap-3 sm:flex-row">
          <div className="relative flex-1">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              placeholder="Order ID (e.g. ORD00001)"
              className="pl-9 bg-background/40 border-border/60 h-11"
            />
          </div>
          <Button
            onClick={handleSearch}
            disabled={loading}
            className="gradient-primary h-11 text-white shadow-lg shadow-primary/30"
          >
            {loading ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Search className="mr-2 h-4 w-4" />
            )}
            Search
          </Button>
        </div>
      </Card>

      {error && (
        <Card className="surface-card border-border/60 p-8 text-center text-sm text-muted-foreground animate-in fade-in duration-300">
          Order not found. Try ORD00001 to ORD00200
        </Card>
      )}

      {order && (
        <Card className="surface-card border-border/60 overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-500">
          <div className="flex flex-col gap-4 border-b border-border/60 p-6 sm:flex-row sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="grid h-12 w-12 place-items-center rounded-2xl gradient-primary glow-shadow">
                <Package className="h-6 w-6 text-white" />
              </div>
              <div>
                <div className="text-xs uppercase tracking-wide text-muted-foreground">
                  Order #{query.trim().replace(/^#/, "")}
                </div>
                <div className="text-lg font-semibold">{order.product_name}</div>
              </div>
            </div>
            <span
              className={`inline-flex items-center gap-1.5 self-start rounded-full px-3 py-1 text-xs font-medium ring-1 ${STATUS_STYLES[order.status] || "bg-muted text-muted-foreground ring-border"}`}
            >
              <span className="h-1.5 w-1.5 rounded-full bg-current" />
              {order.status}
            </span>
          </div>
          <div className="grid divide-border/60 sm:grid-cols-3 sm:divide-x">
            <Field
              icon={<CalendarDays className="h-4 w-4" />}
              label="Order date"
              value={formatDate(order.order_date)}
            />
            <Field
              icon={<CreditCard className="h-4 w-4" />}
              label="Amount"
              value={formatAmount(order.amount)}
            />
            <div className="p-6">
              <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-muted-foreground">
                <RotateCcw className="h-4 w-4" /> Refund status
              </div>
              <div className="mt-3">
                <span
                  className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium ring-1 ${REFUND_STYLES[order.refund_status] || "bg-muted text-muted-foreground ring-border"}`}
                >
                  {order.refund_status}
                </span>
              </div>
            </div>
          </div>
          <div className="border-t border-border/60 p-6">
            <div className="text-xs uppercase tracking-wide text-muted-foreground">Agent notes</div>
            <p className="mt-2 text-sm text-muted-foreground">
              Helix has full read access to this order and can issue refunds, reroute shipments, or generate a return label automatically when a customer asks.
            </p>
          </div>
        </Card>
      )}
    </div>
  );
}

function Field({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="p-6">
      <div className="flex items-center gap-2 text-xs uppercase tracking-wide text-muted-foreground">
        {icon} {label}
      </div>
      <div className="mt-3 text-base font-medium">{value}</div>
    </div>
  );
}
