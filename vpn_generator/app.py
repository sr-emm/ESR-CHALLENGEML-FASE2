import io
import zipfile
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

VPN_PROFILES = {
    "lab_legacy": {
        "name": "🧪 Lab / Legacy (DES-SHA256)",
        "phase1_prop": "des-sha256",
        "phase2_prop": "des-sha256",
        "dh_group": "14",
        "palo_enc": "des-cbc",
        "palo_auth": "sha256"
    },
    "production_std": {
        "name": "🏭 Producción (AES128-SHA256)",
        "phase1_prop": "aes128-sha256",
        "phase2_prop": "aes128-sha256",
        "dh_group": "14",
        "palo_enc": "aes-128-cbc",
        "palo_auth": "sha256"
    }
}

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form.to_dict()
        
        # Inyectar perfil de seguridad
        data.update(VPN_PROFILES[data.get('vpn_profile', 'lab_legacy')])

        # Normalizar booleanos para Jinja2
        # Si el checkbox no viene en el form, es False (Static IP)
        data['fg_is_dhcp'] = 'fg_is_dhcp' in data
        data['pa_is_dhcp'] = 'pa_is_dhcp' in data

        # Lógica de Peer IP (Quién es el vecino)
        # Si es Estático, usamos la IP que el usuario escribió.
        # Si es DHCP, usamos un default o intentamos adivinar (para lab se usa hardcode si es dhcp)
        
        if not data['fg_is_dhcp']:
            # Si FG es estático, la Peer IP para Palo Alto es la IP del FG (quitando la máscara)
            data['pa_peer_ip'] = data['fg_wan_ip'].split('/')[0]
        else:
            # Si FG es DHCP (Lab), asumimos la IP del lab .114
            data['pa_peer_ip'] = "10.100.100.114"

        if not data['pa_is_dhcp']:
            # Si PA es estático, la Remote GW para FG es la IP del PA
            data['fg_remote_gw'] = data['pa_wan_ip'].split('/')[0]
        else:
            # Si PA es DHCP (Lab), asumimos la IP del lab .115
            data['fg_remote_gw'] = "10.100.100.115"

        # Generar ZIP
        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zf:
            # Renderizar plantillas
            for template in ['inventory.j2', 'all_vars.j2', 'site.j2']:
                content = render_template(f'ansible_templates/{template}', **data)
                # Mapear nombre de archivo destino
                dest_name = template.replace('.j2', '.yml')
                if template == 'inventory.j2': dest_name = 'inventory/hosts.yml'
                if template == 'all_vars.j2': dest_name = 'group_vars/all.yml'
                
                zf.writestr(dest_name, content)

            # Agregar config base
            zf.writestr('ansible.cfg', "[defaults]\ninventory=./inventory/hosts.yml\nhost_key_checking=False\n")

        memory_file.seek(0)
        return send_file(memory_file, download_name="ansible_vpn_config.zip", as_attachment=True)

    return render_template('index.html', profiles=VPN_PROFILES)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)