# ESR-CHALLENGEML-FASE2

# Plan de Automatización de VPN IPSec entre Fortigate (Sitio 1) y Palo Alto (Sitio 2)

## 1. Objetivo

Planificar la **automatización** de la configuración de una VPN IPSec **site-to-site** entre:

- **Sitio 1:** Firewall Fortigate
- **Sitio 2:** Firewall Palo Alto

El enfoque es **route-based**, utilizando una **red de túnel /30** dedicada y parametrizando todo lo necesario para que un script (Python / Ansible / API REST) pueda generar la configuración en ambos dispositivos.

---

## 2. Definición de Parámetros

### 2.1. Direcciones IP WAN

#### Sitio 1 – Fortigate

- Interfaz WAN: `port1`
- IP: `100.100.100.1/30`
- Gateway ISP: `100.100.100.2`
- Expuesto directamente a Internet: **Sí**

#### Sitio 2 – Palo Alto

- Interfaz WAN: `ethernet1/1`
- IP: `200.200.200.1/30`
- Gateway ISP: `200.200.200.2`
- Expuesto directamente a Internet: **Sí**

No hay NAT intermedio entre los dos firewalls.

---

### 2.2. Redes locales de ejemplo (LANs)

#### Sitio 1 – Fortigate (LAN)

- Interfaz `port2`
  - IP: `10.100.101.251/24`
  - Red: `10.100.101.0/24`
- Interfaz `port3`
  - IP: `10.100.102.251/24`
  - Red: `10.100.102.0/24`

#### Sitio 2 – Palo Alto (LAN)

- Interfaz `ethernet1/2`
  - IP: `10.200.201.252/24`
  - Red: `10.200.201.0/24`
- Interfaz `ethernet1/3`
  - IP: `10.200.202.252/24`
  - Red: `10.200.202.0/24`

---

### 2.3. Red de túnel

Se utilizará una **subred punto a punto /30 dedicada** para la VPN:

- Red de túnel: `169.255.1.0/30`
- Máscara: `255.255.255.252`

Asignación propuesta:

- **Fortigate (Sitio 1 – interfaz IPsec/túnel):** `169.255.1.1/30`
- **Palo Alto (Sitio 2 – interfaz tunnel.x):** `169.255.1.2/30`

Esta IP de túnel se usará como **next-hop** en las rutas estáticas para las redes remotas.

---

### 2.4. Zonas y puertos

#### Sitio 1 – Fortigate

- Zona `WAN`
  - Miembro: `port1`
- Zona `LAN_S1`
  - Miembros: `port2`, `port3`
- Zona `VPN_S1`
  - Miembro: interfaz IPsec `FGT-to-PA` (túnel)

#### Sitio 2 – Palo Alto

- Zona `untrust`
  - Miembro: `ethernet1/1`
- Zona `trust`
  - Miembros: `ethernet1/2`, `ethernet1/3`
- Zona `vpn`
  - Miembro: `tunnel.1` (interfaz lógica del túnel IPsec)

---

### 2.5. Parámetros IKE (Phase 1)

- **Versión IKE:** `IKEv2`
- **Autenticación:** 
  - Tipo: PSK (Pre-Shared Key)
  - Valor (ejemplo, a parametrizar): `S1-S2_vpn!Q9u5#2025`  
    > En el script se deberá generar o leer una PSK fuerte de forma segura.
- **Identificación (ID):**
  - Tipo de ID: `IP address`
  - Sitio 1 – ID local: `100.100.100.1`
  - Sitio 1 – ID remota: `200.200.200.1`
  - Sitio 2 – ID local: `200.200.200.1`
  - Sitio 2 – ID remota: `100.100.100.1`
- **Criptografía (propuesta IKE):**
  - Cifrado: `AES-256`
  - Integridad: `SHA-256`
  - Grupo Diffie-Hellman: `14` (2048 bits)
  - Tiempo de vida (lifetime): `28800` segundos (8 h)
- **DPD (Dead Peer Detection):**
  - Habilitado
  - Intervalo: `10 s`
  - Reintentos: `3`
  - Acción ante fallo: marcar peer como down y renegociar
- **NAT-T:** Deshabilitado (no hay NAT)
- **Rekey:** Habilitado

Todos estos parámetros deben ser **idénticos** en ambas puntas.

---

### 2.6. Parámetros IPsec (Phase 2)

- **Modo:** Tunnel
- **Protocolo:** ESP
- **Cifrado:** `AES-256`
- **Integridad:** `SHA-256`
- **PFS:** habilitado
  - Grupo DH: `14`
- **Tiempo de vida (lifetime Phase 2):** `3600` segundos (1 h)
- **Redes protegidas (selectors / Proxy IDs):**

Sitio 1 (local) → Sitio 2 (remota):

- `10.100.101.0/24` ↔ `10.200.201.0/24`
- `10.100.101.0/24` ↔ `10.200.202.0/24`
- `10.100.102.0/24` ↔ `10.200.201.0
