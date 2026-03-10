# Threat Modeling as Code (TMasC) — Lab

A short lab demonstrating how threat models can be integrated into CI/CD pipelines for automated security validation.

## Lab Structure

```
TMasC/
├── docs/
│   └── slides.md               # Presentation slides (6 slides)
├── .github/workflows/
│   └── security-check.yml      # CI/CD pipeline example
├── tools/
│   └── threat_check.py        # Threat model validation script
├── threat-model.yaml           # Example threat model (passes validation)
├── threat-model-auth-example.yaml  # Example that fails (exposed API without auth)
├── api-routes-auth-example.yaml    # Manifiesto de rutas (regla: cada ruta debe estar en threat model)
├── requirements.txt            # Python dependencies
└── README.md
```

## Quick Start

### 1. Run the validation locally

```powershell
pip install -r requirements.txt
python tools/threat_check.py threat-model.yaml
```

### 2. Present the slides

- Open `docs/slides.md` and use it with:
  - **Marp** (VS Code extension or CLI) for Markdown-to-slides
  - **Copy/paste** into PowerPoint or Google Slides
  - Any Markdown-compatible presentation tool

### 3. CI/CD integration

Push to a GitHub repository; the workflow in `.github/workflows/security-check.yml` runs automatically on every push and pull request.

## Slide Overview

| Slide | Topic |
|-------|-------|
| 1 | TMasC in a CI/CD Pipeline — concept and benefits |
| 2 | Threat Model as Code — YAML example |
| 3 | CI/CD Pipeline Integration — GitHub Actions |
| 4 | Pipeline Security Flow — validation diagram |
| 5 | Ejemplo: APIs expuestas deben requerir autenticación |
| 6 | Regla: Rutas deben estar en el threat model |

## Example: Exposed APIs must require authentication

The script enforces: **if an API is exposed (`exposed: true`), it must require authentication (`auth_required: true`)**.

```powershell
# This fails (PublicInfoAPI is exposed without auth):
python tools/threat_check.py threat-model-auth-example.yaml
# Output: Security validation FAILED - Public API 'PublicInfoAPI' does not require authentication

# This passes:
python tools/threat_check.py threat-model.yaml
```

## Example: Routes must be in threat model (Regla de negocio)

**Regla:** Cada ruta en `api-routes-*.yaml` debe tener su componente documentado en el threat model.

Si un desarrollador agrega un endpoint en el manifiesto pero no lo pone en el threat model, el pipeline falla.

```powershell
# threat-model-auth-example.yaml + api-routes-auth-example.yaml
# api-routes incluye /api/analytics -> AnalyticsAPI (no está en el threat model)
python tools/threat_check.py threat-model-auth-example.yaml
# Output incluye: Route '/api/analytics' references component 'AnalyticsAPI' which is not in the threat model
```

El script detecta automáticamente `api-routes-auth-example.yaml` cuando validas `threat-model-auth-example.yaml`. También puedes pasarlo explícitamente:

```powershell
python tools/threat_check.py threat-model.yaml api-routes.yaml
```

## Customization

- Edit `threat-model.yaml` to add components and threats for your system
- Modify `tools/threat_check.py` to add custom validation rules
- Extend the GitHub Actions workflow for additional security checks
