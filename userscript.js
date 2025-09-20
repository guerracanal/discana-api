// ==UserScript==
// @name         Discana Album Manager for Spotify (mejorado)
// @namespace    http://tampermonkey.net/
// @version      1.1
// @description  Añade botón para gestionar álbum en Discana desde Spotify (popup fijo, tags, SPA nav)
// @author       TuNombre
// @match        https://open.spotify.com/*/album/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// ==/UserScript==

(function() {
    'use strict';

    const API_URL = 'http://localhost:8080/api/v2/a/find_collection/';
    const API_MODIFY_URL = 'http://localhost:8080/api/v2/a/albums/';
    const ADMIN_TOKEN = 'tok_xxx'; // Cambia por tu token real

    /* -------------------------
       Util: extraer spotify id
       ------------------------- */
    function getSpotifyId() {
        const m = window.location.pathname.match(/album\/([a-zA-Z0-9]+)/);
        return m ? m[1] : null;
    }

    /* ------------------------------------------------
       Añade botón en action bar (si no existe ya)
       ------------------------------------------------ */
    function addButton(collection, albumData) {
        const actionBar = document.querySelector('[data-testid="action-bar-row"]');
        if (!actionBar) return;
        if (document.getElementById('discana-btn')) return;

        const btn = document.createElement('button');
        btn.id = 'discana-btn';
        btn.style.marginLeft = '10px';
        btn.style.background = collection === 'albums' ? '#4caf50' : (collection === 'pendientes' ? '#ff9800' : '#f44336');
        btn.style.color = '#fff';
        btn.style.border = 'none';
        btn.style.padding = '8px 12px';
        btn.style.borderRadius = '999px';
        btn.style.cursor = 'pointer';
        btn.textContent = collection === 'albums' ? 'En colección' : (collection === 'pendientes' ? 'Pendiente' : 'Añadir');
        btn.onclick = () => showForm(albumData, collection);
        actionBar.appendChild(btn);
    }

    /* ------------------------------------------------
       SHOW FORM - popup fijo y estilos Spotify-like
       ------------------------------------------------ */
    function showForm(albumData, collection) {
        const old = document.getElementById('discana-form');
        if (old) old.remove();

        // Contenedor fijo (popup de ancho/alto fijo)
        const form = document.createElement('form');
        form.id = 'discana-form';
        Object.assign(form.style, {
            position: 'fixed',
            top: '80px',
            right: '40px',
            width: '420px',            // ancho fijo
            height: '640px',          // alto fijo
            background: '#121212',
            color: '#fff',
            borderRadius: '10px',
            padding: '16px',
            zIndex: 99999,
            boxShadow: '0 8px 40px rgba(0,0,0,0.6)',
            fontFamily: 'Circular, Helvetica, Arial, sans-serif',
            display: 'flex',
            flexDirection: 'column'
        });

        // Header
        const head = document.createElement('div');
        head.style.display = 'flex';
        head.style.justifyContent = 'space-between';
        head.style.alignItems = 'center';
        head.style.marginBottom = '8px';
        const title = document.createElement('div');
        title.textContent = albumData ? 'Editar álbum' : 'Crear álbum';
        title.style.fontWeight = '600';
        head.appendChild(title);
        const closeX = document.createElement('button');
        closeX.type = 'button';
        closeX.textContent = '✕';
        Object.assign(closeX.style, { background: 'transparent', color: '#b3b3b3', border: 'none', fontSize: '18px', cursor: 'pointer' });
        closeX.onclick = () => form.remove();
        head.appendChild(closeX);
        form.appendChild(head);

        // Contenido con scroll
        const body = document.createElement('div');
        Object.assign(body.style, {
            overflowY: 'auto',
            paddingRight: '8px',
            flex: '1 1 auto'
        });
        form.appendChild(body);

        const allFields = albumData ? Object.keys(albumData) : ['title','artist','spotify_id','year','format','genres','subgenres','mood','compilations'];

        allFields.forEach(name => {
            if (name === 'collection' || name === '_id') return;

            // etiqueta
            const label = document.createElement('label');
            label.textContent = name.charAt(0).toUpperCase() + name.slice(1);
            label.style.display = 'block';
            label.style.marginTop = '10px';
            label.style.fontSize = '13px';
            body.appendChild(label);

            // year -> date
            if (name === 'year' || name === 'release_date') {
                const input = document.createElement('input');
                input.type = 'date';
                input.name = name;
                input.value = albumData?.[name] || '';
                Object.assign(input.style, baseInputStyle());
                body.appendChild(input);
                return;
            }

            // tags fields (plural names)
            if (['genre','subgenres','mood','compilations'].includes(name)) {
                const wrapper = document.createElement('div');
                wrapper.className = 'tags-wrapper';
                Object.assign(wrapper.style, {
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: '6px',
                    background: '#181818',
                    padding: '8px',
                    borderRadius: '6px',
                    alignItems: 'center',
                    minHeight: '40px'
                });

                // normalizar valor (evita .split error)
                let rawVal = albumData?.[name] ?? '';
                if (Array.isArray(rawVal)) rawVal = rawVal.join(',');
                else if (typeof rawVal !== 'string') rawVal = String(rawVal || '');
                const values = rawVal.split(',').map(v => v.trim()).filter(Boolean);

                function renderTags() {
                    // clear keeping input at end
                    wrapper.innerHTML = '';
                    // tags
                    values.forEach((val, i) => {
                        const tag = document.createElement('span');
                        tag.textContent = val;
                        Object.assign(tag.style, {
                            background: '#282828',
                            padding: '6px 10px',
                            borderRadius: '20px',
                            fontSize: '12px',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '8px',
                            maxWidth: '100%'
                        });
                        const rm = document.createElement('button');
                        rm.type = 'button';
                        rm.textContent = '×';
                        Object.assign(rm.style, { background: 'transparent', color: '#bdbdbd', border: 'none', cursor: 'pointer', fontSize: '14px' });
                        rm.onclick = () => { values.splice(i,1); renderTags(); };
                        tag.appendChild(rm);
                        wrapper.appendChild(tag);
                    });

                    // input para añadir
                    const input = document.createElement('input');
                    input.type = 'text';
                    input.placeholder = 'Añadir... (enter)';
                    Object.assign(input.style, {
                        background: 'transparent',
                        border: 'none',
                        outline: 'none',
                        color: '#fff',
                        minWidth: '80px',
                        fontSize: '13px'
                    });
                    input.onkeydown = e => {
                        if (e.key === 'Enter' && input.value.trim()) {
                            e.preventDefault();
                            values.push(input.value.trim());
                            input.value = '';
                            renderTags();
                        }
                    };
                    wrapper.appendChild(input);
                }
                renderTags();

                // hidden para enviar
                const hidden = document.createElement('input');
                hidden.type = 'hidden';
                hidden.name = name;
                form.addEventListener('submit', () => hidden.value = values.join(','));
                body.appendChild(wrapper);
                body.appendChild(hidden);
                return;
            }

            // format -> select
            if (name === 'format') {
                const select = document.createElement('select');
                select.name = 'format';
                ['', 'Card','Vinilo','CD','Cassette'].forEach(opt => {
                    const o = document.createElement('option');
                    o.value = opt;
                    o.textContent = opt || '(vacío)';
                    if (albumData?.format === opt) o.selected = true;
                    select.appendChild(o);
                });
                Object.assign(select.style, baseInputStyle());
                body.appendChild(select);
                return;
            }

            // spotify_id no editable? lo ponemos readonly para evitar meter mal la url
            if (name === 'spotify_id') {
                const input = document.createElement('input');
                input.name = 'spotify_id';
                input.value = albumData?.[name] || getSpotifyId() || '';
                input.readOnly = true;
                Object.assign(input.style, baseInputStyle());
                body.appendChild(input);
                return;
            }

            // default text input
            const input = document.createElement('input');
            input.name = name;
            input.value = albumData?.[name] || '';
            Object.assign(input.style, baseInputStyle());
            body.appendChild(input);
        });

        // collection selector (vacío posible)
        const labCol = document.createElement('label');
        labCol.textContent = 'Colección';
        labCol.style.display = 'block';
        labCol.style.marginTop = '12px';
        body.appendChild(labCol);
        const selectCol = document.createElement('select');
        selectCol.name = 'collection';
        ['', 'albums','pendientes'].forEach(opt => {
            const o = document.createElement('option');
            o.value = opt;
            o.textContent = opt || '(vacío)';
            if ((albumData?.collection || collection) === opt) o.selected = true;
            selectCol.appendChild(o);
        });
        Object.assign(selectCol.style, baseInputStyle());
        body.appendChild(selectCol);

        // footer botones
        const footer = document.createElement('div');
        Object.assign(footer.style, { display:'flex', gap:'8px', marginTop:'12px', justifyContent: 'flex-end' });

        const saveBtn = document.createElement('button');
        saveBtn.type = 'submit';
        saveBtn.textContent = albumData ? 'Modificar álbum' : 'Crear álbum';
        Object.assign(saveBtn.style, { background: '#1db954', color:'#fff', border:'none', padding:'8px 14px', borderRadius:'20px', cursor:'pointer' });
        footer.appendChild(saveBtn);

        if (albumData && albumData._id) {
            const moveBtn = document.createElement('button');
            moveBtn.type = 'button';
            moveBtn.textContent = 'Mover';
            Object.assign(moveBtn.style, { background: '#ff9800', color:'#fff', border:'none', padding:'8px 14px', borderRadius:'20px', cursor:'pointer' });
            moveBtn.onclick = function() {
                const destCol = selectCol.value;
                const originCol = (albumData.collection || collection);
                if (destCol === originCol) { alert('Ya está en esa colección'); return; }
                GM_xmlhttpRequest({
                    method: 'POST',
                    url: 'http://localhost:8080/api/v2/a/move/',
                    headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${ADMIN_TOKEN}`},
                    data: JSON.stringify({ origin_collection: originCol, dest_collection: destCol, album_id: albumData._id }),
                    onload: function(resp){ alert('Álbum movido: '+resp.status); form.remove(); }
                });
            };
            footer.appendChild(moveBtn);
        }

        const cancel = document.createElement('button');
        cancel.type = 'button';
        cancel.textContent = 'Cerrar';
        Object.assign(cancel.style, { background: '#333', color:'#fff', border:'none', padding:'8px 14px', borderRadius:'20px', cursor:'pointer' });
        cancel.onclick = () => form.remove();
        footer.appendChild(cancel);

        form.appendChild(footer);

        // submit handler
        form.onsubmit = function(e) {
            e.preventDefault();
            const data = {};
            [...form.elements].forEach(el => { if (el.name) data[el.name] = el.value; });
            const url = albumData ? `${API_MODIFY_URL}${albumData._id}/` : API_MODIFY_URL;
            GM_xmlhttpRequest({
                method: albumData ? 'PUT' : 'POST',
                url: url,
                headers: {'Content-Type': 'application/json', 'Authorization': `Bearer ${ADMIN_TOKEN}`},
                data: JSON.stringify(data),
                onload: function(response) { alert('Operación realizada: ' + response.status); form.remove(); }
            });
        };

        document.body.appendChild(form);
    }

    /* -------------------------
       Style helper
       ------------------------- */
    function baseInputStyle() {
        return {
            width: '100%',
            padding: '8px',
            marginTop: '6px',
            marginBottom: '6px',
            background: '#181818',
            color: '#fff',
            border: '1px solid #333',
            borderRadius: '6px',
            fontSize: '13px',
            boxSizing: 'border-box'
        };
    }

    /* ------------------------------------------------
       Chequea si existen datos en tu API; si no,
       intenta rellenar con datos de Spotify (oembed/API)
       ------------------------------------------------ */
    function checkAlbumCollection(spotifyId) {
        if (!spotifyId) return;
        const url = `${API_URL}?spotify_id=${spotifyId}`;
        GM_xmlhttpRequest({
            method: 'GET',
            url: url,
            onload: async function(response) {
                let collection = null;
                let albumData = null;
                try {
                    const res = JSON.parse(response.responseText);
                    if (res.collection) collection = res.collection;
                    if (res.album) albumData = res.album;
                } catch (e) { /* ignore parse error */ }

                // Si no existe albumData, intentamos obtener info de Spotify y prefill
                if (!albumData) {
                    const spotifyPrefill = await getSpotifyData(spotifyId);
                    // spotifyPrefill puede ser objeto parcial o string de error
                    if (spotifyPrefill && typeof spotifyPrefill === 'object') {
                        // mapear nombres que use tu API a nuestro formulario
                        albumData = {
                            title: spotifyPrefill.title || spotifyPrefill.name || '',
                            artist: spotifyPrefill.artist || spotifyPrefill.artists?.[0]?.name || '',
                            spotify_id: spotifyId,
                            year: spotifyPrefill.release_date || spotifyPrefill.year || '',
                            genres: (spotifyPrefill.genres && spotifyPrefill.genres.join ? spotifyPrefill.genres.join(',') : (spotifyPrefill.genres || '')),
                            cover_url: spotifyPrefill.cover_url || spotifyPrefill.images?.[0]?.url || '',
                            tracks: spotifyPrefill.tracks || spotifyPrefill.total_tracks || '',
                            duration: spotifyPrefill.duration || '',
                            label: spotifyPrefill.label || ''
                        };
                    } else {
                        // no encontramos nada, prefill mínimo
                        albumData = { spotify_id: spotifyId, title:'', artist:'', year:'', genres:'' };
                    }
                }

                addButton(collection, albumData);
            }
        });
    }

    /* ------------------------------------------------
       getSpotifyData(albumId)
       - primero intenta oEmbed (pública)
       - si hay token embebido en la página, intenta llamada v1/albums
       - devuelve objeto con campos o null/error
       ------------------------------------------------ */
    async function getSpotifyData(albumId) {
        try {
            // 1) oEmbed (siempre pública)
            const oembedUrl = `https://open.spotify.com/oembed?url=spotify:album:${albumId}`;
            let res = await fetch(oembedUrl);
            if (!res.ok) throw new Error('oEmbed failed');
            const oembed = await res.json();
            const pre = {
                title: oembed.title || '',
                artist: oembed.author_name || '',
                cover_url: oembed.thumbnail_url || ''
            };

            // 2) intentar obtener token embebido en scripts de la página
            const token = tryExtractTokenFromPage();
            if (!token) {
                // si no hay token devolvemos lo que tenemos (oembed)
                return pre;
            }

            // 3) con token hacemos llamada real a API v1
            const apiUrl = `https://api.spotify.com/v1/albums/${albumId}`;
            const r2 = await fetch(apiUrl, { headers: { Authorization: `Bearer ${token}` }});
            if (!r2.ok) {
                // token inválido o CORS; devolvemos oembed parcial
                return pre;
            }
            const raw = await r2.json();
            const durationMinutes = Math.round((raw.tracks.items.reduce((s,t)=> s + (t.duration_ms||0),0) || 0)/60000);
            const release_date = raw.release_date || '';
            return {
                title: raw.name,
                artists: raw.artists,
                artist: raw.artists && raw.artists[0] && raw.artists[0].name ? raw.artists[0].name : pre.artist,
                tracks: raw.tracks ? raw.tracks.total : '',
                duration: durationMinutes,
                release_date: release_date,
                cover_url: raw.images && raw.images[0] && raw.images[0].url ? raw.images[0].url : pre.cover_url,
                type: raw.album_type || '',
                genres: raw.genres || [],
                label: raw.label || ''
            };
        } catch (err) {
            console.warn('getSpotifyData error', err);
            return null;
        }
    }

    /* ------------------------------------------------
       tryExtractTokenFromPage
       - busca en los scripts inline una cadena tipo "accessToken":"..."
       - devuelve token si encuentra, else null
       - es heurístico; puede no funcionar si Spotify cambia su bundling
       ------------------------------------------------ */
    function tryExtractTokenFromPage() {
        try {
            // 1) buscar en scripts inline
            const scripts = Array.from(document.scripts).map(s => s.textContent).filter(Boolean);
            for (const txt of scripts) {
                // patrón común encontrado en bundles: "accessToken":"BQ... (base64-like)"
                const m = txt.match(/accessToken\"?\s*:\s*\"([AQA-Za-z0-9\-_\.]{20,})\"/);
                if (m && m[1]) return m[1];
                const m2 = txt.match(/\"token\"\s*:\s*\"([AQA-Za-z0-9\-_\.]{20,})\"/);
                if (m2 && m2[1]) return m2[1];
            }

            // 2) buscar en window.__INITIAL_STATE__ o similares
            if (window.__INITIAL_STATE__) {
                const json = JSON.stringify(window.__INITIAL_STATE__);
                const m = json.match(/accessToken\":\"([AQA-Za-z0-9\-_\.]{20,})\"/);
                if (m && m[1]) return m[1];
            }
        } catch (e) {
            console.warn('token extract fail', e);
        }
        return null;
    }

    /* ------------------------------------------------
       SPA navigation handling:
       - override pushState & replaceState to detect URL changes
       - listen popstate
       - when url cambia, limpiar botón y re-check
       ------------------------------------------------ */
    let lastHandledUrl = location.href;
    function onUrlChange() {
        const spotifyId = getSpotifyId();
        // limpiar botón si existe
        const oldBtn = document.getElementById('discana-btn');
        if (oldBtn) oldBtn.remove();
        if (!spotifyId) return;
        checkAlbumCollection(spotifyId);
    }

    (function interceptHistoryMethods() {
        const _push = history.pushState;
        history.pushState = function() {
            _push.apply(this, arguments);
            setTimeout(() => {
                if (location.href !== lastHandledUrl) { lastHandledUrl = location.href; onUrlChange(); }
            }, 50);
        };
        const _replace = history.replaceState;
        history.replaceState = function() {
            _replace.apply(this, arguments);
            setTimeout(() => {
                if (location.href !== lastHandledUrl) { lastHandledUrl = location.href; onUrlChange(); }
            }, 50);
        };
        window.addEventListener('popstate', () => { if (location.href !== lastHandledUrl) { lastHandledUrl = location.href; onUrlChange(); } });
    })();

    /* ------------------------------------------------
       Inicial (cuando cargue por primera vez)
       ------------------------------------------------ */
    function waitForActionBarAndInit() {
        const actionBar = document.querySelector('[data-testid="action-bar-row"]');
        if (actionBar) {
            const spotifyId = getSpotifyId();
            if (spotifyId) checkAlbumCollection(spotifyId);
        } else {
            setTimeout(waitForActionBarAndInit, 500);
        }
    }
    waitForActionBarAndInit();

})();
