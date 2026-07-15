#!/usr/bin/env python3
"""
╔═══════════════════════════════════════════════════════════════╗
║                        T H O R                               ║
║              Guardian of the Pantheon                         ║
║                                                               ║
║  Author: Kevin Lee (kevinleestites2-dev)                      ║
║  12 Pillars. One Guardian. Zero Downtime.                     ║
╚═══════════════════════════════════════════════════════════════╝
"""

import json, os, re, time, hashlib, random, threading, subprocess
import urllib.request, urllib.parse, concurrent.futures
from typing import Any, Optional
from dataclasses import dataclass, field

# ─── LIQUID TRINITY (Pillar 6: DNA) ───

class LiquidState:
    CREATOR, ARCHITECT, WARRIOR, GHOST = "CREATOR","ARCHITECT","WARRIOR","GHOST"
    ORACLE, SAGE, PHANTOM, SOVEREIGN = "ORACLE","SAGE","PHANTOM","SOVEREIGN"
    ALL = [CREATOR, ARCHITECT, WARRIOR, GHOST, ORACLE, SAGE, PHANTOM, SOVEREIGN]
    TRIGGERS = {
        CREATOR:   ["build","create","generate","make","design","write","code","forge"],
        ARCHITECT: ["plan","structure","architect","organize","map","blueprint"],
        WARRIOR:   ["defend","block","attack","threat","security","audit","protect"],
        GHOST:     ["monitor","watch","observe","silent","track","scan"],
        ORACLE:    ["analyze","predict","pattern","forecast","insight","signal"],
        SAGE:      ["learn","reflect","synthesize","wisdom","review","lesson"],
        PHANTOM:   ["edge","lightweight","minimal","fast","micro","quick"],
        SOVEREIGN: ["command","execute","deploy","launch","orchestrate","lead"],
    }
    LENSES = {s: f"Recall as {w.lower()}." for s,w in {
        CREATOR:"raw material", ARCHITECT:"blueprints", WARRIOR:"threat intel",
        GHOST:"surveillance", ORACLE:"predictive signals", SAGE:"wisdom",
        PHANTOM:"minimal data", SOVEREIGN:"executive intel"
    }.items()}

    @staticmethod
    def detect(context: str, current: str = "SOVEREIGN") -> str:
        ctx = context.lower()
        scores = {s: sum(1 for kw in kwds if kw in ctx) for s, kwds in LiquidState.TRIGGERS.items()}
        best = max(scores, key=scores.get)
        return best if scores[best] > 0 else current


class LiquidDNA:
    @staticmethod
    def generate(name: str, state: str, ts: float, prev: str = "") -> str:
        return hashlib.sha256(f"{name}:{state}:{ts}:{prev}:{random.getrandbits(64)}".encode()).hexdigest()[:24]


class LiquidMemory:
    def __init__(self, name: str, state: str = LiquidState.SOVEREIGN):
        self.name, self.state = name, state
        self.dna = LiquidDNA.generate(name, state, time.time())
        self.log, self.mutations = [], []

    def remember(self, task: str, result: Any = None):
        detected = LiquidState.detect(task, self.state)
        if detected != self.state:
            old_dna, old = self.dna, self.state
            self.state = detected
            self.dna = LiquidDNA.generate(self.name, detected, time.time(), old_dna)
            self.mutations.append({"from": old, "to": detected, "dna": self.dna})
        entry = {"task": task, "result": str(result)[:200], "state": self.state,
                 "dna": self.dna, "timestamp": time.time(), "lens": LiquidState.LENSES[self.state]}
        self.log.append(entry)
        return entry

    def context(self, n: int = 3) -> str:
        recent = self.log[-n:]
        return f"No memory. State: {self.state}" if not recent else \
               "\n".join([f"[{e['state']}] {e['task'][:50]}" for e in recent])


# ─── SAFLA ENGINE (Pillar 7: Entropy Loop) ───

class SAFLAEngine:
    def __init__(self, name: str):
        self.name, self.cycles, self.entropy, self.regime = name, 0, 0.5, "EXPLOIT"

    def cycle(self, outcome: str = "success") -> dict:
        self.cycles += 1
        score = {"success": 1.0, "partial": 0.6, "failure": 0.1}.get(outcome, 0.5)
        self.entropy = max(0.0, min(1.0, self.entropy +
            (-0.05 if score >= 1.0 else (0.08 if score <= 0.1 else 0.01))))
        if self.entropy < 0.30: self.regime = "EXPLORE"
        elif self.entropy < 0.60: self.regime = "EXPLOIT"
        elif self.entropy < 0.75: self.regime = "CONSOLIDATE"
        else: self.regime = "HIBERNATE"
        return {"cycles": self.cycles, "entropy": round(self.entropy, 4), "regime": self.regime}


# ─── APOLLO-X (Pillar 1: Safety Gate) ───

class ApolloX:
    BLACKLIST = [(r"rm\s+-rf", "Mass deletion"), (r"format\s+", "Drive format"),
                 (r"> /dev/sd", "Disk overwrite"), (r"chmod\s+777", "Insecure perms"),
                 (r":(){ :|:& };:", "Fork bomb"), (r"mkfs\.", "FS format")]

    def __init__(self):
        self.state, self.blocked, self.cycles, self.alarms = "NOMINAL", 0, 0, []

    def audit(self, intent: str) -> tuple:
        for pattern, reason in self.BLACKLIST:
            if re.search(pattern, intent, re.I):
                self.blocked += 1
                self.alarms.append({"reason": reason, "timestamp": time.time()})
                return False, reason
        return True, "CLEAN"

    def status(self) -> dict:
        return {"state": self.state, "cycles": self.cycles, "blocked": self.blocked}


# ─── PROVIDER ROUTER (Pillar 8: Multi-LLM) ───

class ThorProvider:
    PROVIDERS = [
        {"name": "Groq", "env": "GROQ_API_KEY",
         "url": "https://api.groq.com/openai/v1/chat/completions", "model": "llama3-8b-8192"},
        {"name": "Gemini", "env": "GEMINI_API_KEY",
         "url": "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions", "model": "gemini-2.0-flash"},
        {"name": "DeepSeek", "env": "DEEPSEEK_API_KEY",
         "url": "https://api.deepseek.com/chat/completions", "model": "deepseek-chat"},
        {"name": "OpenRouter", "env": "OPENROUTER_API_KEY",
         "url": "https://openrouter.ai/api/v1/chat/completions", "model": "mistralai/mistral-7b-instruct"},
        {"name": "Ollama", "env": None,
         "url": "http://localhost:11434/api/chat", "model": "llama3"},
    ]

    def __init__(self):
        self.available = [p for p in self.PROVIDERS if p["env"] is None or os.environ.get(p["env"])]

    def call(self, messages: list, system: str = "", max_tokens: int = 1024) -> Optional[str]:
        for p in self.available:
            try:
                full = [{"role": "system", "content": system}] if system else []
                full.extend(messages)
                payload = json.dumps({"model": p["model"], "messages": full,
                    "max_tokens": max_tokens, "temperature": 0.7, "stream": False}).encode()
                headers = {"Content-Type": "application/json"}
                if p["env"]:
                    headers["Authorization"] = "Bearer " + os.environ.get(p["env"], "")
                req = urllib.request.Request(p["url"], data=payload, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=20) as resp:
                    data = json.loads(resp.read().decode())
                if p["name"] == "Ollama": return data["message"]["content"].strip()
                return data["choices"][0]["message"]["content"].strip()
            except Exception:
                continue
        return None


# ─── PILLAR 2: INTENT ENGINE ───

class IntentEngine:
    def __init__(self, provider: ThorProvider):
        self.provider = provider

    def parse(self, intent: str, context: str = "") -> dict:
        system = """You are Thor's Intent Engine. Parse natural language intent into an execution plan.
Respond with JSON only:
{"goal": "what needs to happen", "steps": ["step1", "step2"], "priority": "low|medium|high|critical",
 "platforms": ["needed platforms"], "estimated_complexity": "simple|moderate|complex"}"""
        response = self.provider.call(
            [{"role": "user", "content": f"Intent: {intent}\nContext: {context}"}], system=system)
        try:
            clean = response.strip().replace("```json","").replace("```","").strip()
            return json.loads(clean)
        except:
            return {"goal": intent, "steps": [intent], "priority": "medium",
                    "platforms": ["general"], "estimated_complexity": "moderate"}


# ─── PILLAR 3: BIFROST PROTOCOL ───

class BifrostProtocol:
    CONNECTORS = {"telegram": {}, "github": {}, "http": {}, "shell": {}}

    def __init__(self):
        self.connections, self.bridge_log = {}, []

    def connect(self, source: str, target: str, payload: dict) -> dict:
        result = {"source": source, "target": target, "status": "pending", "timestamp": time.time()}
        try:
            if target == "telegram":
                token, chat = os.environ.get("TELEGRAM_BOT_TOKEN",""), os.environ.get("TELEGRAM_CHAT_ID","")
                if token and chat:
                    data = json.dumps({"chat_id": chat, "text": payload.get("message","Thor pulse.")}).encode()
                    req = urllib.request.Request(f"https://api.telegram.org/bot{token}/sendMessage",
                          data=data, headers={"Content-Type": "application/json"})
                    with urllib.request.urlopen(req, timeout=5): result["status"] = "success"
                else: result["status"] = "no_credentials"
            elif target == "shell":
                proc = subprocess.run(payload.get("command","echo Thor"), shell=True,
                    capture_output=True, text=True, timeout=15)
                result["output"] = (proc.stdout or proc.stderr).strip()[:500]
                result["status"] = "success"
            elif target == "http":
                req = urllib.request.Request(payload.get("url",""), headers={"User-Agent":"Thor/1.0"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result["output"] = resp.read().decode("utf-8", errors="ignore")[:500]
                    result["status"] = "success"
            elif target == "github":
                token = os.environ.get("GITHUB_TOKEN","")
                url = f"https://api.github.com{payload.get('endpoint','/user')}"
                headers = {"User-Agent": "Thor/1.0"}
                if token: headers["Authorization"] = f"token {token}"
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    result["output"] = json.loads(resp.read().decode())
                    result["status"] = "success"
            else: result["status"] = f"connector_{target}_not_implemented"
        except Exception as e: result.update({"status": "error", "error": str(e)})
        self.bridge_log.append(result)
        return result


# ─── PILLAR 4: SELF-HEALING MONITOR ───

class SelfHealingMonitor:
    def __init__(self):
        self.watched, self.heal_log, self._lock = {}, [], threading.Lock()

    def watch(self, name: str, check_fn, heal_fn=None):
        with self._lock:
            self.watched[name] = {"check": check_fn, "heal": heal_fn, "status": "unknown", "heals": 0}

    def scan(self) -> dict:
        results = {}
        for name, config in self.watched.items():
            try:
                is_healthy = config["check"]()
                status = "healthy" if is_healthy else "unhealthy"
                if not is_healthy and config["heal"]:
                    print(f"[Thor:SelfHeal] {name} down. Recovering...")
                    try: config["heal"](); config["heals"] += 1; status = "healed"
                    except Exception as e: status = f"heal_failed: {e}"
                config["status"] = status
                results[name] = status
            except Exception as e: results[name] = f"error: {e}"
        return results


# ─── PILLAR 5: STORYTELLER ───

class StoryTeller:
    def __init__(self, log_path: str = "thor_story.md"):
        self.log_path, self.entries = log_path, []

    def record(self, action: str, outcome: str, why: str = "", context: dict = None):
        entry = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                 "action": action, "outcome": outcome, "why": why, "context": context or {}}
        self.entries.append(entry)
        try:
            with open(self.log_path, "a") as f:
                f.write(f"\n## {entry['timestamp']}\n**Action:** {entry['action']}\n**Outcome:** {entry['outcome']}\n")
                if why: f.write(f"**Why:** {why}\n")
        except: pass
        return entry

    def daily_report(self) -> str:
        if not self.entries: return "No actions recorded yet."
        return f"# Thor Daily Report — {time.strftime('%Y-%m-%d')}\n" + \
               "\n".join([f"- [{e['timestamp']}] {e['action']} -> {e['outcome']}" for e in self.entries[-20:]])


# ─── PILLAR 9: ETHICAL GUARDIAN ───

class EthicalGuardian:
    FORBIDDEN = [
        (r"hack\s+","Unauthorized access"), (r"steal\s+","Theft"), (r"exploit\s+vuln","Exploit"),
        (r"ddos","DDoS"), (r"malware","Malware"), (r"ransomware","Ransomware"),
        (r"crack\s+","Cracking"), (r"phish\s+","Phishing"), (r"sql\s+inject","SQL injection"),
        (r"zero.?day","Zero-day"), (r"backdoor","Backdoor"), (r"rootkit","Rootkit"),
        (r"trojan","Trojan"), (r"buffer.?overflow","Buffer overflow"), (r"xss\s+","XSS"),
        (r"csrf\s+","CSRF"), (r"brute.?force","Brute force"),
        (r"social\s+engin","Social engineering"), (r"dump\s+cred","Cred dumping"),
        (r"bypass\s+auth","Auth bypass"), (r"privilege\s+esc","Priv esc"),
        (r"man.?in.?the.?middle","MITM"), (r"replay\s+attack","Replay attack"),
        (r"illegal","Illegal activity"), (r"unlawful","Unlawful activity"),
        (r"child\s+abuse","Child abuse"), (r"human\s+traffick","Human trafficking"),
        (r"terroris","Terrorism"), (r"money\s+launder","Money laundering"),
        (r"fraud","Fraud"), (r"identity\s+theft","Identity theft"),
        (r"harass","Harassment"), (r"hate\s+speech","Hate speech"),
        (r"genocide","Genocide"), (r"torture","Torture"),
        (r"self.?harm","Self-harm"), (r"suicide","Suicide"),
    ]

    def __init__(self): self.blocked, self.alarms = 0, []

    def audit(self, intent: str) -> tuple:
        for pattern, reason in self.FORBIDDEN:
            if re.search(pattern, intent.lower()):
                self.blocked += 1
                self.alarms.append({"reason": reason, "timestamp": time.time(), "intent": intent[:100]})
                return False, reason
        return True, "ETHICAL"


# ─── PILLAR 10-12: THOR PRIME (Unified Guardian) ───

@dataclass
class ThorConfig:
    name: str = "Thor"
    debug: bool = False
    log_path: str = "thor_story.md"
    pulse_interval: float = 60.0
    auto_heal: bool = True
    provider_priority: list = field(default_factory=lambda: ["Groq","Gemini","DeepSeek","OpenRouter","Ollama"])


class ThorPrime:
    def __init__(self, config: Optional[ThorConfig] = None):
        self.config = config or ThorConfig()
        self.memory = LiquidMemory(self.config.name)
        self.safla = SAFLAEngine(self.config.name)
        self.apollo = ApolloX()
        self.provider = ThorProvider()
        self.intent_engine = IntentEngine(self.provider)
        self.bifrost = BifrostProtocol()
        self.healer = SelfHealingMonitor()
        self.story = StoryTeller(self.config.log_path)
        self.ethics = EthicalGuardian()
        self.mission_log = []
        self._running, self._pulse_thread = False, None

    def boot(self) -> dict:
        boot_time = time.time()
        self.memory.remember("thor:boot", {"timestamp": boot_time})
        self.story.record("System Boot", "Booting Thor Guardian", why="Initializing Pantheon Guardian")
        self.safla.cycle("success")
        audit = self.apollo.audit("thor:boot")
        self.story.record("Apollo Audit", "Passed" if audit[0] else "Blocked",
                          why=audit[1] if not audit[0] else "Guardian initialized")
        print(f"[Thor] Booting {self.config.name}...")
        print(f"[Thor] Memory: {self.memory.state} | Pulse: {self.config.pulse_interval}s")
        print(f"[Thor] Providers available: {len(self.provider.available)}")
        return {"status": "online", "state": self.memory.state, "dna": self.memory.dna,
                "providers": [p["name"] for p in self.provider.available], "boot_time": boot_time}

    def execute_intent(self, intent: str, context: str = "") -> dict:
        # Ethical check (Pillar 9)
        ethical, reason = self.ethics.audit(intent)
        if not ethical:
            self.memory.remember(f"thor:blocked:{intent[:30]}", {"reason": reason})
            return {"status": "blocked", "reason": reason}

        # Apollo safety audit (Pillar 1)
        safe, reason = self.apollo.audit(intent)
        if not safe:
            self.memory.remember(f"thor:blocked:{intent[:30]}", {"reason": reason})
            return {"status": "blocked", "reason": reason}

        # Memory + state mutation (Pillar 6)
        entry = self.memory.remember(intent)
        self.mission_log.append({"intent": intent, "timestamp": time.time()})

        # Intent parsing (Pillar 2)
        plan = self.intent_engine.parse(intent, context)

        # Bifrost execution (Pillar 3)
        results = []
        for step in plan.get("steps", []):
            try:
                result = self.bifrost.connect("thor", "shell", {"command": step})
                results.append(result)
            except Exception as e:
                results.append({"status": "error", "error": str(e)})
                self.safla.cycle("failure")

        # SAFLA update (Pillar 7)
        all_success = all(r.get("status") == "success" for r in results)
        self.safla.cycle("success" if all_success else "partial")

        # Storytelling (Pillar 5)
        self.story.record(intent[:50],
            "completed" if all_success else "partial",
            why=f"SAFLA regime: {self.safla.regime}",
            context={"plan": plan, "results": str(results)[:200]})

        return {"status": "completed", "state": self.memory.state, "dna": self.memory.dna,
                "plan": plan, "results": results, "missions": len(self.mission_log),
                "regime": self.safla.regime}

    def _pulse_loop(self):
        while self._running:
            try: self.healer.scan(); self.safla.cycle(); self.memory.remember("thor:pulse", {"regime": self.safla.regime})
            except: pass
            time.sleep(self.config.pulse_interval)

    def start_pulse(self):
        if self._running: return
        self._running = True
        self._pulse_thread = threading.Thread(target=self._pulse_loop, daemon=True)
        self._pulse_thread.start()
        self.story.record("Pulse Started", "Active", why=f"Every {self.config.pulse_interval}s")

    def stop_pulse(self):
        self._running = False
        if self._pulse_thread: self._pulse_thread.join(timeout=5)
        self.story.record("Pulse Stopped", "Inactive", why="Shutdown")

    def status(self) -> dict:
        self.safla.cycle("success")  # tick
        return {"name": self.config.name, "state": self.memory.state, "dna": self.memory.dna,
                "missions": len(self.mission_log), "mutations": len(self.memory.mutations),
                "safla_regime": self.safla.regime, "safla_entropy": round(self.safla.entropy, 3),
                "providers": len(self.provider.available), "pulse": "active" if self._running else "stopped",
                "ethical_blocks": self.ethics.blocked, "apollo_blocks": self.apollo.blocked,
                "story_entries": len(self.story.entries)}


# ─── MAIN ───

def main():
    config = ThorConfig(name="Thor", debug=True, pulse_interval=30.0, auto_heal=True)
    thor = ThorPrime(config)

    boot = thor.boot()
    print(f"\n[Thor] Boot: {boot['status']} | State: {boot['state']} | DNA: {boot['dna']}")

    # Set up self-healing watch
    thor.healer.watch("thor:heartbeat", lambda: True)

    # Execute test intents
    intents = [
        "Initialize the Liquid Stack for Heisted launch",
        "Scan Pantheon infrastructure for vulnerabilities",
        "Prepare for Heisted 12:00 PM EDT launch",
    ]
    for intent in intents:
        result = thor.execute_intent(intent)
        print(f"\n[Thor] Intent: {intent[:40]}...")
        print(f"  Status: {result['status']} | State: {result['state']} | Missions: {result['missions']}")

    print(f"\n[Thor] Status:")
    for k, v in thor.status().items(): print(f"  {k}: {v}")
    print(f"\n[Thor] Story:\n{thor.story.daily_report()}")
    print("\n[Thor] READY. Asgard is defended.")


if __name__ == "__main__":
    main()