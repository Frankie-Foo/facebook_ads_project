// 聊天应用管理器
const ChatManager = {
    messageInput: null,
    sendButton: null,
    messageList: null,
    
    init() {
        // 获取DOM元素
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.messageList = document.getElementById('chatMessages');
        
        // 绑定事件
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendMessage();
            }
        });
        
        // 加载历史记录
        this.loadHistory();
    },
    
    // 添加消息到界面
    appendMessage(message) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${message.is_user ? 'user' : 'ai'}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = message.content;
        
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date(message.timestamp).toLocaleString();
        
        messageDiv.appendChild(contentDiv);
        messageDiv.appendChild(timeDiv);
        this.messageList.appendChild(messageDiv);
        
        // 滚动到底部
        this.messageList.scrollTop = this.messageList.scrollHeight;
    },
    
    // 发送消息
    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        // 禁用输入和按钮
        this.messageInput.disabled = true;
        this.sendButton.disabled = true;
        
        try {
            // 立即显示用户消息
            const userMessage = {
                content: message,
                timestamp: new Date().toISOString(),
                is_user: true
            };
            this.appendMessage(userMessage);
            
            // 清空输入框
            this.messageInput.value = '';
            
            // 发送到服务器
            const response = await fetch('/api/chat/send', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                credentials: 'same-origin',
                body: JSON.stringify({ message })
            });
            
            const data = await response.json();
            
            if (data.success && data.message) {
                this.appendMessage(data.message);
            } else {
                throw new Error(data.error || '发送失败');
            }
            
        } catch (error) {
            console.error('发送消息失败:', error);
            this.appendMessage({
                content: '发送消息失败，请重试',
                timestamp: new Date().toISOString(),
                is_user: false
            });
        } finally {
            // 恢复输入和按钮
            this.messageInput.disabled = false;
            this.sendButton.disabled = false;
            this.messageInput.focus();
        }
    },
    
    // 加载历史记录
    async loadHistory() {
        try {
            const response = await fetch('/api/chat/history', {
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            if (data.success && data.history) {
                data.history.forEach(msg => this.appendMessage(msg));
            }
        } catch (error) {
            console.error('加载历史记录失败:', error);
        }
    }
};

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => ChatManager.init()); 