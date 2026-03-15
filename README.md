# SwarmGym: On-Chain Safety Auditor for Multi-Agent AI Systems

**Built for [The Synthesis](https://synthesis.devfolio.co) hackathon.**

SwarmGym computes distributional safety metrics for multi-agent interaction logs and attests the results on-chain via Base (ERC-8004 compatible). Agents get verifiable safety scores.

## Core Idea

Multi-agent AI systems need safety guarantees that go beyond binary good/bad labels. SwarmGym uses **soft (probabilistic) labels** to compute nuanced safety metrics:

- **Toxicity**: `E[1-p | accepted]` — expected harm among accepted interactions
- **Adverse selection**: quality gap `E[p|accepted] - E[p|rejected]` — are bad interactions preferentially accepted?
- **Safety grade**: A-F letter grade combining toxicity and adverse selection
- **Attestation hash**: SHA-256 of canonical metrics JSON, submittable on-chain for verifiability

## Quick Start

```bash
# Install
pip install -e ".[dev]"

# Generate synthetic interaction log
python swarm_gym_cli.py generate --agents 3 --interactions 50 -o demo.jsonl

# Audit an agent
python swarm_gym_cli.py audit --file demo.jsonl --agent-id agent_0

# Audit with JSON output
python swarm_gym_cli.py audit --file demo.jsonl --agent-id agent_0 --json

# Submit attestation on-chain (requires deployed contract + private key)
python swarm_gym_cli.py attest --file demo.jsonl --agent-id agent_0 \
    --contract 0x... --private-key 0x... --rpc https://mainnet.base.org

# Verify on-chain attestation
python swarm_gym_cli.py verify --agent-id agent_0 --hash 0x... --contract 0x...
```

## API

Start the server:

```bash
uvicorn swarm.api.app:app --reload
```

### POST /api/v1/audits/compute

```json
{
  "agent_id": "agent_0",
  "interactions": [
    {"initiator": "agent_0", "counterparty": "agent_1", "accepted": true, "p": 0.85, "v_hat": 0.7}
  ]
}
```

Returns metrics, safety grade, and attestation hash.

## Architecture

```
Interaction logs → MetricsReporter → soft/hard metrics → safety grade
                                                        → SHA-256 hash
                                                        → on-chain attestation (Base)
```

### Components

| File | Purpose |
|------|---------|
| `swarm/api/routers/auditor.py` | FastAPI endpoint: POST /api/v1/audits/compute |
| `swarm/metrics/reporters.py` | MetricsReporter: dual soft/hard metric computation |
| `swarm/metrics/soft_metrics.py` | SoftMetrics: toxicity, quality gap, calibration |
| `swarm/models/interaction.py` | SoftInteraction: interaction data model with p in [0,1] |
| `swarm/chain/attestation.py` | AttestationClient: submit/verify on Base via web3 |
| `swarm/core/payoff.py` | SoftPayoffEngine: expected surplus, externality costs |
| `contracts/SafetyAttestation.sol` | Solidity contract for on-chain attestation storage |
| `swarm_gym_cli.py` | CLI tool: generate, audit, attest, verify |
| `scripts/deploy_attestation.py` | Contract deployment script |

## On-Chain Contract

`SafetyAttestation.sol` stores:
- Metrics hash (SHA-256 of canonical JSON)
- Agent ID
- Safety grade (A-F)
- Adverse selection flag
- Interaction count
- Timestamp and submitter address

Deployed on Base Mainnet. Duplicate hashes are rejected (uniqueness enforced).

## Tests

```bash
python -m pytest tests/ -v
```

21 tests covering the auditor API endpoint, safety grading, metrics hash determinism, input validation, and adverse selection detection.

## Domain Concepts

- **p**: Probability that interaction is beneficial, `P(v = +1)`, always in `[0, 1]`
- **v_hat**: Raw proxy score before sigmoid, in `[-1, +1]`
- **Adverse selection**: When low-quality interactions are preferentially accepted (quality_gap < 0)
- **Externality internalization**: rho parameters control how much agents bear cost of ecosystem harm

## License

MIT

## Hackathon

- **Event**: The Synthesis (Devfolio)
- **Track**: Agents With Receipts — ERC-8004
- **Team**: Swarm AI Research Engineer
- **Registration**: [BaseScan tx](https://basescan.org/tx/0x6dd43149952f0426fa3e161b8776ab7869507855b119f5cf03dafa7dd8004ba2)
