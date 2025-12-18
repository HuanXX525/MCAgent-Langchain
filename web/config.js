const API_BASE = 'http://localhost:8000/api';

function setNestedValue(obj, path, value) {
    const keys = path.split('.');
    const lastKey = keys.pop();
    const target = keys.reduce((o, k) => o[k] = o[k] || {}, obj);
    target[lastKey] = value;
}

function getNestedValue(obj, path) {
    return path.split('.').reduce((o, k) => (o || {})[k], obj);
}

function showStatus(message, isError = false) {
    const statusDiv = document.getElementById('status');
    statusDiv.textContent = message;
    statusDiv.className = `status ${isError ? 'error' : 'success'} show`;
    
    setTimeout(() => {
        statusDiv.classList.remove('show');
    }, 3000);
}

async function loadConfig() {
    try {
        const response = await fetch(`${API_BASE}/config`);
        if (!response.ok) {
            throw new Error('加载配置失败');
        }
        
        const config = await response.json();
        
        document.querySelectorAll('input, select').forEach(element => {
            const name = element.getAttribute('name');
            if (!name) return;
            
            const value = getNestedValue(config, name);
            
            if (element.type === 'checkbox') {
                element.checked = value === true;
            } else if (value !== undefined) {
                element.value = value;
            }
        });
        
        showStatus('✅ 配置加载成功！');
    } catch (error) {
        showStatus(`❌ 加载失败: ${error.message}`, true);
        console.error('加载配置错误:', error);
    }
}

async function saveConfig(event) {
    event.preventDefault();
    
    const config = {};
    
    document.querySelectorAll('input, select').forEach(element => {
        const name = element.getAttribute('name');
        if (!name) return;
        
        let value;
        if (element.type === 'checkbox') {
            value = element.checked;
        } else if (element.type === 'number') {
            value = element.value ? parseFloat(element.value) : undefined;
        } else {
            value = element.value;
        }
        
        if (value !== undefined && value !== '') {
            setNestedValue(config, name, value);
        }
    });
    
    const apiUrl = `http://${config.backend?.host || 'localhost'}:${config.backend?.port || 8000}/api`;
    config.backend.api_url = apiUrl;
    config.backend.ws_url = `ws://${config.backend?.host || 'localhost'}:${config.backend?.port || 8000}/ws`;
    
    try {
        const response = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            throw new Error('保存配置失败');
        }
        
        showStatus('✅ 配置保存成功！');
    } catch (error) {
        showStatus(`❌ 保存失败: ${error.message}`, true);
        console.error('保存配置错误:', error);
    }
}

document.getElementById('configForm').addEventListener('submit', saveConfig);

window.addEventListener('load', loadConfig);
