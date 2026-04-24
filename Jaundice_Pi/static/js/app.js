async function captureImage() {
    const input    = document.getElementById("body-part-input");
    const btn      = document.getElementById("capture-btn");
    const flash    = document.getElementById("capture-flash");
    const bodyPart = input.value.trim();

    if (!bodyPart) {
        showToast("Please enter a body part location.", "error");
        input.focus();
        return;
    }

    btn.disabled = true;
    btn.innerHTML = '<span class="btn__icon">⏳</span> Analysing…';

    flash.classList.add("capture__flash--active");
    flash.addEventListener("animationend",
        () => flash.classList.remove("capture__flash--active"), { once: true });

    _hide("results-panel");
    _hide("pipeline-error");

    try {
        const fd = new FormData();
        fd.append("body_part", bodyPart);

        const res  = await fetch("/capture", { method: "POST", body: fd });
        const data = await res.json();

        if (!data.success) {
            showToast(`❌ ${data.error || "Capture failed."}`, "error");
            return;
        }

        showToast(`✅ Captured: ${data.filename}`, "success");

        const pipe = data.pipeline;

        if (pipe && pipe.success && pipe.stats) {
            _showStats(pipe.stats, data.body_part, pipe.processed, pipe.stages);
            input.value = "";
        } else if (pipe && pipe.error) {
            _showPipelineError(pipe.error);
        }

    } catch (err) {
        showToast(`❌ Network error: ${err.message}`, "error");
    } finally {
        btn.disabled = false;
        btn.innerHTML = '<span class="btn__icon">📸</span> Capture &amp; Analyse';
    }
}

function _showStats(stats, bodyPart, processedFilename, stages) {
    const bpEl = document.getElementById("result-body-part");
    if (bpEl) bpEl.textContent = bodyPart ? `— ${bodyPart}` : "";

    const [L, a, b]     = stats.meanLAB;
    const [sL, sa, sb]  = stats.stdLAB;

    _setText("stat-L",        L.toFixed(2));
    _setText("stat-L-std",    `± ${sL.toFixed(2)}`);
    _setText("stat-a",        a.toFixed(2));
    _setText("stat-a-std",    `± ${sa.toFixed(2)}`);
    _setText("stat-b",        b.toFixed(2));
    _setText("stat-b-std",    `± ${sb.toFixed(2)}`);
    _setText("stat-coverage", `${stats.coverage}%`);

    const cvEl = document.getElementById("stat-cv-b");
    if (cvEl && stats.cv_b !== undefined) {
        cvEl.textContent = `${stats.cv_b}%`;
        cvEl.style.color = stats.cv_b < 15 ? "#4ade80"
                         : stats.cv_b < 30 ? "#facc15" : "#f87171";
    }

    const ssimEl = document.getElementById("stat-ssim");
    if (ssimEl && stats.ssim !== null && stats.ssim !== undefined) {
        ssimEl.textContent = stats.ssim.toFixed(3);
        ssimEl.style.color = stats.ssim > 0.95 ? "#facc15"
                           : stats.ssim > 0.82 ? "#4ade80"
                           : "#60a5fa";
    } else if (ssimEl) {
        ssimEl.textContent = "N/A";
    }

    const swatch = document.getElementById("swatch-preview");
    if (swatch && stats.meanRGB) {
        const [r, g, bv] = stats.meanRGB.map(v => Math.round(v * 255));
        swatch.style.background = `rgb(${r},${g},${bv})`;
        swatch.title = `RGB(${r}, ${g}, ${bv})`;
    }

    const timingsEl = document.getElementById("results-timings");
    if (timingsEl && stages) {
        const labels = {
            load_ms:       "Load",
            blur_ms:       "Blur check",
            preprocess_ms: "Preprocess",
            shading_ms:    "Shading",
            ccm_ms:        "CCM",
            hair_ms:       "Hair",
            skin_ms:       "Skin mask",
            roi_ms:        "ROI",
            stats_ms:      "Stats",
            save_ms:       "Save",
        };
        const items = Object.entries(labels)
            .filter(([k]) => stages[k] !== undefined)
            .map(([k, label]) => `<span class="timing-chip">${label}: ${stages[k]}ms</span>`)
            .join("");
        timingsEl.innerHTML = `<div class="timings-row">${items}</div>`;
        if (stages.total_ms)
            timingsEl.innerHTML += `<div class="timings-total">Total: ${stages.total_ms}ms</div>`;
    }

    if (processedFilename) {
        const thumbRow  = document.getElementById("results-thumb-row");
        const thumb     = document.getElementById("results-thumb");
        const thumbLink = document.getElementById("results-thumb-link");
        if (thumbRow && thumb) {
            const url       = `/processed_images/${processedFilename}`;
            thumb.src       = url;
            thumbLink.href  = url;
            thumbRow.style.display = "flex";
        }
    }

    _show("results-panel");
}

function _showPipelineError(msg) {
    _setText("pipeline-error-msg", msg);
    _show("pipeline-error");
}

function showToast(message, type = "success", duration = 4000) {
    const container = document.getElementById("toast-container");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `toast toast--${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = "slide-out 0.3s ease forwards";
        toast.addEventListener("animationend", () => toast.remove(), { once: true });
    }, duration);
}

function openLightbox(src, caption) {
    const lb  = document.getElementById("lightbox");
    const img = document.getElementById("lightbox-img");
    const cap = document.getElementById("lightbox-caption");
    if (!lb || !img) return;
    img.src = src;
    img.alt = caption || "";
    if (cap) cap.textContent = caption || "";
    lb.classList.add("lightbox--visible");
    document.body.style.overflow = "hidden";
}

function closeLightbox(event) {
    if (event && event.target.id === "lightbox-img") return;
    const lb = document.getElementById("lightbox");
    if (!lb) return;
    lb.classList.remove("lightbox--visible");
    document.body.style.overflow = "";
}

document.addEventListener("keydown", e => {
    if (e.key === "Escape") closeLightbox();
});

function _show(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = "";
}

function _hide(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = "none";
}

function _setText(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
}