// ==================== OLLAMA 配置 ====================
var OLLAMA_URL = 'http://127.0.0.1:11434/api/chat';
var MODEL_NAME = 'deepseek-r1:1.5b';
var STORAGE_KEY = 'ai_chat_history_' + new Date().getFullYear() + '_' + (new Date().getMonth() + 1);
var chatHistory = [];

// ==================== 对话历史管理 ====================
function loadChatHistory() {
    var saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        try {
            chatHistory = JSON.parse(saved);
            var msgDiv = document.getElementById('aiChatMessages');
            msgDiv.innerHTML = '';

            for (var i = 0; i < chatHistory.length && i < 50; i++) {
                var msg = chatHistory[i];
                if (msg.role === 'assistant') {
                    appendMessage(msg.role, msg.content, false);
                } else {
                    appendMessageWithoutButton(msg.role, msg.content);
                }
            }
        } catch (e) {
            console.error('加载对话历史失败:', e);
            chatHistory = [];
        }
    }
}

function saveChatHistory() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(chatHistory));
    } catch (e) {
        console.error('保存对话历史失败:', e);
    }
}

function clearChatHistory() {
    localStorage.removeItem(STORAGE_KEY);
    chatHistory = [];
    document.getElementById('aiChatMessages').innerHTML = '';
    appendMessage('assistant', '你好！我是 AI 助手，基于 deepseek-r1:1.5b 模型。你可以向我提问测试相关问题，或让我帮你生成测试用例。', true);
}

// ==================== 消息显示 ====================
function appendMessage(role, content, isInit) {
    var msgDiv = document.getElementById('aiChatMessages');
    var msgWrapper = document.createElement('div');
    msgWrapper.className = role === 'user' ? 'user-message' : 'ai-message';

    var avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? '' : 'AI';

    var msgContent = document.createElement('div');
    msgContent.className = 'message-content';
    msgContent.innerHTML = formatContent(content);

    msgWrapper.appendChild(avatar);
    msgWrapper.appendChild(msgContent);
    msgDiv.appendChild(msgWrapper);
    msgDiv.scrollTop = msgDiv.scrollHeight;

    // 只有当 AI 回复中包含测试用例相关内容时，才显示"保存为测试用例"按钮
    if (role === 'assistant' && hasTestCaseContent(content)) {
        var saveBtn = document.createElement('button');
        saveBtn.className = 'btn btn-success btn-sm';
        saveBtn.style.marginTop = '10px';
        saveBtn.textContent = '保存为测试用例';
        saveBtn.onclick = function() { saveAsTestcase(this); };
        msgContent.appendChild(saveBtn);
    }

    if (!isInit) {
        chatHistory.push({ role: role, content: content });
        saveChatHistory();
    }
}

// 判断是否包含测试用例内容
function hasTestCaseContent(content) {
    // 检测关键词：测试用例、步骤、预期、Step、Expect、TC等
    var keywords = [
        '测试用例', '用例名称', '用例标题',
        '步骤', '操作', '预期', '期望', '结果',
        'step', 'expect', 'result', 'tc', 'test case',
        '编号', '用例编号', '测试场景'
    ];

    var lowerContent = content.toLowerCase();
    for (var i = 0; i < keywords.length; i++) {
        if (lowerContent.indexOf(keywords[i].toLowerCase()) !== -1) {
            return true;
        }
    }

    // 或者检测是否有数字编号的步骤（如：1.、2.、步骤1、步骤2）
    if (content.match(/[\d]+[\.、]/) || content.match(/步骤[\d]+/i)) {
        return true;
    }

    return false;
}

function appendMessageWithoutButton(role, content) {
    var msgDiv = document.getElementById('aiChatMessages');
    var msgWrapper = document.createElement('div');
    msgWrapper.className = role === 'user' ? 'user-message' : 'ai-message';

    var avatar = document.createElement('div');
    avatar.className = 'avatar';
    avatar.textContent = role === 'user' ? '我' : 'AI';

    var msgContent = document.createElement('div');
    msgContent.className = 'message-content';
    msgContent.innerHTML = formatContent(content);

    msgWrapper.appendChild(avatar);
    msgWrapper.appendChild(msgContent);
    msgDiv.appendChild(msgWrapper);
    msgDiv.scrollTop = msgDiv.scrollHeight;
}

function formatContent(content) {
    return content
        .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
}

function showTyping() {
    var msgDiv = document.getElementById('aiChatMessages');
    var typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'ai-message';
    typingDiv.innerHTML = '<div class="avatar">AI</div><div class="message-content">正在思考...</div>';
    msgDiv.appendChild(typingDiv);
    msgDiv.scrollTop = msgDiv.scrollHeight;
}

function removeTyping() {
    var typingDiv = document.getElementById('typing-indicator');
    if (typingDiv) {
        typingDiv.remove();
    }
}

// ==================== 发送消息 ====================
function sendMessage() {
    var input = document.getElementById('aiChatInput');
    var message = input.value.trim();

    if (!message) {
        alert('请输入消息！');
        return;
    }

    // 显示用户消息
    appendMessage('user', message);
    input.value = '';

    // 显示加载指示器
    showTyping();

    // 系统提示词 - 极简版（强制格式）
    var systemPrompt = "你是一个专业的软件测试工程师助手。当用户要求生成测试用例时，请严格按照以下格式输出，不要添加任何其他文字：\n\n" +
        "### TC1: [具体用例名称]\n" +
        "Given: [前置条件]\n" +
        "When: [操作步骤]\n" +
        "Then: [预期结果]\n\n" +
        "### TC2: [具体用例名称]\n" +
        "Given: [前置条件]\n" +
        "When: [操作步骤]\n" +
        "Then: [预期结果]\n\n" +
        "**重要：**\n" +
        "1. 每个用例必须以 '### TC编号: 用例名称' 开头\n" +
        "2. 用例名称要具体，例如：'正常登录功能测试'\n" +
        "3. 只使用 Given/When/Then 三个关键词\n" +
        "4. 不要用数字编号（如 1. 2. 3.）\n" +
        "5. 用例之间用空行分隔";

    // 调用 Ollama API
    fetch(OLLAMA_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            model: MODEL_NAME,
            messages: [
                { role: 'system', content: systemPrompt },
                ...chatHistory.filter(function(msg) { return msg.role !== 'assistant' || msg.content.indexOf('保存为测试用例') === -1; }).slice(-10),
                { role: 'user', content: message }
            ],
            stream: false
        })
    })
    .then(function(response) {
        return response.json();
    })
    .then(function(data) {
        removeTyping();
        if (data.message && data.message.content) {
            appendMessage('assistant', data.message.content);
        } else {
            appendMessage('assistant', '抱歉，AI 没有返回有效内容。请检查 Ollama 服务是否正常运行。');
        }
    })
    .catch(function(error) {
        removeTyping();
        console.error('AI 请求失败:', error);
        appendMessage('assistant', '❌ 请求失败：' + error.message + '\n\n请确保 Ollama 服务已启动（http://127.0.0.1:11434）');
    });
}

// ==================== 清空对话 ====================
function clearChat() {
    if (confirm('确定要清空当前对话吗？')) {
        document.getElementById('aiChatMessages').innerHTML = '';
        chatHistory = [];
        appendMessage('assistant', '你好！我是 AI 助手，基于 deepseek-r1:1.5b 模型。你可以向我提问测试相关问题，或让我帮你生成测试用例。');
    }
}

// ==================== 页面初始化 ====================
document.addEventListener('DOMContentLoaded', function() {
    // 加载对话历史
    loadChatHistory();

    // 绑定发送按钮事件
    var sendBtn = document.getElementById('sendBtn');
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    // 绑定输入框回车事件
    var input = document.getElementById('aiChatInput');
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // 替换清空对话按钮
    var clearBtn = document.querySelector('[onclick="clearChat()"]');
    if (clearBtn) {
        clearBtn.setAttribute('onclick', 'clearChatHistory()');
    }
});

// ==================== 保存测试用例功能 ====================
function saveAsTestcase(btn) {
    var messageContent = btn.parentNode;
    var fullText = messageContent.innerHTML.replace(/<br>/g, '\n').replace(/<[^>]*>/g, '').trim();

    // 先尝试解析是否包含多个测试用例（通过检测多个"测试用例名称"或数字编号）
    var multipleCases = parseMultipleTestCases(fullText);

    if (multipleCases && multipleCases.length > 1) {
        // 有多个用例，显示批量保存对话框
        showBatchSaveDialog(multipleCases, btn);
    } else {
        // 单个用例，也使用相同的对话框逻辑
        var singleCase = parseSingleTestCase(fullText);
        if (singleCase) {
            showBatchSaveDialog([singleCase], btn);
        } else {
            alert('未能从 AI 回复中提取到测试用例内容！');
        }
    }
}

// 解析单个测试用例（BDD 格式）
function parseSingleTestCase(text) {
    const lines = text.split('\n').filter(line => line.trim());

    console.log('========== 单用例解析 ==========');

    // 提取标题（第一行非空行）
    let title = '';
    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line && !line.startsWith('#') && !line.startsWith('-')) {
            title = line.replace(/^[\d]+[\.、]\s*/, '');
            break;
        }
    }

    if (!title) {
        title = '未命名用例';
    }

    console.log('标题:', title);

    // 解析步骤
    const steps = [];
    let currentStep = null;

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i].trim();

        // 匹配操作步骤
        if (/^-?\s*操作步骤[：:]?/.test(line) || /^-\s*操作/.test(line)) {
            if (currentStep) {
                steps.push(currentStep);
            }
            currentStep = {
                step: line.replace(/^-?\s*操作步骤[：:]?\s*/, '').replace(/^-\s*操作/, ''),
                expected: ''
            };
        }
        // 匹配预期结果
        else if (/^-?\s*预期结果\d*[：:]?/.test(line) || /^-\s*预期/.test(line)) {
            if (currentStep) {
                currentStep.expected = line.replace(/^-?\s*预期结果\d*[：:]?\s*/, '').replace(/^-\s*预期/, '');
                steps.push(currentStep);
                currentStep = null;
            }
        }
        // 列表项
        else if (line.startsWith('-')) {
            const content = line.replace(/^-\s*/, '');

            if (content.includes('操作') || content.includes('用户') || content.includes('输入')) {
                if (currentStep) {
                    steps.push(currentStep);
                }
                currentStep = {
                    step: content,
                    expected: ''
                };
            } else if (content.includes('预期') || content.includes('系统') || content.includes('显示')) {
                if (currentStep) {
                    currentStep.expected = content;
                    steps.push(currentStep);
                    currentStep = null;
                }
            }
        }
        // 普通文本补充
        else if (currentStep && line) {
            if (!currentStep.step) {
                currentStep.step = line;
            } else {
                currentStep.step += ' ' + line;
            }
        }
    }

    if (currentStep) {
        steps.push(currentStep);
    }

    if (steps.length > 0) {
        console.log(`✓ 单用例解析成功: ${steps.length} 步`);
        return {
            title: title,
            steps: steps,
            fullText: text
        };
    }

    console.log('✗ 单用例解析失败');
    return null;
}

// 解析多个测试用例（支持 ### TCX: 格式）
function parseMultipleTestCases(text) {
    const cases = [];

    console.log('========== 开始解析 ==========');
    console.log('原始文本前800字符:', text.substring(0, 800));

    // 按 "### " 分割成多个用例块
    const blocks = text.split(/\n\s*###\s+/).filter(block => block.trim());

    console.log(`分割成 ${blocks.length} 个块`);

    for (let i = 0; i < blocks.length; i++) {
        const block = blocks[i].trim();

        // 跳过过短的块
        if (block.length < 10) {
            console.log(`跳过过短块 ${i + 1}`);
            continue;
        }

        const lines = block.split('\n').filter(line => line.trim());

        if (lines.length === 0) continue;

        console.log(`\n--- 处理块 ${i + 1} ---`);
        console.log('前5行:', lines.slice(0, 5).join('\n'));

        // 第一行是用例名称（去掉 TC编号: ）
        let title = lines[0].trim();
        // 去掉 "TCX: " 或 "TCX：" 前缀
        title = title.replace(/^TC\d+[:：]\s*/, '');
        // 去掉可能残留的 "### "
        title = title.replace(/^#+\s*/, '');

        console.log('用例名称:', title);

        // 解析步骤（Given/When/Then）
        const steps = [];
        let givenLines = [];
        let whenLines = [];
        let thenLines = [];

        for (let j = 1; j < lines.length; j++) {
            const line = lines[j].trim();

            // 匹配 Given
            if (/^Given[:：]?/.test(line)) {
                const content = line.replace(/^Given[:：]?\s*/, '');
                givenLines.push(content);
            }
            // 匹配 When
            else if (/^When[:：]?/.test(line)) {
                const content = line.replace(/^When[:：]?\s*/, '');
                whenLines.push(content);
            }
            // 匹配 Then
            else if (/^Then[:：]?/.test(line)) {
                const content = line.replace(/^Then[:：]?\s*/, '');
                thenLines.push(content);
            }
            // 匹配 And（根据上下文归类）
            else if (/^-?\s*And[:：]?/.test(line)) {
                const content = line.replace(/^-?\s*And[:：]?\s*/, '');

                // 如果已经有 When 但没有 Then，归为 When
                if (whenLines.length > 0 && thenLines.length === 0) {
                    whenLines.push(content);
                }
                // 否则归为 Then
                else {
                    thenLines.push(content);
                }
            }
        }

        console.log(`  Given: ${givenLines.length}, When: ${whenLines.length}, Then: ${thenLines.length}`);

        // 构建步骤：将 Given、When、Then 组合成步骤对
        // 策略：每个 When 对应一个步骤

        if (whenLines.length > 0) {
            for (let k = 0; k < whenLines.length; k++) {
                let stepText = '';
                let expectedText = '';

                // 添加所有 Given 作为前置条件（只在第一个步骤中添加）
                if (k === 0 && givenLines.length > 0) {
                    stepText = givenLines.join('；');
                }

                // 添加当前 When 作为操作
                if (stepText) {
                    stepText += '；' + whenLines[k];
                } else {
                    stepText = whenLines[k];
                }

                // 添加对应的 Then 作为预期结果
                if (thenLines.length > k) {
                    expectedText = thenLines[k];
                } else if (thenLines.length > 0) {
                    // 如果没有对应的 Then，使用最后一个
                    expectedText = thenLines[thenLines.length - 1];
                }

                steps.push({
                    step: stepText,
                    expected: expectedText
                });

                console.log(`  步骤 ${k + 1}:`, stepText.substring(0, 50));
                if (expectedText) {
                    console.log(`    预期:`, expectedText.substring(0, 50));
                }
            }
        } else {
            // 如果没有 When，尝试从 Given 和 Then 构建
            const maxLen = Math.max(givenLines.length, thenLines.length);
            for (let k = 0; k < maxLen; k++) {
                let stepText = givenLines[k] || '';
                let expectedText = thenLines[k] || '';

                if (stepText || expectedText) {
                    steps.push({
                        step: stepText,
                        expected: expectedText
                    });

                    console.log(`  步骤 ${k + 1}:`, stepText ? stepText.substring(0, 50) : '(无)');
                    if (expectedText) {
                        console.log(`    预期:`, expectedText.substring(0, 50));
                    }
                }
            }
        }

        // 只添加有步骤的用例
        if (steps.length > 0) {
            cases.push({
                title: title,
                steps: steps,
                fullText: block
            });
            console.log(`✓ 成功: "${title}" (${steps.length} 步)`);
        } else {
            console.log(` 跳过 "${title}" (无步骤)`);
        }
    }

    console.log(`\n========== 完成: ${cases.length} 个用例 ==========`);
    cases.forEach((c, idx) => {
        console.log(`${idx + 1}. ${c.title} - ${c.steps.length} 步`);
    });

    return cases;
}

// 统一的保存对话框（支持单个或多个用例）
function showBatchSaveDialog(cases, btn) {
    console.log('========== 显示保存对话框 ==========');
    console.log('用例数量:', cases.length);
    console.log('用例列表:', cases);

    if (!cases || cases.length === 0) {
        alert('未检测到可保存的测试用例！');
        return;
    }

    // 创建遮罩层
    const overlay = document.createElement('div');
    overlay.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); z-index: 9999;';

    // 创建弹窗容器
    const modal = document.createElement('div');
    modal.style.cssText = 'position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%); background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 20px rgba(0,0,0,0.3); max-width: 900px; width: 90%; max-height: 80vh; overflow-y: auto; z-index: 10000;';

    // 标题
    const title = document.createElement('h3');
    title.textContent = '💾 保存测试用例到【AI测试用例】临时表';
    title.style.cssText = 'margin-top: 0; margin-bottom: 20px; font-size: 20px; color: #333;';

    // 需求选择区域
    const requirementGroup = document.createElement('div');
    requirementGroup.style.cssText = 'margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 4px;';

    const reqLabel = document.createElement('label');
    reqLabel.innerHTML = '<strong>📌 关联需求ID（可选）:</strong>';
    reqLabel.style.cssText = 'display: block; margin-bottom: 10px;';

    const reqSelect = document.createElement('select');
    reqSelect.id = 'requirement-id-select';
    reqSelect.style.cssText = 'width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; font-size: 14px;';

    const defaultOption = document.createElement('option');
    defaultOption.value = '';
    defaultOption.textContent = '不关联需求';
    reqSelect.appendChild(defaultOption);

    requirementGroup.appendChild(reqLabel);
    requirementGroup.appendChild(reqSelect);

    // 加载需求列表
    loadRequirementsListForDialog(reqSelect);

    // 用例列表标题
    const listTitle = document.createElement('p');
    listTitle.innerHTML = '<strong>待保存的测试用例（请勾选需要保存的用例）:</strong>';
    listTitle.style.cssText = 'margin: 20px 0 10px 0;';

    // 用例表格
    const table = document.createElement('table');
    table.style.cssText = 'width: 100%; border-collapse: collapse; margin-top: 10px;';

    const thead = document.createElement('thead');
    thead.innerHTML = `
        <tr style="background-color: #f5f5f5;">
            <th style="padding: 10px; border: 1px solid #ddd; text-align: center; width: 50px;"><input type="checkbox" onclick="toggleSelectAll(this.checked)" /></th>
            <th style="padding: 10px; border: 1px solid #ddd; text-align: center; width: 60px;">编号</th>
            <th style="padding: 10px; border: 1px solid #ddd; text-align: left;">用例名称</th>
            <th style="padding: 10px; border: 1px solid #ddd; text-align: center; width: 100px;">步骤数</th>
            <th style="padding: 10px; border: 1px solid #ddd; text-align: center; width: 80px;">操作</th>
        </tr>
    `;

    const tbody = document.createElement('tbody');

    // 添加每一行
    cases.forEach((testCase, index) => {
        console.log(`\n--- 添加第 ${index + 1} 行 ---`);
        console.log('用例名称:', testCase.title);
        console.log('步骤数:', testCase.steps.length);

        const row = document.createElement('tr');
        row.style.cssText = index % 2 === 0 ? 'background-color: #fafafa;' : '';

        // 复选框
        const checkboxCell = document.createElement('td');
        checkboxCell.style.cssText = 'text-align: center; padding: 10px; border: 1px solid #ddd;';
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.className = 'case-checkbox';
        checkbox.dataset.index = index;
        checkbox.checked = true;
        checkboxCell.appendChild(checkbox);

        // 编号
        const numCell = document.createElement('td');
        numCell.style.cssText = 'text-align: center; padding: 10px; border: 1px solid #ddd;';
        numCell.textContent = index + 1;

        // 用例名称
        const nameCell = document.createElement('td');
        nameCell.style.cssText = 'padding: 10px; border: 1px solid #ddd;';
        const nameLink = document.createElement('a');
        nameLink.href = 'javascript:void(0)';
        nameLink.textContent = testCase.title;
        nameLink.style.cssText = 'color: #0066cc; text-decoration: none; font-weight: bold;';
        nameLink.onclick = () => toggleSteps(index);
        nameCell.appendChild(nameLink);

        // 步骤数
        const stepCountCell = document.createElement('td');
        stepCountCell.style.cssText = 'text-align: center; padding: 10px; border: 1px solid #ddd;';
        stepCountCell.textContent = `${testCase.steps.length} 个步骤`;

        // 展开按钮
        const actionCell = document.createElement('td');
        actionCell.style.cssText = 'text-align: center; padding: 10px; border: 1px solid #ddd;';
        const expandBtn = document.createElement('button');
        expandBtn.className = 'expand-btn';
        expandBtn.dataset.index = index;
        expandBtn.textContent = '展开';
        expandBtn.style.cssText = 'padding: 5px 10px; background-color: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer;';
        expandBtn.onclick = () => toggleSteps(index);
        actionCell.appendChild(expandBtn);

        row.appendChild(checkboxCell);
        row.appendChild(numCell);
        row.appendChild(nameCell);
        row.appendChild(stepCountCell);
        row.appendChild(actionCell);

        // 详情行（默认隐藏）
        const detailRow = document.createElement('tr');
        detailRow.id = `steps-row-${index}`;
        detailRow.style.display = 'none';
        detailRow.style.backgroundColor = '#f9f9f9';

        const detailCell = document.createElement('td');
        detailCell.colSpan = 5;
        detailCell.style.cssText = 'padding: 15px; border: 1px solid #ddd;';

        // 步骤表格
        const stepsTable = document.createElement('table');
        stepsTable.style.cssText = 'width: 100%; border-collapse: collapse;';

        const stepsThead = document.createElement('thead');
        stepsThead.innerHTML = `
            <tr style="background-color: #e9ecef;">
                <th style="padding: 8px; border: 1px solid #ccc; text-align: center; width: 50px;">序号</th>
                <th style="padding: 8px; border: 1px solid #ccc; text-align: left;">步骤</th>
                <th style="padding: 8px; border: 1px solid #ccc; text-align: left;">预期结果</th>
            </tr>
        `;

        const stepsTbody = document.createElement('tbody');
        testCase.steps.forEach((step, stepIndex) => {
            const stepRow = document.createElement('tr');
            stepRow.innerHTML = `
                <td style="padding: 8px; border: 1px solid #ccc; text-align: center;">${stepIndex + 1}</td>
                <td style="padding: 8px; border: 1px solid #ccc;">${step.step || '-'}</td>
                <td style="padding: 8px; border: 1px solid #ccc;">${step.expected || '-'}</td>
            `;
            stepsTbody.appendChild(stepRow);
        });

        stepsTable.appendChild(stepsThead);
        stepsTable.appendChild(stepsTbody);
        detailCell.appendChild(stepsTable);
        detailRow.appendChild(detailCell);

        tbody.appendChild(row);
        tbody.appendChild(detailRow);
    });

    table.appendChild(thead);
    table.appendChild(tbody);

    // 按钮区域
    const buttonGroup = document.createElement('div');
    buttonGroup.style.cssText = 'text-align: right; margin-top: 20px; padding-top: 20px; border-top: 1px solid #eee;';

    const cancelBtn = document.createElement('button');
    cancelBtn.textContent = '取消';
    cancelBtn.style.cssText = 'padding: 10px 25px; margin-right: 10px; background-color: #6c757d; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;';
    cancelBtn.onclick = closeSaveDialog;

    const confirmBtn = document.createElement('button');
    confirmBtn.textContent = '确认保存';
    confirmBtn.style.cssText = 'padding: 10px 25px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 14px;';
    confirmBtn.onclick = () => confirmSaveTestCases(cases, btn);

    buttonGroup.appendChild(cancelBtn);
    buttonGroup.appendChild(confirmBtn);

    // 组装弹窗
    modal.appendChild(title);
    modal.appendChild(requirementGroup);
    modal.appendChild(listTitle);
    modal.appendChild(table);
    modal.appendChild(buttonGroup);

    // 添加到页面
    document.body.appendChild(overlay);
    document.body.appendChild(modal);

    // 点击遮罩层关闭
    overlay.onclick = closeSaveDialog;
}

function loadRequirementsListForDialog(selectElement) {
    console.log('开始加载需求列表...');

    if (!selectElement) {
        console.error('selectElement 为空');
        return;
    }

    $.ajax({
        url: '/autotest/requirements/getTableData/',
        type: 'POST',
        success: function(response) {
            console.log('需求列表响应:', response);

            if (response && response.data && response.data.length > 0) {
                response.data.forEach(function(item) {
                    // item[0] 是 ID
                    const option = document.createElement('option');
                    option.value = item[0];
                    option.textContent = `${item[0]} - ${item[1] || '未命名需求'}`;
                    selectElement.appendChild(option);
                });
                console.log(`成功加载 ${response.data.length} 个需求`);
            } else {
                console.log('没有找到需求数据');
                var option = document.createElement('option');
                option.value = '';
                option.textContent = '暂无可用需求';
                option.disabled = true;
                selectElement.appendChild(option);
            }
        },
        error: function(xhr, status, error) {
            console.error('加载需求列表失败:', error);
            var option = document.createElement('option');
            option.value = '';
            option.textContent = '加载需求失败';
            option.disabled = true;
            selectElement.appendChild(option);
        }
    });
}

function toggleSteps(index) {
    const detailRow = document.getElementById(`steps-row-${index}`);
    const expandBtn = document.querySelector(`.expand-btn[data-index="${index}"]`);

    if (detailRow) {
        if (detailRow.style.display === 'none' || detailRow.style.display === '') {
            detailRow.style.display = 'table-row';
            if (expandBtn) {
                expandBtn.textContent = '收起';
            }
        } else {
            detailRow.style.display = 'none';
            if (expandBtn) {
                expandBtn.textContent = '展开';
            }
        }
    }
}

function toggleSelectAll(checked) {
    const checkboxes = document.querySelectorAll('.case-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = checked;
    });
}

function closeSaveDialog() {
    const overlay = document.querySelector('body > div[style*="z-index: 9999"]');
    const modal = document.querySelector('body > div[style*="z-index: 10000"]');

    if (overlay) overlay.remove();
    if (modal) modal.remove();
}

function confirmSaveTestCases(cases, btn) {
    const checkboxes = document.querySelectorAll('.case-checkbox:checked');

    if (checkboxes.length === 0) {
        alert('请至少选择一个测试用例！');
        return;
    }

    const selectedCases = [];
    checkboxes.forEach(checkbox => {
        const index = parseInt(checkbox.dataset.index);
        selectedCases.push(cases[index]);
    });

    const requirementsId = document.getElementById('requirement-id-select').value;

    console.log('准备保存的用例:', selectedCases);
    console.log('关联需求ID:', requirementsId);

    batchSaveTestCases(selectedCases, requirementsId, btn);
}

function batchSaveTestCases(cases, requirementsId, btn) {
    let savedCount = 0;
    const total = cases.length;

    console.log('========== 开始批量保存 ==========');
    console.log('用例总数:', total);
    console.log('关联需求ID:', requirementsId);
    console.log('用例列表:', cases);

    if (total === 0) {
        alert('没有可保存的测试用例！');
        return;
    }

    // 禁用确认按钮，防止重复点击
    const confirmBtn = document.querySelector('.btn-success[onclick*="confirmSaveTestCases"]');
    if (confirmBtn) {
        confirmBtn.disabled = true;
        confirmBtn.textContent = '保存中...';
    }

    cases.forEach((testCase, index) => {
        // 构建步骤字符串
        let stepsText = '';
        testCase.steps.forEach((step, stepIndex) => {
            stepsText += `步骤${stepIndex + 1}: ${step.step}\n`;
            stepsText += `预期结果${stepIndex + 1}: ${step.expected}\n\n`;
        });

        // 生成唯一的用例编码（每条用例独立）
        const testcaseCode = 'AI' + Date.now() + '_' + index + '_' + Math.random().toString(36).substr(2, 9);

        console.log(`\n--- 准备保存用例 ${index + 1}/${total} ---`);
        console.log('用例编码:', testcaseCode);
        console.log('用例名称:', testCase.title);
        console.log('步骤数:', testCase.steps.length);
        console.log('步骤文本:', stepsText);

        // 发送保存请求到新接口
        $.ajax({
            url: '/autotest/aitestcasetemp/saveFromChat/',
            type: 'POST',
            data: {
                'ai_testcase_code': testcaseCode,
                'ai_testcase_name': testCase.title,
                'ai_testcase_result': stepsText,
                'requirements_id': requirementsId || '',
                'product_id': window.userProductId || ''
            },
            beforeSend: function(xhr) {
                console.log('发送请求中...');
            },
            success: function(response) {
                console.log(`用例 ${index + 1} 响应:`, response);
                savedCount++;

                if (savedCount === total) {
                    alert(`成功保存 ${savedCount} 个测试用例到【AI测试用例】临时表！`);
                    closeSaveDialog();

                    // 不再自动刷新页面，避免触发 AI 重新生成
                    // 用户可以手动刷新或点击导航栏查看
                    console.log('保存完成，请手动刷新页面或点击导航栏查看结果');

                    // 恢复按钮状态
                    if (confirmBtn) {
                        confirmBtn.disabled = false;
                        confirmBtn.textContent = '确认保存';
                    }
                }
            },
            error: function(xhr, status, error) {
                console.error(`用例 ${index + 1} 保存失败:`, error);
                console.error('响应状态:', xhr.status);
                console.error('响应文本:', xhr.responseText);
                alert(`保存失败：${xhr.responseText}`);

                // 恢复按钮状态
                if (confirmBtn) {
                    confirmBtn.disabled = false;
                    confirmBtn.textContent = '确认保存';
                }
            }
        });
    });
}

