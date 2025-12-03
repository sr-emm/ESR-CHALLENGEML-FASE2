import io
import zipfile
import ipaddress
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# --- PERFILES DE ENCRIPTACIÓN (CORREGIDOS) ---
VPN_PROFILES = {
    "lab_legacy": {
        "name": "🧪 Lab / Legacy (DES-SHA256)",
        "phase1_prop": "des-sha256",   # Fortinet
        "phase2_prop": "des-sha256",   # Fortinet
        "palo_enc": "des",             # <--- CORREGIDO (Era des-cbc)
        "palo_auth": "sha256"
    },
    "production_std": {
        "name": "🏭 Producción (AES128-SHA256)",
        "phase1_prop": "aes128-sha256",
        "phase2_prop": "aes128-sha256",
        "palo_enc": "aes-128-cbc",     # Este sí lleva -cbc en Ansible
        "palo_auth": "sha256"
    },
    "high_security": {
        "name": "🛡️ Alta Seguridad (AES256-SHA256)",
        "phase1_prop": "aes256-sha256",
        "phase2_prop": "aes256-sha256",
        "palo_enc": "aes-256-cbc",     # Este también
        "palo_auth": "sha256"
    }
}

# ... (El resto del archivo app.py con la función 'to_forti_format' y las rutas sigue IGUAL) ...
# Solo asegúrate de mantener la función to_forti_format que agregamos antes.

def to_forti_format(cidr_str):
    try:
        iface = ipaddress.IPv4Interface(cidr_str)
        return f"{iface.ip} {iface.netmask}"
    except Exception:
        return cidr_str

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # 1. Aplicar Perfil
        data.update(VPN_PROFILES[data.get('vpn_profile', 'lab_legacy')])
        data['dh_group'] = data.get('dh_group_select', '14')

        # 2. Normalizar booleanos
        data['fg_is_dhcp'] = 'fg_is_dhcp' in data
        data['pa_is_dhcp'] = 'pa_is_dhcp' in data

        # 3. Lógica de Peer IP
        if not data['fg_is_dhcp']:
            data['pa_peer_ip'] = data['fg_wan_ip'].split('/')[0]
        else:
            data['pa_peer_ip'] = "10.100.100.114"

        if not data['pa_is_dhcp']:
            data['fg_remote_gw'] = data['pa_wan_ip'].split('/')[0]
        else:
            data['fg_remote_gw'] = "10.100.100.115"

        # 4. Variables de Túnel
        data['fg_tunnel_ip'] = "169.255.1.1 255.255.255.255"
        data['fg_remote_tunnel_ip'] = "169.255.1.2 255.255.255.255"
        data['pa_tunnel_ip'] = "169.255.1.2/32"
        data['pa_nexthop_ip'] = "169.255.1.1"
        
        # 5. Formato Fortinet
        data['fg_lan1_fmt'] = to_forti_format(data['fg_lan1_ip'])
        data['fg_lan2_fmt'] = to_forti_format(data['fg_lan2_ip'])
        data['pa_lan_subnet_fmt'] = to_forti_format(data['pa_lan_subnet'])

        # 6. Generar ZIP
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            
            templates_map = {
                'inventory.j2': 'inventory/hosts.yml',
                'all_vars.j2': 'group_vars/all.yml',
                'site.j2': 'site.yml'
            }

            for template_file, dest_path in templates_map.items():
                content = render_template(f'ansible_templates/{template_file}', **data)
                zf.writestr(dest_path, content)

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

    return render_template('index.html', profiles=VPN_PROFILES)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)