> **DEPRECATED / ARCHIVED**: This repository has been merged into the canonical **[authshield-lab](https://github.com/anya12forger12-max/authshield-lab)** project. Please use authshield-lab instead. No further updates will be made here.

<!-- Badges Placeholder -->
<!-- [![Build Status](https://img.shields.io/github/actions/workflow/status/anya12forger12-max/authshield-lab/ci.yml?branch=main)](https://github.com/anya12forger12-max/authshield-lab/actions) -->
<!-- [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) -->
<!-- [![WCAG 2.2 AA](https://img.shields.io/badge/WCAG-2.2%20AA-brightgreen.svg)](ACCESSIBILITY.md) -->
<!-- [![Version](https://img.shields.io/badge/version-5.0.0-blue.svg)](https://github.com/anya12forger12-max/authshield-lab/releases) -->

# AuthShield Lab

**An enterprise-grade, offline-first authentication security testing and education platform.**

AuthShield Lab provides a comprehensive environment for security professionals, developers, and educators to learn, test, and validate authentication mechanisms against real-world attack vectors. Built with privacy and accessibility at its core, the platform operates entirely offline with zero external dependencies.

---

## Features

### Security

- **Authentication Testing Engine** — Simulate and analyze attacks against multiple authentication protocols
- **Attack Vector Library** — Pre-built attack scenarios covering credential stuffing, brute force, MFA bypass, session hijacking, and more
- **Vulnerability Scanner** — Automated detection of common authentication weaknesses
- **Threat Modeling Dashboard** — Visualize attack surfaces and threat actor profiles
- **Credential Analysis** — Password strength analysis and breach database simulation
- **Token Security Testing** — JWT, OAuth, SAML, and session token validation and attack simulation

### Learning Management System (LMS)

- **Structured Learning Paths** — Beginner, intermediate, and advanced security curricula
- **Interactive Labs** — Hands-on exercises with real-time feedback
- **Progress Tracking** — Track completion, scores, and skill development over time
- **Certification Prep** — Practice scenarios aligned with industry certifications
- **Instructor Tools** — Classroom management, assignment creation, and grading

### Simulation

- **Realistic Attack Scenarios** — Run full attack chains in a safe, sandboxed environment
- **Blue Team / Red Team Exercises** — Collaborative defense and offense simulations
- **Incident Response Playbooks** — Practice responding to security incidents step by step
- **Time-Limited Challenges** — Capture-the-flag style exercises with scoring
- **Custom Scenario Builder** — Design and share your own attack/defense scenarios

### Developer Platform

- **REST API** — Full programmatic access to all platform features
- **Webhook Integrations** — Event-driven notifications for lab completions and alerts
- **Plugin Architecture** — Extend functionality with custom modules
- **CLI Toolkit** — Command-line interface for automation and CI/CD integration
- **SDK Support** — JavaScript/TypeScript and Python SDKs for rapid development

### Quality

- **Unit Test Coverage** — >90% code coverage with comprehensive unit tests
- **Integration Tests** — End-to-end testing of critical user workflows
- **Accessibility Audits** — Automated and manual WCAG 2.2 AA compliance testing
- **Performance Benchmarks** — Load testing and response time monitoring
- **Code Quality Gates** — ESLint, Prettier, and type checking enforced in CI

### Production

- **Docker Deployment** — Containerized deployment with Docker Compose
- **Database Migrations** — Versioned, reversible migration system
- **Configuration Management** — Environment-based configuration with sensible defaults
- **Health Checks** — Built-in health endpoint monitoring
- **Graceful Shutdown** — Proper resource cleanup on termination signals

### Analytics

- **Learning Analytics Dashboard** — Visualize learner progress and engagement
- **Security Metrics** — Track vulnerability detection rates and remediation times
- **Usage Statistics** — Platform usage reports for administrators
- **Export Capabilities** — CSV and JSON export of all analytics data

### Accessibility

- **WCAG 2.2 AA Compliance** — Full compliance with Web Content Accessibility Guidelines
- **Keyboard Navigation** — Complete keyboard-only operation support
- **Screen Reader Compatibility** — Tested with NVDA, JAWS, and VoiceOver
- **High Contrast Mode** — Enhanced visual presentation for low-vision users
- **Reduced Motion Support** — Respects `prefers-reduced-motion` system preference
- **Multi-Language Support** — Internationalization framework with RTL language support

---

## Quick Start

### Prerequisites

- **Node.js** v20.x or later
- **npm** v10.x or later (or **yarn** v4.x / **pnpm** v9.x)
- **Docker** v24.x and Docker Compose v2.x (optional, for containerized deployment)
- **Git** v2.40 or later

### Installation

```bash
# Clone the repository
git clone https://github.com/anya12forger12-max/authshield-lab.git
cd authshield-lab

# One-command install (backend + frontend)
./install.sh

# Set up environment variables
cp backend/.env.example backend/.env
```

### Running Locally

```bash
# Start the development server
npm run dev

# The application will be available at http://localhost:3000
```

### Running with Docker

```bash
# Build and start all services
docker compose up --build

# Run in detached mode
docker compose up -d
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage

# Run accessibility tests
npm run test:a11y
```

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        AuthShield Lab                           │
├─────────────┬──────────────┬──────────────┬────────────────────┤
│   Web UI    │   REST API   │     CLI      │     SDK Layer      │
│  (React)    │  (Express)   │  (Node.js)   │  (JS/Python)       │
├─────────────┴──────────────┴──────────────┴────────────────────┤
│                     Core Engine Layer                           │
├──────────┬──────────┬──────────┬──────────┬───────────────────┤
│  Attack  │  Auth    │  Token   │  Session │  Credential       │
│  Sim     │  Protocol│  Engine  │  Manager │  Analyzer         │
├──────────┴──────────┴──────────┴──────────┴───────────────────┤
│                    Data & Storage Layer                         │
├──────────────┬───────────────┬─────────────────────────────────┤
│  SQLite      │  File Store   │  In-Memory Cache                │
│  (Primary)   │  (Assets)     │  (Sessions/Tokens)              │
├──────────────┴───────────────┴─────────────────────────────────┤
│                 Learning Management System                      │
├──────────┬──────────┬──────────┬──────────────────────────────┤
│  Course  │  Lab     │  Grading │  Progress                    │
│  Engine  │  Runner  │  System  │  Tracker                     │
├──────────┴──────────┴──────────┴──────────────────────────────┤
│              Security & Compliance Layer                        │
├──────────────┬───────────────┬─────────────────────────────────┤
│  Audit Log   │  Access Ctrl  │  Encryption                    │
│  (Immutable) │  (RBAC)       │  (AES-256-GCM)                 │
└──────────────┴───────────────┴─────────────────────────────────┘
```

---

## Module Overview

| Module | Description | Status |
|--------|-------------|--------|
| `@authshield/core` | Core authentication testing engine | Stable |
| `@authshield/attacks` | Attack simulation library | Stable |
| `@authshield/tokens` | JWT, OAuth, SAML token testing | Stable |
| `@authshield/lms` | Learning management system | Stable |
| `@authshield/labs` | Interactive lab runner | Stable |
| `@authshield/api` | REST API server | Stable |
| `@authshield/cli` | Command-line interface | Stable |
| `@authshield/sdk` | JavaScript/TypeScript SDK | Stable |
| `@authshield/ui` | React web interface | Stable |
| `@authshield/analytics` | Analytics and reporting | Beta |
| `@authshield/plugins` | Plugin framework | Beta |
| `@authshield/i18n` | Internationalization | Alpha |

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript 5, Vite, Tailwind CSS |
| Backend | Node.js 20, Express 4, TypeScript 5 |
| Database | SQLite 3 (via better-sqlite3) |
| Testing | Vitest, Playwright, axe-core |
| Build | Vite, esbuild, TypeScript compiler |
| Linting | ESLint 9, Prettier 3 |
| CI/CD | GitHub Actions |
| Deployment | Docker, Docker Compose |
| Accessibility | axe-core, pa11y, manual testing |

---

## Documentation

- [Contributing Guide](CONTRIBUTING.md) — How to contribute to AuthShield Lab
- [Governance](GOVERNANCE.md) — Project governance and decision-making
- [Security Policy](SECURITY.md) — Reporting vulnerabilities and security practices
- [Accessibility Statement](ACCESSIBILITY.md) — WCAG 2.2 AA compliance details
- [Code of Conduct](CODE_OF_CONDUCT.md) — Community standards
- [Support](SUPPORT.md) — Getting help and support channels
- [Roadmap](ROADMAP.md) — Project direction and milestones
- [Changelog](CHANGELOG.md) — Release history and changes
- [Developer Onboarding](docs/development/ONBOARDING.md) — Setup and getting started guide
- [Branch Strategy](governance/policies/BRANCH_STRATEGY.md) — Git branching model
- [Commit Conventions](governance/policies/COMMIT_CONVENTIONS.md) — Commit message format
- [Review Process](governance/processes/REVIEW_PROCESS.md) — Code review guidelines
- [Release Process](governance/processes/RELEASE_PROCESS.md) — How releases are managed

---

## Contributing

We welcome contributions from the community! Please read our [Contributing Guide](CONTRIBUTING.md) before submitting a pull request. All contributors must adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>AuthShield Lab</strong> — Securing authentication, one test at a time.
</p>
