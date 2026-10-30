#!/usr/bin/env python3
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wallet.ledger import Wallet
W = Wallet(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "wallet.json"))
def main():
    p = argparse.ArgumentParser(); sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("balance"); f = sub.add_parser("fund"); f.add_argument("--provider", required=True); f.add_argument("--amount", type=float, required=True)
    af = sub.add_parser("approve-fund"); af.add_argument("--fund", required=True)
    s = sub.add_parser("spend"); s.add_argument("--agent", required=True); s.add_argument("--to", required=True); s.add_argument("--amount", type=float, required=True); s.add_argument("--category", default="models")
    asp = sub.add_parser("approve-spend"); asp.add_argument("--spend", required=True)
    sub.add_parser("kill"); sub.add_parser("receipts")
    r = sub.add_parser("receive"); r.add_argument("--from", dest="src", required=True); r.add_argument("--amount", type=float, required=True)
    ar = sub.add_parser("approve-receive"); ar.add_argument("--receive", required=True)
    sv = sub.add_parser("save"); sv.add_argument("--amount", type=float, required=True)
    sb = sub.add_parser("subscribe"); sb.add_argument("--merchant", required=True); sb.add_argument("--amount", type=float, required=True); sb.add_argument("--interval", default="monthly")
    asb = sub.add_parser("approve-sub"); asb.add_argument("--sub", required=True)
    csb = sub.add_parser("cancel-sub"); csb.add_argument("--sub", required=True)
    ch = sub.add_parser("charge-sub"); ch.add_argument("--sub", required=True)
    sub.add_parser("subs")
    a = p.parse_args()
    if a.cmd == "balance": print(f"Ledger balance: ${W.data['balance']} | Savings: ${W.data['savings']} (mock, $0 real) | killed: {W.data['killed']}")
    elif a.cmd == "fund": print(f"Fund intent: {W.fund_intent(a.provider, a.amount)} — INTENT ONLY, no money moved. Complete payment in your own {a.provider} account, then approve-fund.")
    elif a.cmd == "approve-fund": print("Fund approved (ledger only)" if W.approve_fund(a.fund) else "Fund not found / already approved")
    elif a.cmd == "spend":
        sid, reason = W.spend(a.agent, a.to, a.amount, a.category); print(f"Spend {sid}: {'BLOCKED: '+reason if reason else 'pending approval — approve-spend to execute (ledger only)'}")
    elif a.cmd == "approve-spend": print("Spend approved (ledger only)" if W.approve_spend(a.spend) else "Spend not approved — check status / kill switch")
    elif a.cmd == "receive": print(f"Receive intent: {W.receive_intent(a.src, a.amount)} — INTENT ONLY, get paid via your own provider, then approve-receive.")
    elif a.cmd == "approve-receive": print("Receive approved (ledger only)" if W.approve_receive(a.receive) else "Receive not found")
    elif a.cmd == "save": print("Saved to savings pot" if W.save_to_savings(a.amount) else "Save failed — check balance")
    elif a.cmd == "subscribe":
        sid, reason = W.subscribe(a.merchant, a.amount, a.interval); print(f"Subscription {sid} pending approval" if sid else f"Subscription rejected: {reason}")
    elif a.cmd == "approve-sub": print("Subscription active — pre-approved recurring only" if W.approve_subscription(a.sub) else "Subscription not found")
    elif a.cmd == "cancel-sub": print("Subscription cancelled" if W.cancel_subscription(a.sub) else "Subscription not found / not active")
    elif a.cmd == "charge-sub": print("Autopilot subscription charge (ledger only)" if W.subscription_charge(a.sub) else "Charge blocked — not active / cancelled / killed / insufficient")
    elif a.cmd == "subs":
        for s in W.data["subscriptions"]: print(f"{s['id']} {s['merchant']} ${s['amount']}/{s['interval']} {s['status']}")
    elif a.cmd == "kill": W.kill(); print("KILL SWITCH ON — all spending stopped")
    elif a.cmd == "receipts":
        for r in W.data["receipts"]: print(f"{r['kind']}: {r['detail']}")
main()
