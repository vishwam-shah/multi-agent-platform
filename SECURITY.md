# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it privately rather than opening a public issue.

- Open a [GitHub Security Advisory](../../security/advisories/new) for this repository, or
- Contact the maintainer directly via the email on the GitHub profile.

Please include:

- A description of the vulnerability and its potential impact
- Steps to reproduce
- Any relevant logs or proof-of-concept code

We'll acknowledge reports within a few days and aim to release a fix promptly once confirmed.

## Scope

This project uses third-party LLM APIs (OpenAI, Anthropic, Tavily) and a code execution tool (`app/tools/code_exec.py`).

**Known limitation:** `code_exec` runs LLM-generated Python in a plain subprocess with a timeout — it is *not* isolated (no container, no restricted filesystem/network/user permissions). Treat any deployment that exposes this tool to untrusted input as high risk until it's backed by real sandboxing (e.g. a container, gVisor, or a service like Vercel Sandbox). Reports and PRs improving this are especially welcome.

Never commit real API keys — use `.env` (gitignored) with `backend/.env.example` as a template.
