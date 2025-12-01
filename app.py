from flask import Flask, render_template, request, redirect, url_for, flash
import re
import yaml
from pathlib import Path

app = Flask(__name__)
app.secret_key = "cambia_esto_en_produccion"

# Validadores simples -----------------------------

IP_REGEX = re.compile(
    r"^((25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(25[0-5]|2[0-4]\d|1?\d?\d)$"
)
NAME_REGEX = re.compile(r"^[A-Za-z0-9_\-]{1,30}$")


def is_valid_ip(ip: str) -> bool:
    return bool(IP_REGEX.match(ip.strip()))


def is_valid_name(name: str, max_len: int = 30) -> bool:
    if not name:
        return False
    if len(name) > max_len:
        return False
    return bool(NAME_REGEX.match(name))


def validate_form(form):
    errors = []

    # VPN
    vpn_name = form.get("vpn_name", "")
    psk = form.get("psk", "")

    if not is_valid_name(vpn_name, 30):
        errors.append("Nombre de VPN inválido (máx 30 chars, letras/números/_/-).")

    if len(psk) < 12 or " " in psk:
        errors.append("PSK inválida (mínimo 12 caracteres, sin espacios).")

    # Fortigate
    fgt_mgmt_ip = form.get("fgt_mgmt_ip", "")
    fgt_mgmt_user = form.get("fgt_mgmt_user", "")
    fgt_mgmt_pass = form.get("fgt_mgmt_pass", "")
    fgt_wan_if = form.get("fgt_wan_if", "")
    fgt_wan_zone = form.get("fgt_wan_zone", "")
    fgt_lan_if = form.get("fgt_lan_if", "")
    fgt_lan_zone = form.get("fgt_lan_zone", "")

    if not is_valid_ip(fgt_mgmt_ip):
        errors.append("IP de gestión Fortigate inválida.")
    if not fgt_mgmt_user:
        errors.append("Usuario Fortigate obligatorio.")
    if not fgt_mgmt_pass:
        errors.append("Password Fortigate obligatorio.")

    for field_name, value in [
        ("Interfaz WAN Fortigate", fgt_wan_if),
        ("Zona WAN Fortigate", fgt_wan_zone),
        ("Interfaz LAN Fortigate", fgt_lan_if),
        ("Zona LAN Fortigate", fgt_lan_zone),
    ]:
        if not is_valid_name(value, 20):
            errors.append(f"{field_name} inválida (máx 20 chars, letras/números/_/-).")

    # Palo Alto
    pa_mgmt_ip = form.get("pa_mgmt_ip", "")
    pa_mgmt_user = form.get("pa_mgmt_user", "")
    pa_mgmt_pass = form.get("pa_mgmt_pass", "")
    pa_wan_if = form.get("pa_wan_if", "")
    pa_wan_zone = form.get("pa_wan_zone", "")
    pa_trust_if = form.get("pa_trust_if", "")
    pa_trust_zone = form.get("pa_trust_zone", "")
    pa_vr_name = form.get("pa_vr_name", "")
    pa_tunnel_if = form.get("pa_tunnel_if", "")
    pa_vpn_zone = form.get("pa_vpn_zone", "")

    if not is_valid_ip(pa_mgmt_ip):
        errors.append("IP de gestión Palo Alto inválida.")
    if not pa_mgmt_user:
        errors.append("Usuario Palo Alto obligatorio.")
    if not pa_mgmt_pass:
        errors.append("Password Palo Alto obligatorio.")

    for field_name, value in [
        ("Interfaz WAN Palo Alto", pa_wan_if),
        ("Zona WAN Palo Alto", pa_wan_zone),
        ("Interfaz TRUST Palo Alto", pa_trust_if),
        ("Zona TRUST Palo Alto", pa_trust_zone),
        ("Virtual Router Palo Alto", pa_vr_name),
        ("Interfaz túnel Palo Alto", pa_tunnel_if),
        ("Zona VPN Palo Alto", pa_vpn_zone),
    ]:
        if not is_valid_name(value, 30):
            errors.append(f"{field_name} inválida (máx 30 chars, letras/números/_/-).")

    return errors


def build_yaml_from_form(form):
    """
    Construye un dict con la estructura de vpn_params.yaml
    usando las IPs/parametros del ejercicio como valores por defecto.
    """

    vpn_name = form["vpn_name"]
    psk = form["psk"]

    # Campos Fortigate
    fgt = {
        "name": "sitio1-fortigate",
        "role": "primary",
        "vendor": "fortigate",
        "management": {
            "hostname": "FGT-S1",
            "ip": form["fgt_mgmt_ip"],
            "username": form["fgt_mgmt_user"],
            "password": form["fgt_mgmt_pass"],
            "protocol": "https",
            "port": 443,
        },
        "wan": {
            "interface": form["fgt_wan_if"],
            "ip": "100.100.100.1",
            "mask": "255.255.255.252",
            "network": "100.100.100.0/30",
            "gateway": "100.100.100.2",
            "zone": form["fgt_wan_zone"],
        },
        "lans": [
            {
                "name": "lan1",
                "interface": form["fgt_lan_if"],
                "ip": "10.100.101.251",
                "mask": "255.255.255.0",
                "network": "10.100.101.0/24",
                "zone": form["fgt_lan_zone"],
            },
            # segunda LAN fija / opcional
            {
                "name": "lan2",
                "interface": "port3",
                "ip": "10.100.102.251",
                "mask": "255.255.255.0",
                "network": "10.100.102.0/24",
                "zone": form["fgt_lan_zone"],
            },
        ],
        "tunnel": {
            "name": "FGT-to-PA",
            "interface_type": "ipsec",
            "ip": "169.255.1.1",
            "mask": "255.255.255.252",
            "zone": "VPN_S1",
            "peer_wan_ip": "200.200.200.1",
        },
    }

    pa = {
        "name": "sitio2-paloalto",
        "role": "secondary",
        "vendor": "paloalto",
        "management": {
            "hostname": "PA-S2",
            "ip": form["pa_mgmt_ip"],
            "username": form["pa_mgmt_user"],
            "password": form["pa_mgmt_pass"],
            "protocol": "https",
            "port": 443,
        },
        "wan": {
            "interface": form["pa_wan_if"],
            "ip": "200.200.200.1",
            "mask": "255.255.255.252",
            "network": "200.200.200.0/30",
            "gateway": "200.200.200.2",
            "zone": form["pa_wan_zone"],
        },
        "lans": [
            {
                "name": "lan1",
                "interface": form["pa_trust_if"],
                "ip": "10.200.201.252",
                "mask": "255.255.255.0",
                "network": "10.200.201.0/24",
                "zone": form["pa_trust_zone"],
            },
            {
                "name": "lan2",
                "interface": "ethernet1/3",
                "ip": "10.200.202.252",
                "mask": "255.255.255.0",
                "network": "10.200.202.0/24",
                "zone": form["pa_trust_zone"],
            },
        ],
        "tunnel": {
            "name": "TUN-S2-to-S1",
            "interface_type": "tunnel",
            "interface": form["pa_tunnel_if"],
            "ip": "169.255.1.2",
            "mask": "255.255.255.252",
            "zone": form["pa_vpn_zone"],
            "peer_wan_ip": "100.100.100.1",
            "virtual_router": form["pa_vr_name"],
        },
    }

    data = {
        "vpn": {
            "name": vpn_name,
            "description": "VPN IPSec auto-generada entre Fortigate y Palo Alto",
            "tunnel_network": "169.255.1.0/30",
        },
        "sites": {
            "site1": fgt,
            "site2": pa,
        },
        "ike": {
            "version": "ikev2",
            "psk": psk,
            "id_type": "ip",
            "site1_id_local": "100.100.100.1",
            "site1_id_remote": "200.200.200.1",
            "site2_id_local": "200.200.200.1",
            "site2_id_remote": "100.100.100.1",
            "proposal": {
                "encryption": "aes256",
                "integrity": "sha256",
                "dh_group": 14,
                "lifetime_seconds": 28800,
            },
            "dpd": {
                "enabled": True,
                "interval_seconds": 10,
                "retries": 3,
                "action": "restart",
            },
            "nat_traversal": {"enabled": False},
        },
        "ipsec": {
            "mode": "tunnel",
            "protocol": "esp",
            "proposal": {
                "encryption": "aes256",
                "integrity": "sha256",
                "pfs_enabled": True,
                "pfs_dh_group": 14,
                "lifetime_seconds": 3600,
            },
            "selectors": [
                {
                    "name": "s1-lan1_to_s2-lan1",
                    "local_subnet": "10.100.101.0/24",
                    "remote_subnet": "10.200.201.0/24",
                },
                {
                    "name": "s1-lan1_to_s2-lan2",
                    "local_subnet": "10.100.101.0/24",
                    "remote_subnet": "10.200.202.0/24",
                },
                {
                    "name": "s1-lan2_to_s2-lan1",
                    "local_subnet": "10.100.102.0/24",
                    "remote_subnet": "10.200.201.0/24",
                },
                {
                    "name": "s1-lan2_to_s2-lan2",
                    "local_subnet": "10.100.102.0/24",
                    "remote_subnet": "10.200.202.0/24",
                },
            ],
        },
    }

    return data


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        errors = validate_form(request.form)
        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("form.html", form=request.form)

        data = build_yaml_from_form(request.form)

        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        yaml_path = output_dir / "vpn_params.yaml"

        with yaml_path.open("w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, allow_unicode=True)

        flash(f"Archivo {yaml_path} generado correctamente.", "success")
        return redirect(url_for("index"))

    return render_template("form.html", form={})


if __name__ == "__main__":
    app.run(debug=True)
