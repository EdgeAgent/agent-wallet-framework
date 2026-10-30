import json, os, hashlib, time
PROVIDERS = ("stripe", "paypal", "interac", "visa", "bitcoin", "ethereum")
ALLOWLIST = {"openrouter", "openai", "anthropic", "github", "cloudflare", "domain-renewal", "models", "hosting"}

class Wallet:
    def __init__(self, path):
        self.path = path; self.data = {"balance": 0, "savings": 0, "funds": [], "spends": [], "subscriptions": [], "killed": False, "daily_cap": 100, "per_spend_cap": 25, "receipts": [], "prev_hash": "GENESIS"}
        if os.path.exists(path): self.data = json.load(open(path))
    def _save(self): os.makedirs(os.path.dirname(self.path), exist_ok=True); json.dump(self.data, open(self.path, "w"), indent=2)
    def _receipt(self, kind, detail):
        payload = json.dumps({"prev": self.data["prev_hash"], "kind": kind, "detail": detail}, sort_keys=True)
        h = hashlib.sha256(payload.encode()).hexdigest(); self.data["prev_hash"] = h; self.data["receipts"].append({"kind": kind, "detail": detail, "hash": h}); return h
    def fund_intent(self, provider, amount):
        if provider not in PROVIDERS: raise ValueError(f"unknown provider {provider}")
        if amount <= 0: raise ValueError("amount must be positive")
        fid = f"fund-{len(self.data['funds'])+1}"
        self.data["funds"].append({"id": fid, "provider": provider, "amount": amount, "status": "pending_intent", "real_money_moved": False})
        self._receipt("fund_intent", f"{fid} {provider} ${amount} — INTENT ONLY, no money moved"); self._save(); return fid
    def approve_fund(self, fid):
        for f in self.data["funds"]:
            if f["id"] == fid and f["status"] == "pending_intent":
                f["status"] = "approved_ledger_only"; self.data["balance"] += f["amount"]
                self._receipt("fund_approved", f"{fid} ledger balance +${f['amount']} (provider checkout is user's own step)"); self._save(); return True
        return False
    def spend(self, agent, to, amount, category):
        sid = f"spend-{len(self.data['spends'])+1}"
        reason = None
        if self.data["killed"]: reason = "kill switch on"
        elif amount > self.data["per_spend_cap"]: reason = f"over per-spend cap ${self.data['per_spend_cap']}"
        elif amount > self.data["balance"]: reason = "insufficient ledger balance"
        elif to not in ALLOWLIST and category not in ALLOWLIST: reason = "merchant/category not allowlisted"
        self.data["spends"].append({"id": sid, "agent": agent, "to": to, "amount": amount, "category": category, "status": "blocked" if reason else "pending_approval", "reason": reason})
        self._receipt("spend_blocked" if reason else "spend_pending", f"{sid} {agent} -> {to} ${amount} {reason or 'awaiting exact approval'}"); self._save(); return sid, reason
    def approve_spend(self, sid):
        for s in self.data["spends"]:
            if s["id"] == sid and s["status"] == "pending_approval" and not self.data["killed"]:
                s["status"] = "approved"; self.data["balance"] -= s["amount"]
                self._receipt("spend_approved", f"{sid} ${s['amount']} to {s['to']}"); self._save(); return True
        return False

    def receive_intent(self, source, amount):
        rid = f"receive-{len([x for x in self.data['funds'] if x['id'].startswith('receive')])+1}"
        self.data["funds"].append({"id": rid, "provider": "receive", "source": source, "amount": amount, "status": "pending_intent", "real_money_moved": False})
        self._receipt("receive_intent", f"{rid} from {source} ${amount} — INTENT ONLY, get paid via your own provider checkout / payout, then approve"); self._save(); return rid
    def approve_receive(self, rid):
        for f in self.data["funds"]:
            if f["id"] == rid and f["status"] == "pending_intent":
                f["status"] = "approved_ledger_only"; self.data["balance"] += f["amount"]
                self._receipt("receive_approved", f"{rid} ledger balance +${f['amount']}"); self._save(); return True
        return False
    def save_to_savings(self, amount):
        if amount <= 0 or amount > self.data["balance"]: return False
        self.data["balance"] -= amount; self.data["savings"] += amount
        self._receipt("savings", f"moved ${amount} to savings pot"); self._save(); return True
    def subscribe(self, merchant, amount, interval="monthly"):
        if merchant not in ALLOWLIST: return None, "merchant not allowlisted"
        if amount > self.data["per_spend_cap"]: return None, f"over per-spend cap ${self.data['per_spend_cap']}"
        sid = f"sub-{len(self.data['subscriptions'])+1}"
        self.data["subscriptions"].append({"id": sid, "merchant": merchant, "amount": amount, "interval": interval, "status": "pending_approval"})
        self._receipt("subscription_pending", f"{sid} {merchant} ${amount}/{interval} awaiting exact approval"); self._save(); return sid, None
    def approve_subscription(self, sid):
        for s in self.data["subscriptions"]:
            if s["id"] == sid and s["status"] == "pending_approval":
                s["status"] = "active"; self._receipt("subscription_active", f"{sid} {s['merchant']} ${s['amount']}/{s['interval']} — pre-approved recurring only, cancel anytime"); self._save(); return True
        return False
    def cancel_subscription(self, sid):
        for s in self.data["subscriptions"]:
            if s["id"] == sid and s["status"] == "active":
                s["status"] = "cancelled"; self._receipt("subscription_cancelled", f"{sid} cancelled — no further autopilot charges"); self._save(); return True
        return False
    def subscription_charge(self, sid):
        """The ONLY autopilot spend: a pre-approved, active, allowlisted subscription, under cap, kill switch off."""
        for s in self.data["subscriptions"]:
            if s["id"] == sid and s["status"] == "active" and not self.data["killed"] and s["amount"] <= self.data["balance"]:
                self.data["balance"] -= s["amount"]
                self._receipt("subscription_charge", f"{sid} {s['merchant']} ${s['amount']} autopilot charge (pre-approved recurring)"); self._save(); return True
        return False
    def kill(self):
        self.data["killed"] = True; self._receipt("kill_switch", "all spending stopped"); self._save()
