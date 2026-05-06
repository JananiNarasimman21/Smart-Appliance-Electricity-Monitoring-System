(function () {
    const assistantName = 'Jervis';
    const RESTART_DELAY_MS = 80;
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const speechSynthesisApi = window.speechSynthesis || null;
    const androidVoiceBridge = window.AndroidVoice || null;

    const routes = {
        home: '/',
        welcome: '/',
        homepage: '/',
        'home page': '/',
        dashboard: '/',
        instructions: '/instructions',
        setup: '/instructions',
        appliance: '/appliance',
        appliances: '/appliance',
        'select appliance': '/appliance',
        realtime: '/realtime',
        'real time': '/realtime',
        'real-time': '/realtime',
        'real time monitoring': '/realtime',
        'real-time monitoring': '/realtime',
        monitoring: '/realtime',
        history: '/history',
        'bill history': '/history'
    };

    const applianceRoutes = {
        geyser: '/realtime?appliance=Appliance1',
        fridge: '/realtime?appliance=Appliance2',
        microwave: '/realtime?appliance=Appliance3',
        'air conditioner': '/realtime?appliance=Appliance4',
        ac: '/realtime?appliance=Appliance4',
        'washing machine': '/realtime?appliance=Appliance5',
        television: '/realtime?appliance=Appliance6',
        tv: '/realtime?appliance=Appliance6',
        'water purifier': '/realtime?appliance=Appliance7',
        purifier: '/realtime?appliance=Appliance7',
        kettle: '/realtime?appliance=Appliance8',
        'electric kettle': '/realtime?appliance=Appliance8',
        laptop: '/realtime?appliance=Appliance9',
        'laptop charger': '/realtime?appliance=Appliance9'
    };
    const lastApplianceKey = 'jervis-last-appliance';
    const pendingReplyKey = 'jervis-pending-reply';

    const body = document.body;
    if (!body) return;

    enhanceAccessibility();
    const panel = buildPanel();
    const ui = {
        panel,
        fab: panel.querySelector('[data-voice-fab]'),
        sheet: panel.querySelector('[data-voice-sheet]'),
        close: panel.querySelector('[data-voice-close]'),
        chip: panel.querySelector('.voice-assistant-chip'),
        status: panel.querySelector('.voice-assistant-status'),
        heard: panel.querySelector('.voice-assistant-command'),
        live: panel.querySelector('[data-voice-live]'),
        toggle: panel.querySelector('[data-voice-toggle]'),
        quickButtons: panel.querySelectorAll('[data-voice-command]')
    };

    let recognition = null;
    let listening = false;
    let shouldStayListening = false;
    let isManualStop = false;
    let selectedVoice = null;
    let pendingSpeechMessage = '';

    if (!SpeechRecognition) {
        setState('error', assistantName + ' is unavailable in this browser.');
        ui.toggle.disabled = true;
        return;
    }

    recognition = new SpeechRecognition();
    recognition.lang = 'en-US';
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onstart = function () {
        listening = true;
        setState('listening', assistantName + ' is listening.');
    };

    recognition.onend = function () {
        listening = false;
        setState('idle', assistantName + ' is ready.');
        if (pendingSpeechMessage) {
            const message = pendingSpeechMessage;
            pendingSpeechMessage = '';
            speakNow(message);
        }
        restartIfNeeded();
    };

    recognition.onerror = function (event) {
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
            shouldStayListening = false;
            isManualStop = false;
        }

        const message = event.error === 'not-allowed'
            ? 'Microphone permission is blocked. Allow microphone access to use ' + assistantName + '.'
            : assistantName + ' had a voice recognition problem: ' + event.error + '.';
        setState('error', message);
    };

    recognition.onresult = function (event) {
        const result = event.results[event.results.length - 1];
        if (!result) return;

        const transcript = result[0].transcript.trim();
        ui.heard.textContent = transcript ? 'Heard: "' + transcript + '"' : '';

        if (result.isFinal) {
            setState('processing', assistantName + ' is executing.');
            executeCommand(transcript);
            if (recognition && listening) {
                recognition.stop();
            }
        }
    };

    ui.toggle.addEventListener('click', toggleListening);
    ui.fab.addEventListener('click', function () {
        ui.sheet.hidden = false;
        ui.fab.hidden = true;
    });
    ui.close.addEventListener('click', function () {
        ui.sheet.hidden = true;
        ui.fab.hidden = false;
    });
    ui.quickButtons.forEach(function (button) {
        button.addEventListener('click', function () {
            const command = button.getAttribute('data-voice-command') || '';
            if (command) {
                executeCommand(command);
            }
        });
    });

    document.addEventListener('keydown', function (event) {
        if (event.altKey && event.key.toLowerCase() === 'v') {
            event.preventDefault();
            toggleListening();
        }
    });

    document.addEventListener('focusin', function (event) {
        if (event.target instanceof HTMLElement) {
            event.target.classList.add('voice-highlight');
            window.setTimeout(function () {
                event.target.classList.remove('voice-highlight');
            }, 1200);
        }
    });

    setState('idle', assistantName + ' is ready.');
    selectPreferredVoice();
    speakPendingReply();

    function toggleListening() {
        if (!recognition) return;
        if (shouldStayListening || listening) {
            shouldStayListening = false;
            isManualStop = true;
            recognition.stop();
        } else {
            shouldStayListening = true;
            startRecognition();
        }
    }

    function setState(state, message) {
        ui.chip.dataset.state = state;
        const label = ui.chip.querySelector('[data-voice-chip-label]');
        if (label) {
            label.textContent = state === 'listening' ? 'Listening' : assistantName + ' Ready';
        }
        ui.status.textContent = message;
        ui.live.textContent = message;
        ui.toggle.textContent = (listening || shouldStayListening) ? 'Stop ' + assistantName : 'Start ' + assistantName;
    }

    function startRecognition() {
        if (!recognition || listening) {
            return;
        }

        try {
            recognition.start();
        } catch (error) {
            // Recognition can throw if called too quickly after ending.
            window.setTimeout(function () {
                if (shouldStayListening && !listening) {
                    try {
                        recognition.start();
                    } catch (retryError) {
                        // Keep silent; onend/onerror flow will continue recovery.
                    }
                }
            }, RESTART_DELAY_MS);
        }
    }

    function restartIfNeeded() {
        if (!shouldStayListening) {
            isManualStop = false;
            return;
        }

        if (isManualStop) {
            isManualStop = false;
            return;
        }

        // Avoid picking up assistant speech while it is talking.
        if (speechSynthesisApi && speechSynthesisApi.speaking) {
            window.setTimeout(restartIfNeeded, RESTART_DELAY_MS);
            return;
        }

        window.setTimeout(function () {
            if (shouldStayListening && !listening) {
                startRecognition();
            }
        }, RESTART_DELAY_MS);
    }

    function executeCommand(rawCommand) {
        const command = normalizeCommand(rawCommand);
        const currentAppliance = getCurrentApplianceSlug() || getRememberedAppliance();
        const shortcutHandled = handlePageShortcut(command, currentAppliance);

        if (shortcutHandled) {
            return;
        }

        if (command === 'go back' || command === 'previous page') {
            queueReplyForNextPage('Going back.');
            window.history.back();
            setState('success', 'Going back.');
            return;
        }

        if (command === 'scroll down') {
            window.scrollBy({ top: Math.round(window.innerHeight * 0.8), behavior: 'smooth' });
            return success('Scrolled down.');
        }

        if (command === 'scroll up') {
            window.scrollBy({ top: -Math.round(window.innerHeight * 0.8), behavior: 'smooth' });
            return success('Scrolled up.');
        }

        if (command === 'close popup' || command === 'close dialog') {
            const popup = document.getElementById('popup');
            if (popup && getComputedStyle(popup).display !== 'none') {
                const closeButton = popup.querySelector('button');
                if (closeButton) {
                    highlightAndClick(closeButton);
                    return success('Popup closed.');
                }
            }
        }

        const routeMatch = Object.keys(routes).find(function (key) {
            return command.includes('go to ' + key) || command === 'open ' + key || command === key;
        });
        if (routeMatch) {
            navigateWithReply(routes[routeMatch], 'Opening ' + routeMatch + '.');
            return;
        }

        const applianceMatch = Object.keys(applianceRoutes).find(function (key) {
            return command.includes('select ' + key) || command.includes('open ' + key) || command === key;
        });
        if (applianceMatch) {
            rememberAppliance(applianceRoutes[applianceMatch].split('/').pop());
            navigateWithReply(applianceRoutes[applianceMatch], 'Opening ' + applianceMatch + '.');
            return;
        }

        if (matchesAny(command, [
            'show daily data',
            'daily data',
            'daily usage',
            'daily electricity usage',
            'daily electricity',
            'daily',
            'daily monitoring',
            'track daily electricity usage of appliances'
        ])) {
            return navigateToType(currentAppliance, 'daily', 'Opening daily data.');
        }

        if (matchesAny(command, [
            'show monthly data',
            'monthly data',
            'monthly usage',
            'monthly electricity usage',
            'monthly electricity',
            'monthly',
            'monthly reports',
            'view monthly energy consumption'
        ])) {
            return navigateToType(currentAppliance, 'monthly', 'Opening monthly data.');
        }

        if (matchesAny(command, [
            'open real time monitoring',
            'show real time data',
            'real time data',
            'real time electricity',
            'real-time electricity',
            'real time power',
            'real-time power',
            'real time',
            'realtime',
            'live smart plug electricity monitoring'
        ])) {
            navigateWithReply('/realtime', 'Opening real-time monitoring.');
            return;
        }

        if (command.startsWith('set ip to ')) {
            return fillField('ip', spokenValue(rawCommand, 'set ip to '));
        }

        if (command.startsWith('set email to ')) {
            return fillField('email', normalizeEmail(spokenValue(rawCommand, 'set email to ')));
        }

        if (command.startsWith('set password to ')) {
            return fillField('password', spokenValue(rawCommand, 'set password to '));
        }

        if (command === 'clear ip' || command === 'clear ip address') {
            return fillField('ip', '');
        }

        if (command === 'clear email') {
            return fillField('email', '');
        }

        if (command === 'clear password') {
            return fillField('password', '');
        }

        if (command === 'start monitoring' || command === 'start') {
            const startButton = document.getElementById('start-monitoring');
            if (startButton) {
                highlightAndClick(startButton);
                return success('Monitoring started.');
            }
        }

        if (command === 'stop monitoring' || command === 'stop') {
            const stopButton = document.getElementById('stop-monitoring');
            if (stopButton) {
                highlightAndClick(stopButton);
                return success('Monitoring stopped.');
            }
        }

        if (command === 'download csv') {
            const csvButton = document.getElementById('download-csv');
            if (csvButton) {
                highlightAndClick(csvButton);
                return success('Downloading CSV.');
            }
        }

        if (command === 'csv' || command === 'download csv file') {
            const csvButton = document.getElementById('download-csv');
            if (csvButton) {
                highlightAndClick(csvButton);
                return success('Downloading CSV.');
            }
        }

        if (command === 'download pdf') {
            const pdfButton = document.getElementById('download-pdf');
            if (pdfButton) {
                highlightAndClick(pdfButton);
                return success('Downloading PDF.');
            }
        }

        if (command === 'pdf' || command === 'download pdf file' || command === 'electricity bill report') {
            const pdfButton = document.getElementById('download-pdf');
            if (pdfButton) {
                highlightAndClick(pdfButton);
                return success('Downloading PDF.');
            }
        }

        if (command === 'download graph' || command === 'save graph') {
            const graphButton = document.getElementById('download-graph');
            if (graphButton) {
                highlightAndClick(graphButton);
                return success('Downloading graph image.');
            }
        }

        if (command === 'graph' || command === 'graph image' || command === 'download graph image') {
            const graphButton = document.getElementById('download-graph');
            if (graphButton) {
                highlightAndClick(graphButton);
                return success('Downloading graph image.');
            }
        }

        failure(assistantName + ' recognized the command, but there is no matching action on this page yet.');
    }

    function success(message) {
        setState('success', message);
        speak(message);
    }

    function failure(message) {
        setState('error', message);
        speak(message);
    }

    function highlightAndClick(element) {
        element.classList.add('voice-highlight');
        element.focus({ preventScroll: false });
        window.setTimeout(function () {
            element.classList.remove('voice-highlight');
        }, 1500);
        element.click();
    }

    function fillField(id, value) {
        const input = document.getElementById(id);
        if (!input) {
            return failure('That field is not available on this page.');
        }

        input.focus();
        input.value = value;
        input.dispatchEvent(new Event('input', { bubbles: true }));
        input.dispatchEvent(new Event('change', { bubbles: true }));
        input.classList.add('voice-highlight');
        window.setTimeout(function () {
            input.classList.remove('voice-highlight');
        }, 1500);
        success('Filled ' + id + ' with the spoken value.');
    }

    function navigateToType(currentAppliance, type, message) {
        if (!currentAppliance) {
            return failure('Select an appliance first, then ask for daily or monthly history.');
        }
        navigateWithReply('/history?appliance=' + currentAppliance + '&period=' + type, message);
    }

    function handlePageShortcut(command, currentAppliance) {
        const path = window.location.pathname;

        if (command === 'select appliance' || command === 'select appliances') {
            navigateWithReply('/appliance', 'Opening appliance selection.');
            return true;
        }

        if (command === 'start page' || command === 'welcome page') {
            navigateWithReply('/', 'Opening homepage.');
            return true;
        }

        if (
            command === 'history page' ||
            command === 'history screen' ||
            command === 'open history'
        ) {
            if (currentAppliance) {
                navigateWithReply('/history?appliance=' + currentAppliance, 'Opening history view.');
            } else {
                navigateWithReply('/appliance', 'Opening appliance selection first.');
            }
            return true;
        }

        if (command === 'homepage' || command === 'home page' || command === 'go to homepage') {
            navigateWithReply('/', 'Opening homepage.');
            return true;
        }

        if (command === 'instructions page' || command === 'setup page') {
            navigateWithReply('/instructions', 'Opening instructions.');
            return true;
        }

        if (command === 'appliance page' || command === 'select appliance page') {
            navigateWithReply('/appliance', 'Opening appliance selection.');
            return true;
        }

        if (command === 'daily page' || command === 'daily data page' || command === 'daily electricity page') {
            if (currentAppliance) {
                navigateWithReply('/history?appliance=' + currentAppliance + '&period=daily', 'Opening daily history.');
                return true;
            }
        }

        if (command === 'monthly page' || command === 'monthly data page' || command === 'monthly electricity page') {
            if (currentAppliance) {
                navigateWithReply('/history?appliance=' + currentAppliance + '&period=monthly', 'Opening monthly history.');
                return true;
            }
        }

        if (command === 'realtime page' || command === 'real time page' || command === 'real-time page') {
            navigateWithReply('/realtime', 'Opening real-time monitoring.');
            return true;
        }

        if (command === 'next') {
            if (path === '/' || path === '/welcome') {
                navigateWithReply('/instructions', 'Opening instructions.');
                return true;
            }

            if (path === '/instructions') {
                navigateWithReply('/appliance', 'Opening appliance selection.');
                return true;
            }

        }

        if (command === 'start') {
            if (path === '/' || path === '/welcome') {
                window.location.href = '/instructions';
                success('Opening instructions.');
                return true;
            }

            if (path === '/realtime') {
                const startButton = document.getElementById('start-monitoring');
                if (startButton) {
                    highlightAndClick(startButton);
                    success('Monitoring started.');
                    return true;
                }
            }
        }

        return false;
    }

    function getCurrentApplianceSlug() {
        const queryAppliance = new URLSearchParams(window.location.search).get('appliance');
        const appliance = queryAppliance || '';
        if (appliance) {
            rememberAppliance(appliance);
        }
        return appliance;
    }

    function rememberAppliance(appliance) {
        try {
            window.localStorage.setItem(lastApplianceKey, appliance);
        } catch (error) {
            // Ignore local storage problems.
        }
    }

    function getRememberedAppliance() {
        try {
            return window.localStorage.getItem(lastApplianceKey) || '';
        } catch (error) {
            return '';
        }
    }

    function navigateWithReply(url, message) {
        queueReplyForNextPage(message);
        setState('success', message);
        window.location.href = url;
    }

    function queueReplyForNextPage(message) {
        try {
            window.sessionStorage.setItem(pendingReplyKey, message);
        } catch (error) {
            // Ignore session storage problems.
        }
    }

    function speakPendingReply() {
        try {
            const message = window.sessionStorage.getItem(pendingReplyKey) || '';
            if (!message) {
                return;
            }
            window.sessionStorage.removeItem(pendingReplyKey);
            window.setTimeout(function () {
                speakNow(message);
            }, 250);
        } catch (error) {
            // Ignore session storage problems.
        }
    }

    function selectPreferredVoice() {
        if (!speechSynthesisApi) {
            return;
        }

        const voices = speechSynthesisApi.getVoices();
        if (!voices.length) {
            speechSynthesisApi.addEventListener('voiceschanged', selectPreferredVoice, { once: true });
            return;
        }

        selectedVoice = voices.find(function (voice) {
            return /en/i.test(voice.lang) && /female|zira|aria|samantha|google us english/i.test(voice.name);
        }) || voices.find(function (voice) {
            return /en/i.test(voice.lang);
        }) || voices[0];
    }

    function speak(message) {
        if (!message) {
            return;
        }

        if (listening) {
            pendingSpeechMessage = message;
            return;
        }

        speakNow(message);
    }

    function speakNow(message) {
        if (!message) {
            return;
        }

        if (speechSynthesisApi) {
            const utterance = new SpeechSynthesisUtterance(message);
            utterance.rate = 0.95;
            utterance.pitch = 1;
            utterance.volume = 1;

            if (selectedVoice) {
                utterance.voice = selectedVoice;
            }

            speechSynthesisApi.cancel();
            speechSynthesisApi.speak(utterance);
            return;
        }

        if (androidVoiceBridge && typeof androidVoiceBridge.speak === 'function') {
            androidVoiceBridge.speak(message);
        }
    }

    function normalizeCommand(text) {
        return text
            .toLowerCase()
            .replace(/[.,!?]/g, ' ')
            .replace(/\b(?:jervis|jarvis)\b/g, ' ')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function spokenValue(rawText, prefix) {
        const normalizedRaw = rawText.trim();
        const lowered = normalizedRaw.toLowerCase();
        const index = lowered.indexOf(prefix);
        const spoken = index >= 0 ? normalizedRaw.slice(index + prefix.length) : normalizedRaw;
        return normalizeGenericValue(spoken);
    }

    function normalizeGenericValue(value) {
        return value
            .replace(/\s+dot\s+/gi, '.')
            .replace(/\s+dash\s+/gi, '-')
            .replace(/\s+underscore\s+/gi, '_')
            .replace(/\s+slash\s+/gi, '/')
            .replace(/\s+colon\s+/gi, ':')
            .replace(/\s+at\s+/gi, '@')
            .replace(/\s+/g, ' ')
            .trim();
    }

    function normalizeEmail(value) {
        return normalizeGenericValue(value)
            .replace(/\s*@\s*/g, '@')
            .replace(/\s*\.\s*/g, '.')
            .replace(/\s+/g, '');
    }

    function matchesAny(command, phrases) {
        return phrases.some(function (phrase) {
            return command === phrase || command.indexOf(phrase) !== -1;
        });
    }

    function enhanceAccessibility() {
        document.querySelectorAll('button').forEach(function (button) {
            if (!button.getAttribute('aria-label')) {
                button.setAttribute('aria-label', button.textContent.trim() || 'Button');
            }
        });

        document.querySelectorAll('a').forEach(function (link) {
            if (!link.getAttribute('aria-label')) {
                const text = link.textContent.trim();
                if (text) link.setAttribute('aria-label', text);
            }
        });

        document.querySelectorAll('input').forEach(function (input) {
            if (!input.getAttribute('aria-label')) {
                input.setAttribute('aria-label', input.placeholder || input.id || 'Input field');
            }
            if (!input.autocomplete) {
                input.autocomplete = 'off';
            }
        });
    }

    function buildPanel() {
        const panel = document.createElement('section');
        panel.className = 'voice-assistant-root';
        panel.setAttribute('aria-label', assistantName + ' voice assistant');
        panel.innerHTML = [
            '<button type="button" class="voice-assistant-fab" data-voice-fab aria-label="Open voice assistant">',
            '  <span class="voice-assistant-fab-dot"></span>',
            '  <span class="voice-assistant-fab-text">Talk</span>',
            '</button>',
            '<div class="voice-assistant-panel" data-voice-sheet hidden>',
            '  <div class="voice-assistant-header">',
            '    <div class="voice-assistant-title">' + assistantName + '</div>',
            '    <button type="button" class="voice-assistant-close" data-voice-close aria-label="Close voice assistant">Close</button>',
            '  </div>',
            '  <div class="voice-assistant-body">',
            '    <div class="voice-assistant-chip" data-state="idle"><span class="voice-assistant-dot"></span><span data-voice-chip-label>' + assistantName + ' Ready</span></div>',
            '    <p class="voice-assistant-status"></p>',
            '    <p class="voice-assistant-command" aria-live="polite"></p>',
            '    <div class="voice-assistant-quick">',
            '      <button type="button" class="voice-assistant-quick-btn" data-voice-command="open instructions">Instructions</button>',
            '      <button type="button" class="voice-assistant-quick-btn" data-voice-command="select appliance">Appliances</button>',
            '      <button type="button" class="voice-assistant-quick-btn" data-voice-command="realtime page">Realtime</button>',
            '      <button type="button" class="voice-assistant-quick-btn" data-voice-command="bill history">History</button>',
            '    </div>',
            '    <button type="button" class="voice-assistant-btn" data-voice-toggle>Start ' + assistantName + '</button>',
            '    <div class="voice-assistant-sr" aria-live="assertive" data-voice-live></div>',
            '  </div>',
            '</div>'
        ].join('');

        document.body.appendChild(panel);
        return panel;
    }
})();
