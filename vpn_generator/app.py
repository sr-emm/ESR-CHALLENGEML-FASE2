import io
import zipfile
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# --- PERFILES DE ENCRIPTACIÓN ---
# Solo definen los algoritmos. El grupo DH se inyecta dinámicamente desde el form.
VPN_PROFILES = {
    "lab_legacy": {
        "name": "🧪 Lab / Legacy (DES-SHA256)",
        "phase1_prop": "des-sha256",
        "phase2_prop": "des-sha256",
        "palo_enc": "des-cbc",
        "palo_auth": "sha256"
    },
    "production_std": {
        "name": "🏭 Producción (AES128-SHA256)",
        "phase1_prop": "aes128-sha256",
        "phase2_prop": "aes128-sha256",
        "palo_enc": "aes-128-cbc",
        "palo_auth": "sha256"
    },
    "high_security": {
        "name": "🛡️ Alta Seguridad (AES256-SHA256)",
        "phase1_prop": "aes256-sha256",
        "phase2_prop": "aes256-sha256",
        "palo_enc": "aes-256-cbc",
        "palo_auth": "sha256"
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # 1. Aplicar Perfil de Encriptación seleccionado
        data.update(VPN_PROFILES[data.get('vpn_profile', 'lab_legacy')])

        # 2. Aplicar Selección Manual de Diffie-Hellman
        # Esto permite desacoplar el algoritmo de cifrado del grupo de intercambio de claves
        data['dh_group'] = data.get('dh_group_select', '14')

        # 3. Normalizar booleanos (Checkbox HTML no envía valor si está desmarcado)
        data['fg_is_dhcp'] = 'fg_is_dhcp' in data
        data['pa_is_dhcp'] = 'pa_is_dhcp' in data

        # 4. Lógica de Peer IP (Determinación de vecinos)
        
        # Para Palo Alto (Quién es su Peer Fortinet)
        if not data['fg_is_dhcp']:
            # Si FG es Estático, su IP WAN es la Peer IP (quitamos la máscara CIDR)
            data['pa_peer_ip'] = data['fg_wan_ip'].split('/')[0]
        else:
            # Si FG es DHCP (Lab), asumimos la IP conocida del laboratorio
            data['pa_peer_ip'] = "10.100.100.114"

        # Para Fortinet (Quién es su Remote Gateway Palo Alto)
        if not data['pa_is_dhcp']:
            # Si PA es Estático
            data['fg_remote_gw'] = data['pa_wan_ip'].split('/')[0]
        else:
            # Si PA es DHCP (Lab)
            data['fg_remote_gw'] = "10.100.100.115"

        # 5. Generar ZIP en Memoria
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            
            # Renderizar y mapear cada plantilla a su destino final
            templates_map = {
                'inventory.j2': 'inventory/hosts.yml',
                'all_vars.j2': 'group_vars/all.yml',
                'site.j2': 'site.yml'
            }

            for template_file, dest_path in templates_map.items():
                content = render_template(f'ansible_templates/{template_file}', **data)
                zf.writestr(dest_path, content)

            # Agregar archivo de configuración base de Ansible
            ansible_cfg = """[defaults]
inventory = ./inventory/hosts.yml
host_key_checking = False
retry_files_enabled = False
deprecation_warnings = False
interpreter_python = auto_silent
timeout = 30
"""
            zf.writestr('ansible.cfg', ansible_cfg)

        memory_file.seek(0)
        return send_file(
            memory_file,
            download_name="ansible_vpn_config.zip",
            as_attachment=True
        )

    # Renderizado inicial del formulario (GET)
    return render_template('index.html', profiles=VPN_PROFILES)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)