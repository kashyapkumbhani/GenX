/**
 * Content Editor - Visual HTML Content Editor
 * Provides double-click-to-edit functionality for generated HTML pages
 */

class ContentEditor {
    constructor() {
        this.isEditMode = false;
        this.currentVersion = null;
        this.currentPage = null;
        this.editableElements = [];
        this.originalContent = new Map();
        this.unsavedChanges = false;
        
        this.init();
    }
    
    init() {
        // Check if we're in edit mode
        const urlParams = new URLSearchParams(window.location.search);
        this.isEditMode = urlParams.get('edit') === 'true';
        
        if (this.isEditMode) {
            this.extractVersionAndPage();
            this.setupEditMode();
        }
    }
    
    extractVersionAndPage() {
        // Extract version and page from URL path
        const path = window.location.pathname;
        const matches = path.match(/\/output\/(\d+)\/(.+)/);
        
        if (matches) {
            this.currentVersion = parseInt(matches[1]);
            this.currentPage = matches[2];
        }
    }
    
    setupEditMode() {
        // Add editor styles
        this.injectEditorStyles();
        
        // Create editor toolbar
        this.createEditorToolbar();
        
        // Make elements editable
        this.makeElementsEditable();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Show edit mode indicator
        this.showEditModeIndicator();
    }
    
    injectEditorStyles() {
        const style = document.createElement('style');
        style.textContent = `
            /* Content Editor Styles */
            .content-editor-toolbar {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #2c3e50;
                color: white;
                padding: 10px 20px;
                z-index: 10000;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                flex-wrap: wrap;
                gap: 15px;
            }
            
            .content-editor-toolbar h3 {
                margin: 0;
                font-size: 16px;
                color: #ecf0f1;
            }
            
            .content-editor-page-selector {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            
            .content-editor-page-selector label {
                font-size: 14px;
                font-weight: 500;
            }
            
            .content-editor-select {
                padding: 5px 10px;
                border: 1px solid #34495e;
                border-radius: 4px;
                background: #34495e;
                color: white;
                font-size: 14px;
                min-width: 200px;
            }
            
            .content-editor-select:focus {
                outline: none;
                border-color: #3498db;
            }
            
            .content-editor-actions {
                display: flex;
                gap: 10px;
                align-items: center;
            }
            
            .content-editor-btn {
                background: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
                transition: background-color 0.2s;
            }
            
            .content-editor-btn:hover {
                background: #2980b9;
            }
            
            .content-editor-btn.save {
                background: #27ae60;
            }
            
            .content-editor-btn.save:hover {
                background: #229954;
            }
            
            .content-editor-btn.exit {
                background: #e74c3c;
            }
            
            .content-editor-btn.exit:hover {
                background: #c0392b;
            }
            
            .content-editor-btn:disabled {
                background: #95a5a6;
                cursor: not-allowed;
            }
            
            .content-editor-status {
                font-size: 14px;
                color: #bdc3c7;
            }
            
            .content-editor-status.unsaved {
                color: #f39c12;
            }
            
            /* Only apply editable styles when NOT editing and NOT buttons */
            .content-editable:not(.editing):not(button):not(.btn):not([class*="btn"]):not(a[class*="btn"]) {
                position: relative;
                transition: all 0.2s ease;
                border: 2px solid transparent;
                border-radius: 4px;
                padding: 4px;
                margin: 2px;
            }
            
            /* Buttons get absolutely NO styling when editable */
            .content-editable.btn,
            .content-editable[class*="btn"],
            button.content-editable,
            a.content-editable[class*="btn"] {
                /* Completely empty - no styles at all */
            }
            
            /* Links that are NOT buttons */
            a.content-editable:not([class*="btn"]):not(.editing) {
                text-decoration: none !important;
                border: 2px solid transparent;
                border-radius: 4px;
                padding: 4px;
                margin: 2px;
                transition: all 0.2s ease;
            }
            
            /* Hover effects only for non-buttons and only when not editing */
            .content-editable:not(.editing):not(button):not(.btn):not([class*="btn"]):not(a[class*="btn"]):hover,
            a.content-editable:not([class*="btn"]):not(.editing):hover {
                border-color: #3498db;
                background-color: rgba(52, 152, 219, 0.1);
            }
            
            .content-editable.editing {
                border-color: #27ae60;
                background-color: rgba(39, 174, 96, 0.1);
                outline: none;
            }
            
            .content-editable::before {
                content: '✏️ Double-click to edit';
                position: absolute;
                top: -25px;
                left: 0;
                background: #2c3e50;
                color: white;
                padding: 2px 8px;
                border-radius: 4px;
                font-size: 12px;
                opacity: 0;
                transition: opacity 0.2s;
                pointer-events: none;
                white-space: nowrap;
                z-index: 1000;
            }
            
            .content-editable:hover::before {
                opacity: 1;
            }
            
            .content-editable.editing::before {
                content: '✅ Editing - Press Enter to save, Esc to cancel';
                background: #27ae60;
            }
            
            /* Adjust body padding for toolbar */
            body.content-editor-active {
                padding-top: 60px !important;
            }
            
            /* Modal styles */
            .content-editor-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 10001;
            }
            
            .content-editor-modal-content {
                background: white;
                padding: 20px;
                border-radius: 8px;
                max-width: 500px;
                width: 90%;
            }
            
            .content-editor-modal h4 {
                margin-top: 0;
                color: #2c3e50;
            }
            
            .content-editor-modal-actions {
                display: flex;
                gap: 10px;
                justify-content: flex-end;
                margin-top: 20px;
            }
        `;
        document.head.appendChild(style);
    }
    
    createEditorToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'content-editor-toolbar';
        toolbar.innerHTML = `
            <div>
                <h3>Content Editor</h3>
                <span class="content-editor-status" id="editor-status">Ready to edit</span>
            </div>
            <div class="content-editor-page-selector">
                <label for="page-selector">Page:</label>
                <select id="page-selector" class="content-editor-select">
                    <option value="">Loading pages...</option>
                </select>
            </div>
            <div class="content-editor-actions">
                <button class="content-editor-btn save" id="save-all-btn" disabled>Save All Changes</button>
                <button class="content-editor-btn" id="view-changes-btn">View Changes</button>
                <button class="content-editor-btn exit" id="exit-editor-btn">Exit Editor</button>
            </div>
        `;
        
        document.body.insertBefore(toolbar, document.body.firstChild);
        document.body.classList.add('content-editor-active');
        
        // Load available pages
        this.loadAvailablePages();
    }
    
    makeElementsEditable() {
        // Find elements that should be editable
        const selectors = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'button', 'a', '.btn', '.button', '.editable'];
        const elements = document.querySelectorAll(selectors.join(', '));
        
        elements.forEach((element, index) => {
            // Skip if element is inside toolbar or has no text content
            if (element.closest('.content-editor-toolbar') || !element.textContent.trim()) {
                return;
            }
            
            const editableId = `editable-${index}`;
            element.setAttribute('data-editable-id', editableId);
            element.classList.add('content-editable');
            
            // Store original content
            this.originalContent.set(editableId, element.textContent.trim());
            
            this.editableElements.push({
                id: editableId,
                element: element,
                originalContent: element.textContent.trim()
            });
        });
    }
    
    setupEventListeners() {
        // Prevent default click behavior on editable elements (like links/buttons)
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('content-editable')) {
                e.preventDefault();
                e.stopPropagation();
            }
        });
        
        // Double-click to edit
        document.addEventListener('dblclick', (e) => {
            if (e.target.classList.contains('content-editable')) {
                e.preventDefault();
                e.stopPropagation();
                this.startEditing(e.target);
            }
        });
        
        // Toolbar buttons
        document.getElementById('save-all-btn').addEventListener('click', () => {
            this.saveAllChanges();
        });
        
        document.getElementById('view-changes-btn').addEventListener('click', () => {
            this.viewChanges();
        });
        
        document.getElementById('exit-editor-btn').addEventListener('click', () => {
            this.exitEditor();
        });
        
        // Page selector change
        document.getElementById('page-selector').addEventListener('change', (e) => {
            this.switchPage(e.target.value);
        });
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 's') {
                e.preventDefault();
                this.saveAllChanges();
            }
            
            if (e.key === 'Escape') {
                this.cancelEditing();
            }
        });
        
        // Warn before leaving with unsaved changes
        window.addEventListener('beforeunload', (e) => {
            if (this.unsavedChanges) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            }
        });
    }
    
    startEditing(element) {
        // Cancel any existing editing
        this.cancelEditing();
        
        const editableId = element.getAttribute('data-editable-id');
        const originalContent = element.textContent.trim();
        
        // Make element contenteditable
        element.contentEditable = true;
        element.classList.add('editing');
        element.focus();
        
        // Select all text
        const range = document.createRange();
        range.selectNodeContents(element);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        
        // Handle Enter and Escape keys
        const handleKeydown = (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.finishEditing(element, editableId);
            } else if (e.key === 'Escape') {
                e.preventDefault();
                element.textContent = originalContent;
                this.cancelEditing();
            }
        };
        
        const handleBlur = () => {
            this.finishEditing(element, editableId);
        };
        
        element.addEventListener('keydown', handleKeydown);
        element.addEventListener('blur', handleBlur);
        
        // Store event listeners for cleanup
        element._editHandlers = { handleKeydown, handleBlur };
        
        this.updateStatus('Editing...');
    }
    
    finishEditing(element, editableId) {
        const newContent = element.textContent.trim();
        const originalContent = this.originalContent.get(editableId);
        
        // Clean up
        element.contentEditable = false;
        element.classList.remove('editing');
        
        // Remove event listeners
        if (element._editHandlers) {
            element.removeEventListener('keydown', element._editHandlers.handleKeydown);
            element.removeEventListener('blur', element._editHandlers.handleBlur);
            delete element._editHandlers;
        }
        
        // Check if content changed
        if (newContent !== originalContent) {
            this.markAsChanged(editableId, newContent);
        }
        
        this.updateStatus('Ready to edit');
    }
    
    cancelEditing() {
        const editingElement = document.querySelector('.content-editable.editing');
        if (editingElement) {
            const editableId = editingElement.getAttribute('data-editable-id');
            const originalContent = this.originalContent.get(editableId);
            
            editingElement.textContent = originalContent;
            editingElement.contentEditable = false;
            editingElement.classList.remove('editing');
            
            // Remove event listeners
            if (editingElement._editHandlers) {
                editingElement.removeEventListener('keydown', editingElement._editHandlers.handleKeydown);
                editingElement.removeEventListener('blur', editingElement._editHandlers.handleBlur);
                delete editingElement._editHandlers;
            }
        }
        
        this.updateStatus('Ready to edit');
    }
    
    markAsChanged(editableId, newContent) {
        // Find the editable element data
        const editableData = this.editableElements.find(item => item.id === editableId);
        if (editableData) {
            editableData.changed = true;
            editableData.newContent = newContent;
        }
        
        this.unsavedChanges = true;
        this.updateSaveButton();
        this.updateStatus('Unsaved changes', true);
    }
    
    updateSaveButton() {
        const saveBtn = document.getElementById('save-all-btn');
        saveBtn.disabled = !this.unsavedChanges;
    }
    
    updateStatus(message, isUnsaved = false) {
        const status = document.getElementById('editor-status');
        status.textContent = message;
        status.className = `content-editor-status ${isUnsaved ? 'unsaved' : ''}`;
    }
    
    async loadAvailablePages() {
        try {
            const response = await fetch(`/api/pages/${this.currentVersion}`);
            const data = await response.json();
            
            if (data.success) {
                const selector = document.getElementById('page-selector');
                selector.innerHTML = '';
                
                data.pages.forEach(page => {
                    const option = document.createElement('option');
                    option.value = page.filename;
                    option.textContent = page.friendly_name;
                    
                    // Mark current page as selected
                    if (page.filename === this.currentPage) {
                        option.selected = true;
                    }
                    
                    selector.appendChild(option);
                });
            } else {
                console.error('Failed to load pages:', data.error);
            }
        } catch (error) {
            console.error('Error loading pages:', error);
        }
    }
    
    async switchPage(newPage) {
        if (!newPage || newPage === this.currentPage) return;
        
        // Check for unsaved changes
        if (this.unsavedChanges) {
            const confirmed = confirm('You have unsaved changes. Do you want to save them before switching pages?');
            if (confirmed) {
                await this.saveAllChanges();
            }
        }
        
        // Navigate to the new page
        const url = new URL(window.location);
        url.pathname = `/output/${this.currentVersion}/${newPage}`;
        url.searchParams.set('edit', 'true');
        window.location.href = url.toString();
    }

    async saveAllChanges() {
        if (!this.unsavedChanges) return;
        
        const saveBtn = document.getElementById('save-all-btn');
        saveBtn.disabled = true;
        saveBtn.textContent = 'Saving...';
        
        this.updateStatus('Saving changes...');
        
        try {
            // Get current page content
            const response = await fetch(`/api/content/${this.currentVersion}/${this.currentPage}`);
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error);
            }
            
            let content = data.content;
            
            // Apply all changes to the content
            const changedElements = this.editableElements.filter(item => item.changed);
            
            console.log('Changed elements:', changedElements);
            
            if (changedElements.length === 0) {
                this.updateStatus('No changes to save');
                return;
            }
            
            // Parse the content once
            const parser = new DOMParser();
            const doc = parser.parseFromString(content, 'text/html');
            
            // Apply all changes to the parsed document
            for (const item of changedElements) {
                // Find the element by its original content and tag type
                const originalElement = item.element;
                const tagName = originalElement.tagName.toLowerCase();
                const originalText = item.originalContent;
                
                console.log(`Looking for ${tagName} with text: "${originalText}"`);
                
                // Find matching element in the parsed document
                const elements = doc.querySelectorAll(tagName);
                let targetElement = null;
                
                for (const el of elements) {
                    if (el.textContent.trim() === originalText) {
                        targetElement = el;
                        break;
                    }
                }
                
                if (targetElement) {
                    console.log(`Updating element from "${originalText}" to "${item.newContent}"`);
                    targetElement.textContent = item.newContent;
                } else {
                    console.warn(`Could not find element with text: "${originalText}"`);
                }
            }
            
            // Get the complete HTML content with proper DOCTYPE
            const doctype = '<!DOCTYPE html>';
            const htmlContent = doc.documentElement.outerHTML;
            content = doctype + '\n' + htmlContent;
            
            console.log('Sending content to server, length:', content.length);
            
            // Save the updated content
            const saveResponse = await fetch(`/api/content/${this.currentVersion}/${this.currentPage}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ content: content })
            });
            
            const saveData = await saveResponse.json();
            
            if (saveData.success) {
                // Update original content and reset changed flags
                changedElements.forEach(item => {
                    this.originalContent.set(item.id, item.newContent);
                    item.originalContent = item.newContent;
                    item.changed = false;
                    delete item.newContent;
                });
                
                this.unsavedChanges = false;
                this.updateStatus('All changes saved successfully');
                
                // Show success message
                this.showMessage('Changes saved successfully!', 'success');
                
                // Refresh the page to show updated content
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            } else {
                throw new Error(saveData.error);
            }
        } catch (error) {
            console.error('Save error:', error);
            this.updateStatus('Error saving changes', true);
            this.showMessage(`Error saving changes: ${error.message}`, 'error');
        } finally {
            saveBtn.disabled = false;
            saveBtn.textContent = 'Save All Changes';
            this.updateSaveButton();
        }
    }
    
    viewChanges() {
        // Get current URL without edit parameter
        const url = new URL(window.location);
        url.searchParams.delete('edit');
        
        // Open in new tab
        window.open(url.toString(), '_blank');
    }

    togglePreview() {
        const editableElements = document.querySelectorAll('.content-editable');
        const previewBtn = document.getElementById('preview-btn');
        const toolbar = document.querySelector('.content-editor-toolbar');
        
        if (previewBtn.textContent === 'Preview') {
            // Hide editor indicators
            editableElements.forEach(el => {
                el.style.border = 'none';
                el.style.backgroundColor = 'transparent';
                el.classList.remove('content-editable');
            });
            
            // Keep toolbar visible but modify it for preview mode
            toolbar.style.backgroundColor = 'rgba(44, 62, 80, 0.9)';
            
            // Hide edit-specific buttons
            document.getElementById('save-all-btn').style.display = 'none';
            document.getElementById('view-changes-btn').style.display = 'none';
            
            // Adjust body padding
            document.body.style.paddingTop = '60px';
            
            previewBtn.textContent = 'Exit Preview';
        } else {
            // Show editor indicators
            editableElements.forEach(el => {
                el.style.border = '';
                el.style.backgroundColor = '';
                el.classList.add('content-editable');
            });
            
            // Restore toolbar
            toolbar.style.backgroundColor = '#2c3e50';
            
            // Show edit-specific buttons
            document.getElementById('save-all-btn').style.display = 'inline-block';
            document.getElementById('view-changes-btn').style.display = 'inline-block';
            
            // Restore body padding
            document.body.style.paddingTop = '60px';
            
            previewBtn.textContent = 'Preview';
        }
    }
    
    exitEditor() {
        if (this.unsavedChanges) {
            this.showConfirmDialog(
                'Unsaved Changes',
                'You have unsaved changes. Are you sure you want to exit?',
                () => {
                    this.doExitEditor();
                }
            );
        } else {
            this.doExitEditor();
        }
    }
    
    doExitEditor() {
        // Remove edit parameter from URL
        const url = new URL(window.location);
        url.searchParams.delete('edit');
        window.location.href = url.toString();
    }
    
    showEditModeIndicator() {
        // Add a subtle indicator that we're in edit mode
        const indicator = document.createElement('div');
        indicator.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 9999;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        `;
        indicator.textContent = '✏️ Edit Mode Active';
        document.body.appendChild(indicator);
    }
    
    showMessage(message, type = 'info') {
        const messageEl = document.createElement('div');
        messageEl.style.cssText = `
            position: fixed;
            top: 70px;
            right: 20px;
            background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
            color: white;
            padding: 12px 20px;
            border-radius: 4px;
            z-index: 10000;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            max-width: 300px;
        `;
        messageEl.textContent = message;
        
        document.body.appendChild(messageEl);
        
        setTimeout(() => {
            messageEl.remove();
        }, 3000);
    }
    
    showConfirmDialog(title, message, onConfirm) {
        const modal = document.createElement('div');
        modal.className = 'content-editor-modal';
        modal.innerHTML = `
            <div class="content-editor-modal-content">
                <h4>${title}</h4>
                <p>${message}</p>
                <div class="content-editor-modal-actions">
                    <button class="content-editor-btn" id="modal-cancel">Cancel</button>
                    <button class="content-editor-btn exit" id="modal-confirm">Confirm</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('modal-cancel').addEventListener('click', () => {
            modal.remove();
        });
        
        document.getElementById('modal-confirm').addEventListener('click', () => {
            modal.remove();
            onConfirm();
        });
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });
    }
}

// Initialize the content editor when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ContentEditor();
});