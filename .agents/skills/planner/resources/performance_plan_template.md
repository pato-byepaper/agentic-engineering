# Performance Optimization Plan: <Target Area>

- **Type**: Performance & Web Vitals Optimization
- **Target Area**: Frontend Speed | API Latency | Database Query Performance
- **Issue Reference**: #<ISSUE_NUMBER>

---

## 1. Baseline Measurements (Current State)
Record raw profiling measurements before making any changes:
- **Metric 1 (e.g. LCP / Latency)**: Current = `...` | Target = `...`
- **Metric 2 (e.g. INP / Throughput)**: Current = `...` | Target = `...`
- **Metric 3 (e.g. CLS / DB Query Duration)**: Current = `...` | Target = `...`

---

## 2. Profiling & Bottleneck Analysis
- **Identified Bottlenecks**:
  1. (e.g. Unindexed foreign key query causing sequential scan)
  2. (e.g. Large uncompressed hero image blocking Largest Contentful Paint)
  3. (e.g. Heavy CPU computation in render loop blocking main thread > 50ms)

---

## 3. Targeted Interventions
| Area | Intervention | Expected Gain |
| :--- | :--- | :--- |
| Database | Add composite index `idx_tenant_created` | Query duration drops from 120ms to 4ms |
| Frontend | Preload hero banner & add explicit aspect-ratio | LCP drops from 3.2s to 1.4s, CLS to 0.0 |
| Backend | Cache idempotent calculation in Redis / memory | API p95 drops from 250ms to 20ms |

---

## 4. Post-Optimization Verification
- [ ] Run benchmark commands and capture raw performance reports.
- [ ] Confirm zero behavioral regressions or altered response payloads.
- [ ] Re-run frontend bundle audit (`check_bundle_budget.sh`) or DB `EXPLAIN ANALYZE`.
