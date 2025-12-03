# Plan de Automatización: VPN IPSec Site-to-Site (FortiGate <-> Palo Alto)

## 1. Descripción del Proyecto
Este repositorio contiene la planificación técnica, los scripts de configuración (Ansible Playbooks) y la estrategia de validación para automatizar el despliegue de un túnel VPN IPSec entre dos fabricantes distintos: **Fortinet (FortiGate)** y **Palo Alto Networks (PAN-OS)**.

El objetivo es establecer una conexión segura y escalable utilizando estándares modernos (IKEv2, Route-Based VPN), adaptándose a las restricciones de un entorno de laboratorio virtualizado.

---

## 2. Definición de Parámetros Técnicos

Para garantizar la interoperabilidad y escalabilidad, se ha seleccionado una arquitectura **Route-Based (VTI)**. Esto desacopla la capa de encriptación (IPSec) de la capa de políticas de seguridad.

### 2.1 Direccionamiento IP y Red
| Componente | Detalle | Valor / Rango |
| :--- | :--- | :--- |
| **Red de Túnel (P2P)** | Subred de enlace | `169.255.1.0/30` (Diseño) |
| **IP Túnel FortiGate** | Local Gateway (Site A) | `169.255.1.1/32` (Ajuste técnico por limitación FortiOS) |
| **IP Túnel Palo Alto** | Local Gateway (Site B) | `169.255.1.2/32` |
| **Interfaz Física** | Uplink WAN | `port1` |
| **Enrutamiento** | Tipo | Estático (Static Route) hacia `10.200.200.0/22` |
| **NAT** | Configuración | **No-NAT** (Deshabilitado en políticas) |

### 2.2 Parámetros Criptográficos (IKEv2 & IPSec)

Se han estandarizado los parámetros buscando el equilibrio entre seguridad y compatibilidad. A continuación se detallan los valores seleccionados para el laboratorio frente a los estándares de industria recomendados.

| Fase | Parámetro | Valor Estándar (Prod) | **Valor Lab (Actual)** | Notas Técnicas |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 1** | Versión | IKEv2 | IKEv2 | Estándar actual (RFC 7296). |
| | Encriptación | AES-256-GCM / CBC | **DES-SHA256** | *Limitado por licencia (Ver Nota 1)* |
| | DH Group | 19, 20, 21 (ECDH) | **14 (2048-bit)** | Grupo 14 es el mínimo seguro aceptable. |
| | Lifetime | 43200 - 86400 sec | 43200 sec | Estándar. |
| **Phase 2** | Encriptación | AES-256-GCM / CBC | **DES-SHA256** | *Limitado por licencia (Ver Nota 1)* |
| | PFS | Enable | Enable | Perfect Forward Secrecy. |
| | **Lifetime** | 3600 sec | **3600 sec** | **Crítico:** Sincronización con default de Palo Alto. |
| | Selectores | 0.0.0.0/0 | 0.0.0.0/0 | **Crítico:** Route-Based puro (Wildcard). |

#### 📚 Profundización: Opciones de Criptografía Disponibles
Para un despliegue en producción, el orquestador y los playbooks están diseñados para soportar los siguientes conjuntos de cifrado, dependiendo de la capacidad del hardware:

* **Grupos Diffie-Hellman (DH):**
    * **Modernos (Recomendados):** Group 19, 20, 21 (Elliptic Curve - ECDH). Ofrecen mayor seguridad con menor consumo de CPU.
    * **Estándar (Línea base):** Group 14 (Modular Exponentiation 2048-bit). Es el estándar mínimo hoy en día.
    * **Legacy (A evitar):** Group 2, 5 (Débiles/Crackeables).

* **Algoritmos de Encriptación:**
    * **Recomendados:** `AES-256-GCM` (Mayor rendimiento y autenticación integrada), `AES-128-GCM`.
    * **Aceptables:** `AES-256-CBC`, `AES-128-CBC` (Requieren SHA para integridad).
    * **Lab/Legacy:** `DES`, `3DES`, `RC4` (Inseguros, usados aquí solo por restricción de licencia).

> **⚠️ Nota 1 (Restricción de Laboratorio - LENC):**
> La máquina virtual (VM) de FortiGate utilizada para este despliegue tiene una licencia de evaluación **Low Encryption (LENC)**, la cual **bloquea algoritmos fuertes como AES**.
> **Acción:** Se ha degradado la criptografía a **DES** en los playbooks de Ansible únicamente para validar la funcionalidad del túnel (Handshake IKE y flujo de paquetes). En un entorno productivo, la variable `proposal` debe revertirse a `aes256-gcm`.

---

## 3. Desafíos y Ajustes de Implementación (Troubleshooting Log)

Durante la fase de automatización se encontraron y resolvieron los siguientes bloqueos técnicos específicos del entorno virtual (Proxmox/KVM).

### 3.1 Máscara de IP del Túnel (Error API `-8`)
* **Problema:** FortiOS v7.x rechaza la configuración de direcciones IP con máscara `/30` (255.255.255.252) en interfaces de tipo `tunnel` punto a punto cuando no son numeradas.
* **Solución:** Se configuró la IP local del túnel como host único `/32` (`255.255.255.255`) y se definió explícitamente la `remote_ip` para mantener la lógica de enrutamiento.

### 3.2 Idempotencia en Ansible (Error `missing required arguments`)
* **Problema:** Los módulos `router_static` y `firewall_policy` de la colección `fortinet.fortios` requieren identificadores explícitos para gestionar el estado (present/absent) correctamente y no duplicar objetos.
* **Solución:** Se asignaron IDs fijos en el código (`seq_num: 10`, `policyid: 100`, `policyid: 101`) para garantizar que el playbook sea **idempotente**.

### 3.3 Limitación en Validación de Palo Alto (VM Boot Failure)
* **Estado:** ⚠️ **Partially Tested** (Código desarrollado pero no aplicado en vivo).
* **Bloqueo Técnico:** La instancia virtual de Palo Alto (VM-Series sobre KVM/Proxmox) presentó una falla crítica en el arranque del **Management Plane**.
* **Evidencia:** La consola muestra el error `Error: unable to connect to Sysd` y `sysd_construct_sync_importer failed`, impidiendo el login administrativo.
* **Mitigación:** Se ha desarrollado el rol de Ansible `paloalto_vpn` basándose estrictamente en la documentación oficial de la colección `paloaltonetworks.panos`.

<img width="1060" height="199" alt="image" src="https://github.com/user-attachments/assets/12eb0fca-8d7d-4d3e-b52a-a1068e3ac52c" />

---

## 4. Herramientas y APIs Seleccionadas

Para la orquestación se utiliza un enfoque **Agentless** basado en **Ansible**.

* **Control Node:** Contenedor LXC (Ubuntu 24.04) en Proxmox.
* **Fortinet:** Colección `fortinet.fortios` (API REST/HTTPS).
* **Palo Alto:** Colección `paloaltonetworks.panos` (API XML).
* **Gestión de Dependencias:** Uso de `pipx` para aislar el entorno de Python y evitar conflictos `externally-managed-environment`.

---

## 5. Estrategia de Validación y Evidencia

### 5.1 Resultado de Ejecución (FortiGate)
El playbook se ejecutó exitosamente contra el FortiGate, configurando todo el stack de red y seguridad sin errores (`failed=0`).

<img width="957" height="544" alt="image" src="https://github.com/user-attachments/assets/a72b2746-6299-489a-a2ed-1e5d83111bf5" />

### 5.2 Script de Verificación
Se incluye el script `scripts/vpn_health_check.py` para realizar validaciones de "Día 2":
1. **Control Plane Check:** Consulta vía API el estado de las Fases 1 y 2 (`UP`/`Active`).
2. **Data Plane Check:** Realiza pruebas de conectividad ICMP (Ping) a través del túnel.

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

---

# VPN Orchestrator: Documentación del Módulo de Despliegue

Si bien la primera parte cumple con lo mínimo que se requiere, me parece que puede ser poco útil para lo que realmente se busca, que es automatizar y acelerar procesos.

Para esto usé parte de lo aprendido en la parte 1 y generé una aplicación web con Flask. La misma toma los datos que se necesitan para levantar la VPN Site-to-Site y te da un archivo .zip para descargar con el playbook listo para correr.

<img width="1430" height="1049" alt="image" src="https://github.com/user-attachments/assets/53592557-f81e-4610-a832-65c527ccc54a" />

Por ahora deja elegir siguientes opciones:

<img width="315" height="202" alt="image" src="https://github.com/user-attachments/assets/4e0ab9b9-388f-42b5-9e82-099564bbd1cd" />

<img width="322" height="177" alt="image" src="https://github.com/user-attachments/assets/88eaa6db-3b85-4222-a141-869215301e01" />

Coloqué valores que fueran compatibles en ambos equipos y busqué tener opciones, por más de que se puede tunear para seguir los estándares de la empresa.
También me encontré que algunos símbolos como pueden ser `'` o `"` no son compatibles con los lenguajes de programación por lo que evité que se puedan usar en el PSK.

<img width="597" height="56" alt="image" src="https://github.com/user-attachments/assets/bca97aa5-ee2c-4465-82b4-e2b4f3ede578" />

Lamentablemente, por más que lo intenté, no logré levantar el firewall Palo Alto en GNS3 con las imágenes que conseguí. Me da un error que parece ser común: se queda colgado en el login diciendo "Login Incorrect".

En foros dicen que hay que asignarle 8GB de RAM y 4 vCPU pero sigue dando el mismo error:

<img width="1580" height="783" alt="image" src="https://github.com/user-attachments/assets/1d95d20a-6866-448c-b0f3-abbfb06aca70" />

Si llegan a tener acceso a una instancia funcional (y de alguna forma me pueden dejar probar en ella), me encantaría poder terminar el trabajo y hacer el challenge más útil/completo sin importar lo que pase con mi candidatura.

Afortunadamente, sí logré simular todo lo de Fortinet. Por lo que la configuración está probada en FortiOS, con alguna limitación como baja encriptación (es la que me permite la versión de evaluación), pero logrando obtener estos datos:

<img width="1347" height="633" alt="image" src="https://github.com/user-attachments/assets/b61c92d0-1bc7-458d-a735-8983aa3fc312" />
<img width="950" height="1237" alt="image" src="https://github.com/user-attachments/assets/19db05a4-09e4-4ffb-b17a-5c20b187d2f7" />
<img width="734" height="1244" alt="image" src="https://github.com/user-attachments/assets/ac732b46-0d2f-478e-9f7c-cc96f663fc56" />
<img width="378" height="794" alt="image" src="https://github.com/user-attachments/assets/201fb010-1543-42fa-8714-98190376288f" />
<img width="758" height="709" alt="image" src="https://github.com/user-attachments/assets/a8387ce1-6a7b-43a0-acf1-ccc2910d116e" />

Antes de que entre en producción, claramente, necesitaría hacer pruebas más rigurosas/ajustes de seguridad.

## Principios de Diseño y Arquitectura

<summary>Detalles de Arquitectura y Flujo de Control</summary>

El módulo está diseñado para ser ejecutado desde un único nodo de control (Control Node).

### A. Estructura del ZIP de Despliegue

Para simplificar la ejecución, la estructura del repositorio se consolida en **3 archivos principales** en la raíz del directorio de configuración:

| Archivo | Contenido |
| :--- | :--- |
| `site.yml` | Contiene toda la lógica de los Playbooks (Tareas y Variables). |
| `hosts.yml` | Inventario simple con las credenciales de gestión. |
| `ansible.cfg` | Configuración básica para apuntar al inventario (`inventory=./hosts.yml`). |

### B. Flujo del Playbook (`site.yml`)

El Playbook sigue una secuencia estricta para garantizar la inserción correcta de objetos:

1. **Play 0 (Instalación de Dependencias):** Se ejecuta en `localhost` con `become: yes` para asegurar la instalación de las librerías Python (`pan-python`, `xmltodict`, `requests`) necesarias para la colección `paloaltonetworks.panos`. Esto resuelve el error común de `Missing required library`.

2. **Play 1 (FortiGate):** Configuración completa del Site A vía `httpapi`.

3. **Play 2 (Palo Alto):** Configuración completa del Site B.

### C. Mapeo de Conexiones

| Fabricante | Tipo de Conexión | Módulos Principales | Función |
| :--- | :--- | :--- | :--- |
| **FortiGate** | `httpapi` | `fortios_vpn_ipsec_phase1_interface`, `fortios_firewall_address` | Conexión nativa REST API (puerto 443). |
| **Palo Alto** | `local` | `panos_interface`, `panos_ike_crypto_profile`, `panos_commit_firewall` | Módulos Python que se ejecutan localmente y se comunican con el firewall vía API XML/REST usando el `provider` object. |

Esto último sobre Palo Alto, repito, no está probado.

---

# 🐍 Backend Documentation: `app.py`

> **Core del VPN Orchestrator**

Este script de Python (`Flask`) actúa como el motor de lógica del orquestador. Su función no es solo servir el HTML, sino actuar como una capa de abstracción y validación entre la intención del usuario (frontend) y la ejecución técnica (Ansible).

---

## 🧠 Lógica de Ingeniería

El script no es solo un "pasamanos" de variables. Implementa lógica de red para asegurar que el Playbook resultante sea válido y cumpla con los RFCs y limitaciones de los vendors.

### 1. Conversión de CIDR a Máscara Decimal (`cidr_to_ip_mask`)
Muchos módulos de Ansible (y APIs de firewalls antiguos) no aceptan notación CIDR (ej. `/24`) y requieren la máscara explícita (ej. `255.255.255.0`).
* **Función:** Transforma `192.168.1.0/24` -> `192.168.1.0 255.255.255.0`.
* **Propósito:** Garantizar compatibilidad con módulos `fortios_system_interface` y objetos de dirección legacy.

### 2. Abstracción de Criptografía Multi-Vendor
El usuario selecciona un perfil genérico (ej. "AES256-SHA256"). El backend traduce esto al dialecto específico de cada fabricante:
* **Fortinet:** Requiere strings combinadas (`aes256-sha256`).
* **Palo Alto:** Requiere listas separadas para encriptación y hash (`['aes-256-cbc']`, `['sha256']`).

### 3. Normalización de Seguridad (Sanitization)
Antes de procesar la **PSK (Pre-Shared Key)**, el script elimina comillas simples `'` y dobles `"` para evitar inyección de código o rotura de sintaxis en el archivo YAML generado.

---

## ⚙️ Generación Dinámica de Playbooks

En lugar de usar múltiples archivos Jinja2 externos (lo cual complicaría la portabilidad del script en un entorno de challenge), opté por **Template Injection** dentro del mismo código.

### El "Hard-Fix" de la IP del Túnel
Dentro de `generate_vars_content`, se aplica programáticamente la decisión de diseño de las interfaces VTI:

```python
# Lógica aplicada en app.py:
# FortiGate requiere /32 en túneles P2P para evitar conflictos de rutas.
tunnel_mask_32 = "255.255.255.255"

# Palo Alto maneja correctamente /30.
tunnel_mask_ip = "255.255.255.252"
pa_tunnel_cidr = "/30"
```

Esto asegura que, sin importar qué IP ponga el usuario, el orquestador **fuerza** la máscara correcta para evitar errores de capa 3 en el despliegue.

---

## 📡 API Endpoints

### `GET /`
Renderiza el frontend (`templates/frontend.html`).

### `POST /generate`
El endpoint principal. Recibe un JSON con los parámetros del formulario.

**Flujo de ejecución:**
1.  **Validación:** Verifica caracteres ilegales en la PSK.
2.  **Cálculo:** Convierte CIDRs a Máscaras y mapea perfiles crypto.
3.  **Ensamblaje:** Inyecta las variables procesadas en el template maestro (`generate_site_yml_template`).
4.  **Empaquetado:** Genera un archivo `.zip` en memoria (usando `io.BytesIO` para no tocar disco) que contiene:
    * `site.yml` (Playbook)
    * `hosts.yml` (Inventario dinámico)
    * `ansible.cfg` (Configuración local)
5.  **Entrega:** Retorna el ZIP al navegador con un nombre basado en Timestamp.

---

## 📦 Dependencias

El orquestador es ligero y requiere mínimas librerías para funcionar:

* **Flask:** Servidor web y manejo de requests.
* **Standard Libs:** `os`, `io`, `zipfile`, `textwrap`, `datetime`.

```bash
pip install flask
```

---

> **Nota del Desarrollador:**
> Se decidió mantener el template YAML dentro de `app.py` (`generate_site_yml_template`) para mantener el entregable como un artefacto monolítico fácil de auditar, en lugar de dispersar la lógica en múltiples archivos `.j2`.

# 🎨 Frontend Documentation: `templates/frontend.html`

> **Interfaz de Usuario (Single Page Application)**

El frontend actúa como la capa de entrada de datos. No es solo un formulario estático; incluye lógica interactiva para prevenir errores de configuración antes de que los datos lleguen al servidor.

---

## 💅 Sistema de Diseño (Tailwind CSS)

Se utilizó **Tailwind CSS** (vía CDN) para prototipado rápido, implementando un diseño **Dark Mode** nativo para reducir la fatiga visual durante operaciones nocturnas.

### Paleta de Colores Semántica
Para evitar confusiones visuales al configurar dos vendors distintos en la misma pantalla, se extendió la configuración de Tailwind con colores corporativos específicos:

```javascript
// tailwind.config
colors: {
    forti: { DEFAULT: '#C53030' }, // Rojo Fortinet
    palo:  { DEFAULT: '#0284c7' }  // Azul Palo Alto
}
```

* **Columna Izquierda (FortiGate):** Bordes e indicadores visuales en tonos Rojos.
* **Columna Derecha (Palo Alto):** Bordes e indicadores visuales en tonos Azules (Sky).

---

## 🧠 Lógica del Lado del Cliente (JavaScript)

El script incluye funciones de "Calidad de Vida" (QoL) para el operador:

### 1. Validación Dinámica de Puertos (`validate...Ports`)
Evita que el usuario asigne la misma interfaz física a múltiples zonas lógicas (WAN vs LAN).
* **Comportamiento:** Si seleccionas `port1` como WAN, automáticamente se deshabilita `port1` en los selectores de LAN1 y LAN2, mostrando el texto `(En uso)`.
* **Beneficio:** Previene errores de capa 2/3 en el Playbook generado.

### 2. Sincronización Cruzada de IPs (`syncRemoteIPs`)
Para reducir la entrada manual de datos y errores de tipeo, el script infiere automáticamente los valores del "Peer Remoto".
* **Lógica:**
    * Lo que escribes en **FortiGate WAN IP** se copia automáticamente al campo oculto **Palo Alto Peer IP**.
    * Lo que escribes en **Tunnel IP Site A** se copia al campo de enrutamiento del Site B.
* **Resultado:** El usuario solo llena los datos "Locales" de cada equipo; el sistema calcula la topología.

### 3. Gestión de Descarga Asíncrona (`fetch`)
El formulario no realiza un submit tradicional (que recargaría la página).
1. Intercepta el evento `submit`.
2. Envía un JSON vía `POST` al backend Flask.
3. Recibe un **BLOB** (Binary Large Object) como respuesta.
4. Lee el header personalizado `X-Filename` para nombrar el archivo `.zip` correctamente (ej: `2023-10-27-VPN_Project.zip`).
5. Genera un enlace temporal en el DOM para forzar la descarga del navegador.

---

## 🧩 Estructura del DOM

* **Global Settings:** Inputs comunes (PSK, DH Group).
* **Grid Layout:** Diseño responsivo. En móviles se apila verticalmente; en escritorio muestra los firewalls lado a lado para fácil comparación visual.
* **Selectores Inteligentes:** Los dropdowns de interfaces (`port1`...`port10`) se generan programáticamente al cargar la página, facilitando la expansión futura a modelos con 24/48 puertos.

---

> **Nota de Implementación:**
> Se eligió incluir el CSS y JS dentro del mismo archivo HTML (`<style>` y `<script>`) para mantener la portabilidad del proyecto. En un entorno de producción real, estos se separarían en `static/css/style.css` y `static/js/app.js`.

---
