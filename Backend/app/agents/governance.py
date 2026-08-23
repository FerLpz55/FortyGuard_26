from dataclasses import dataclass, field
from enum import Enum
import re
import time
from collections import defaultdict
from typing import Optional, List

class PolicyAction(Enum):
    ALLOW = "allow"
    DENY = "deny"
    REVIEW = "review"

@dataclass
class GovernancePolicy:
    name: str
    allowed_tools: List[str] = field(default_factory=list)
    blocked_tools: List[str] = field(default_factory=list)
    blocked_patterns: List[str] = field(default_factory=list)
    max_calls_per_request: int = 15
    require_human_approval: List[str] = field(default_factory=list)

    def check_tool(self, tool_name: str) -> PolicyAction:
        if tool_name in self.blocked_tools:
            return PolicyAction.DENY
        if tool_name in self.require_human_approval:
            return PolicyAction.REVIEW
        if self.allowed_tools and tool_name not in self.allowed_tools:
            return PolicyAction.DENY
        return PolicyAction.ALLOW

    def check_content(self, content: str) -> Optional[str]:
        for pattern in self.blocked_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return pattern
        return None

# Policy MVP
AGENT_POLICY = GovernancePolicy(
    name="omnitherm-agent",
    allowed_tools=[
        "get_current_temperature",
        "get_temperature_forecast",
        "query_site_data",
        "create_alert",
        "send_notification",
        "analyze_energy_waste",
        "query_knowledge_base",
    ],
    blocked_tools=[],
    require_human_approval=["adjust_hvac_setpoint"],
    blocked_patterns=[
        r"(?i)(api[_-]?key|secret|password)\s*[:=]",
        r"(?i)(drop|truncate|delete from)\s+\w+",
    ],
    max_calls_per_request=15,
)

# Contador global de llamadas por request
_call_counters: dict[str, int] = defaultdict(int)

def governed_tool(func, policy: GovernancePolicy, audit_trail):
    """Decorator que aplica governance a tool function."""
    import functools
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        tool_name = func.__name__
        
        # 1. Check tool allowlist
        action = policy.check_tool(tool_name)
        if action == PolicyAction.DENY:
            raise PermissionError(f"Policy '{policy.name}' blocks tool '{tool_name}'")
        if action == PolicyAction.REVIEW:
            raise PermissionError(f"Tool '{tool_name}' requires human approval")
        
        # 2. Rate limit
        _call_counters[policy.name] += 1
        if _call_counters[policy.name] > policy.max_calls_per_request:
            raise PermissionError(f"Rate limit exceeded: {policy.max_calls_per_request} calls")
        
        # 3. Content check on string args
        for arg in list(args) + list(kwargs.values()):
            if isinstance(arg, str):
                matched = policy.check_content(arg)
                if matched:
                    raise PermissionError(f"Blocked pattern detected: {matched}")
        
        # 4. Execute + audit
        start = time.monotonic()
        try:
            result = await func(*args, **kwargs)
            audit_trail.append({
                "tool": tool_name,
                "action": "allowed",
                "duration_ms": (time.monotonic() - start) * 1000,
                "timestamp": time.time(),
                "site_id": kwargs.get("site_id")
            })
            return result
        except Exception as e:
            audit_trail.append({
                "tool": tool_name,
                "action": "error",
                "error": str(e),
                "timestamp": time.time()
            })
            raise
    
    return wrapper

# Audit trail (append-only)
audit_trail = []

# Trust scoring
@dataclass
class TrustScore:
    score: float = 0.5
    successes: int = 0
    failures: int = 0
    last_updated: float = field(default_factory=time.time)

    def record_success(self):
        self.successes += 1
        self.score = min(1.0, self.score + 0.05 * (1 - self.score))
        self.last_updated = time.time()

    def record_failure(self):
        self.failures += 1
        self.score = max(0.0, self.score - 0.15 * self.score)
        self.last_updated = time.time()

    def current(self, decay_rate: float = 0.001) -> float:
        import math
        elapsed = time.time() - self.last_updated
        return self.score * (math.e ** (-decay_rate * elapsed))

trust_registry = {"omnitherm_agent": TrustScore()}