// Adicionar CSS para o toast se ainda não existir
if (!document.getElementById('toast-styles')) {
    const style = document.createElement('style');
    style.id = 'toast-styles';
    style.textContent = `
        .toast-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
            pointer-events: none;
        }
        
        .toast {
            padding: 16px 24px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: 500;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            animation: slideIn 0.3s ease-out forwards;
            pointer-events: auto;
        }
        
        .toast.success {
            background-color: #10b981;
            color: white;
        }
        
        .toast.error {
            background-color: #ef4444;
            color: white;
        }
        
        .toast.info {
            background-color: #3b82f6;
            color: white;
        }
        
        .toast.warning {
            background-color: #f59e0b;
            color: white;
        }
        
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes fadeOut {
            from {
                opacity: 1;
            }
            to {
                opacity: 0;
                transform: translateX(400px);
            }
        }
    `;
    document.head.appendChild(style);
}

function mostrarNotificacao(mensagem, tipo = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${tipo}`;
    toast.textContent = mensagem;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease-out forwards';
        toast.addEventListener('animationend', () => {
            toast.remove();
        });
    }, 3000);
}
