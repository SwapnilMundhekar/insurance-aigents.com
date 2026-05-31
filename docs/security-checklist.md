# Security Checklist

This project is a public portfolio repository. The repository must never include local secrets, generated data, private documents, or machine-specific paths.

## Do not commit

- `.env` files
- `.venv` or `venv` folders
- uploaded PDFs
- generated chunks
- generated vector indexes
- agent trace logs
- Cloudflare tunnel credentials
- API keys or tokens
- private keys
- local Windows paths
- temporary setup scripts

## Safe to commit

- backend source code
- README files
- documentation
- configuration templates such as `.env.example`
- Docker Compose templates
- tests

## Before every push

Run:

```bash
git status
git diff --cached --name-only
```

Confirm the staged files do not include local generated data or secrets.
