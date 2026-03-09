window.addEventListener("load", function () {
    const configuracaoCores = {
        'turistico': { cor: 'gold', label: 'Ponto Turístico' },
        'empreendedor': { cor: 'violet', label: 'Empreendedor Local' },
        'onibus': { cor: 'blue', label: 'Ponto de Ônibus' }
    };

    function criarIcone(cor) {
        return new L.Icon({
            iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${cor}.png`,
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        });
    }

    // 1. Inicialização do Mapa
    const map = L.map('map').setView([-19.1834, -40.3089], 7);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    const legenda = L.control({ position: 'bottomright' });

    legenda.onAdd = function () {
        const div = L.DomUtil.create('div', 'info legend');
        div.style.backgroundColor = 'white';
        div.style.padding = '10px';
        div.style.border = '2px solid rgba(0,0,0,0.2)';
        div.style.borderRadius = '8px';
        div.style.lineHeight = '24px';
        div.style.fontSize = '12px';

        div.innerHTML = '<h6 style="margin:0 0 5px 0; font-weight:bold;">Legenda</h6>';
        
        Object.keys(configuracaoCores).forEach(key => {
            const item = configuracaoCores[key];
            div.innerHTML += `
                <div style="display: flex; align-items: center; margin-bottom: 4px;">
                    <img src="https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${item.cor}.png" 
                         style="width: 12px; height: 20px; margin-right: 8px;">
                    <span>${item.label}</span>
                </div>
            `;
        });
        return div;
    };
    legenda.addTo(map);

    // 2. Parâmetros da URL
    const urlParams = new URLSearchParams(window.location.search);
    const targetLat = parseFloat(urlParams.get('lat'));
    const targetLon = parseFloat(urlParams.get('lon'));

    if (targetLat && targetLon) {
        map.flyTo([targetLat, targetLon], 16, { animate: true, duration: 2 });
    }

    // 3. Travamento de Limites
    var bounds = [[-21.5, -42.0], [-17.8, -39.0]];
    map.setMaxBounds(bounds);
    map.on('drag', function() { map.panInsideBounds(bounds, { animate: false }); });

    // 4. Correção de renderização
    setTimeout(() => { map.invalidateSize(true); }, 500);

    // 5. Busca dos dados e criação dos Marcadores (CORRIGIDO AQUI)
    fetch('/api/pontos')
        .then(res => res.json())
        .then(pontos => {
            pontos.forEach(ponto => {
                const lat = parseFloat(ponto.latitude);
                const lng = parseFloat(ponto.longitude);

                if (!isNaN(lat) && !isNaN(lng)) {
                    // --- AQUI ESTÁ A MUDANÇA ---
                    // Pegamos a cor baseada na origem, se não existir, usa 'blue'
                    const config = configuracaoCores[ponto.origem] || { cor: 'blue' };
                    
                    // Adicionamos o { icon: criarIcone(...) } no marker
                    const marker = L.marker([lat, lng], { 
                        icon: criarIcone(config.cor) 
                    }).addTo(map);
                    // ---------------------------
                    
                    const rotaDetail = ponto.origem === 'turistico' ? 'detalhes' : 'detalhes_empreendedor';
                    
                    marker.bindPopup(`
                        <div style="text-align: center;">
                            <strong>${ponto.nome}</strong><br>
                            <span style="font-size: 0.8rem; color: #666;">${ponto.origem.toUpperCase()}</span><br>
                            <hr style="margin: 5px 0;">
                            <a href="/${rotaDetail}/${ponto.id}" style="font-weight: bold; color: #007bff;">Ver detalhes</a>
                        </div>
                    `);

                    if (lat === targetLat && lng === targetLon) {
                        marker.openPopup();
                    }
                }
            });
        })
        .catch(err => console.error('Erro ao carregar pontos na API:', err));
});
