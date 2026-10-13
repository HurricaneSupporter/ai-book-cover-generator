# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security-only |
| < 0.5   | no        |

## Reporting a vulnerability

Do **not** open a public issue for security problems. Email
`security@covergen.dev` with:

- A description of the issue.
- Steps to reproduce.
- Impact assessment (RCE, path traversal, key exfiltration, etc.).
- A suggested fix, if you have one.

We aim to acknowledge within 72 hours and ship a patch within 14 days for
high-severity issues.

## Threat model

`ai-book-cover-generator` is a **local desktop tool**. It:

- Reads and writes files under the user's project directory and
  `outputs/`.
- Optionally calls remote inference APIs when a backend is configured with
  a remote endpoint (Stability, Replicate, custom).
- Loads model weights from `.models/` (local disk only by default).

Out of scope: a compromised local model file, a user pasting a malicious
prompt into a third-party backend, a fully compromised host.

In scope: path traversal in prompt preset loading, unsafe YAML
deserialization, SSRF via a user-supplied remote backend URL, and
unvalidated model checkpoint deserialization.

## Secrets

API keys live in `secrets.toml` or the environment
(`COVERGEN_API_KEY`, `COVERGEN_BACKEND_URL`). Never commit them.
`secrets.toml` and `config/local.yaml` are gitignored.

## Prompt-injection note

Prompts are user input. The tool does not execute prompt text. If a
backend returns a URL, it is fetched only if `allow_remote_fetch: true`
in config.