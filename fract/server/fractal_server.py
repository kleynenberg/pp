#!/usr/bin/env python3
"""
Multi-user Fractal Multiverse PWA
Draait via Python aiohttp op poort 31415.
Bevat: 100% Standalone index.html (inclusief inline Infinity favicon Data URI en PWA manifest Data URI),
Perturbation Theory via Decimal.js, geen blokken bij extreme deep-zoom, Toast notificatie,
Ingangspunt URL behoud, Semi-transparante HUD, Universe-specifieke Warp Home.
"""

import aiohttp
import aiohttp.web
import json
import logging

logging.basicConfig(level=logging.INFO)

HTML_CLIENT = """<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>3D Fractal Multiverse PWA</title>
    <!-- Inline Data URI voor het Infinity Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect width='100' height='100' fill='%23000000'/%3E%3Cpath d='M 30,50 C 15,30 15,70 30,50 C 45,30 55,70 70,50 C 85,30 85,70 70,50 C 55,30 45,70 30,50 Z' fill='none' stroke='%2338bdf8' stroke-width='8' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E">
    <!-- Decimal.js voor arbitraire precisie referentie-banen -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/decimal.js/10.4.3/decimal.min.js"></script>
    <link rel="manifest" href="data:application/manifest+json,{
        'name': 'Fractal Multiverse',
        'short_name': 'Multiverse',
        'start_url': '/',
        'scope': '/',
        'display': 'fullscreen',
        'orientation': 'any',
        'background_color': '#000000',
        'theme_color': '#000000',
        'icons': [{
            'src': 'data:image/svg+xml,%3Csvg xmlns=\\'http://www.w3.org/2000/svg\\' viewBox=\\'0 0 100 100\\'%3E%3Crect width=\\'100\\' height=\\'100\\' fill=\\'%23000000\\'/%3E%3Cpath d=\\'M 30,50 C 15,30 15,70 30,50 C 45,30 55,70 70,50 C 85,30 85,70 70,50 C 55,30 45,70 30,50 Z\\' fill=\\'none\\' stroke=\\'%2338bdf8\\' stroke-width=\\'8\\' stroke-linecap=\\'round\\' stroke-linejoin=\\'round\\'/%3E%3C/svg%3E',
            'sizes': '512x512',
            'type': 'image/svg+xml'
        }]
    }">
    <style>
        body, html {
            margin: 0;
            padding: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            background: #000;
            font-family: monospace;
            color: #fff;
            touch-action: none;
        }
        canvas {
            width: 100%;
            height: 100%;
            display: block;
        }
        #hud {
            position: absolute;
            top: 12px;
            left: 12px;
            pointer-events: none;
            background: rgba(0, 0, 0, 0.35);
            backdrop-filter: blur(4px);
            padding: 10px;
            border-radius: 6px;
            font-size: 11px;
            border: 1px solid rgba(255,255,255,0.1);
            line-height: 1.4;
            z-index: 10;
            opacity: 0.85;
            transition: opacity 0.2s ease;
        }
        #hud:hover {
            opacity: 1.0;
        }
        #hud label {
            pointer-events: auto;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            margin-top: 4px;
            color: #ffcc00;
        }
        .btn-group {
            position: absolute;
            bottom: 15px;
            right: 15px;
            display: flex;
            gap: 8px;
            pointer-events: auto;
            z-index: 10;
        }
        .action-btn {
            background: rgba(15, 15, 15, 0.5);
            backdrop-filter: blur(4px);
            color: rgba(255, 255, 255, 0.85);
            border: 1px solid rgba(255,255,255,0.25);
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-family: monospace;
            font-size: 11px;
            font-weight: bold;
            transition: all 0.2s ease;
        }
        .action-btn:hover {
            background: rgba(40, 40, 40, 0.8);
            color: #fff;
            border-color: rgba(255,255,255,0.5);
        }
        .action-btn:active {
            transform: scale(0.95);
        }
        #footer {
            position: absolute;
            bottom: 6px;
            left: 12px;
            font-size: 8px;
            color: rgba(255, 255, 255, 0.2);
            text-decoration: none;
            pointer-events: auto;
            z-index: 10;
            transition: color 0.2s ease;
        }
        #footer:hover {
            color: rgba(255, 255, 255, 0.6);
        }
        #toast {
            position: absolute;
            bottom: 65px;
            left: 50%;
            transform: translateX(-50%) translateY(10px);
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(6px);
            color: #38bdf8;
            border: 1px solid rgba(56, 189, 248, 0.4);
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.3s ease, transform 0.3s ease;
            z-index: 100;
            box-shadow: 0 4px 16px rgba(0,0,0,0.6);
        }
        #toast.show {
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }
    </style>
</head>
<body>
    <canvas id="glCanvas"></canvas>
    <div id="hud">
        Universum: <span id="uniName">Mandelbrot</span><br>
        Zoom: <span id="zoomVal">3.00</span><br>
        Status: <span id="connStatus">Verbinden...</span><br>
        <label><input type="checkbox" id="connToggle" checked> Connected</label>
    </div>
    <div class="btn-group">
        <button class="action-btn" id="fsBtn">Full</button>
        <button class="action-btn" id="homeBtn">Home</button>
        <button class="action-btn" id="shareBtn">Share</button>
    </div>
    <a id="footer" href="https://kleynenberg.com" target="_blank">&copy; steven steven.kleynenberg@gmail.com</a>
    <div id="toast">Link gekopieerd naar klembord!</div>

    <script>
        Decimal.set({ precision: 50 });

        const canvas = document.getElementById('glCanvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        if (!gl) {
            alert('WebGL niet beschikbaar!');
        }

        const baseEntryUrl = window.location.origin + window.location.pathname;

        let state = {
            universe: 0,
            x: -0.5,
            y: 0.0,
            zoom: 3.0
        };

        let targetState = {
            universe: 0,
            x: -0.5,
            y: 0.0,
            zoom: 3.0
        };

        function parseHash() {
            if (window.location.hash) {
                const params = new URLSearchParams(window.location.hash.substring(1));
                if (params.has('uni')) targetState.universe = state.universe = parseInt(params.get('uni')) % 3;
                if (params.has('x')) targetState.x = state.x = parseFloat(params.get('x'));
                if (params.has('y')) targetState.y = state.y = parseFloat(params.get('y'));
                if (params.has('z')) targetState.zoom = state.zoom = parseFloat(params.get('z'));
            }
        }
        parseHash();

        let ws = null;
        let isRemoteUpdate = false;
        const connToggle = document.getElementById('connToggle');
        const connStatus = document.getElementById('connStatus');

        function updateConnectionState() {
            if (connToggle.checked) {
                connStatus.innerText = 'Verbinden...';
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

                ws.onopen = () => connStatus.innerText = 'Online';
                ws.onclose = () => {
                    if (connToggle.checked) connStatus.innerText = 'Verbroken';
                };
                ws.onerror = () => {
                    connStatus.innerText = 'Fout';
                };
                ws.onmessage = (event) => {
                    try {
                        const remoteState = JSON.parse(event.data);
                        isRemoteUpdate = true;
                        targetState.universe = remoteState.universe;
                        targetState.x = remoteState.x;
                        targetState.y = remoteState.y;
                        targetState.zoom = remoteState.zoom;
                        isRemoteUpdate = false;
                    } catch(e) {}
                };
            } else {
                if (ws) {
                    ws.close();
                    ws = null;
                }
                connStatus.innerText = 'Standalone';
            }
        }

        connToggle.addEventListener('change', updateConnectionState);
        updateConnectionState();

        function broadcastState() {
            if (!isRemoteUpdate && connToggle.checked && ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify(targetState));
            }
        }

        const vsSource = `
            attribute vec2 aPosition;
            void main() {
                gl_Position = vec4(aPosition, 0.0, 1.0);
            }
        `;

        const fsSource = `
            precision highp float;
            uniform vec2 u_resolution;
            uniform vec2 u_center;
            uniform float u_zoom;
            uniform int u_universe;
            uniform float u_blur;
            uniform vec2 u_orbit[128];

            void main() {
                vec2 st = (gl_FragCoord.xy - 0.5 * u_resolution.xy) / u_resolution.y;
                vec2 dc = st * u_zoom;

                float n = 0.0;
                float maxIt = 128.0;
                bool escaped = false;

                if (u_universe == 0 && u_zoom < 1e-4) {
                    vec2 dz = dc;
                    for (int i = 0; i < 128; i++) {
                        if (float(i) >= maxIt) break;
                        vec2 Z = u_orbit[i];
                        float twoZr = 2.0 * Z.x;
                        float twoZi = 2.0 * Z.y;
                        vec2 term1 = vec2(twoZr * dz.x - twoZi * dz.y, twoZr * dz.y + twoZi * dz.x);
                        vec2 dz2 = vec2(dz.x * dz.x - dz.y * dz.y, 2.0 * dz.x * dz.y);
                        dz = term1 + dz2 + dc;

                        vec2 z = Z + dz;
                        if (dot(z, z) > 4.0) {
                            n = float(i);
                            escaped = true;
                            break;
                        }
                        n = float(i);
                    }
                } else {
                    vec2 c = st * u_zoom + u_center;
                    vec2 z = c;
                    for (float i = 0.0; i < 128.0; i++) {
                        if (i > maxIt) break;
                        if (u_universe == 0) {
                            z = vec2(z.x * z.x - z.y * z.y, 2.0 * z.x * z.y) + c;
                        } else if (u_universe == 1) {
                            float x2 = z.x * z.x;
                            float y2 = z.y * z.y;
                            z = vec2(z.x * (x2 - 3.0 * y2), z.y * (3.0 * x2 - y2)) + c;
                        } else {
                            vec2 absZ = abs(z);
                            z = vec2(absZ.x * absZ.x - absZ.y * absZ.y, 2.0 * absZ.x * absZ.y) + c;
                        }
                        if (dot(z, z) > 4.0) {
                            n = i;
                            escaped = true;
                            break;
                        }
                        n = i;
                    }
                }

                vec3 color = vec3(0.0);
                if (escaped) {
                    float t = n / maxIt;
                    color = 0.5 + 0.5 * cos(6.28318 * (1.5 * t + vec3(0.0, 0.33, 0.67)));
                    color *= smoothstep(0.0, 0.15, t);
                }

                color = mix(color, vec3(0.02, 0.04, 0.08), u_blur);
                gl_FragColor = vec4(color, 1.0);
            }
        `;

        function createShader(gl, type, source) {
            const shader = gl.createShader(type);
            gl.shaderSource(shader, source);
            gl.compileShader(shader);
            return shader;
        }

        const shaderProg = gl.createProgram();
        gl.attachShader(shaderProg, createShader(gl, gl.VERTEX_SHADER, vsSource));
        gl.attachShader(shaderProg, createShader(gl, gl.FRAGMENT_SHADER, fsSource));
        gl.linkProgram(shaderProg);
        gl.useProgram(shaderProg);

        const positionBuffer = gl.createBuffer();
        gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
        gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([
            -1, -1,  1, -1, -1,  1,
            -1,  1,  1, -1,  1,  1,
        ]), gl.STATIC_DRAW);

        const aPositionLoc = gl.getAttribLocation(shaderProg, "aPosition");
        gl.enableVertexAttribArray(aPositionLoc);
        gl.vertexAttribPointer(aPositionLoc, 2, gl.FLOAT, false, 0, 0);

        const uOrbitLocs = [];
        for (let i = 0; i < 128; i++) {
            uOrbitLocs.push(gl.getUniformLocation(shaderProg, `u_orbit[${i}]`));
        }

        let blurFactor = 0.0;
        let lastOrbitX = null;
        let lastOrbitY = null;
        const orbitReal = new Float32Array(128);
        const orbitImag = new Float32Array(128);

        function updateReferenceOrbit(cx, cy) {
            try {
                let zr = new Decimal(cx);
                let zi = new Decimal(cy);
                let cr = new Decimal(cx);
                let ci = new Decimal(cy);

                for (let i = 0; i < 128; i++) {
                    orbitReal[i] = zr.toNumber();
                    orbitImag[i] = zi.toNumber();

                    let zr2 = zr.mul(zr);
                    let zi2 = zi.mul(zi);
                    let zri = zr.mul(zi);

                    zr = zr2.minus(zi2).plus(cr);
                    zi = zri.plus(zri).plus(ci);

                    if (zr2.plus(zi2).gt(100)) {
                        for (let j = i + 1; j < 128; j++) {
                            orbitReal[j] = orbitReal[i];
                            orbitImag[j] = orbitImag[i];
                        }
                        break;
                    }
                }
            } catch(e) {}
        }

        function render() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            gl.viewport(0, 0, canvas.width, canvas.height);

            const damping = 0.12;
            state.x += (targetState.x - state.x) * damping;
            state.y += (targetState.y - state.y) * damping;
            state.zoom += (targetState.zoom - state.zoom) * damping;
            state.universe = targetState.universe;

            if (state.zoom < 1e-12) {
                blurFactor = Math.min(1.0, blurFactor + 0.05);
                if (blurFactor >= 1.0) {
                    targetState.universe = (targetState.universe + 1) % 3;
                    targetState.zoom = 3.0;
                    if (targetState.universe === 1) {
                        targetState.x = 0.0; targetState.y = 0.0;
                    } else if (targetState.universe === 2) {
                        targetState.x = -0.5; targetState.y = -0.5;
                    } else {
                        targetState.x = -0.5; targetState.y = 0.0;
                    }
                    blurFactor = 0.0;
                    broadcastState();
                }
            } else if (state.zoom > 3.5) {
                blurFactor = Math.min(1.0, blurFactor + 0.05);
                if (blurFactor >= 1.0) {
                    targetState.universe = (targetState.universe - 1 + 3) % 3;
                    targetState.zoom = 1e-11;
                    blurFactor = 0.0;
                    broadcastState();
                }
            } else {
                blurFactor = Math.max(0.0, blurFactor - 0.05);
            }

            if (lastOrbitX === null || Math.abs(state.x - lastOrbitX) > state.zoom * 0.1 || Math.abs(state.y - lastOrbitY) > state.zoom * 0.1) {
                updateReferenceOrbit(state.x, state.y);
                lastOrbitX = state.x;
                lastOrbitY = state.y;
            }

            for (let i = 0; i < 128; i++) {
                gl.uniform2f(uOrbitLocs[i], orbitReal[i], orbitImag[i]);
            }

            gl.uniform2f(gl.getUniformLocation(shaderProg, "u_resolution"), canvas.width, canvas.height);
            gl.uniform2f(gl.getUniformLocation(shaderProg, "u_center"), state.x, state.y);
            gl.uniform1f(gl.getUniformLocation(shaderProg, "u_zoom"), state.zoom);
            gl.uniform1i(gl.getUniformLocation(shaderProg, "u_universe"), state.universe);
            gl.uniform1f(gl.getUniformLocation(shaderProg, "u_blur"), blurFactor);

            gl.drawArrays(gl.TRIANGLES, 0, 6);

            const names = ["Mandelbrot", "Cubic (z^3)", "Burned Ship"];
            document.getElementById('uniName').innerText = names[state.universe];
            document.getElementById('zoomVal').innerText = state.zoom.toExponential(2);

            requestAnimationFrame(render);
        }
        requestAnimationFrame(render);

        function zoomAtPixel(clientX, clientY, zoomFactor) {
            const rect = canvas.getBoundingClientRect();
            const px = clientX - rect.left;
            const py = clientY - rect.top;

            const stX = (px - 0.5 * canvas.width) / canvas.height;
            const stY = (0.5 * canvas.height - py) / canvas.height;

            const clickReal = stX * targetState.zoom + targetState.x;
            const clickImag = stY * targetState.zoom + targetState.y;

            targetState.zoom *= zoomFactor;
            targetState.x = clickReal - stX * targetState.zoom;
            targetState.y = clickImag - stY * targetState.zoom;

            broadcastState();
        }

        function showToast() {
            const toast = document.getElementById('toast');
            toast.classList.add('show');
            setTimeout(() => {
                toast.classList.remove('show');
            }, 2200);
        }

        window.addEventListener('wheel', (e) => {
            if (e.target.closest('#hud') || e.target.closest('.btn-group') || e.target.closest('#footer')) return;
            e.preventDefault();
            const zoomFactor = Math.pow(1.002, e.deltaY);
            targetState.zoom *= zoomFactor;
            broadcastState();
        }, { passive: false });

        let isDragging = false;
        let startX = 0, startY = 0;
        let hasMoved = false;

        window.addEventListener('mousedown', (e) => {
            if (e.target.closest('#hud') || e.target.closest('.btn-group') || e.target.closest('#footer')) return;
            isDragging = true;
            startX = e.clientX;
            startY = e.clientY;
            hasMoved = false;
        });

        window.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            const dx = e.clientX - startX;
            const dy = e.clientY - startY;
            if (Math.abs(dx) > 2 || Math.abs(dy) > 2) {
                hasMoved = true;
            }
            startX = e.clientX;
            startY = e.clientY;

            const scale = targetState.zoom / canvas.height;
            targetState.x -= dx * scale;
            targetState.y += dy * scale;
            broadcastState();
        });

        window.addEventListener('mouseup', (e) => {
            if (isDragging && !hasMoved) {
                zoomAtPixel(e.clientX, e.clientY, 0.5);
            }
            isDragging = false;
        });

        let lastTouchDist = null;
        let touchStartX = 0, touchStartY = 0;
        let touchHasMoved = false;

        window.addEventListener('touchstart', (e) => {
            if (e.target.closest('#hud') || e.target.closest('.btn-group') || e.target.closest('#footer')) return;
            if (e.touches.length === 2) {
                lastTouchDist = Math.hypot(
                    e.touches[0].clientX - e.touches[1].clientX,
                    e.touches[0].clientY - e.touches[1].clientY
                );
                touchHasMoved = true;
            } else if (e.touches.length === 1) {
                startX = e.touches[0].clientX;
                startY = e.touches[0].clientY;
                touchStartX = startX;
                touchStartY = startY;
                touchHasMoved = false;
            }
        }, { passive: true });

        window.addEventListener('touchmove', (e) => {
            if (e.touches.length === 1) {
                const t = e.touches[0];
                const dx = t.clientX - startX;
                const dy = t.clientY - startY;
                if (Math.abs(dx) > 2 || Math.abs(dy) > 2) {
                    touchHasMoved = true;
                }
                startX = t.clientX;
                startY = t.clientY;

                const scale = targetState.zoom / canvas.height;
                targetState.x -= dx * scale;
                targetState.y += dy * scale;
                broadcastState();
            } else if (e.touches.length === 2) {
                touchHasMoved = true;
                const dist = Math.hypot(
                    e.touches[0].clientX - e.touches[1].clientX,
                    e.touches[0].clientY - e.touches[1].clientY
                );
                if (lastTouchDist !== null) {
                    const factor = lastTouchDist / dist;
                    targetState.zoom *= factor;
                }
                lastTouchDist = dist;
                broadcastState();
            }
        }, { passive: true });

        window.addEventListener('touchend', (e) => {
            if (e.touches.length === 0) {
                if (!touchHasMoved) {
                    zoomAtPixel(touchStartX, touchStartY, 0.5);
                }
                startX = null;
                startY = null;
            }
            if (e.touches.length < 2) {
                lastTouchDist = null;
            }
        });

        document.getElementById('fsBtn').addEventListener('click', () => {
            if (!document.fullscreenElement) {
                document.documentElement.requestFullscreen().catch(err => {});
            } else {
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                }
            }
        });

        document.getElementById('homeBtn').addEventListener('click', () => {
            targetState.zoom = 3.0;
            if (targetState.universe === 0) {
                targetState.x = -0.5;
                targetState.y = 0.0;
            } else if (targetState.universe === 1) {
                targetState.x = 0.0;
                targetState.y = 0.0;
            } else {
                targetState.x = -0.5;
                targetState.y = -0.5;
            }
            blurFactor = 0.0;
            broadcastState();
        });

        document.getElementById('shareBtn').addEventListener('click', () => {
            const hash = `#uni=${targetState.universe}&x=${targetState.x}&y=${targetState.y}&z=${targetState.zoom}`;
            const shareUrl = baseEntryUrl + hash;

            if (navigator.clipboard && navigator.clipboard.writeText && window.isSecureContext) {
                navigator.clipboard.writeText(shareUrl).then(() => {
                    showToast();
                }).catch(() => {
                    fallbackCopy(shareUrl);
                });
            } else {
                fallbackCopy(shareUrl);
            }
        });

        function fallbackCopy(text) {
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.focus();
            textarea.select();
            try {
                const successful = document.execCommand('copy');
                if (successful) {
                    showToast();
                } else {
                    prompt('Kopieer deze URL voor WhatsApp:', text);
                }
            } catch (err) {
                prompt('Kopieer deze URL voor WhatsApp:', text);
            }
            document.body.removeChild(textarea);
        }
    </script>
</body>
</html>
"""

async def handle_index(request):
    return aiohttp.web.Response(text=HTML_CLIENT, content_type='text/html')

connected_clients = set()

async def websocket_handler(request):
    ws = aiohttp.web.WebSocketResponse()
    await ws.prepare(request)
    connected_clients.add(ws)
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                for client in connected_clients:
                    if client != ws:
                        await client.send_str(msg.data)
    finally:
        try:
            connected_clients.remove(ws)
        except KeyError:
            pass
    return ws

def init_app():
    app = aiohttp.web.Application()
    app.router.add_get('/', handle_index)
    app.router.add_get('/ws', websocket_handler)
    return app

if __name__ == '__main__':
    app = init_app()
    print("Multiversum server gestart op http://hp.kleynenberg.net:31415 (of http://localhost:31415). Statuspagina: https://gemini.google.com/settings/limits")
    aiohttp.web.run_app(app, host='0.0.0.0', port=31415)