import io
import zipfile
import ipaddress
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# --- PERFILES DE ENCRIPTACIÓN (Recuperados los 3 niveles) ---
VPN_PROFILES = {
    "lab_legacy": {
        "name": "🧪 Lab / Legacy (DES-SHA256)",
        "desc": "Compatible con hardware antiguo o licencias Trial (LENC).",
        "phase1_prop": "des-sha256",
        "phase2_prop": "des-sha256",
        "palo_enc": "des",
        "palo_auth": "sha256"
    },
    "production_std": {
        "name": "🏭 Producción (AES128-SHA256)",
        "desc": "Estándar de industria, buen balance seguridad/rendimiento.",
        "phase1_prop": "aes128-sha256",
        "phase2_prop": "aes128-sha256",
        "palo_enc": "aes-128-cbc",
        "palo_auth": "sha256"
    },
    "high_security": {
        "name": "🛡️ Alta Seguridad (AES256-SHA256)",
        "desc": "Máxima protección para datos sensibles (Requiere hardware moderno).",
        "phase1_prop": "aes256-sha256",
        "phase2_prop": "aes256-sha256",
        "palo_enc": "aes-256-cbc",
        "palo_auth": "sha256"
    }
}

def to_forti_subnet(cidr):
    try:
        net = ipaddress.ip_network(cidr, strict=False)
        return f"{net.network_address} {net.netmask}"
    except:
        return cidr

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # 1. Aplicar Perfil
        profile_key = data.get('vpn_profile', 'lab_legacy')
        data.update(VPN_PROFILES[profile_key])
        
        # 2. Aplicar DH Group (Recuperado del formulario)
        data['dh_group'] = data.get('dh_group_select', '14')

        # 3. Configurar Peers (Cruce de IPs)
        data['fg_remote_gw'] = data['pa_wan_ip']
        data['pa_peer_ip'] = data['fg_wan_ip']

        # 4. Calcular IPs del Túnel /32
        data['fg_tunnel_ip'] = f"{data['fg_tunnel_ip_input']} 255.255.255.255"
        data['fg_remote_tunnel_ip'] = f"{data['pa_tunnel_ip_input']} 255.255.255.255"
        data['pa_tunnel_ip'] = f"{data['pa_tunnel_ip_input']}/32"
        data['pa_nexthop_ip'] = data['fg_tunnel_ip_input']

        # 5. Formatear Subnets para Rutas Estáticas Fortinet
        data['fg_route_dst1'] = to_forti_subnet(data['pa_lan1_subnet'])
        data['fg_route_dst2'] = to_forti_subnet(data['pa_lan2_subnet'])

        # 6. Generar ZIP
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            
            templates = {
                'inventory.j2': 'inventory/hosts.yml',
                'all_vars.j2': 'group_vars/all.yml',
                'site.j2': 'site.yml'
            }
            
            for tmpl, dest in templates.items():
                content = render_template(f'ansible_templates/{tmpl}', **data)
                zf.writestr(dest, content)
            
            # Config base
            zf.writestr('ansible.cfg', "[defaults]\ninventory=./inventory/hosts.yml\nhost_key_checking=False\ntimeout=30\n")

        memory_file.seek(0)
        return send_file(memory_file, download_name=f"ansible_vpn_{profile_key}.zip", as_attachment=True)

    return render_template('index.html', profiles=VPN_PROFILES)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)