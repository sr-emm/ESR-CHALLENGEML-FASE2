# 🔐 VPN Orchestrator Pro

<div align="center">

```
██╗   ██╗██████╗ ███╗   ██╗     ██████╗ ██████╗  ██████╗██╗  ██╗███████╗███████╗████████╗██████╗  █████╗ ████████╗ ██████╗ ██████╗ 
██║   ██║██╔══██╗████╗  ██║    ██╔═══██╗██╔══██╗██╔════╝██║  ██║██╔════╝██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔═══██╗██╔══██╗
██║   ██║██████╔╝██╔██╗ ██║    ██║   ██║██████╔╝██║     ███████║█████╗  ███████╗   ██║   ██████╔╝███████║   ██║   ██║   ██║██████╔╝
╚██╗ ██╔╝██╔═══╝ ██║╚██╗██║    ██║   ██║██╔══██╗██║     ██╔══██║██╔══╝  ╚════██║   ██║   ██╔══██╗██╔══██║   ██║   ██║   ██║██╔══██╗
 ╚████╔╝ ██║     ██║ ╚████║    ╚██████╔╝██║  ██║╚██████╗██║  ██║███████╗███████║   ██║   ██║  ██║██║  ██║   ██║   ╚██████╔╝██║  ██║
  ╚═══╝  ╚═╝     ╚═╝  ╚═══╝     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
```

**🚀 Automatiza VPNs Site-to-Site entre FortiGate y Palo Alto en minutos, no horas**

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-yellow.svg)
![Ansible](https://img.shields.io/badge/ansible-2.15+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

[🎯 Quick Start](#-quick-start) •
[📦 Instalación](#-instalación) •
[🎮 Uso](#-flujo-de-uso) •
[🔧 Componentes](#-componentes) •
[🛠️ API](#-api-reference)

</div>

---

## 🤔 ¿Qué es esto?

**VPN Orchestrator Pro** es tu traductor universal. Una aplicación web que genera y ejecuta playbooks de Ansible para crear túneles IPSec Site-to-Site entre **FortiGate** y **Palo Alto** de forma automática.

### ✨ La magia en 30 segundos

```
1. 🔌 Conectas tus dispositivos
2. 📤 Extraes la configuración actual  
3. 🔍 El sistema analiza qué falta o cambió
4. ▶️ Ejecutas y... ¡VPN lista!
5. 🧪 Verificas que todo funcione
```
<img width="1892" height="885" alt="image" src="https://github.com/user-attachments/assets/ece9782a-e3a7-4bb9-82e8-e0b872027e06" />

---

## 🎯 Quick Start

```bash
# Clonar el repo
git clone -b v2 https://github.com/sr-emm/ESR-CHALLENGEML-FASE2.git
cd ESR-CHALLENGEML-FASE2

# Crear entorno virtual y activar
python3 -m venv venv && source venv/bin/activate

# Instalar Flask (mínimo para arrancar)
pip install flask requests

# Correr la app
cd vpn_orchestrator
python app.py

# Abrir http://localhost:5000
# Hacer clic en "Instalar Dependencias" 🔮
# ¡Listo! El botón hace el resto automáticamente
```
<img width="436" height="121" alt="image" src="https://github.com/user-attachments/assets/711b371b-b191-4720-b1dc-cd06128980fc" />

---

## 📦 Instalación

<details>
<summary><b>📋 Requisitos del Sistema</b></summary>

### Hardware Mínimo
| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 1 core | 2+ cores |
| RAM | 512 MB | 1 GB |
| Disco | 500 MB | 1 GB |

### Software
| Software | Versión | Notas |
|----------|---------|-------|
| Python | 3.10+ | 3.12 recomendado |
| pip | 21+ | Se actualiza automáticamente |
| Ansible | 2.15+ | Se instala con el orquestador |

### Conectividad de Red
```
Tu Servidor ──► FortiGate (HTTPS/443)
     │
     └──────► Palo Alto (HTTPS/443)
```

⚠️ **Importante**: Necesitas credenciales con permisos de administrador en ambos firewalls.

</details>

<details>
<summary><b>🐍 Paso 1: Crear Virtual Environment</b></summary>

### ¿Por qué un venv?
Porque no queremos romper tu sistema. El venv es como una burbuja protectora donde instalamos todo sin afectar nada más.

```bash
# Navegar al directorio del proyecto
cd vpn-orchestrator-pro

# Crear el entorno virtual
python3 -m venv venv

# Activar el entorno (Linux/Mac)
source venv/bin/activate

# Activar el entorno (Windows)
.\venv\Scripts\activate

# Sabrás que está activo cuando veas (venv) al inicio del prompt
(venv) usuario@maquina:~/vpn-orchestrator-pro$
```

### 🔄 Desactivar cuando termines
```bash
deactivate
```

</details>

<details>
<summary><b>📚 Paso 2: Instalar Flask (mínimo)</b></summary>

```bash
# Solo necesitas Flask para arrancar
(venv) $ pip install flask requests

# ¡Eso es todo! El resto se instala con el botón 🔮
```

### ¿Y las demás dependencias?
El botón **"Instalar Dependencias"** en la interfaz web se encarga de:
- ✅ Ansible
- ✅ Colecciones FortiGate y Palo Alto
- ✅ Librerías Python (pan-python, pan-os-python, xmltodict)
- ✅ Verificar que todo esté correcto

</details>

<details>
<summary><b>🎭 Paso 3: Ejecutar y el Botón Mágico</b></summary>

```bash
# Arrancar la aplicación
(venv) $ python app.py
```

### En el navegador (http://localhost:5000):

1. Busca el badge **"Instalar Dependencias"** en la esquina superior
2. Haz clic y espera ~30 segundos
3. Verás en la consola:
```
[INFO] Iniciando instalación de dependencias...
[STEP 1/5] Verificando pip...
[STEP 2/5] Instalando Ansible...
[STEP 3/5] Instalando librerías Python...
[STEP 4/5] Instalando colección FortiGate...
[STEP 5/5] Instalando colección Palo Alto...
[SUCCESS] ✓ Todas las dependencias instaladas correctamente
```

### ¿Por qué así?
- 🎯 Menos pasos manuales = menos errores
- 🔄 Siempre instala las versiones correctas
- 🧪 Verifica que todo funcione antes de continuar

</details>

<details>
<summary><b>🚀 Paso 4: Verificar Instalación (Opcional)</b></summary>

Si quieres verificar manualmente que todo está instalado:

```bash
# Verificar Ansible
(venv) $ ansible --version

# Verificar colecciones
(venv) $ ansible-galaxy collection list | grep -E "fortinet|paloalto"

# Verificar librerías Python
(venv) $ python -c "import pan; import panos; print('✓ Todo OK')"
```

### 🔒 Para producción
```bash
# Usar Gunicorn en lugar del servidor de desarrollo
(venv) $ pip install gunicorn
(venv) $ gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

</details>

<details>
<summary><b>🐳 Alternativa: Docker</b></summary>

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
COPY app.py .
COPY templates/ templates/

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install ansible-core && \
    ansible-galaxy collection install fortinet.fortios paloaltonetworks.panos

EXPOSE 5000
CMD ["python", "app.py"]
```

```bash
docker build -t vpn-orchestrator .
docker run -p 5000:5000 vpn-orchestrator
```

</details>

---

## 🎮 Flujo de Uso

> **El camino del guerrero VPN** 🥷

```
┌────────────────────────────────────────────────────────────────────────────┐
│                                                                            │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌─────┐  │
│   │   TEST   │───►│ EXTRAER  │───►│ EJECUTAR │───►│   VPN    │───►│ ZIP │  │
│   │ CONEXIÓN │    │  CONFIG  │    │          │    │  TESTER  │    │     │  │
│   └──────────┘    └──────────┘    └──────────┘    └──────────┘    └─────┘  │
│        │               │               │               │              │    │
│        ▼               ▼               ▼               ▼              ▼    │
│   Verificar       Auto-fill      Pre-validar     Verificar       Guardar   │
│   HTTPS 443       + Análisis     + Ansible       túnel UP        configs   │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

<details>
<summary><b>🔌 Paso 1: Test Conexión</b></summary>

<img width="197" height="82" alt="image" src="https://github.com/user-attachments/assets/d94b6f8a-bfc4-45a7-802f-7250c8a71971" />

### ¿Qué hace?
Verifica que puedes alcanzar ambos firewalls por HTTPS (puerto 443).

### ¿Cuándo usarlo?
**Siempre primero.** Es como verificar que tienes gasolina antes de un viaje.

### ¿Qué esperar?
```
🚀 Iniciando test de conectividad...
✓ FortiGate (10.100.100.173): Conectado
✓ Palo Alto (10.100.100.107): Conectado
✓ Todos los dispositivos están accesibles
```

### ❌ Si falla
- Verifica IPs de gestión
- Confirma que HTTPS está habilitado
- Revisa reglas de firewall hacia tu servidor

</details>

<details>
<summary><b>📤 Paso 2: Extraer Config</b></summary>

<img width="190" height="70" alt="image" src="https://github.com/user-attachments/assets/47b52c4e-25e6-4df9-9d04-2ea6204ba49a" />

### ¿Qué hace?
1. **Extrae IPs** de las interfaces seleccionadas
2. **Detecta zonas** (solo Palo Alto)
3. **Analiza config VPN existente**
4. **Compara** lo que hay vs lo que quieres

### Auto-fill mágico ✨
El sistema auto-completa:
- IP WAN de cada dispositivo
- CIDR de las LANs (convierte IP a red)
- Zonas de seguridad en Palo Alto

### Análisis de Configuración
```
📊 Análisis de Configuración VPN:

FortiGate:                     Palo Alto:
✓ Phase 1 (Config idéntica)    ✓ IKE Crypto Profile (Ya existe)
✓ Phase 2 (Ya existe)          ✓ IPsec Crypto Profile (Ya existe)
✓ Tunnel Interface (Ya existe) ✓ IKE Gateway (Ya existe)
✓ Rutas (2) (Ya existen)       ✓ IPsec Tunnel (Ya existe)
                               ✓ Tunnel Interface (Ya existe)
                               ✓ Rutas (2) (Ya existen)

✓ 4 iguales                    ✓ 6 iguales
```

### Leyenda de símbolos
| Símbolo | Significado |
|---------|-------------|
| ✓ Verde | Ya existe y es idéntico (se omite) |
| 🔄 Amarillo | Existe pero hay diferencias (se modifica) |
| ➕ Azul | No existe (se crea) |

</details>

<details>
<summary><b>▶️ Paso 3: Ejecutar</b></summary>

<img width="188" height="50" alt="image" src="https://github.com/user-attachments/assets/146ad5bf-7080-4081-b164-c0232d1d33b2" />

### ¿Qué hace?
1. **Pre-validación**: Analiza una vez más antes de actuar
2. **Genera playbooks**: Crea los archivos de Ansible
3. **Ejecuta**: Aplica la configuración en tiempo real
4. **Streaming**: Ves cada tarea mientras se ejecuta

### Pre-validación inteligente
Si todo está 100% idéntico:
```
══════════════════════════════════════════
✅ RESULTADO: Configuración 100% idéntica
ℹ️  No hay cambios que aplicar. Playbook omitido.
💡 Si deseas forzar la reconfiguración, marca "Recrear túnel"
══════════════════════════════════════════
```

### Si hay cambios
```
📋 PLAN DE EJECUCIÓN:
   • 8 componentes sin cambios (se omitirán)
   • 1 componentes a modificar
   • 2 componentes a crear

▶ Iniciando ejecución de Ansible Playbook...

PLAY [Configurar Overlay FortiGate] ****
TASK [Configurar VPN Phase 1] **********
ok: [forti_site_a]
...
```

### ⚠️ Checkbox "Recrear túnel"
Marca esta opción si:
- Quieres forzar recreación completa
- Recibes errores "Error in repo"
- Cambiaste el PSK y necesitas aplicarlo

**Cuidado**: Elimina y recrea toda la VPN (puede causar caída temporal).

</details>

<details>
<summary><b>🧪 Paso 4: VPN Tester</b></summary>

<img width="188" height="61" alt="image" src="https://github.com/user-attachments/assets/4297b516-453e-44eb-aa5f-e1d376369e0d" />

### ¿Qué hace?
Consulta el estado del túnel **en ambos dispositivos** simultáneamente.

### APIs consultadas
| Dispositivo | API | Datos |
|-------------|-----|-------|
| FortiGate | `/api/v2/monitor/vpn/ipsec` | Phase 1/2 status, bytes TX/RX |
| Palo Alto | `<show><vpn><ike-sa>` | IKE SA state |
| Palo Alto | `<show><vpn><ipsec-sa>` | IPsec SA state |

### Estados posibles

| Estado | Icono | Significado |
|--------|-------|-------------|
| UP | 🟢 | Túnel completamente establecido |
| PARTIAL | 🟡 | Solo Phase 1 o Phase 2 activo |
| DOWN | 🔴 | Túnel no establecido |
| NOT_FOUND | 🔴 | El túnel no existe |

### Output ejemplo
```
═══════════════════════════════════════════════════
🔍 Verificando estado del túnel VPN...

━━━ FortiGate ━━━
🟢 Estado: ACTIVO
   Phase 1 (IKE): up
   Phase 2 (IPsec): up
   Peer IP: 200.200.200.1
   Tráfico: ↓ 1.25 MB | ↑ 0.89 MB

━━━ Palo Alto ━━━
🟢 Estado: ACTIVO
   IKE SA: established
   IPsec SA: active
   Tráfico: ↑ 934521 bytes | ↓ 1312456 bytes

✅ VPN ESTABLECIDA CORRECTAMENTE
═══════════════════════════════════════════════════
```

</details>

<details>
<summary><b>📦 Paso 5: Descargar ZIP</b></summary>

 <img width="189" height="54" alt="image" src="https://github.com/user-attachments/assets/ec7981be-d7f7-405d-b6f8-0df4a2f11f3f" />

### ¿Qué incluye?
```
2024-12-08-221500-S2S-OVERLAY.zip
├── ansible.cfg      # Configuración de Ansible
├── hosts.yml        # Inventario con credenciales
├── site.yml         # Playbook principal
└── README.md        # Instrucciones de ejecución manual
```

### ¿Para qué sirve?
- **Backup** de la configuración generada
- **Ejecución manual** desde otro servidor
- **Auditoría** y documentación
- **Modificaciones** personalizadas

### Ejecutar manualmente
```bash
cd vpn_config_extracted/
ansible-playbook -i hosts.yml site.yml
```

</details>

---

## 🔧 Componentes

<details>
<summary><b>🏗️ Arquitectura del Sistema</b></summary>

```
┌────────────────────────────────────────────────────────────────────────────┐
│                              TU NAVEGADOR                                  │
│                          http://localhost:5000                             │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND (HTML/JS)                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐           │
│  │ Formulario  │ │  Consola    │ │  Status     │ │  Config     │           │
│  │ VPN Config  │ │  Real-time  │ │  Badges     │ │  Diff Panel │           │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘           │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                              Fetch API
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                            BACKEND (Flask)                                 │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         ENDPOINTS                                   │   │
│  │  /test-connectivity  →  Verificar HTTPS a ambos FWs                 │   │
│  │  /extract-info       →  Obtener IPs, zonas, interfaces              │   │
│  │  /compare-config     →  Analizar config actual vs deseada           │   │
│  │  /run                →  Ejecutar Ansible (streaming)                │   │
│  │  /verify-vpn         →  Consultar estado del túnel                  │   │
│  │  /generate           →  Descargar ZIP con playbooks                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      GENERADORES                                    │   │
│  │  generate_vars_block()   →  Variables del playbook                  │   │
│  │  generate_hosts_yml()    →  Inventario de Ansible                   │   │
│  │  generate_site_yml()     →  Playbook principal                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      EXTRACTORES                                    │   │
│  │  extract_fortigate_info()      →  API REST FortiGate                │   │
│  │  extract_paloalto_info()       →  XML API Palo Alto                 │   │
│  │  extract_fortigate_vpn_config()→  Config VPN actual FG              │   │
│  │  extract_paloalto_vpn_config() →  Config VPN actual PA              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                         Subprocess + Streaming
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                              ANSIBLE                                       │
│  ┌──────────────────────────────┐  ┌──────────────────────────────┐        │
│  │      fortinet.fortios        │  │   paloaltonetworks.panos     │        │
│  │                              │  │                              │        │
│  │  fortios_vpn_ipsec_phase1    │  │  panos_ike_crypto_profile    │        │
│  │  fortios_vpn_ipsec_phase2    │  │  panos_ipsec_profile         │        │
│  │  fortios_system_interface    │  │  panos_ike_gateway           │        │
│  │  fortios_router_static       │  │  panos_ipsec_tunnel          │        │
│  │  fortios_firewall_policy     │  │  panos_static_route          │        │
│  │  fortios_firewall_address    │  │  panos_security_rule         │        │
│  └──────────────────────────────┘  └──────────────────────────────┘        │
└────────────────────────────────────────────────────────────────────────────┘
                                    │
                            HTTPS/443 (API)
                                    │
              ┌─────────────────────┴─────────────────────┐
              ▼                                           ▼
┌──────────────────────────┐             ┌──────────────────────────┐
│       FORTIGATE          │             │       PALO ALTO          │
│                          │             │                          │
│  ┌────────────────────┐  │             │  ┌────────────────────┐  │
│  │ VPN IPSec Phase1   │  │◄═══════════►│  │ IKE Gateway        │  │
│  │ VPN IPSec Phase2   │  │   TUNNEL    │  │ IPSec Tunnel       │  │
│  │ Tunnel Interface   │  │             │  │ Tunnel Interface   │  │
│  │ Static Routes      │  │             │  │ Static Routes      │  │
│  │ Firewall Policies  │  │             │  │ Security Policies  │  │
│  └────────────────────┘  │             │  └────────────────────┘  │
│                          │             │                          │
│  REST API (HTTPS)        │             │  XML API (HTTPS)         │
└──────────────────────────┘             └──────────────────────────┘
```

</details>

<details>
<summary><b>📁 Estructura de Archivos</b></summary>

```
vpn-orchestrator-pro/
│
├── 📄 app.py                    # Backend Flask (el cerebro 🧠)
│   ├── Generadores de playbooks
│   ├── Extractores de configuración
│   ├── Comparadores de diff
│   └── Endpoints REST
│
├── 📁 templates/
│   └── 📄 frontend.html         # UI completa (Tailwind CSS)
│       ├── Formulario de configuración
│       ├── Consola de ejecución
│       ├── Panel de análisis
│       └── Botones de acción
│
├── 📄 requirements.txt          # Dependencias Python
├── 📄 README.md                 # Esta documentación
│
└── 📁 [generado al ejecutar]
    └── 📁 ansible_workspace_YYYYMMDD_HHMMSS/
        ├── ansible.cfg
        ├── hosts.yml
        └── site.yml
```

</details>

<details>
<summary><b>🔐 Componentes de VPN Configurados</b></summary>

### FortiGate (Site A)

| Componente | Módulo Ansible | Descripción |
|------------|----------------|-------------|
| Phase 1 | `fortios_vpn_ipsec_phase1_interface` | IKE Gateway (IKEv2) |
| Phase 2 | `fortios_vpn_ipsec_phase2_interface` | IPSec SA |
| Tunnel Interface | `fortios_system_interface` | VTI con IP |
| Address Objects | `fortios_firewall_address` | LANs locales/remotas |
| Static Routes | `fortios_router_static` | Rutas hacia PA |
| Policies | `fortios_firewall_policy` | Permitir tráfico VPN |

### Palo Alto (Site B)

| Componente | Módulo Ansible | Descripción |
|------------|----------------|-------------|
| VPN Zone | `panos_zone` | Zona para el túnel |
| Tunnel Interface | `panos_tunnel` | tunnel.1 con IP |
| IKE Profile | `panos_ike_crypto_profile` | Crypto Phase 1 |
| IPSec Profile | `panos_ipsec_profile` | Crypto Phase 2 |
| IKE Gateway | `panos_ike_gateway` | Peer configuration |
| IPSec Tunnel | `panos_ipsec_tunnel` | Tunnel binding |
| Proxy ID | `panos_config_element` | Traffic selectors |
| Static Routes | `panos_static_route` | Rutas hacia FG |
| Security Rules | `panos_security_rule` | Policies bidireccionales |
| Commit | `panos_commit_firewall` | Aplicar cambios |

</details>

<details>
<summary><b>🔒 Perfiles Criptográficos Disponibles</b></summary>

| Perfil | Encryption | Hash | DH Group | Caso de Uso |
|--------|------------|------|----------|-------------|
| **Producción** | AES-128-CBC | SHA256 | 14 (2048-bit) | Balance seguridad/rendimiento |
| **Alta Seguridad** | AES-256-CBC | SHA256 | 14 (2048-bit) | Datos sensibles |
| **Compatibilidad** | 3DES | SHA256 | 14 (2048-bit) | Equipos legacy |
| **Legacy/LAB** ⚠️ | DES | SHA256 | 14 (2048-bit) | Solo laboratorio |

### Lifetimes Configurados

| Phase | Lifetime | Notas |
|-------|----------|-------|
| Phase 1 (IKE) | 28800s (8h) | Rekey automático |
| Phase 2 (IPSec) | 3600s (1h) | PFS habilitado |

</details>

---

## 🛠️ API Reference

<details>
<summary><b>GET / - Interfaz Web</b></summary>

Retorna la página HTML principal.

```bash
curl http://localhost:5000/
```

</details>

<details>
<summary><b>POST /test-connectivity - Test de Conexión</b></summary>

Verifica conectividad HTTPS a ambos dispositivos.

**Request:**
```json
{
  "fg_mgmt_ip": "10.100.100.173",
  "pa_mgmt_ip": "10.100.100.107"
}
```

**Response:**
```json
{
  "fortigate": {
    "success": true,
    "message": "Conectado",
    "ip": "10.100.100.173"
  },
  "paloalto": {
    "success": true,
    "message": "Conectado",
    "ip": "10.100.100.107"
  }
}
```

</details>

<details>
<summary><b>POST /extract-info - Extraer Información</b></summary>

Extrae IPs y zonas de interfaces seleccionadas.

**Request:**
```json
{
  "fg_mgmt_ip": "10.100.100.173",
  "fg_user": "admin",
  "fg_password": "****",
  "fg_wan_intf": "port1",
  "fg_lan1_intf": "port2",
  "fg_lan2_intf": "port3",
  "pa_mgmt_ip": "10.100.100.107",
  "pa_user": "admin",
  "pa_password": "****",
  "pa_wan_intf": "ethernet1/1",
  "pa_lan1_intf": "ethernet1/2",
  "pa_lan2_intf": "ethernet1/3"
}
```

**Response:**
```json
{
  "fortigate": {
    "success": true,
    "interfaces": {
      "port1": {"ip": "100.100.100.1/30", "status": "up"},
      "port2": {"ip": "10.100.102.1/24", "status": "up"}
    }
  },
  "paloalto": {
    "success": true,
    "interfaces": {
      "ethernet1/1": {"ip": "200.200.200.1/30", "zone": "untrust"},
      "ethernet1/2": {"ip": "10.200.202.1/24", "zone": "trust"}
    }
  }
}
```

</details>

<details>
<summary><b>POST /compare-config - Comparar Configuración</b></summary>

Analiza config actual vs deseada.

**Response:**
```json
{
  "fortigate": {
    "success": true,
    "exists": true,
    "diff": {
      "skip": [
        {"component": "Phase 1", "reason": "Config idéntica"},
        {"component": "Phase 2", "reason": "Ya existe"}
      ],
      "modify": [],
      "create": []
    }
  },
  "paloalto": {
    "success": true,
    "exists": true,
    "diff": {
      "skip": ["..."],
      "modify": [
        {"component": "IKE Gateway", "changes": "Peer: 1.1.1.1 → 2.2.2.2"}
      ],
      "create": [
        {"component": "Rutas (faltan 1)"}
      ]
    }
  }
}
```

</details>

<details>
<summary><b>POST /run - Ejecutar Playbook</b></summary>

Ejecuta Ansible con streaming de salida.

**Response:** `text/event-stream`

```
PLAY [Configurar Overlay FortiGate] ****
TASK [Configurar VPN Phase 1] **********
ok: [forti_site_a]
...
PLAY RECAP ****************************
forti_site_a: ok=11 changed=2
palo_site_b: ok=12 changed=5
```

</details>

<details>
<summary><b>POST /verify-vpn - Verificar Estado VPN</b></summary>

Consulta estado del túnel en ambos dispositivos.

**Response:**
```json
{
  "fortigate": {
    "success": true,
    "status": "up",
    "details": {
      "phase1": "up",
      "phase2": "up",
      "incoming_bytes": 1312456,
      "outgoing_bytes": 934521,
      "peer_ip": "200.200.200.1"
    }
  },
  "paloalto": {
    "success": true,
    "status": "up",
    "details": {
      "ike_status": "established",
      "ipsec_status": "active"
    }
  }
}
```

</details>

<details>
<summary><b>POST /generate - Descargar ZIP</b></summary>

Genera y descarga ZIP con playbooks.

**Response:** `application/zip`

Archivo: `2024-12-08-221500-S2S-OVERLAY.zip`

</details>

---

## 🐛 Troubleshooting

<details>
<summary><b>❌ "Missing required library pan-python"</b></summary>

### Causa
Las librerías de Palo Alto no están instaladas o no está activo el venv correcto.

### Solución
```bash
# Activar venv correcto
source venv/bin/activate

# Reinstalar
pip install pan-python pan-os-python

# Verificar
python -c "import pan; print('✓ pan-python OK')"
```

</details>

<details>
<summary><b>❌ "Error in repo" en FortiGate</b></summary>

### Causa
Intentas modificar un túnel existente y FortiOS no lo permite sin eliminar primero.

### Solución
Marca el checkbox **⚠️ Recrear túnel** y vuelve a ejecutar.

</details>

<details>
<summary><b>❌ "HTTP 403" en Palo Alto</b></summary>

### Causa
API access deshabilitado o credenciales sin permisos.

### Solución
1. Verificar credenciales
2. En PAN-OS GUI:
   ```
   Device → Setup → Management → Management Interface Settings
   ✅ Habilitar HTTPS
   ✅ Habilitar API
   ```
3. El usuario debe tener rol `superuser` o `Device Administrator`

</details>

<details>
<summary><b>❌ VPN no levanta (Phase 1 timeout)</b></summary>

### Checklist
- [ ] IPs WAN correctas y alcanzables entre sí
- [ ] Puertos UDP 500 y 4500 abiertos
- [ ] PSK idéntica en ambos lados
- [ ] Crypto profiles coinciden exactamente

</details>

<details>
<summary><b>❌ VPN levanta pero no pasa tráfico</b></summary>

### Checklist
- [ ] Rutas estáticas apuntan a la interfaz túnel
- [ ] Políticas de firewall permiten el tráfico
- [ ] Zonas correctamente asignadas

</details>

---

## 📊 Diagrama de Red

```
                              INTERNET
                                 │
         ┌───────────────────────┴──────────────────────┐
         │                                              │
┌────────┴────────┐                           ┌─────────┴────────┐
│   FORTIGATE     │                           │    PALO ALTO     │
│   Site A        │                           │    Site B        │
│                 │   ════════════════════    │                  │
│ WAN: port1      │◄──► IPSec VPN Tunnel ◄───►│ WAN: eth1/1      │
│ 100.100.100.1   │   IKEv2 + AES-128         │ 200.200.200.1    │
│                 │   169.255.1.1 ←→ .2       │                  │
│ LAN1: port2     │                           │ LAN1: eth1/2     │
│ 10.100.102.0/24 │◄───── Encrypted ─────────►│ 10.200.202.0/24  │
│ LAN2: port3     │       Traffic             │ LAN2: eth1/3     │
│ 10.100.100.0/24 │                           │ 10.200.203.0/24  │
└─────────────────┘                           └──────────────────┘
```

---

## 📄 Licencia

MIT License - Usa, modifica, distribuye. Solo no nos culpes si algo explota. 💥

---

<div align="center">

### 🎉 ¡Gracias por usar VPN Orchestrator Pro!

**Hecho con ☕, 🎵 e 🤖**

[⬆️ Volver arriba](#-vpn-orchestrator-pro)

</div>
