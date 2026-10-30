import sys, os, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from wallet.ledger import Wallet
def fresh(): return Wallet(os.path.join(tempfile.mkdtemp(), "w.json"))
def test_fund_is_intent_only():
    w = fresh(); fid = w.fund_intent("stripe", 50); assert w.data["funds"][0]["real_money_moved"] is False; assert w.data["balance"] == 0
def test_approve_fund_credits_ledger():
    w = fresh(); fid = w.fund_intent("paypal", 50); assert w.approve_fund(fid); assert w.data["balance"] == 50
def test_unapproved_spend_never_executes():
    w = fresh(); w.fund_intent("stripe", 50); w.approve_fund("fund-1"); sid, _ = w.spend("agent-1", "openrouter", 5, "models"); assert w.data["balance"] == 50
def test_over_cap_blocked():
    w = fresh(); w.fund_intent("stripe", 100); w.approve_fund("fund-1"); sid, reason = w.spend("agent-1", "openrouter", 999, "models"); assert reason and w.data["spends"][0]["status"] == "blocked"
def test_non_allowlisted_blocked():
    w = fresh(); w.fund_intent("stripe", 100); w.approve_fund("fund-1"); sid, reason = w.spend("agent-1", "random-shop", 5, "unknown"); assert reason
def test_kill_switch_blocks_all():
    w = fresh(); w.fund_intent("stripe", 100); w.approve_fund("fund-1"); w.kill(); sid, reason = w.spend("agent-1", "openrouter", 5, "models"); assert reason == "kill switch on"
def test_interac_is_stub_not_api():
    from wallet.providers import PROVIDERS; assert "No public agent API" in PROVIDERS["interac"]

def test_receive_and_get_paid():
    w = fresh(); rid = w.receive_intent("client-payment", 200); assert w.data["funds"][-1]["real_money_moved"] is False; assert w.approve_receive(rid); assert w.data["balance"] == 200
def test_save_to_savings():
    w = fresh(); w.fund_intent("stripe", 100); w.approve_fund("fund-1"); assert w.save_to_savings(40); assert w.data["savings"] == 40 and w.data["balance"] == 60
def test_subscription_autopilot_only_when_preapproved():
    w = fresh(); w.fund_intent("stripe", 100); w.approve_fund("fund-1"); sid, _ = w.subscribe("openrouter", 10); assert not w.subscription_charge(sid); assert w.approve_subscription(sid); assert w.subscription_charge(sid); assert w.data["balance"] == 90
def test_cancel_subscription_stops_charges():
    w = fresh(); w.fund_intent("stripe", 100); w.approve_fund("fund-1"); sid, _ = w.subscribe("openrouter", 10); w.approve_subscription(sid); assert w.cancel_subscription(sid); assert not w.subscription_charge(sid)
def test_subscription_over_cap_rejected():
    w = fresh(); sid, reason = w.subscribe("openrouter", 999); assert reason and sid is None

if __name__ == "__main__":
    for n, fn in list(globals().items()):
        if n.startswith("test_"): fn(); print(f"PASS {n}")
    print("ALL PASS")
