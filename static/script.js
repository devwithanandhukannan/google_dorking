// OSINT Footprint Tool - Windows 95 Style
let generatedResults = [];

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    updateClock();
    setInterval(updateClock, 1000);
});

function initializeApp() {
    // Initialize counters
    updateCount();
    
    // Event listeners
    document.getElementById('select-all-btn').addEventListener('click', selectAll);
    document.getElementById('deselect-all-btn').addEventListener('click', deselectAll);
    document.getElementById('generate-btn').addEventListener('click', generateDorks);
    document.getElementById('copy-all-btn').addEventListener('click', copyAllUrls);
    document.getElementById('open-all-btn').addEventListener('click', openAllUrls);
    document.getElementById('export-txt-btn').addEventListener('click', () => exportResults('txt'));
    document.getElementById('export-html-btn').addEventListener('click', () => exportResults('html'));
    
    // Category toggle
    document.querySelectorAll('.category-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const category = this.dataset.category;
            const treeCategory = this.closest('.tree-category');
            const dorkCheckboxes = treeCategory.querySelectorAll('.dork-checkbox');
            
            // Toggle expanded state
            if (this.checked) {
                treeCategory.classList.add('expanded');
            }
            
            // Check/uncheck all dorks in category
            dorkCheckboxes.forEach(cb => {
                cb.checked = this.checked;
            });
            
            updateCount();
        });
        
        // Toggle expand on label click
        checkbox.nextElementSibling.addEventListener('click', function(e) {
            if (e.target.tagName !== 'INPUT') {
                const treeCategory = checkbox.closest('.tree-category');
                treeCategory.classList.toggle('expanded');
            }
        });
    });
    
    // Dork checkbox change
    document.querySelectorAll('.dork-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateCategoryCheckbox(this.dataset.category);
            updateCount();
        });
    });
    
    // Double-click to select all in category
    document.querySelectorAll('.tree-category-header').forEach(header => {
        header.addEventListener('dblclick', function() {
            const checkbox = this.querySelector('.category-checkbox');
            checkbox.checked = true;
            checkbox.dispatchEvent(new Event('change'));
        });
    });
    
    setStatus('Ready - Select dorks and enter target domain');
}

function updateClock() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit',
        hour12: true 
    });
    document.getElementById('tray-time').textContent = timeStr;
    document.getElementById('status-time').textContent = now.toLocaleString();
}

function updateCount() {
    const total = document.querySelectorAll('.dork-checkbox').length;
    const selected = document.querySelectorAll('.dork-checkbox:checked').length;
    document.getElementById('total-count').textContent = total;
    document.getElementById('selected-count').textContent = selected;
}

function updateCategoryCheckbox(category) {
    const categoryCheckbox = document.querySelector(`.category-checkbox[data-category="${category}"]`);
    const dorkCheckboxes = document.querySelectorAll(`.dork-checkbox[data-category="${category}"]`);
    const checkedCount = document.querySelectorAll(`.dork-checkbox[data-category="${category}"]:checked`).length;
    
    if (categoryCheckbox) {
        categoryCheckbox.checked = checkedCount === dorkCheckboxes.length;
        categoryCheckbox.indeterminate = checkedCount > 0 && checkedCount < dorkCheckboxes.length;
    }
}

function selectAll() {
    document.querySelectorAll('.dork-checkbox').forEach(cb => cb.checked = true);
    document.querySelectorAll('.category-checkbox').forEach(cb => cb.checked = true);
    document.querySelectorAll('.tree-category').forEach(tc => tc.classList.add('expanded'));
    updateCount();
    playSound('click');
    setStatus('All dorks selected');
}

function deselectAll() {
    document.querySelectorAll('.dork-checkbox').forEach(cb => cb.checked = false);
    document.querySelectorAll('.category-checkbox').forEach(cb => {
        cb.checked = false;
        cb.indeterminate = false;
    });
    updateCount();
    playSound('click');
    setStatus('All dorks deselected');
}

async function generateDorks() {
    const target = document.getElementById('target').value.trim();
    const searchEngine = document.getElementById('search-engine').value;
    const customQuery = document.getElementById('custom-query').value.trim();
    
    if (!target && !customQuery) {
        showAlert('Please enter a target domain or custom query!');
        return;
    }
    
    const selectedDorks = [];
    document.querySelectorAll('.dork-checkbox:checked').forEach(cb => {
        selectedDorks.push(cb.dataset.name);
    });
    
    if (selectedDorks.length === 0 && !customQuery) {
        showAlert('Please select at least one dork or enter a custom query!');
        return;
    }
    
    showLoading(true);
    setStatus('Generating dork links...');
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target: target,
                dorks: selectedDorks,
                search_engine: searchEngine,
                custom_query: customQuery
            })
        });
        
        const data = await response.json();
        generatedResults = data.results;
        displayResults(data.results);
        
        document.getElementById('export-btn').style.display = 'inline-flex';
        document.getElementById('results-count').textContent = data.count;
        
        playSound('complete');
        setStatus(`Generated ${data.count} dork links successfully`);
        
    } catch (error) {
        console.error('Error:', error);
        showAlert('Error generating dorks: ' + error.message);
        setStatus('Error generating dorks');
    } finally {
        showLoading(false);
    }
}

function displayResults(results) {
    const container = document.getElementById('results-container');
    container.innerHTML = '';
    
    if (results.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <div class="empty-text">No results</div>
            </div>
        `;
        return;
    }
    
    results.forEach((result, index) => {
        const item = document.createElement('div');
        item.className = 'result-item';
        item.innerHTML = `
            <div class="result-header">
                <span class="result-category">${escapeHtml(result.category)}</span>
            </div>
            <div class="result-name">${escapeHtml(result.name)}</div>
            <div class="result-query">${escapeHtml(result.query)}</div>
            <div class="result-actions">
                <a href="${result.url}" target="_blank" class="result-btn primary">🔍 Search</a>
                <button class="result-btn" onclick="copyQuery(${index})">📋 Copy</button>
                <button class="result-btn" onclick="copyUrl(${index})">🔗 URL</button>
            </div>
        `;
        container.appendChild(item);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function copyQuery(index) {
    navigator.clipboard.writeText(generatedResults[index].query);
    setStatus('Query copied to clipboard');
    playSound('click');
}

function copyUrl(index) {
    navigator.clipboard.writeText(generatedResults[index].url);
    setStatus('URL copied to clipboard');
    playSound('click');
}

function copyAllUrls() {
    if (generatedResults.length === 0) {
        showAlert('No results to copy!');
        return;
    }
    const urls = generatedResults.map(r => r.url).join('\n');
    navigator.clipboard.writeText(urls);
    setStatus(`Copied ${generatedResults.length} URLs to clipboard`);
    playSound('click');
}

function openAllUrls() {
    if (generatedResults.length === 0) {
        showAlert('No results to open!');
        return;
    }
    
    if (generatedResults.length > 10) {
        if (!confirm(`This will open ${generatedResults.length} tabs. Continue?`)) {
            return;
        }
    }
    
    generatedResults.forEach((result, index) => {
        setTimeout(() => {
            window.open(result.url, '_blank');
        }, index * 300);
    });
    
    setStatus(`Opening ${generatedResults.length} tabs...`);
}

async function exportResults(format) {
    if (generatedResults.length === 0) {
        showAlert('No results to export!');
        return;
    }
    
    const target = document.getElementById('target').value.trim();
    
    try {
        const response = await fetch(`/export/${format}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                results: generatedResults,
                target: target
            })
        });
        
        const data = await response.json();
        
        const blob = new Blob([data.content], { 
            type: format === 'html' ? 'text/html' : 'text/plain' 
        });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = data.filename;
        a.click();
        URL.revokeObjectURL(url);
        
        setStatus(`Exported to ${data.filename}`);
        playSound('complete');
        
    } catch (error) {
        console.error('Export error:', error);
        showAlert('Error exporting: ' + error.message);
    }
}

function showLoading(show) {
    document.getElementById('loading-dialog').style.display = show ? 'flex' : 'none';
}

function showAlert(message) {
    // Create Windows-style alert
    const dialog = document.createElement('div');
    dialog.className = 'dialog';
    dialog.innerHTML = `
        <div class="dialog-window" style="min-width: 250px;">
            <div class="title-bar">
                <div class="title-bar-text">⚠️ Alert</div>
                <div class="title-bar-controls">
                    <button class="close-btn" onclick="this.closest('.dialog').remove()">×</button>
                </div>
            </div>
            <div class="dialog-body" style="text-align: left;">
                <div style="display: flex; align-items: flex-start; gap: 15px;">
                    <span style="font-size: 32px;">⚠️</span>
                    <p style="margin: 0; padding-top: 8px;">${escapeHtml(message)}</p>
                </div>
                <div style="text-align: center; margin-top: 15px;">
                    <button class="result-btn primary" onclick="this.closest('.dialog').remove()" style="padding: 5px 30px;">OK</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(dialog);
    playSound('error');
}

function setStatus(text) {
    document.getElementById('status-text').textContent = text;
}

function playSound(type) {
    // Optional: Add Windows sounds
    // You can add actual sound files if desired
    console.log('Sound:', type);
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl+A - Select All
    if (e.ctrlKey && e.key === 'a' && !e.target.matches('input, textarea')) {
        e.preventDefault();
        selectAll();
    }
    
    // Ctrl+G - Generate
    if (e.ctrlKey && e.key === 'g') {
        e.preventDefault();
        generateDorks();
    }
    
    // Escape - Close dialogs
    if (e.key === 'Escape') {
        document.querySelectorAll('.dialog').forEach(d => {
            if (d.id !== 'loading-dialog') {
                d.remove();
            }
        });
    }
});