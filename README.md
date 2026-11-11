# Shealsi PetPet API

API simples que recebe uma URL pública de imagem e devolve um GIF PetPet.

## Endpoint

`GET /pet?image=https%3A%2F%2F...`

A resposta bem-sucedida tem `Content-Type: image/gif`.

## Formatos aceitos

PNG, JPG/JPEG, WEBP e GIF. A imagem é convertida para RGBA antes da animação para preservar a transparência quando o gerador e o formato GIF permitirem.

Limite de download: 8 MB.

## Executar localmente

```bash
pip install -r requirements.txt
python app.py
```

## Publicar

O arquivo `render.yaml` configura a publicação no Render. Depois de publicar, teste:

`https://SEU-ENDERECO.onrender.com/`

E depois:

`https://SEU-ENDERECO.onrender.com/pet?image=URL_ENCODED_DA_IMAGEM`

## Integração BDFD

Use a URL do endpoint diretamente como URL da imagem no embed, codificando a URL original no parâmetro `image`. Exemplo conceitual:

`$image[https://SEU-ENDERECO.onrender.com/pet?image=URL_CODIFICADA]`

O BDFD/Discord precisa conseguir acessar publicamente a imagem e o endpoint.
