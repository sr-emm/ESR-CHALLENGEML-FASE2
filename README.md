# Plan de Automatización: VPN IPSec Site-to-Site (FortiGate <-> Palo Alto)

## 1. Descripción del Proyecto
Este repositorio contiene la planificación técnica, los scripts de configuración y la estrategia de validación para automatizar el despliegue de un túnel VPN IPSec entre dos fabricantes distintos: **Fortinet (FortiGate)** y **Palo Alto Networks (PAN-OS)**.

El objetivo es establecer una conexión segura, estable y escalable utilizando estándares modernos (IKEv2, Route-Based VPN) y mitigar los problemas de interoperabilidad comunes en entornos heterogéneos.

---

## 2. Definición de Parámetros Técnicos

Para garantizar la interoperabilidad, se ha seleccionado una arquitectura **Route-Based (VTI)** en lugar de Policy-Based. Esto desacopla la capa de encriptación (IPSec) de la capa de políticas de seguridad, simplificando la automatización.

### 2.1 Direccionamiento IP y Red
| Componente | Detalle | Valor / Rango |
| :--- | :--- | :--- |
| **Red de Túnel (P2P)** | Subred de enlace /30 | `169.255.1.0/30` |
| **IP Túnel FortiGate** | Local Gateway (Site A) | `169.255.1.1` |
| **IP Túnel Palo Alto** | Local Gateway (Site B) | `169.255.1.2` |
| **Enrutamiento** | Tipo | Estático (Static Route) |
| **NAT** | Configuración | **No-NAT** (Deshabilitado en políticas) |

### 2.2 Parámetros Criptográficos (IKEv2 & IPSec)
Se han estandarizado los parámetros para coincidir con los *defaults* más restrictivos (Palo Alto) y evitar renegociaciones fallidas.

| Fase | Parámetro | Valor Configurado | Justificación Técnica |
| :--- | :--- | :--- | :--- |
| **Phase 1** | Versión | **IKEv2** | Estándar actual, mejor manejo de DPD y Rekey. |
| (IKE Proposal) | Encriptación | AES-256-CBC | Seguridad robusta. |
| | Integridad | SHA-256 | Balance seguridad/rendimiento. |
| | DH Group | Group 14 (2048-bit) | Requisito mínimo de seguridad actual. |
| | Lifetime | 43200 sec (12 horas) | Estándar de industria. |
| **Phase 2** | Encriptación | AES-256-CBC | Coincidencia con Fase 1. |
| (IPSec Proposal)| PFS | **Enable** (Group 14) | Perfect Forward Secrecy requerido. |
| | **Lifetime** | **3600 sec (1 hora)** | **Crítico:** Palo Alto usa 3600s por defecto. Fortinet debe ajustarse a este valor para evitar *flapping*. |
| | **Selectores** | **0.0.0.0/0** (Wildcard) | **Crítico:** Permite modo Route-Based puro. Evita "mismatches" de Proxy ID al agregar nuevas VLANs. |

---

## 3. Herramientas y APIs Seleccionadas

Para la orquestación se propone un enfoque **Agentless** basado en **Ansible**, interactuando directamente con las APIs REST/XML de los dispositivos.

### 3.1 Controlador de Automatización
* **Lenguaje:** Python 3.9+
* **Orquestador:** Ansible Core
* **Gestión de Secretos:** Ansible Vault (Para proteger PSK y credenciales).

### 3.2 Módulos Específicos
* **Fortinet:** Colección `fortinet.fortios`.
    * *Uso:* Configuración de `phase1-interface`, `phase2-interface` y `system interface` (tunnel) via REST API.
* **Palo Alto:** Colección `paloaltonetworks.panos`.
    * *Uso:* Configuración de `ike-crypto-profiles`, `ipsec-tunnels` y `commit` operations via XML API.

---

## 4. Pasos Lógicos de Automatización

El script de despliegue sigue un flujo secuencial estricto para gestionar las dependencias de objetos.

### Flujo A: Configuración FortiGate (Site 1)
1.  **Definir Interfaces:** Crear la interfaz lógica tipo *Tunnel* sobre la WAN.
2.  **Configurar VPN (Phase 1):** Establecer IKEv2, Remote Gateway y PSK. Habilitar `nattraversal`.
3.  **Configurar VPN (Phase 2):** Establecer propuestas IPSec. **Importante:** Definir `src-subnet` y `dst-subnet` como `0.0.0.0/0`.
4.  **Enrutamiento:** Crear ruta estática hacia las LANs del Sitio 2 apuntando a la interfaz del túnel.
5.  **Políticas:** Crear reglas de firewall (Inbound/Outbound) con `Action: Accept` y `NAT: Disable`.
    * *Optimización:* Aplicar `tcp-mss-sender 1360` para prevenir fragmentación.

### Flujo B: Configuración Palo Alto (Site 2)
1.  **Network Profiles:** Crear perfiles IKE y IPSec Crypto coincidiendo con FortiGate.
2.  **Tunnel Interface:** Crear interfaz `tunnel.1`, asignar IP `169.255.1.2/30`, Virtual Router y Zona de Seguridad (`VPN_Zone`).
3.  **IKE Gateway:** Asociar perfil IKE y definir Peer IP.
4.  **IPSec Tunnel:** Crear el túnel asociando la interfaz `tunnel.1` y el IKE Gateway.
    * **Acción de Automatización Clave:** Configurar explícitamente el **Proxy ID** como `Local: 0.0.0.0/0` / `Remote: 0.0.0.0/0` para "engañar" al Palo Alto y forzar compatibilidad con el FortiGate.
5.  **Commit:** Ejecutar comando de commit y esperar validación asíncrona.

---

## 5. Desafíos en Entornos Heterogéneos (Multi-Vendor)

Durante la planificación se identificaron y mitigaron los siguientes riesgos de interoperabilidad:

### 5.1 Proxy ID Mismatch (El problema del "Proposal Chosen")
* **Desafío:** Fortinet en modo interfaz propone selectores "Wildcard" (`0.0.0.0`). Palo Alto espera selectores específicos. Si no coinciden, la VPN no levanta.
* **Solución:** Se fuerza la configuración de Proxy IDs `0.0.0.0/0` en el lado de Palo Alto. Esto simula un comportamiento "Route-Based" puro en ambos extremos.

### 5.2 Discrepancia de Lifetimes
* **Desafío:** Palo Alto renegocia la Fase 2 cada 1 hora (3600s). Fortinet suele tener tiempos mayores (8-12 horas). Cuando Palo Alto inicia la renegociación, Fortinet puede rechazarla si los parámetros no coinciden exactamente.
* **Solución:** Se hardcodea el valor `keylifeseconds: 3600` en el script de Fortinet para alinearse con el estándar más restrictivo (Palo Alto).

### 5.3 MTU y Fragmentación
* **Desafío:** El overhead de los encabezados ESP/IKE puede causar que paquetes de 1500 bytes se fragmenten o descarten.
* **Solución:** Se configura *MSS Clamping* a 1360 bytes en las políticas de Fortinet y se habilita `adjust-tcp-mss` en la interfaz del Palo Alto.

---

## 6. Estrategia de Validación y Alertas

Una vez desplegada la configuración, se ejecuta un "Health Check" automatizado (Day-2 Operation).

### 6.1 Script de Validación (`scripts/vpn_health_check.py`)
Se incluye un script en Python que realiza las siguientes validaciones:

1.  **Control Plane Check (API):**
    * Consulta a FortiGate: Verifica que `phase2-interface` esté en estado "UP".
    * Consulta a Palo Alto: Verifica que `ipsec-tunnel-status` sea "Active".
2.  **Data Plane Check (Ping):**
    * Realiza un ping ICMP desde la IP del túnel local (`.1`) hacia la remota (`.2`).
    * Esto valida que el tráfico está siendo encriptado y desencriptado correctamente, independientemente de las reglas de firewall de las LANs.

### 6.2 Alertas
* **Escenario de Éxito:** Log "VPN OPERATIONAL" (Código de salida 0).
* **Escenario de Fallo:**
    * Si falla la API: Alerta "CRITICAL: Management Plane Error".
    * Si falla el Ping: Alerta "CRITICAL: IPSec Tunnel Established but No Traffic Passing (Check Routing/Firewall)".
    * **Notificación:** Integración propuesta con Webhooks (Slack/Teams) para notificar al equipo de NetOps inmediatamente.

---

## 7. Estructura del Repositorio

* `README.md`: Este documento de planificación.
* `/configs`: Plantillas de configuración generadas (FortiOS CLI y PAN-OS Set commands).
    * `fortigate_vpn_wildcard.conf`
    * `paloalto_vpn_wildcard.set`
* `/scripts`: Scripts opcionales de validación.
    * `vpn_health_check.py`: Script de Python para validar conectividad post-deploy.