# Gabagool Clone — Polymarket Arb Bot

Bot de arbitraje para mercados BTC/ETH/SOL/XRP Up/Down en Polymarket.

**Estrategia:** Cuando `precio_UP + precio_DOWN < $1.00`, compra ambos lados y garantiza ganancia sin importar la dirección del mercado.

---

## Indice

1. [Como funciona](#como-funciona)
2. [Requisitos](#requisitos)
3. [Paso 1 — Crear wallet MetaMask](#paso-1--crear-wallet-metamask)
4. [Paso 2 — Conseguir USDC en Polygon](#paso-2--conseguir-usdc-en-polygon)
5. [Paso 3 — Crear cuenta en Polymarket](#paso-3--crear-cuenta-en-polymarket)
6. [Paso 4 — Obtener API Keys de Polymarket](#paso-4--obtener-api-keys-de-polymarket)
7. [Paso 5 — Setup local del bot](#paso-5--setup-local-del-bot)
8. [Paso 6 — Deploy en Google Cloud (gratis)](#paso-6--deploy-en-google-cloud-gratis)
9. [Monitoreo y P&L](#monitoreo-y-pl)
10. [Como saber si funciona](#como-saber-si-funciona)

---

## Como funciona

En los mercados de Polymarket, UP + DOWN siempre resuelve a $1.00 (uno gana, el otro pierde). Si el bot encuentra un momento donde:

```
precio_UP ($0.48) + precio_DOWN ($0.47) = $0.95
```

Compra ambos lados por $0.95 y garantiza recibir $1.00 al resolver = **5% de ganancia garantizada**.

El bot monitorea BTC, ETH, SOL y XRP en todos los timeframes (5min, 15min, 1hr) simultáneamente, 24/7.

---

## Requisitos

- Python 3.11 o superior
- $5 en USDC (en la red Polygon)
- Cuenta en MetaMask
- Cuenta en Polymarket
- Cuenta en Google Cloud (gratis)

---

## Paso 1 — Crear wallet MetaMask

1. Ir a [metamask.io](https://metamask.io) e instalar la extension del browser
2. Crear nueva wallet → guardar la **seed phrase** en un lugar seguro (papel, nunca digital)
3. Agregar la red **Polygon** a MetaMask:
   - Abrir MetaMask → Network → Add Network → Add manually
   - Network name: `Polygon Mainnet`
   - RPC URL: `https://polygon-rpc.com`
   - Chain ID: `137`
   - Currency symbol: `MATIC`
   - Block explorer: `https://polygonscan.com`
4. Exportar la **Private Key**:
   - MetaMask → los tres puntos → Account details → Export private key
   - Guardarla para el archivo `.env` (nunca compartirla)

---

## Paso 2 — Conseguir USDC en Polygon

La forma mas barata de conseguir $5 USDC en Polygon:

**Opcion A (recomendada) — Via exchange:**
1. Comprar USDC en Coinbase, Binance, o cualquier exchange
2. Al retirar, seleccionar red **Polygon** (no Ethereum — las fees son altisimas)
3. Retirar a tu address de MetaMask

**Opcion B — Bridge desde otra red:**
1. Si ya tenes USDC en otra red, usar [Polygon Bridge](https://portal.polygon.technology)
2. O [Stargate Finance](https://stargate.finance) para bridgear desde otras redes

> ⚠️ **Importante:** Necesitas tambien una pequeña cantidad de MATIC para pagar gas en Polygon (~$0.10 es suficiente para meses). Si retiras de exchange, algunos permiten retirar MATIC gratis o compralo junto con el USDC.

---

## Paso 3 — Crear cuenta en Polymarket

1. Ir a [polymarket.com](https://polymarket.com)
2. Click en **Sign In** → **MetaMask**
3. Aprobar la conexion en MetaMask
4. Firmar el mensaje de verificacion (no cuesta gas)
5. Tu cuenta queda creada automaticamente con tu wallet address

---

## Paso 4 — Obtener API Keys de Polymarket

Las API keys permiten al bot operar en tu nombre sin exponer tu private key en cada operacion.

1. En Polymarket ir a **Settings** (icono de perfil arriba a la derecha)
2. Click en **API Keys** o **Developer**
3. Click en **Create API Key**
4. Polymarket te mostrara 3 valores — copialos inmediatamente (no se vuelven a mostrar):
   - `API Key`
   - `API Secret`
   - `Passphrase`
5. Estos van en tu archivo `.env`

---

## Paso 5 — Setup local del bot

### Clonar el repo

```bash
git clone https://github.com/byronbogasai-cmd/gabagool-clone.git
cd gabagool-clone
```

### Instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configurar credenciales

```bash
cp .env.example .env
nano .env   # o abrilo con cualquier editor de texto
```

Completar con tus datos:

```env
POLY_API_KEY=tu_api_key_aqui
POLY_API_SECRET=tu_api_secret_aqui
POLY_API_PASSPHRASE=tu_passphrase_aqui
POLY_PRIVATE_KEY=tu_private_key_de_metamask
POLY_WALLET_ADDRESS=0xtu_direccion_publica

MIN_SPREAD=0.030    # 3% minimo de spread para operar
COMPOUND=true       # reinvertir ganancias automaticamente
```

### Probar en modo DRY (sin dinero real)

```bash
python main.py --capital 5.00 --dry
```

Deberias ver logs como:
```
10:23:01 [monitor] INFO Opportunity: BTC Up or Down - Feb 28, 4AM ET | UP=0.471 DOWN=0.502 SPREAD=0.027 (2.7%)
10:23:01 [strategy] DEBUG Skipped: Spread 2.7% below minimum 3.0%
```

Si ves oportunidades apareciendo → el bot funciona. Cuando superen el 3% las ejecutara.

### Correr en vivo

```bash
python main.py --capital 5.00
```

---

## Paso 6 — Deploy en Google Cloud (gratis)

Google Cloud tiene una instancia **siempre gratuita** (e2-micro) que es suficiente para el bot.

### Crear cuenta Google Cloud

1. Ir a [cloud.google.com](https://cloud.google.com) → **Get started for free**
2. Requiere tarjeta de credito para verificar identidad (no te cobran nada)
3. Recibes $300 de credito gratis por 90 dias + la instancia e2-micro es gratis para siempre

### Crear la VM

1. En Google Cloud Console ir a **Compute Engine → VM instances**
2. Click **Create Instance**
3. Configurar:
   - Name: `gabagool-bot`
   - Region: `us-central1` (requerido para el tier gratuito)
   - Machine type: `e2-micro` (0.25 vCPU, 1GB RAM) — **seleccionar este exactamente**
   - Boot disk: Debian GNU/Linux 11, 30GB
   - Firewall: dejar como esta
4. Click **Create**

### Conectar a la VM

En la lista de instancias, click en **SSH** al lado de tu VM. Se abre una terminal en el browser.

### Setup en la VM

Copiar y pegar este comando completo:

```bash
curl -sSL https://raw.githubusercontent.com/byronbogasai-cmd/gabagool-clone/main/deploy/setup.sh | bash
```

Esto instala Python, clona el repo y prepara todo automaticamente.

### Configurar el .env en la VM

```bash
cd gabagool-clone
nano .env
```

Pegar tus credenciales (las mismas del Paso 4 y 5).

### Arrancar el bot en background

```bash
screen -S bot                          # crear sesion persistente
source venv/bin/activate
python main.py --capital 5.00
```

Presionar `Ctrl+A` luego `D` para desconectarte — el bot sigue corriendo.

### Reconectarse para ver el bot

```bash
screen -r bot
```

---

## Monitoreo y P&L

### Ver resumen de ganancias

```bash
python main.py --summary
```

Output esperado:
```
╔═══════════════════════════════════╗
║         BOT P&L SUMMARY          ║
╠═══════════════════════════════════╣
║ Initial capital:  $5.0000         ║
║ Current capital:  $5.3420         ║
║ Total profit:     $0.3420         ║
║ Return:           +6.84%          ║
║ Total trades:     47              ║
║ Win rate:         83.0%           ║
╚═══════════════════════════════════╝
```

### Ver el historial completo

```bash
cat ledger.json
```

---

## Como saber si funciona

| Tiempo | Capital minimo esperado | Si esta por debajo... |
|--------|------------------------|----------------------|
| Semana 1 | $5.10 | Revisar logs — puede ser que el spread minimo este muy alto |
| Semana 2 | $5.20 | El bot esta funcionando |
| Mes 1 | $5.50 | Solido — subir MIN_SPREAD a 0.025 para mas trades |
| Mes 3 | $7.00+ | Considerar aumentar capital para mayor volumen |

### Ajustar el spread minimo

Si el bot encuentra pocas oportunidades, bajar `MIN_SPREAD` en `.env`:

```env
MIN_SPREAD=0.025   # 2.5% — mas trades, menor margen por trade
```

Si encuentra muchas pero las pierde por slippage, subirlo:

```env
MIN_SPREAD=0.040   # 4% — menos trades, mayor seguridad
```

---

## Preguntas frecuentes

**¿Necesito tener Claude o una IA corriendo?**
No. El bot es codigo Python puro. Una vez deployado corre solo para siempre.

**¿Es realmente ganancia garantizada?**
El arbitraje *en teoria* es garantizado. En la practica existe riesgo de ejecucion parcial (que se llene solo un lado), por eso el bot usa MIN_SPREAD para asegurarse que el margen cubra imprevistos.

**¿Que pasa si el bot se cae?**
Con Google Cloud la VM corre 24/7. Si el proceso muere, reconectarse via SSH y `screen -r bot` o reiniciar con `python main.py --capital X` donde X es el capital actual (ver en `ledger.json`).

**¿Puedo aumentar el capital despues?**
Si, simplemente transferir mas USDC a tu wallet de Polymarket. El bot usa el balance real de la cuenta, no solo el `--capital` inicial.
