# Plan de Automatización: VPN IPSec Site-to-Site (FortiGate <-> Palo Alto)

## 1. Descripción del Proyecto
Este repositorio contiene la planificación técnica, los scripts de configuración (Ansible Playbooks) y la estrategia de validación para automatizar el despliegue de un túnel VPN IPSec entre dos fabricantes distintos: **Fortinet (FortiGate)** y **Palo Alto Networks (PAN-OS)**.

El objetivo es establecer una conexión segura y escalable utilizando estándares modernos (IKEv2, Route-Based VPN), adaptándose a las restricciones de un entorno de laboratorio virtualizado.

---

## 2. Definición de Parámetros Técnicos

Para garantizar la interoperabilidad, se ha seleccionado una arquitectura **Route-Based (VTI)**. Esto desacopla la capa de encriptación (IPSec) de la capa de políticas de seguridad.

### 2.1 Direccionamiento IP y Red
| Componente | Detalle | Valor / Rango |
| :--- | :--- | :--- |
| **Red de Túnel (P2P)** | Subred de enlace | `169.255.1.0` |
| **IP Túnel FortiGate** | Local Gateway (Site A) | `169.255.1.1/32` (Ajuste por requerimiento FortiOS) |
| **IP Túnel Palo Alto** | Local Gateway (Site B) | `169.255.1.2/32` |
| **Interfaz Física** | Uplink WAN | `port1` |
| **Enrutamiento** | Tipo | Estático (Static Route) hacia `10.200.200.0/22` |
| **NAT** | Configuración | **No-NAT** (Deshabilitado en políticas) |

### 2.2 Parámetros Criptográficos (IKEv2 & IPSec)
Se han estandarizado los parámetros para coincidir con los *defaults* más restrictivos (Palo Alto) y evitar renegociaciones fallidas.

| Fase | Parámetro | Valor Diseño (Prod) | **Valor Lab (Actual)** | Justificación |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | Versión | IKEv2 | IKEv2 | Estándar actual. |
| | Encriptación | AES-256-CBC | **DES-SHA256** | *Ver Nota 1* |
| | DH Group | 14 (2048-bit) | 14 | Requisito mínimo. |
| | Lifetime | 43200 sec | 43200 sec | Estándar. |
| **Phase 2** | Encriptación | AES-256-CBC | **DES-SHA256** | *Ver Nota 1* |
| | PFS | Enable | Enable | Seguridad. |
| | **Lifetime** | 3600 sec | **3600 sec** | **Crítico:** Sincronización con default de Palo Alto. |
| | Selectores | 0.0.0.0/0 | 0.0.0.0/0 | **Crítico:** Route-Based puro (Wildcard). |

> **⚠️ Nota 1 (Restricción de Laboratorio - LENC):**
> La máquina virtual (VM) de FortiGate utilizada para este despliegue tiene una licencia de evaluación **Low Encryption (LENC)**, la cual **no soporta algoritmos fuertes como AES**.
> **Acción:** Se ha degradado la criptografía a **DES** en los playbooks de Ansible únicamente para validar la funcionalidad del túnel y la lógica de automatización. En un entorno productivo con licencias completas, la variable `proposal` debe revertirse a `aes256-sha256`.

---

## 3. Desafíos y Ajustes de Implementación (Troubleshooting Log)

Durante la fase de automatización se encontraron y resolvieron los siguientes bloqueos técnicos específicos del entorno virtual (Proxmox/KVM).

### 3.1 Máscara de IP del Túnel (Error API `-8`)
* **Problema:** FortiOS v7.x rechaza la configuración de direcciones IP con máscara `/30` (255.255.255.252) en interfaces de tipo `tunnel` punto a punto.
* **Solución:** Se configuró la IP local del túnel como host único `/32` (`255.255.255.255`) y se definió explícitamente la `remote_ip` para mantener la lógica de enrutamiento punto a punto.

### 3.2 Idempotencia en Ansible (Error `missing required arguments`)
* **Problema:** Los módulos `router_static` y `firewall_policy` de la colección `fortinet.fortios` requieren identificadores explícitos para gestionar el estado (present/absent) correctamente.
* **Solución:** Se asignaron IDs fijos en el código (`seq_num: 10`, `policyid: 100`, `policyid: 101`) para garantizar que el playbook sea **idempotente** (se puede ejecutar múltiples veces sin duplicar errores).

### 3.3 Limitación en Validación de Palo Alto (VM Boot Failure)
* **Estado:** ⚠️ **Partially Tested** (Código desarrollado pero no aplicado en vivo).
* **Bloqueo Técnico:** La instancia virtual de Palo Alto (VM-Series sobre KVM/Proxmox) presentó una falla crítica en el arranque del **Management Plane**.
* **Evidencia:** La consola muestra el error `Error: unable to connect to Sysd` y `sysd_construct_sync_importer failed`, impidiendo el login administrativo.
* **Mitigación:** Se ha desarrollado el rol de Ansible `paloalto_vpn` basándose estrictamente en la documentación oficial de la colección `paloaltonetworks.panos`, listo para ser ejecutado una vez se disponga de una instancia sana.

<img width="1060" height="199" alt="image" src="https://github.com/user-attachments/assets/12eb0fca-8d7d-4d3e-b52a-a1068e3ac52c" />

---

## 4. Herramientas y APIs Seleccionadas

Para la orquestación se utiliza un enfoque **Agentless** basado en **Ansible**.

* **Control Node:** Contenedor LXC (Ubuntu 24.04) en Proxmox.
* **Fortinet:** Colección `fortinet.fortios` (API REST).
* **Palo Alto:** Colección `paloaltonetworks.panos` (API XML).
* **Gestión de Dependencias:** Uso de `pipx` para aislar el entorno de Python y evitar conflictos `externally-managed-environment`.

---

## 5. Estrategia de Validación y Evidencia

### 5.1 Resultado de Ejecución (FortiGate)
El playbook se ejecutó exitosamente contra el FortiGate, configurando todo el stack de red y seguridad sin errores (`failed=0`).

<img width="957" height="544" alt="image" src="https://github.com/user-attachments/assets/a72b2746-6299-489a-a2ed-1e5d83111bf5" />

### 5.2 Script de Verificación
Se incluye el script `scripts/vpn_health_check.py` para realizar validaciones de "Día 2":
1.  **Control Plane Check:** Consulta vía API el estado de las Fases 1 y 2 (`UP`/`Active`).
2.  **Data Plane Check:** Realiza pruebas de conectividad ICMP (Ping) a través del túnel.

---

## 6. Estructura del Repositorio

* `README.md`: Este documento de planificación y bitácora técnica.
* `site.yml`: Playbook maestro de Ansible.
* `/inventory`: Definición de hosts y grupos.
* `/group_vars`: Variables globales (credenciales, PSK).
* `/roles`: Lógica modularizada.
    * `fortigate_vpn`: Tareas probadas para FortiOS (Interfaces, Routing, VPN, Políticas).
    * `paloalto_vpn`: Tareas desarrolladas para PAN-OS.
* `/configs`: Plantillas de configuración de referencia.
