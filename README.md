# Plan de Automatización: VPN IPSec Site-to-Site (FortiGate <-> Palo Alto)

## 1. Descripción del Proyecto
Este repositorio contiene la planificación técnica, los scripts de configuración (Ansible Playbooks) y la estrategia de validación para automatizar el despliegue de un túnel VPN IPSec entre dos fabricantes distintos: **Fortinet (FortiGate)** y **Palo Alto Networks (PAN-OS)**.

El objetivo es establecer una conexión segura y escalable utilizando estándares modernos (IKEv2, Route-Based VPN), adaptándose a las restricciones de un entorno de laboratorio virtualizado.

---

## 2. Definición de Parámetros Técnicos (Diseño Objetivo)

Para garantizar la interoperabilidad, se ha seleccionado una arquitectura **Route-Based (VTI)**. Esto desacopla la capa de encriptación (IPSec) de la capa de políticas de seguridad.

### 2.1 Direccionamiento IP y Red
| Componente | Detalle | Valor / Rango |
| :--- | :--- | :--- |
| **Red de Túnel (P2P)** | Subred de enlace | `169.255.1.0` |
| **IP Túnel FortiGate** | Local Gateway (Site A) | `169.255.1.1/32` (Ajustado por requerimiento FortiOS) |
| **IP Túnel Palo Alto** | Local Gateway (Site B) | `169.255.1.2/32` |
| **Enrutamiento** | Tipo | Estático (Static Route) |
| **NAT** | Configuración | **No-NAT** (Deshabilitado en políticas) |

### 2.2 Parámetros Criptográficos (IKEv2 & IPSec)
Se han estandarizado los parámetros para coincidir con los *defaults* más restrictivos (Palo Alto) y evitar renegociaciones fallidas.

| Fase | Parámetro | Valor Estándar (Prod) | **Valor Lab (Actual)** | Justificación |
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
> La máquina virtual (VM) de FortiGate utilizada para este despliegue tiene una licencia de evaluación **Low Encryption (LENC)**, la cual no soporta algoritmos fuertes como AES.
> **Acción:** Se ha degradado la criptografía a **DES** únicamente para validar la funcionalidad del túnel y la automatización. En producción, la variable `proposal` en Ansible debe revertirse a `aes256-sha256`.

---

## 3. Desviaciones y Ajustes de Implementación (Troubleshooting)

Durante la fase de automatización y pruebas, se realizaron ajustes técnicos y se documentaron bloqueos específicos del entorno virtual (Proxmox/KVM).

### 3.1 Cambio de Interfaz WAN (`port1` -> `port2`)
* **Problema:** La interfaz `port1` de la VM FortiGate presentaba conflictos al intentar asociar un túnel IPSec estático.
* **Solución:** Se migró la terminación de la VPN a la interfaz **`port2`**, validando previamente su configuración estática vía Ansible (Tarea 0).

### 3.2 Máscara de IP del Túnel (`/30` -> `/32`)
* **Problema:** FortiOS v7.x rechaza la configuración de direcciones IP con máscara `/30` en interfaces de tipo `tunnel` punto a punto (Error API: `-8`).
* **Solución:** Se configuró la IP local del túnel como `/32` (`255.255.255.255`) y se definió explícitamente la `remote_ip`.

### 3.3 Idempotencia en Ansible
* **Problema:** Los módulos de enrutamiento y políticas requerían identificadores explícitos para no duplicar entradas.
* **Solución:** Se asignaron IDs fijos en el código (`seq_num: 10`, `policyid: 100`) para garantizar la **idempotencia** del playbook.

### 3.4 Limitación en Validación de Palo Alto (VM Boot Failure)
* **Estado:** ⚠️ **Partially Tested** (Código desarrollado pero no aplicado en vivo).
* **Bloqueo Técnico:** La instancia virtual de Palo Alto (VM-Series sobre KVM/Proxmox) presentó una falla crítica en el arranque del **Management Plane**.
* **Evidencia:** La consola muestra el error `Error: unable to connect to Sysd` y `sysd_construct_sync_importer failed`.
* **Impacto:** Esto impide que el demonio de autenticación cargue, generando un bucle de "Login Incorrecto" incluso con las credenciales por defecto, haciendo inaccesible la API XML para Ansible.
* **Mitigación:** Se ha desarrollado el rol de Ansible `paloalto_vpn` basándose en la documentación oficial de la colección `paloaltonetworks.panos`, listo para ser ejecutado una vez se disponga de una instancia sana.

---

## 4. Herramientas y APIs Seleccionadas

Para la orquestación se utiliza un enfoque **Agentless** basado en **Ansible**.

* **Control Node:** Contenedor LXC (Ubuntu 24.04) en Proxmox.
* **Fortinet:** Colección `fortinet.fortios` (API REST).
* **Palo Alto:** Colección `paloaltonetworks.panos` (API XML).
* **Gestión de Dependencias:** Uso de `pipx` para aislar el entorno de Python.

---

## 5. Estrategia de Validación

Se incluye el script `scripts/vpn_health_check.py` para realizar validaciones post-deployment:

1.  **Control Plane Check:** Consulta vía API el estado de las Fases 1 y 2 (`UP`/`Active`).
2.  **Data Plane Check:** Realiza pruebas de conectividad ICMP (Ping) a través del túnel.

---

## 6. Estructura del Repositorio

* `README.md`: Este documento de planificación y bitácora técnica.
* `site.yml`: Playbook maestro de Ansible.
* `/inventory`: Definición de hosts y grupos.
* `/group_vars`: Variables globales (credenciales, PSK).
* `/roles`: Lógica modularizada.
    * `fortigate_vpn`: Tareas funcionales y probadas para FortiOS.
    * `paloalto_vpn`: Tareas desarrolladas para PAN-OS (Pending Validation).
* `/configs`: Plantillas de configuración de referencia.
---

## 7. Evidencia de Ejecución (Proof of Concept)

A continuación se presenta la evidencia de la ejecución exitosa del playbook de Ansible sobre el FortiGate.

Se observa la configuración idempotente de todos los componentes del stack (Interfaces, VPN Phase 1/2, Routing y Políticas) sin errores.

<img width="941" height="569" alt="image" src="https://github.com/user-attachments/assets/f35e9734-8e37-4ff5-a221-fdc463e1d3a2" />


> **Nota:** El resumen `changed=3` indica que Ansible detectó y aplicó las configuraciones faltantes (Rutas y Políticas), mientras que `ok=9` valida que el resto de la configuración (Interfaces y VPN) ya estaba en el estado deseado.
