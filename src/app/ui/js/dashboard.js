class FileUploadHandler {
    constructor() {
        this.allowedTypes = {
            text: ['txt', 'md'],
            pdf: ['pdf']
        };
        this.maxFileSize = 100 * 1024 * 1024;
    }

    validateFile(file) {
        const errors = [];
        
        if (file.size > this.maxFileSize) {
            errors.push('File size must be less than 100MB');
        }
        
        const extension = file.name.split('.').pop().toLowerCase();
        const isValidType = Object.values(this.allowedTypes).some(types => 
            types.includes(extension)
        );
        
        if (!isValidType) {
            errors.push('File type not supported');
        }
        
        return errors;
    }

    getFileType(filename) {
        const extension = filename.split('.').pop().toLowerCase();
        
        for (const [type, extensions] of Object.entries(this.allowedTypes)) {
            if (extensions.includes(extension)) {
                return type;
            }
        }
        
        return 'unknown';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
}

class ConfigManager {
    constructor() {
        this.defaultConfig = {
            prompt: 'Thematic',
            model: 'openai/gpt-4.1-mini'
        };
        this.loadSavedConfig();
    }

    loadSavedConfig() {
        const saved = localStorage.getItem('summarizer_config');
        if (saved) {
            try {
                const config = JSON.parse(saved);
                this.applyConfig(config);
            } catch (error) {
                console.error('Failed to load saved config:', error);
            }
        }
    }

    saveConfig() {
        const config = this.getCurrentConfig();
        localStorage.setItem('summarizer_config', JSON.stringify(config));
    }

    getCurrentConfig() {
        return {
            prompt: document.getElementById('prompt').value,
            model: document.getElementById('model').value
        };
    }

    applyConfig(config) {
        Object.entries(config).forEach(([key, value]) => {
            const element = document.getElementById(key) || document.getElementById(key.replace('_', '-'));
            if (element) {
                element.value = value;
            }
        });
    }

    resetToDefaults() {
        this.applyConfig(this.defaultConfig);
        this.saveConfig();
    }
}

class SummaryManager {
    constructor() {
        this.summaryHistory = this.loadSummaryHistory();
    }

    loadSummaryHistory() {
        const stored = localStorage.getItem('summary_history');
        return stored ? JSON.parse(stored) : [];
    }

    saveSummaryHistory() {
        localStorage.setItem('summary_history', JSON.stringify(this.summaryHistory));
    }

    addSummary(summary, config, filename = null) {
        const entry = {
            id: Date.now(),
            summary,
            config,
            filename,
            timestamp: new Date().toISOString()
        };
        
        this.summaryHistory.unshift(entry);
        
        if (this.summaryHistory.length > 10) {
            this.summaryHistory = this.summaryHistory.slice(0, 10);
        }
        
        this.saveSummaryHistory();
        return entry;
    }

    getSummaryHistory() {
        return this.summaryHistory;
    }

    clearHistory() {
        this.summaryHistory = [];
        this.saveSummaryHistory();
    }
}

class DashboardController {
    constructor() {
        this.fileHandler = new FileUploadHandler();
        this.configManager = new ConfigManager();
        this.summaryManager = new SummaryManager();
        this.currentFile = null;
        this.isProcessing = false;
        this.iconAnimationInterval = null;
    }

    initialize() {
        this.setupEventListeners();
        this.setupScrollHandler();
        this.updateUI();
    }

    setupScrollHandler() {
        const navbar = document.querySelector('.navbar');
        if (!navbar) return;

        let isScrolled = false;
        
        window.addEventListener('scroll', () => {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            if (scrollTop > 20 && !isScrolled) {
                navbar.classList.add('scrolled');
                isScrolled = true;
            } else if (scrollTop <= 20 && isScrolled) {
                navbar.classList.remove('scrolled');
                isScrolled = false;
            }
        });
    }

    startIconAnimation(button) {
        if (!button) return;
        
        const icons = [
            'fas fa-hourglass-start',
            'fas fa-hourglass-half', 
            'fas fa-hourglass-end'
        ];
        
        let currentIndex = 0;
        
        button.innerHTML = `<i class="${icons[currentIndex]} btn-icon-animated"></i>Processing...`;
        
        this.iconAnimationInterval = setInterval(() => {
            currentIndex = (currentIndex + 1) % icons.length;
            const iconElement = button.querySelector('i');
            if (iconElement) {
                iconElement.className = `${icons[currentIndex]} btn-icon-animated`;
            }
        }, 800);
    }

    stopIconAnimation() {
        if (this.iconAnimationInterval) {
            clearInterval(this.iconAnimationInterval);
            this.iconAnimationInterval = null;
        }
    }

    setupEventListeners() {
        const fileInput = document.getElementById('file-upload');
        const textInput = document.getElementById('text-input');
        const dragDropArea = document.getElementById('drag-drop-area');
        const summarizeBtn = document.getElementById('summarize-btn');

        if (fileInput) {
            fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        }

        if (textInput) {
            textInput.addEventListener('input', (e) => this.handleTextInput(e));
        }

        if (dragDropArea) {
            dragDropArea.addEventListener('dragover', (e) => this.handleDragOver(e));
            dragDropArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
            dragDropArea.addEventListener('drop', (e) => this.handleDrop(e));
        }

        if (summarizeBtn) {
            summarizeBtn.addEventListener('click', () => this.handleSummarize());
        }

        const configElements = ['prompt', 'model'];
        configElements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.addEventListener('change', () => this.configManager.saveConfig());
            }
        });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            const errors = this.fileHandler.validateFile(file);
            if (errors.length > 0) {
                event.target.value = '';
                return;
            }
            
            this.currentFile = file;
            this.showFileInfo(file);
            this.updateSummarizeButton();
            
            const textInput = document.getElementById('text-input');
            if (textInput) textInput.value = '';
        }
    }

    handleTextInput(event) {
        const text = event.target.value.trim();
        if (text) {
            this.currentFile = null;
            this.clearFileDisplay();
            
            const fileInput = document.getElementById('file-upload');
            if (fileInput) fileInput.value = '';
        }
        this.updateSummarizeButton();
    }

    handleDragOver(event) {
        event.preventDefault();
        event.currentTarget.classList.add('drag-over');
    }

    handleDragLeave(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drag-over');
    }

    handleDrop(event) {
        event.preventDefault();
        event.currentTarget.classList.remove('drag-over');
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            const fileInput = document.getElementById('file-upload');
            if (fileInput) {
                fileInput.files = files;
                this.handleFileSelect({ target: { files: files } });
            }
        }
    }

    showFileInfo(file) {
        const dragDropArea = document.getElementById('drag-drop-area');
        if (!dragDropArea) return;

        const fileType = this.fileHandler.getFileType(file.name);
        const fileSize = this.fileHandler.formatFileSize(file.size);
        
        const typeIcons = {
            text: '📄',
            pdf: '📄',
            unknown: '📁'
        };

        dragDropArea.innerHTML = `
            <div class="file-info">
                <div class="file-icon">${typeIcons[fileType]}</div>
                <div class="file-details">
                    <p class="file-name">${file.name}</p>
                    <p class="file-size">${fileSize} • ${fileType.toUpperCase()}</p>
                </div>
                <button type="button" onclick="dashboard.clearFile()" class="clear-btn">×</button>
            </div>
        `;
    }

    clearFileDisplay() {
        const dragDropArea = document.getElementById('drag-drop-area');
        if (!dragDropArea) return;

        dragDropArea.innerHTML = `
            <div class="upload-icon"><i class="fas fa-folder-open"></i></div>
                    <p class="upload-text">Drag & drop your file here</p>
                    <p class="upload-or">or</p>
                    <label for="file-upload" class="upload-btn"><i class="fas fa-file-circle-plus"></i> Choose File</label>
                    <p class="upload-info">Supports: <i class="fas fa-file-lines"></i> Text (.txt), <i class="fab fa-markdown"></i> Markdown (.md), <i class="fas fa-file-pdf"></i> PDF (.pdf)</p>
        `;
    }

    clearFile() {
        this.currentFile = null;
        const fileInput = document.getElementById('file-upload');
        if (fileInput) fileInput.value = '';
        this.clearFileDisplay();
        this.updateSummarizeButton();
    }

    updateSummarizeButton() {
        const btn = document.getElementById('summarize-btn');
        const textInput = document.getElementById('text-input');
        
        if (!btn) return;

        const hasFile = this.currentFile !== null;
        const hasText = textInput?.value.trim().length > 0;
        
        btn.disabled = !(hasFile || hasText) || this.isProcessing;
    }

    async handleSummarize() {
        if (this.isProcessing) return;

        const textInput = document.getElementById('text-input');
        const loadingSection = document.getElementById('loading-section');
        const resultsSection = document.getElementById('results-section');
        const summarizeBtn = document.getElementById('summarize-btn');

        try {
            this.isProcessing = true;
            
            if (loadingSection) loadingSection.classList.remove('hidden');
            if (resultsSection) resultsSection.classList.add('hidden');
            if (summarizeBtn) {
                summarizeBtn.disabled = true;
                this.startIconAnimation(summarizeBtn);
            }

            const formData = new FormData();
            
            if (this.currentFile) {
                formData.append('file', this.currentFile);
            } else if (textInput?.value.trim()) {
                formData.append('text', textInput.value.trim());
            } else {
                throw new Error('No content provided for summarization');
            }

            const config = this.configManager.getCurrentConfig();
            Object.entries(config).forEach(([key, value]) => {
                formData.append(key, value);
            });

            const response = await fetch('/api/v1/summarize/', {
                method: 'POST',
                body: formData,
                credentials: 'include',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });

            if (response.ok) {
                const result = await response.json();
                this.displaySummary(result.summary);
                
                this.summaryManager.addSummary(
                    result.summary,
                    config,
                    this.currentFile?.name
                );
                
            } else {
                if (response.status === 401) {
                    return AuthUtils.handleAuthFailure(new Error('Unauthorized access. Please log in again.'));
                }
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
            }

        } catch (error) {
            console.error('Summarization error:', error);
            this.displayError(error.message);
        } finally {
            this.isProcessing = false;
            this.stopIconAnimation();
            
            if (loadingSection) loadingSection.classList.add('hidden');
            if (summarizeBtn) {
                summarizeBtn.disabled = false;
                summarizeBtn.innerHTML = '<i class="fas fa-rocket"></i> Generate Summary';
            }
            this.updateSummarizeButton();
        }
    }

    displaySummary(summary) {
        const resultsSection = document.getElementById('results-section');
        const summaryOutput = document.getElementById('summary-output');
        
        if (summaryOutput) {
            summaryOutput.innerHTML = `
                <div class="summary-text">${this.formatSummaryText(summary)}</div>
                <br />
                <div class="summary-actions">
                    <button onclick="dashboard.copySummary()" class="copy-btn"><i class="fas fa-copy"></i> Copy</button>
                    <button onclick="dashboard.downloadSummary()" class="download-btn"><i class="fas fa-file-arrow-down"></i> Download</button>
                </div>
            `;
        }

        if (resultsSection) {
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    displayError(message) {
        const resultsSection = document.getElementById('results-section');
        const summaryOutput = document.getElementById('summary-output');
        
        if (summaryOutput) {
            summaryOutput.innerHTML = `<div class="error-message"><i class="fas fa-xmark fa-xl" style="color: red;"></i> ${message}</div>`;
        }
        
        if (resultsSection) {
            resultsSection.classList.remove('hidden');
            resultsSection.scrollIntoView({ behavior: 'smooth' });
        }
    }

    formatSummaryText(text) {
        return text
    }

    copySummary() {
        const summaryText = document.querySelector('.summary-text');
        const copyBtn = document.querySelector('.copy-btn');
        
        if (summaryText) {
            const text = summaryText.textContent || summaryText.innerText;
            
            navigator.clipboard.writeText(text).then(() => {
                const originalContent = copyBtn.innerHTML;
                
                copyBtn.innerHTML = '<i class="fas fa-clipboard-check"></i> Copied!';
                copyBtn.style.pointerEvents = 'none';
                
                setTimeout(() => {
                    copyBtn.innerHTML = originalContent;
                    copyBtn.style.pointerEvents = 'auto';
                }, 1000);
            }).catch(err => {
                console.error('Failed to copy text: ', err);
            });
        }
    }

    downloadSummary() {
        const summaryText = document.querySelector('.summary-text');
        if (summaryText) {
            const text = summaryText.textContent || summaryText.innerText;
            const blob = new Blob([text], { type: 'text/plain' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `summary-${new Date().toISOString().split('T')[0]}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
    }

    updateUI() {
        this.updateSummarizeButton();
    }
}

let dashboard;
document.addEventListener('DOMContentLoaded', function() {
    dashboard = new DashboardController();
    dashboard.initialize();
});
