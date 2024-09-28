document.getElementById('analyze-btn').addEventListener('click', function() {
    const fingerprint = getBrowserFingerprint();
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Hide results and show the loading message
    document.getElementById('results').style.display = 'none';
    document.getElementById('results').innerHTML = '<p>Analyzing...</p>';
    
    fetch('/analyze_fingerprint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(fingerprint)
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text); });
        }
        return response.json();
    })
    .then(data => {
        // Display the results section once data is received
        document.getElementById('results').style.display = 'block'; // Make it visible
        let riskLevelClass = '';
        let riskProgressClass = '';
        let riskProgress = 0;

        if (data.risk_level === 'High') {
            riskLevelClass = 'bg-danger';
            riskProgressClass = 'progress-100';
            riskProgress = 100;
        } else if (data.risk_level === 'Medium') {
            riskLevelClass = 'bg-warning';
            riskProgressClass = 'progress-70';
            riskProgress = 70;
        } else {
            riskLevelClass = 'bg-success';
            riskProgressClass = 'progress-30';
            riskProgress = 30;
        }

        let detailsHTML = `
            <h2>Analysis Results</h2>
            <span class="badge ${riskLevelClass}" style="font-size: 1.2rem;">Risk Level: ${data.risk_level}</span>
            <div class="progress mt-3">
                <div class="progress-bar ${riskLevelClass} ${riskProgressClass}" role="progressbar" aria-valuenow="${riskProgress}" aria-valuemin="0" aria-valuemax="100"></div>
            </div>
            <p class="mt-3"><strong>Fingerprint Hash:</strong> ${data.fingerprint_hash}</p>
            <h3>Detailed Breakdown</h3>
            <button class="btn btn-info mb-3" type="button" data-bs-toggle="collapse" data-bs-target="#breakdown" aria-expanded="false" aria-controls="breakdown">
                Show Details
            </button>
            <div class="collapse" id="breakdown">`;

        data.detailed_analysis.forEach(detail => {
            const isUncommon = detail.description.includes('uncommon and may make your browser more identifiable');
            const descriptionColorClass = isUncommon ? 'text-danger' : 'text-white';
            const recommendationColorClass = detail.recommendation ? 'text-warning' : 'text-white';
            const isValueLong = detail.value.length > 50;
            const truncatedValue = isValueLong ? detail.value.substring(0, 50) + '...' : detail.value;
            const collapseId = `${detail.attribute.replace(/\s+/g, '_')}_collapse`;

            detailsHTML += `
                <div class="row bg-dark text-light p-3 mb-2">
                    <div class="col-12">
                        <h5 class="mb-1 text-light"><i class="fas ${isUncommon ? 'fa-exclamation-circle' : 'fa-check-circle'}"></i> ${detail.attribute}</h5>
                        <p class="mb-1 text-light"><strong>Value:</strong> ${isValueLong ? truncatedValue : detail.value}</p>
                        ${isValueLong ? `
                        <button class="btn btn-link text-light p-0" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">
                            Show Full Value
                        </button>
                        <div class="collapse mt-2" id="${collapseId}">
                            <div class="scrollable-content text-light">
                                <p class="card-text">${detail.value}</p>
                            </div>
                        </div>` : ''}
                        <p class="mb-1 ${descriptionColorClass} text-light"><small>${detail.description}</small></p>
                        <p class="mb-0 ${recommendationColorClass} text-light"><strong>Recommendation:</strong> ${detail.recommendation ? detail.recommendation : 'None'}</p>
                    </div>
                </div>`;
        });

        document.getElementById('results').innerHTML = detailsHTML;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('results').style.display = 'block'; // Ensure the error message is visible
        document.getElementById('results').innerHTML = `<div class="alert alert-danger" role="alert">An error occurred: ${error.message}</div>`;
    });
});

function getBrowserFingerprint() {
    const fingerprint = {
        userAgent: navigator.userAgent,
        platform: navigator.platform,
        screenResolution: `${screen.width}x${screen.height}`,
        colorDepth: screen.colorDepth,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        language: navigator.language,
        languages: navigator.languages,
        hardwareConcurrency: navigator.hardwareConcurrency,
        deviceMemory: navigator.deviceMemory || 'N/A',
        plugins: getPlugins(),
        mimeTypes: getMimeTypes(),
        doNotTrack: navigator.doNotTrack,
        canvasFingerprint: getCanvasFingerprint(),
        webglFingerprint: getWebGLFingerprint(),
        audioFingerprint: getAudioFingerprint(),
        fonts: getFonts(),
        touchSupport: getTouchSupport(),
        pointerSupport: getPointerSupport(),
        connectionType: getConnectionType(),
        maxTouchPoints: navigator.maxTouchPoints || 'N/A',
        javaEnabled: navigator.javaEnabled(),
        cookieEnabled: navigator.cookieEnabled,
    };
    return fingerprint;
}

function getPlugins() {
    return Array.from(navigator.plugins).map(plugin => plugin.name);
}

function getMimeTypes() {
    return Array.from(navigator.mimeTypes).map(mimeType => mimeType.type);
}

function getCanvasFingerprint() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    ctx.textBaseline = 'top';
    ctx.font = '14px Arial';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = '#f60';
    ctx.fillRect(125, 1, 62, 20);
    ctx.fillStyle = '#069';
    ctx.fillText('Browser Fingerprint', 2, 15);
    ctx.fillStyle = 'rgba(102, 204, 0, 0.7)';
    ctx.fillText('Browser Fingerprint', 4, 17);
    return canvas.toDataURL();
}

function getWebGLFingerprint() {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (!gl) return null;
    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    return gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL) + '~' + gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
}

function getAudioFingerprint() {
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    oscillator.type = 'triangle';
    oscillator.frequency.setValueAtTime(10000, audioContext.currentTime);
    const compressor = audioContext.createDynamicsCompressor();
    oscillator.connect(compressor);
    compressor.connect(audioContext.destination);
    oscillator.start(0);
    const fingerprint = compressor.getParameters ? compressor.getParameters() : 'AudioContext';
    oscillator.stop(0);
    return JSON.stringify(fingerprint);
}

function getFonts() {
    return ['Arial', 'Courier New', 'Georgia'];
}

function getTouchSupport() {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

function getPointerSupport() {
    return 'onpointerdown' in window;
}

function getConnectionType() {
    if (navigator.connection) {
        return {
            effectiveType: navigator.connection.effectiveType,
            downlink: navigator.connection.downlink,
            rtt: navigator.connection.rtt,
        };
    }
    return 'N/A';
}
