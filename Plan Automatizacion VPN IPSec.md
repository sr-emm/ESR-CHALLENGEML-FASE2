# ESR-CHALLENGEML-FASE2

# Plan de Automatización de VPN IPSec entre Fortigate (Sitio 1) y Palo Alto (Sitio 2)

## 1. Objetivo

Planificar la **automatización** de la configuración de una VPN IPSec **site-to-site** entre:

- **Sitio 1:** Firewall Fortigate  
- **Sitio 2:** Firewall Palo Alto

El enfoque es **route-based**, utilizando una **red de túnel /30** dedicada y parametrizando todo lo necesario para que un script (Python / Ansible / API REST) pueda generar la configuración en ambos dispositivos.

Además, se implementa una **interfaz web en Flask** que:

- Solicita parámetros mínimos y seguros
- Valida compatibilidad
- Genera automáticamente el archivo `vpn_params.yaml`
- Facilita la generación posterior de configuraciones CLI o API

---

## 2. Definición de Parámetros

### 2.1. Direcciones IP WAN

#### Sitio 1 – Fortigate

- Interfaz WAN: `port1`  
- IP: `100.100.100.1/30`  
- Gateway: `100.100.100.2`  

#### Sitio 2 – Palo Alto

- Interfaz WAN: `ethernet1/1`  
- IP: `200.200.200.1/30`  
- Gateway: `200.200.200.2`  

Ambos están **directamente expuestos a Internet**, sin NAT intermedio.

---

### 2.2. Redes locales (LANs)

#### Sitio 1 – Fortigate

| Interfaz | IP | Red |
|----------|------|-------|
| port2 | 10.100.101.251/24 | 10.100.101.0/24 |
| port3 | 10.100.102.251/24 | 10.100.102.0/24 |

#### Sitio 2 – Palo Alto

| Interfaz | IP | Red |
|----------|------|-------|
| ethernet1/2 | 10.200.201.252/24 | 10.200.201.0/24 |
| ethernet1/3 | 10.200.202.252/24 | 10.200.202.0/24 |

---

### 2.3. Red de túnel

- Red: `169.255.1.0/30`  
- Fortigate: `169.255.1.1`  
- Palo Alto: `169.255.1.2`  

Esta IP será el **next-hop** en las rutas hacia el sitio remoto.

---

### 2.4. Zonas y puertos

#### Fortigate

- `WAN` → port1  
- `LAN_S1` → port2, port3  
- `VPN_S1` → interfaz IPsec del túnel  

#### Palo Alto

- `untrust` → ethernet1/1  
- `trust` → ethernet1/2, ethernet1/3  
- `vpn` → tunnel.1  

---

### 2.5. Parámetros IKE (Phase 1)

- **IKEv2**
- Autenticación: PSK (definida por el usuario)
- Propuesta:
  - AES-256
  - SHA-256
  - Grupo Diffie-Hellman (seleccionable):
    - 2
    - 5
    - 14
    - 19
    - 20
    - 21  
  - Lifetime: 28800 s
- DPD: habilitado (10s, 3 reintentos)
- Rekey: habilitado
- NAT-T: deshabilitado

---

### 2.6. Parámetros IPsec (Phase 2)

- Protocolo: ESP  
- Cifrado: AES-256  
- Integridad: SHA-256  
- PFS: habilitado (mismo DH que Phase 1)  
- Lifetime: 3600 s  

**Selectors / Proxy-IDs:**

- 10.100.101.0/24 ↔ 10.200.201.0/24  
- 10.100.101.0/24 ↔ 10.200.202.0/24  
- 10.100.102.0/24 ↔ 10.200.201.0/24  
- 10.100.102.0/24 ↔ 10.200.202.0/24  

---

### 2.7. Rutas requeridas

#### Fortigate

```
0.0.0.0/0 → 100.100.100.2 vía port1
10.200.201.0/24 → 169.255.1.2 vía túnel
10.200.202.0/24 → 169.255.1.2 vía túnel
```

#### Palo Alto (VR1)

```
0.0.0.0/0 → 200.200.200.2 vía ethernet1/1
10.100.101.0/24 → 169.255.1.1 vía tunnel.1
10.100.102.0/24 → 169.255.1.1 vía tunnel.1
```

---

### 2.8. PSK – Reglas de compatibilidad

#### Caracteres **permitidos** en ambos equipos

```
A-Z a-z 0-9 ! # $ % & ( ) * + , - . / : ; < = > ? @ [ ] ^ _ { | } ~
```

#### Caracteres **NO permitidos**

- Espacios  
- Tildes / ñ / Unicode  
- Comillas `'`  
- Comillas `"`  
- Backslash `\`

#### Validación aplicada en el formulario

    pattern="[A-Za-z0-9!#$%&()*+,./:;<=>?@\[\]\^_{|}~-]{12,}"

---

## 3. Políticas de Firewall necesarias

### 3.1. Fortigate

#### LAN → VPN

- `srcintf`: LAN_S1  
- `dstintf`: VPN_S1  
- `srcaddr`: 10.100.101.0/24, 10.100.102.0/24  
- `dstaddr`: 10.200.201.0/24, 10.200.202.0/24  
- `service`: ALL  
- `nat`: disable  

#### VPN → LAN

- Inverso de la regla anterior

---

### 3.2. Palo Alto

#### trust → vpn

- Desde redes LAN del Sitio 2 hacia Sitio 1  
- `action`: allow  

#### vpn → trust

- Desde LAN del Sitio 1 hacia Sitio 2  
- `action`: allow  

#### Regla OBLIGATORIA para permitir IKE/ESP desde Internet

```
from: untrust
to: untrust
source: 100.100.100.1  (o any)
destination: 200.200.200.1
application: ike, ipsec-esp
action: allow
```

---

## 4. Herramientas / APIs disponibles

### Fortigate

- API REST FortiOS
- SSH (netmiko, paramiko, scrapli)
- Ansible (`fortios_*`)

### Palo Alto

- XML API / REST API
- SSH
- Ansible (`panos_*`)

---

## 5. Pasos de Automatización

### 5.1. Flujo general

1. Usuario completa formulario Flask  
2. Validación HTML + Backend  
3. Generación de `vpn_params.yaml`  
4. Scripts usan YAML para:
   - Crear configuraciones CLI
   - Aplicar cambios vía API REST/XML
   - Generar plantillas Jinja2  
   - Validar funcionamiento

---

## 6. Interfaz Web (Flask)

### 6.1. Formulario

- Diseño oscuro  
- Columnas fijas 50/50  
- Inputs ocupan 100% de celda  
- Validación:
  - PSK segura
  - IPs válidas
  - Interfaces válidas
  - Selección de DH  
- Exporta todo a YAML

### 6.2. Backend (`app.py`)

- Valida toda la data
- Construye YAML:
  - Sitio 1
  - Sitio 2
  - PSK
  - DH
  - IKE/IPsec
  - Selectores
  - Políticas
  - Rutas
- Guarda resultado en `output/vpn_params.yaml`

---

## 7. Verificación y Troubleshooting

### Fortigate

```
diagnose vpn ike gateway list
diagnose vpn tunnel list
```

### Palo Alto

```
show vpn ike-sa
show vpn ipsec-sa
```

### Ping LAN ↔ LAN

- 10.100.101.251 → 10.200.201.252  
- 10.200.201.252 → 10.100.101.251  

---

## 8. Próximos pasos

- Crear `generate_cli.py` para generar:
  - CLI de Fortigate
  - CLI de Palo Alto  
- Integrar llamadas API  
- Crear módulo de verificación automática  

---

## 9. Archivos del proyecto

- `app.py`  
- `templates/form.html`  
- `output/vpn_params.yaml`  
- `docs/ESR-CHALLENGEML-FASE2.md`  
- `generate_cli.py` *(pendiente)*  
- Plantillas Jinja2 *(opcional)*

---
