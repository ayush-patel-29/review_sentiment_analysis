// Sentiment Analysis Web App JavaScript
class SentimentAnalyzer {
    constructor() {
        this.init();
    }

    init() {
        // Get DOM elements
        this.form = document.getElementById('sentimentForm');
        this.textArea = document.getElementById('reviewText');
        this.batchTextArea = document.getElementById('batchTexts');
        this.analyzeBtn = document.getElementById('analyzeBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.charCount = document.getElementById('charCount');
        this.batchCharCount = document.getElementById('batchCharCount');
        this.lineCount = document.getElementById('lineCount');
        this.loadingSpinner = document.getElementById('loadingSpinner');
        this.results = document.getElementById('results');
        this.batchResults = document.getElementById('batchResults');
        this.errorMessage = document.getElementById('errorMessage');
        this.exampleCards = document.querySelectorAll('.example-card');
        
        // Mode elements
        this.singleModeBtn = document.getElementById('singleModeBtn');
        this.batchModeBtn = document.getElementById('batchModeBtn');
        this.singleSection = document.getElementById('singleAnalysisSection');
        this.batchSection = document.getElementById('batchAnalysisSection');
        
        this.currentMode = 'single';

        // Bind event listeners
        this.bindEvents();
        
        // Initialize character counters
        this.updateCharCount();
        this.updateBatchInfo();
    }

    bindEvents() {
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Clear button
        this.clearBtn.addEventListener('click', () => this.clearForm());
        
        // Character counters
        this.textArea.addEventListener('input', () => this.updateCharCount());
        this.batchTextArea.addEventListener('input', () => this.updateBatchInfo());
        
        // Mode switching
        this.singleModeBtn.addEventListener('click', () => this.switchMode('single'));
        this.batchModeBtn.addEventListener('click', () => this.switchMode('batch'));
        
        // Example cards
        this.exampleCards.forEach(card => {
            card.addEventListener('click', () => this.loadExample(card));
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.handleSubmit(e);
            }
            if (e.ctrlKey && e.key === 'l') {
                e.preventDefault();
                this.clearForm();
            }
        });
    }

    updateCharCount() {
        const count = this.textArea.value.length;
        this.charCount.textContent = count.toLocaleString();
        
        // Update color based on length
        if (count > 1000) {
            this.charCount.style.color = '#ff1744';
        } else if (count > 500) {
            this.charCount.style.color = '#ffa000';
        } else {
            this.charCount.style.color = '#b8bcc8';
        }
    }

    updateBatchInfo() {
        const text = this.batchTextArea.value;
        const charCount = text.length;
        const lines = text.split('\n').filter(line => line.trim().length > 0);
        const lineCount = lines.length;
        
        this.batchCharCount.textContent = charCount.toLocaleString();
        this.lineCount.textContent = lineCount;
        
        // Update colors
        if (lineCount > 100) {
            this.lineCount.style.color = '#ff1744';
        } else if (lineCount > 50) {
            this.lineCount.style.color = '#ffa000';
        } else {
            this.lineCount.style.color = '#b8bcc8';
        }
    }

    switchMode(mode) {
        this.currentMode = mode;
        
        // Update button states
        if (mode === 'single') {
            this.singleModeBtn.classList.add('active');
            this.batchModeBtn.classList.remove('active');
            this.singleSection.style.display = 'block';
            this.batchSection.style.display = 'none';
            this.analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Sentiment';
        } else {
            this.batchModeBtn.classList.add('active');
            this.singleModeBtn.classList.remove('active');
            this.singleSection.style.display = 'none';
            this.batchSection.style.display = 'block';
            this.analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Batch Analyze';
        }
        
        // Clear previous results
        this.results.style.display = 'none';
        this.batchResults.style.display = 'none';
        this.hideError();
    }

    async handleSubmit(e) {
        e.preventDefault();
        
        if (this.currentMode === 'single') {
            const text = this.textArea.value.trim();
            if (!text) {
                this.showError('Please enter some text to analyze.');
                return;
            }

            if (text.length < 3) {
                this.showError('Text must be at least 3 characters long.');
                return;
            }

            if (text.length > 5000) {
                this.showError('Text must be less than 5000 characters.');
                return;
            }

            try {
                await this.analyzeSentiment(text);
            } catch (error) {
                console.error('Analysis error:', error);
                this.showError('Failed to analyze sentiment. Please try again.');
            }
        } else {
            // Batch mode
            const batchText = this.batchTextArea.value.trim();
            if (!batchText) {
                this.showError('Please enter texts to analyze (one per line).');
                return;
            }

            const texts = batchText.split('\n')
                .map(line => line.trim())
                .filter(line => line.length > 0);

            if (texts.length === 0) {
                this.showError('Please enter at least one text to analyze.');
                return;
            }

            if (texts.length > 100) {
                this.showError('Maximum 100 texts allowed for batch analysis.');
                return;
            }

            for (let i = 0; i < texts.length; i++) {
                if (texts[i].length > 5000) {
                    this.showError(`Text ${i + 1} is too long. Maximum 5000 characters per text.`);
                    return;
                }
            }

            try {
                await this.analyzeBatchSentiment(texts);
            } catch (error) {
                console.error('Batch analysis error:', error);
                this.showError('Failed to analyze batch sentiment. Please try again.');
            }
        }
    }

    async analyzeSentiment(text) {
        const startTime = performance.now();
        
        // Show loading state
        this.setLoadingState(true);
        
        try {
            const response = await fetch('/api/v1/sentiment/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: text })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            const endTime = performance.now();
            const analysisTime = Math.round(endTime - startTime);

            this.displayResults(result, analysisTime, text.length);
        } catch (error) {
            console.error('API Error:', error);
            this.showError(`Analysis failed: ${error.message}`);
        } finally {
            this.setLoadingState(false);
        }
    }

    async analyzeBatchSentiment(texts) {
        const startTime = performance.now();
        
        // Show loading state
        this.setLoadingState(true);
        
        try {
            const response = await fetch('/api/v1/sentiment/analyze/batch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ texts: texts })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            const endTime = performance.now();
            const analysisTime = Math.round(endTime - startTime);

            this.displayBatchResults(result, analysisTime);
        } catch (error) {
            console.error('Batch API Error:', error);
            this.showError(`Batch analysis failed: ${error.message}`);
        } finally {
            this.setLoadingState(false);
        }
    }

    displayResults(data, analysisTime, textLength) {
        // Hide error message if visible
        this.hideError();

        // Extract sentiment data
        const sentiment = data.sentiment || data.predicted_sentiment;
        const confidence = data.confidence || 0;
        const scores = data.scores || {};

        // Update sentiment badge
        const sentimentBadge = document.getElementById('sentimentBadge');
        const sentimentLabel = document.getElementById('sentimentLabel');
        
        sentimentLabel.textContent = sentiment;
        sentimentBadge.className = `sentiment-badge ${sentiment.toLowerCase()}`;

        // Update confidence score
        document.getElementById('confidenceScore').textContent = `${(confidence * 100).toFixed(1)}%`;

        // Update detailed scores (no neutral for binary classification)
        this.updateScoreBar('positive', scores.positive || scores.pos || 0);
        this.updateScoreBar('negative', scores.negative || scores.neg || 0);

        // Update metadata
        document.getElementById('analysisTime').textContent = analysisTime;
        document.getElementById('textLength').textContent = textLength.toLocaleString();

        // Show results with animation
        this.results.style.display = 'block';
        setTimeout(() => {
            this.results.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }

    updateScoreBar(type, score) {
        const percentage = (score * 100).toFixed(1);
        const scoreElement = document.getElementById(`${type}Score`);
        const fillElement = document.getElementById(`${type}Fill`);
        
        scoreElement.textContent = `${percentage}%`;
        
        // Animate the bar fill
        setTimeout(() => {
            fillElement.style.width = `${percentage}%`;
        }, 100);
    }

    setLoadingState(isLoading) {
        if (isLoading) {
            this.loadingSpinner.style.display = 'block';
            this.results.style.display = 'none';
            this.hideError();
            this.analyzeBtn.disabled = true;
            this.analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        } else {
            this.loadingSpinner.style.display = 'none';
            this.analyzeBtn.disabled = false;
            this.analyzeBtn.innerHTML = '<i class="fas fa-search"></i> Analyze Sentiment';
        }
    }

    showError(message) {
        const errorText = document.getElementById('errorText');
        errorText.textContent = message;
        this.errorMessage.style.display = 'block';
        this.results.style.display = 'none';
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    hideError() {
        this.errorMessage.style.display = 'none';
    }

    displayBatchResults(data, analysisTime) {
        // Hide error message if visible
        this.hideError();

        const results = data.results || [];
        let positiveCount = 0;
        let negativeCount = 0;

        // Count sentiments
        results.forEach(result => {
            if (result.sentiment === 'positive') positiveCount++;
            if (result.sentiment === 'negative') negativeCount++;
        });

        // Update summary
        document.getElementById('totalTexts').textContent = results.length;
        document.getElementById('positiveCount').textContent = positiveCount;
        document.getElementById('negativeCount').textContent = negativeCount;

        // Build results list
        const resultsList = document.getElementById('batchResultsList');
        resultsList.innerHTML = '';

        results.forEach((result, index) => {
            const item = document.createElement('div');
            item.className = 'batch-result-item';
            item.innerHTML = `
                <div class="batch-result-sentiment ${result.sentiment}">
                    ${result.sentiment}
                </div>
                <div class="batch-result-text">
                    ${result.text.length > 100 ? result.text.substring(0, 100) + '...' : result.text}
                </div>
            `;
            resultsList.appendChild(item);
        });

        // Show batch results
        this.batchResults.style.display = 'block';
        setTimeout(() => {
            this.batchResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }, 100);
    }

    clearForm() {
        if (this.currentMode === 'single') {
            this.textArea.value = '';
            this.updateCharCount();
            this.textArea.focus();
        } else {
            this.batchTextArea.value = '';
            this.updateBatchInfo();
            this.batchTextArea.focus();
        }
        
        this.results.style.display = 'none';
        this.batchResults.style.display = 'none';
        this.hideError();
        
        // Reset score bars
        document.querySelectorAll('.score-fill').forEach(fill => {
            fill.style.width = '0%';
        });
    }

    loadExample(card) {
        const exampleText = card.getAttribute('data-text');
        this.textArea.value = exampleText;
        this.updateCharCount();
        this.textArea.focus();
        
        // Add visual feedback
        card.style.transform = 'scale(0.98)';
        setTimeout(() => {
            card.style.transform = '';
        }, 150);
    }

    // Utility method to debounce function calls
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
}

// Utility functions for better UX
const Utils = {
    // Format numbers with commas
    formatNumber: (num) => {
        return num.toLocaleString();
    },

    // Copy text to clipboard
    copyToClipboard: async (text) => {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (err) {
            console.error('Failed to copy text:', err);
            return false;
        }
    },

    // Show toast notification
    showToast: (message, type = 'info') => {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        Object.assign(toast.style, {
            position: 'fixed',
            top: '20px',
            right: '20px',
            padding: '12px 24px',
            backgroundColor: type === 'error' ? '#ff4b2b' : '#4facfe',
            color: 'white',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
            zIndex: '10000',
            fontSize: '14px',
            fontWeight: '500',
            opacity: '0',
            transform: 'translateX(100%)',
            transition: 'all 0.3s ease'
        });

        document.body.appendChild(toast);

        // Animate in
        setTimeout(() => {
            toast.style.opacity = '1';
            toast.style.transform = 'translateX(0)';
        }, 10);

        // Auto remove
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 300);
        }, 3000);
    }
};

// Service Worker registration for offline support (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(registration => {
                console.log('SW registered: ', registration);
            })
            .catch(registrationError => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Initialize the sentiment analyzer
    window.sentimentApp = new SentimentAnalyzer();
    
    // Add keyboard shortcuts info to help
    const helpInfo = document.createElement('div');
    helpInfo.className = 'help-info';
    helpInfo.innerHTML = `
        <small style="color: #666; font-size: 0.8rem; text-align: center; display: block; margin-top: 10px;">
            💡 Tip: Use <kbd>Ctrl+Enter</kbd> to analyze, <kbd>Ctrl+L</kbd> to clear
        </small>
    `;
    
    const form = document.getElementById('sentimentForm');
    form.appendChild(helpInfo);
    
    // Add CSS for kbd elements
    const style = document.createElement('style');
    style.textContent = `
        kbd {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 3px;
            padding: 1px 4px;
            font-size: 0.75rem;
            font-family: monospace;
        }
    `;
    document.head.appendChild(style);

    console.log('🎉 Sentiment Analysis Web App initialized successfully!');
});
