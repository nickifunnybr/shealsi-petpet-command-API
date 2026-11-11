import io
import ipaddress
import socket
from urllib.parse import urlparse

import requests
from flask import Flask, jsonify, request, send_file
from PIL import Image, UnidentifiedImageError
from petpetgif import petpet

app = Flask(__name__)

MAX_IMAGE_BYTES = 8 * 1024 * 1024
ALLOWED_MIME = {"image/png", "image/jpeg", "image/webp", "image/gif"}


def is_public_host(hostname: str) -> bool:
    """Reject localhost and private/reserved IP addresses."""
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(hostname, None)}
    except socket.gaierror:
        return False

    if not addresses:
        return False

    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            return False
    return True


def download_image(url: str) -> bytes:
    parsed = urlparse(url)

    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Use uma URL HTTPS válida.")

    if not is_public_host(parsed.hostname):
        raise ValueError("Esse endereço não pode ser acessado.")

    # Redirects are disabled to avoid redirecting requests to private addresses.
    with requests.get(
        url,
        stream=True,
        timeout=(5, 15),
        allow_redirects=False,
        headers={"User-Agent": "Shealsi-PetPet/1.0"},
    ) as response:
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "").split(";")[0].lower()
        if content_type not in ALLOWED_MIME:
            raise ValueError("Envie PNG, JPG, WEBP ou GIF.")

        content = bytearray()
        for chunk in response.iter_content(chunk_size=64 * 1024):
            if not chunk:
                continue
            content.extend(chunk)
            if len(content) > MAX_IMAGE_BYTES:
                raise ValueError("A imagem ultrapassa o limite de 8 MB.")

    return bytes(content)


@app.get("/")
def home():
    return jsonify({
        "name": "Shealsi PetPet API",
        "status": "online",
        "usage": "/pet?image=URL_DA_IMAGEM"
    })


@app.get("/pet")
def make_petpet():
    image_url = request.args.get("image", "").strip()
    if not image_url:
        return jsonify({"success": False, "error": "Informe o parâmetro image."}), 400

    try:
        raw_image = download_image(image_url)

        # Validate and normalize the source while retaining its alpha channel.
        with Image.open(io.BytesIO(raw_image)) as source:
            source.seek(0)
            normalized = source.convert("RGBA")
            source_buffer = io.BytesIO()
            normalized.save(source_buffer, format="PNG")
            source_buffer.seek(0)

        output = io.BytesIO()
        petpet.make(source_buffer, output)
        output.seek(0)

        return send_file(
            output,
            mimetype="image/gif",
            as_attachment=False,
            download_name="petpet.gif",
            max_age=0,
        )

    except (requests.RequestException, ValueError, UnidentifiedImageError) as error:
        return jsonify({"success": False, "error": str(error)}), 400
    except Exception:
        app.logger.exception("Erro inesperado ao gerar PetPet")
        return jsonify({"success": False, "error": "Não foi possível gerar o GIF."}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port= int(__import__("os").environ.get("PORT", "10000")))
