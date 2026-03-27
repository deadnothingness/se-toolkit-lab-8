"""Async HTTP client, models, and formatters for the LMS backend API."""

import httpx
from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class HealthResult(BaseModel):
    status: str
    item_count: int | str = "unknown"
    error: str = ""


class Item(BaseModel):
    id: int | None = None
    type: str = "step"
    parent_id: int | None = None
    title: str = ""
    description: str = ""


class Learner(BaseModel):
    id: int | None = None
    external_id: str = ""
    student_group: str = ""


class PassRate(BaseModel):
    task: str
    avg_score: float
    attempts: int


class TimelineEntry(BaseModel):
    date: str
    submissions: int


class GroupPerformance(BaseModel):
    group: str
    avg_score: float
    students: int


class TopLearner(BaseModel):
    learner_id: int
    avg_score: float
    attempts: int


class CompletionRate(BaseModel):
    lab: str
    completion_rate: float
    passed: int
    total: int


class SyncResult(BaseModel):
    new_records: int
    total_records: int


# ---------------------------------------------------------------------------
# Observability Models (VictoriaLogs)
# ---------------------------------------------------------------------------


class LogEntry(BaseModel):
    timestamp: str
    level: str
    service: str
    message: str
    raw: dict = {}


class ErrorCount(BaseModel):
    service: str
    count: int
    window_minutes: int


# ---------------------------------------------------------------------------
# Observability Models (VictoriaTraces)
# ---------------------------------------------------------------------------


class TraceSpan(BaseModel):
    trace_id: str
    span_id: str
    operation_name: str
    service_name: str
    start_time: int
    duration: int
    tags: list[dict] = []


class Trace(BaseModel):
    trace_id: str
    spans: list[TraceSpan]


# ---------------------------------------------------------------------------
# HTTP client
# ---------------------------------------------------------------------------


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_key}"}

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(headers=self._headers, timeout=10.0)

    async def health_check(self) -> HealthResult:
        async with self._client() as c:
            try:
                r = await c.get(f"{self.base_url}/items/")
                r.raise_for_status()
                items = [Item.model_validate(i) for i in r.json()]
                return HealthResult(status="healthy", item_count=len(items))
            except httpx.ConnectError:
                return HealthResult(
                    status="unhealthy", error=f"connection refused ({self.base_url})"
                )
            except httpx.HTTPStatusError as e:
                return HealthResult(
                    status="unhealthy", error=f"HTTP {e.response.status_code}"
                )
            except Exception as e:
                return HealthResult(status="unhealthy", error=str(e))

    async def get_items(self) -> list[Item]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/items/")
            r.raise_for_status()
            return [Item.model_validate(i) for i in r.json()]

    async def get_learners(self) -> list[Learner]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/learners/")
            r.raise_for_status()
            return [Learner.model_validate(i) for i in r.json()]

    async def get_pass_rates(self, lab: str) -> list[PassRate]:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/analytics/pass-rates", params={"lab": lab}
            )
            r.raise_for_status()
            return [PassRate.model_validate(i) for i in r.json()]

    async def get_timeline(self, lab: str) -> list[TimelineEntry]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/analytics/timeline", params={"lab": lab})
            r.raise_for_status()
            return [TimelineEntry.model_validate(i) for i in r.json()]

    async def get_groups(self, lab: str) -> list[GroupPerformance]:
        async with self._client() as c:
            r = await c.get(f"{self.base_url}/analytics/groups", params={"lab": lab})
            r.raise_for_status()
            return [GroupPerformance.model_validate(i) for i in r.json()]

    async def get_top_learners(self, lab: str, limit: int = 5) -> list[TopLearner]:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/analytics/top-learners",
                params={"lab": lab, "limit": limit},
            )
            r.raise_for_status()
            return [TopLearner.model_validate(i) for i in r.json()]

    async def get_completion_rate(self, lab: str) -> CompletionRate:
        async with self._client() as c:
            r = await c.get(
                f"{self.base_url}/analytics/completion-rate", params={"lab": lab}
            )
            r.raise_for_status()
            return CompletionRate.model_validate(r.json())

    async def sync_pipeline(self) -> SyncResult:
        async with self._client() as c:
            r = await c.post(f"{self.base_url}/pipeline/sync")
            r.raise_for_status()
            return SyncResult.model_validate(r.json())


# ---------------------------------------------------------------------------
# Observability Client (VictoriaLogs and VictoriaTraces)
# ---------------------------------------------------------------------------


class ObservabilityClient:
    """Client for VictoriaLogs and VictoriaTraces APIs."""

    def __init__(self, logs_url: str = "", traces_url: str = ""):
        self.logs_url = logs_url.rstrip("/") or "http://victorialogs:9428"
        self.traces_url = traces_url.rstrip("/") or "http://victoriatraces:10428"

    def _logs_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=30.0)

    def _traces_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(timeout=30.0)

    async def logs_search(
        self, query: str = "", limit: int = 100
    ) -> list[LogEntry]:
        """Search VictoriaLogs using LogsQL query."""
        async with self._logs_client() as c:
            r = await c.get(
                f"{self.logs_url}/select/logsql/query",
                params={"query": query, "limit": limit},
            )
            r.raise_for_status()
            # VictoriaLogs returns JSON array of log entries
            data = r.json()
            entries = []
            for item in data if isinstance(data, list) else [data]:
                if isinstance(item, dict):
                    entries.append(
                        LogEntry(
                            timestamp=item.get("_time", item.get("timestamp", "")),
                            level=item.get("level", item.get("severity", "info")),
                            service=item.get("service", item.get("app", "unknown")),
                            message=item.get("message", item.get("msg", str(item))),
                            raw=item,
                        )
                    )
            return entries

    async def logs_error_count(
        self, service: str = "", window_minutes: int = 60
    ) -> list[ErrorCount]:
        """Count errors per service over a time window."""
        # Build LogsQL query for errors
        if service:
            query = f'_stream:{{service="{service}"}} AND (level:error OR severity:error OR status:5*)'
        else:
            query = "_stream:{} AND (level:error OR severity:error OR status:5*)"
        
        async with self._logs_client() as c:
            r = await c.get(
                f"{self.logs_url}/select/logsql/query",
                params={"query": query, "limit": 1000},
            )
            r.raise_for_status()
            data = r.json()
            
            # Count errors by service
            error_counts: dict[str, int] = {}
            for item in data if isinstance(data, list) else [data]:
                if isinstance(item, dict):
                    svc = item.get("service", item.get("app", "unknown"))
                    error_counts[svc] = error_counts.get(svc, 0) + 1
            
            return [
                ErrorCount(service=svc, count=cnt, window_minutes=window_minutes)
                for svc, cnt in sorted(error_counts.items(), key=lambda x: -x[1])
            ]

    async def traces_list(
        self, service: str = "", limit: int = 20
    ) -> list[Trace]:
        """List recent traces from VictoriaTraces (Jaeger API)."""
        async with self._traces_client() as c:
            params = {"limit": limit}
            if service:
                params["service"] = service
            r = await c.get(f"{self.traces_url}/jaeger/api/traces", params=params)
            r.raise_for_status()
            data = r.json()
            
            traces = []
            for trace_data in data.get("data", []):
                trace_id = trace_data.get("traceID", "")
                spans = []
                for span_data in trace_data.get("spans", []):
                    spans.append(
                        TraceSpan(
                            trace_id=trace_id,
                            span_id=span_data.get("spanID", ""),
                            operation_name=span_data.get("operationName", ""),
                            service_name=span_data.get("process", {}).get(
                                "serviceName", "unknown"
                            ),
                            start_time=span_data.get("startTime", 0),
                            duration=span_data.get("duration", 0),
                            tags=span_data.get("tags", []),
                        )
                    )
                traces.append(Trace(trace_id=trace_id, spans=spans))
            return traces

    async def traces_get(self, trace_id: str) -> Trace | None:
        """Get a specific trace by ID."""
        async with self._traces_client() as c:
            r = await c.get(f"{self.traces_url}/jaeger/api/traces/{trace_id}")
            if r.status_code != 200:
                return None
            data = r.json()
            
            trace_data = data.get("data", [{}])[0] if data.get("data") else {}
            if not trace_data:
                return None
                
            tid = trace_data.get("traceID", trace_id)
            spans = []
            for span_data in trace_data.get("spans", []):
                spans.append(
                    TraceSpan(
                        trace_id=tid,
                        span_id=span_data.get("spanID", ""),
                        operation_name=span_data.get("operationName", ""),
                        service_name=span_data.get("process", {}).get(
                            "serviceName", "unknown"
                        ),
                        start_time=span_data.get("startTime", 0),
                        duration=span_data.get("duration", 0),
                        tags=span_data.get("tags", []),
                    )
                )
            return Trace(trace_id=tid, spans=spans)


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------


def format_health(result: HealthResult) -> str:
    if result.status == "healthy":
        return f"\u2705 Backend is healthy. {result.item_count} items available."
    return f"\u274c Backend error: {result.error or 'Unknown'}"


def format_labs(items: list[Item]) -> str:
    labs = sorted(
        [i for i in items if i.type == "lab"],
        key=lambda x: str(x.id),
    )
    if not labs:
        return "\U0001f4ed No labs available."
    text = "\U0001f4da Available labs:\n\n"
    text += "\n".join(f"\u2022 {lab.title}" for lab in labs)
    return text


def format_scores(lab: str, rates: list[PassRate]) -> str:
    if not rates:
        return f"\U0001f4ed No scores found for {lab}."
    text = f"\U0001f4ca Pass rates for {lab}:\n\n"
    text += "\n".join(
        f"\u2022 {r.task}: {r.avg_score:.1f}% ({r.attempts} attempts)" for r in rates
    )
    return text
