# Publicador automático Facebook / Instagram

Publica automáticamente, cada ~20hs, una foto de la carpeta `images/` en tu
página de Facebook y tu cuenta de Instagram, sin agregar descripción (las
fotos ya vienen con el texto incluido) y sin repetir imágenes ya usadas.

## Cómo funciona

1. GitHub Actions corre el script cada 2 horas.
2. El script chequea `state.json`: si pasaron menos de 20hs desde el último
   posteo, no hace nada.
3. Si ya pasaron 20hs, elige una imagen de `images/` que no esté en
   `used_images` y la publica en Facebook e Instagram, sin caption.
4. Guarda la imagen usada y la fecha en `state.json` y hace commit al repo.

## Requisitos previos

### 1. El repo tiene que ser público

Instagram necesita descargar la imagen desde una URL pública
(`raw.githubusercontent.com/...`). Si el repo es privado, esa URL no
funciona y hay que usar otro hosting de imágenes (puedo ayudarte a adaptarlo
si preferís mantenerlo privado).

### 2. Crear una app en Meta for Developers

1. Andá a https://developers.facebook.com/apps y creá una app tipo "Business".
2. Agregá el producto **Instagram Graph API** (o "Instagram" según la versión
   del panel).
3. Tu cuenta de Instagram tiene que ser **cuenta profesional (Business o
   Creator)** y estar **vinculada a una página de Facebook**.
4. Conseguí:
   - `FB_PAGE_ID`: el ID de tu página de Facebook.
   - `FB_PAGE_ACCESS_TOKEN`: token de acceso de la página, con permisos
     `pages_manage_posts`, `pages_read_engagement` y
     `instagram_content_publish`. Idealmente generá un **token de larga
     duración** (no expira mientras la página siga activa) desde el
     Graph API Explorer o intercambiando un token de usuario de corta
     duración por uno de larga duración y luego por el de página.
   - `IG_USER_ID`: el ID de cuenta de Instagram Business, se obtiene con
     `GET /{page-id}?fields=instagram_business_account&access_token=...`.

⚠️ Los tokens de Facebook pueden expirar (los de usuario, a los 60 días). El
token de página de larga duración generalmente no expira solo, pero
revisalo cada tanto para evitar que el workflow falle en silencio.

### 3. Cargar los secrets en GitHub

En el repo: **Settings → Secrets and variables → Actions → New repository
secret**, y cargá:

- `FB_PAGE_ID`
- `FB_PAGE_ACCESS_TOKEN`
- `IG_USER_ID`
- `IG_ACCESS_TOKEN` (si usás el mismo token que Facebook, podés omitir este
  y el script usa `FB_PAGE_ACCESS_TOKEN` por defecto)

### 4. Subir tus fotos

Poné los archivos `.jpg` / `.jpeg` / `.png` dentro de la carpeta `images/` y
hacé commit + push.

## Probarlo manualmente

En la pestaña **Actions** del repo, elegí el workflow "Publicador automatico
FB/IG" y usá **Run workflow** para probarlo sin esperar al cron.

## Notas

- El intervalo de "cada 20hs" es aproximado (entre 20 y 22hs), porque el
  cron de GitHub Actions corre cada 2hs y el script decide si corresponde
  publicar o no. Si necesitás precisión exacta al minuto, se puede migrar a
  un servidor con `cron` real o un servicio tipo Render/Railway.
- Cuando se acaben las imágenes sin usar, el script simplemente no publica
  y lo indica en el log — no falla el workflow. Podés resetear
  `used_images` en `state.json` o subir fotos nuevas.
- GitHub Actions "schedule" puede demorar unos minutos en dispararse en
  horarios de mucho tráfico; no es instantáneo al segundo.
