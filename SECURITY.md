# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in AI Signal, please report it responsibly:

1. **Do not** open a public issue for security vulnerabilities
2. Email the maintainer directly or use [GitHub's private vulnerability reporting](https://github.com/vhdesai/ai-signal/security/advisories/new)
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Assessment:** Within 1 week
- **Fix/Disclosure:** Coordinated with reporter

## Security Considerations

### Data Handling

- Raw news digests in `news/` are git-ignored and never deployed
- The generated `site/` contains only public-facing article summaries and metadata
- No user authentication or personal data is collected
- The SQLite database may contain full article text — treat `indexes/` as sensitive if needed

### URL Validation

- The URL repair stage (`urls.py`) makes outbound HTTP requests to validate article links
- Outbound requests use a generic User-Agent header
- DuckDuckGo search is used for URL discovery — no API keys required

### Dependencies

- All Python dependencies are declared in `pyproject.toml` and `requirements.txt`
- Regularly update dependencies to patch known vulnerabilities
- Run `pip audit` to check for known CVEs in dependencies

### Deployment

- Cloudflare Pages deployment requires `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID` stored as GitHub secrets
- Never commit API tokens or credentials to the repository
- The GitHub Actions workflow has minimal permissions (`contents: read`, `deployments: write`)

## Best Practices

- Keep secrets in GitHub repository settings, never in code
- Review PR diffs before merging to ensure no credentials are included
- Use `pip audit` or `safety check` periodically to scan dependencies
