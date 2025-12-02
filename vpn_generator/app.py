import io
import zipfile
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# --- 1. PERFILES DE COMPATIBILIDAD ---
# Esto evita errores humanos. Si eliges "Lab", forzamos DES en ambos extremos.
VPN_PROFILES = {
    "lab_legacy": {
        "name": "🧪 Lab / Legacy (Compatibilidad LENC)",
        "phase1_prop": "des-sha256",
        "phase2_prop": "des-sha256",
        "dh_group": "14",
        "palo_enc": "des-cbc",  # Traducción para Palo Alto
        "palo_auth": "sha256"
    },
    "production_std": {
        "name": "🏭 Producción Estándar (AES-128)",
        "phase1_prop": "aes128-sha256",
        "phase2_prop": "aes128-sha256",
        "dh_group": "14",
        "palo_enc": "aes-128-cbc",
        "palo_auth": "sha256"
    },
    "high_security": {
        "name": "🛡️ Alta Seguridad (AES-256)",
        "phase1_prop": "aes256-sha256",
        "phase2_prop": "aes256-sha256",
        "dh_group": "21",
        "palo_enc": "aes-256-cbc",
        "palo_auth": "sha256"
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # A. Capturar datos del formulario HTML
        # Convertimos a dict mutable para poder inyectar valores
        data = request.form.to_dict()
        
        # B. Aplicar el Perfil de Seguridad seleccionado
        profile_key = data.get('vpn_profile', 'lab_legacy')
        profile_data = VPN_PROFILES[profile_key]
        
        # Fusionamos los datos del perfil en el diccionario de datos
        data.update(profile_data)

        # C. Lógica para IPs de Túnel (Máscara /32 para FortiOS 7.x)
        # Calculamos las IPs remotas/locales basándonos en la red base ingresada
        # (Nota: En un app real, usaríamos la librería 'ipaddress' para calcular esto dinámicamente)
        # Aquí asumimos que el usuario mete los datos correctos o usamos defaults seguros.
        
        # D. Generar el ZIP en memoria (sin guardar en disco)
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            
            # 1. Generar Inventory
            inventory_content = render_template('ansible_templates/inventory.j2', **data)
            zf.writestr('inventory/hosts.yml', inventory_content)

            # 2. Generar Group Vars (All)
            vars_content = render_template('ansible_templates/all_vars.j2', **data)
            zf.writestr('group_vars/all.yml', vars_content)

            # 3. Generar Playbook Maestro
            site_content = render_template('ansible_templates/site.j2', **data)
            zf.writestr('site.yml', site_content)

            # 4. Generar un ansible.cfg básico para que funcione out-of-the-box
            ansible_cfg = """[defaults]
inventory = ./inventory/hosts.yml
host_key_checking = False
retry_files_enabled = False
deprecation_warnings = False
interpreter_python = auto_silent
timeout = 30
"""
            zf.writestr('ansible.cfg', ansible_cfg)

        # E. Enviar el archivo al navegador
        memory_file.seek(0)
        return send_file(
            memory_file,
            download_name=f"ansible_vpn_{profile_key}.zip",
            as_attachment=True
        )

    # Si es GET, mostramos el formulario
    return render_template('index.html', profiles=VPN_PROFILES)

if __name__ == '__main__':
    # Escucha en todas las interfaces para que puedas entrar desde tu PC
    app.run(debug=True, host='0.0.0.0', port=5000)
