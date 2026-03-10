---
marp: true
theme: default
paginate: true
---

# Threat Modeling as Code — Lab Presentation

> A short lab to explain the TMasC approach and CI/CD integration

---

## Slide 1 — TMasC in a CI/CD Pipeline

### Threat Modeling as Code in CI/CD

Threat models can be integrated into CI/CD pipelines to **automate security checks**.

**During the build process:**
- The pipeline reads the threat model file
- Security tools analyze threats and mitigations
- The build fails if security requirements are missing

This ensures **continuous security validation** during development.

**What to say:** Threat Modeling as Code allows threat models to be stored in the same repository as the application code. Because of this, the threat model can be automatically analyzed inside the CI/CD pipeline every time the system is updated.

---

## Slide 2 — Threat Model as Code (Example)

### Example TMasC file written in YAML

```yaml
system: Online Store API

components:
  - name: WebApp
    type: service
  - name: Database
    type: storage

threats:
  - id: T1
    name: SQL Injection
    component: WebApp
    mitigation: Input validation and prepared statements
```

**What to say:** This file defines the system, its components, possible threats, and the security mitigations that should be implemented. Because the model is written as code, it can be automatically processed by security tools.

---

## Slide 3 — CI/CD Pipeline Integration

### Example GitHub Actions security check

```yaml
name: Security Check

on: [push, pull_request]

jobs:
  threat-model-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Validate Threat Model
        run: python tools/threat_check.py threat-model.yaml
```

**What to say:** In this pipeline, every time code is pushed to the repository, the pipeline runs automatically. A script analyzes the threat model file and verifies that security requirements are defined.

---

## Slide 4 — Pipeline Security Flow

### Automated Threat Model Validation

1. Developer pushes code to the repository  
2. CI/CD pipeline starts automatically  
3. Pipeline reads the threat model file  
4. Security tool analyzes threats and mitigations  
5. If issues are detected → the build fails or generates warnings  

**Visual flow:**
```
Developer pushes code
        ↓
CI/CD Pipeline starts
        ↓
Threat model file is read
        ↓
Security tool analyzes threats
        ↓
Security validation
   ↓            ↓
Pass        Fail / Warning
```

**What to say:** This process ensures that every system change is automatically checked against the threat model. If new components are added without security analysis, the pipeline can stop the deployment.

---

## Slide 5 — Ejemplo: APIs expuestas deben requerir autenticación

### Regla de seguridad

**Política:** Todas las APIs públicas deben requerir autenticación.

**Modelo TMasC:**
```yaml
components:
  - name: UserAPI
    type: api
    exposed: true
    auth_required: true

  - name: PublicInfoAPI
    type: api
    exposed: true
    auth_required: false
```

**Qué valida el pipeline:**
- Componentes con `type: api` y `exposed: true`
- Verifica que `auth_required` sea `true`
- Si encuentra `auth_required: false` → **falla**

**Resultado del pipeline (error):**
```
Security validation FAILED
Public API 'PublicInfoAPI' does not require authentication
```

**What to say:** En este ejemplo definimos una política de seguridad: todas las APIs públicas deben requerir autenticación. El pipeline revisa el modelo TMasC y si detecta una API expuesta sin autenticación, bloquea el build.

---

## Slide 6 — Regla: Rutas deben estar en el threat model

### El problema

Un desarrollador crea un nuevo endpoint y **no lo pone en el YAML** → el pipeline pasaría sin detectarlo.

### Solución: Manifiesto de rutas

**`api-routes-auth-example.yaml`:**
```yaml
routes:
  - path: /api/users
    component: UserAPI
  - path: /api/public
    component: PublicInfoAPI
  - path: /api/analytics    # Nuevo endpoint — NO está en threat model
    component: AnalyticsAPI
```

**Regla:** Cada ruta en el manifiesto debe tener su componente en el threat model.

**Resultado del pipeline (error):**
```
Security validation FAILED
  - Route '/api/analytics' references component 'AnalyticsAPI' which is not in the threat model.
    Add it to the threat model for security analysis.
```

**What to say:** El desarrollador debe agregar cada nuevo endpoint al manifiesto de rutas. El pipeline valida que todo lo que está en el manifiesto esté documentado en el threat model. Si agrega una ruta sin actualizar el modelo, el build falla.
