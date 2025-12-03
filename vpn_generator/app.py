import io
import zipfile
import ipaddress
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# Perfiles (Mantenemos LENC como default para tu lab)
VPN_PROFILES = {
    "lab_legacy": { "name": "Lab (DES-SHA256)", "phase1_prop": "des-sha256", "phase2_prop": "des-sha256", "palo_enc": "des", "palo_auth": "sha256" },
    "production": { "name": "Producción (AES256)", "phase1_prop": "aes256-sha256", "phase2_prop": "aes256-sha256", "palo_enc": "aes-256-cbc", "palo_auth": "sha256" }
}

# Función auxiliar para formatear Subnets para Fortinet (requiere "IP MASK")
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
        data.update(VPN_PROFILES[data.get('vpn_profile', 'lab_legacy')])
        data['dh_group'] = "14"

        # 1. Calcular Peers (Solo para saber a dónde conectar)
        # Aunque no configuremos la WAN, necesitamos saber la IP del vecino.
        data['fg_remote_gw'] = data['pa_wan_ip'] # Forti apunta a PA
        data['pa_peer_ip'] = data['fg_wan_ip']   # PA apunta a Forti

        # 2. Calcular IPs del Túnel (VTI)
        # El usuario ingresa la IP (ej 169.255.1.1), nosotros le agregamos la máscara /32
        data['fg_tunnel_ip_cidr'] = f"{data['fg_tunnel_ip_input']} 255.255.255.255"
        data['fg_remote_tunnel_ip_cidr'] = f"{data['pa_tunnel_ip_input']} 255.255.255.255"
        
        data['pa_tunnel_ip_cidr'] = f"{data['pa_tunnel_ip_input']}/32"
        data['pa_nexthop_ip'] = data['fg_tunnel_ip_input']

        # 3. Formatear Subnets para Rutas Estáticas
        # Fortinet necesita formato "10.x.x.0 255.255.255.0" para el destino de la ruta
        data['fg_route_dst1'] = to_forti_subnet(data['pa_lan1_subnet'])
        data['fg_route_dst2'] = to_forti_subnet(data['pa_lan2_subnet'])

        # 4. Generar ZIP
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
        return send_file(memory_file, download_name="ansible_overlay_config.zip", as_attachment=True)

    return render_template('index.html', profiles=VPN_PROFILES)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)