/**
 * Call State Manager
 * Manages call lifecycle, states, and user experience
 */

class CallStateManager {
    constructor() {
        this.state = 'idle'; // idle, preview, connecting, ringing, connected, reconnecting, ended, failed
        this.participants = new Map();
        this.callDuration = 0;
        this.durationInterval = null;
        this.connectionTimeout = null;
        this.eventHandlers = new Map();
    }

    /**
     * Event system
     */
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }

    emit(event, data) {
        const handlers = this.eventHandlers.get(event) || [];
        handlers.forEach(handler => {
            try {
                handler(data);
            } catch (err) {
                console.error(`State manager event error for ${event}:`, err);
            }
        });
    }

    /**
     * Transition to new state
     */
    transitionTo(newState, reason = null) {
        const oldState = this.state;
        this.state = newState;

        console.log(`Call state: ${oldState} → ${newState}`, reason || '');

        this.emit('state_changed', {
            from: oldState,
            to: newState,
            reason
        });

        // State-specific actions
        switch (newState) {
            case 'preview':
                this._handlePreviewState();
                break;
            case 'connecting':
                this._handleConnectingState();
                break;
            case 'connected':
                this._handleConnectedState();
                break;
            case 'reconnecting':
                this._handleReconnectingState();
                break;
            case 'ended':
            case 'failed':
                this._handleEndState(reason);
                break;
        }
    }

    /**
     * Add participant
     */
    addParticipant(userId, data = {}) {
        this.participants.set(userId, {
            userId,
            joined: new Date(),
            audioEnabled: data.audioEnabled !== false,
            videoEnabled: data.videoEnabled !== false,
            screenSharing: data.screenSharing || false,
            ...data
        });

        this.emit('participant_added', {
            userId,
            count: this.participants.size
        });
    }

    /**
     * Remove participant
     */
    removeParticipant(userId) {
        const participant = this.participants.get(userId);
        if (participant) {
            this.participants.delete(userId);
            
            this.emit('participant_removed', {
                userId,
                count: this.participants.size
            });

            // End call if no participants left
            if (this.participants.size === 0 && this.state === 'connected') {
                this.transitionTo('ended', 'all_participants_left');
            }
        }
    }

    /**
     * Update participant state
     */
    updateParticipant(userId, updates) {
        const participant = this.participants.get(userId);
        if (participant) {
            Object.assign(participant, updates);
            
            this.emit('participant_updated', {
                userId,
                updates
            });
        }
    }

    /**
     * Start call duration timer
     */
    startDurationTimer() {
        this.callDuration = 0;
        this.durationInterval = setInterval(() => {
            this.callDuration++;
            this.emit('duration_updated', {
                duration: this.callDuration
            });
        }, 1000);
    }

    /**
     * Stop duration timer
     */
    stopDurationTimer() {
        if (this.durationInterval) {
            clearInterval(this.durationInterval);
            this.durationInterval = null;
        }
    }

    /**
     * Get formatted duration
     */
    getFormattedDuration() {
        const hours = Math.floor(this.callDuration / 3600);
        const minutes = Math.floor((this.callDuration % 3600) / 60);
        const seconds = this.callDuration % 60;

        if (hours > 0) {
            return `${hours}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
        }
        return `${minutes}:${String(seconds).padStart(2, '0')}`;
    }

    /**
     * Preview state handler
     */
    _handlePreviewState() {
        // Waiting for user to confirm and join
    }

    /**
     * Connecting state handler
     */
    _handleConnectingState() {
        // Set timeout for connection
        this.connectionTimeout = setTimeout(() => {
            if (this.state === 'connecting') {
                this.transitionTo('failed', 'connection_timeout');
            }
        }, 30000); // 30 second timeout
    }

    /**
     * Connected state handler
     */
    _handleConnectedState() {
        if (this.connectionTimeout) {
            clearTimeout(this.connectionTimeout);
            this.connectionTimeout = null;
        }
        this.startDurationTimer();
    }

    /**
     * Reconnecting state handler
     */
    _handleReconnectingState() {
        // Show reconnecting UI
    }

    /**
     * End state handler
     */
    _handleEndState(reason) {
        this.stopDurationTimer();
        
        if (this.connectionTimeout) {
            clearTimeout(this.connectionTimeout);
            this.connectionTimeout = null;
        }

        // Clean up participants
        this.participants.clear();
    }

    /**
     * Get current state
     */
    getState() {
        return this.state;
    }

    /**
     * Check if call is active
     */
    isActive() {
        return ['preview', 'connecting', 'ringing', 'connected', 'reconnecting'].includes(this.state);
    }

    /**
     * Get participant count
     */
    getParticipantCount() {
        return this.participants.size;
    }
}


/**
 * Call UI Controller
 * Manages UI updates and user interactions
 */

class CallUIController {
    constructor(stateManager) {
        this.stateManager = stateManager;
        this.elements = {};
        this.audioContext = null;
        this.audioAnalyser = null;
    }

    /**
     * Initialize UI elements
     */
    init() {
        this.elements = {
            // Videos
            localVideo: document.getElementById('local-video'),
            videoGrid: document.getElementById('video-grid'),
            
            // Controls
            muteBtn: document.getElementById('mute-btn'),
            videoBtn: document.getElementById('video-btn'),
            screenShareBtn: document.getElementById('screen-share-btn'),
            endCallBtn: document.getElementById('end-call-btn'),
            switchCameraBtn: document.getElementById('switch-camera-btn'),
            
            // Status
            callStatus: document.getElementById('call-status'),
            participantCount: document.getElementById('participant-count'),
            callDuration: document.getElementById('call-duration'),
            networkQuality: document.getElementById('network-quality'),
            
            // Modals/Overlays
            permissionModal: document.getElementById('permission-modal'),
            previewModal: document.getElementById('preview-modal'),
            reconnectingOverlay: document.getElementById('reconnecting-overlay'),
            
            // Preview
            previewVideo: document.getElementById('preview-video'),
            joinCallBtn: document.getElementById('join-call-btn'),
            cancelCallBtn: document.getElementById('cancel-call-btn')
        };

        this._setupEventListeners();
    }

    /**
     * Setup event listeners
     */
    _setupEventListeners() {
        // State manager events
        this.stateManager.on('state_changed', (data) => this._handleStateChange(data));
        this.stateManager.on('participant_added', (data) => this._updateParticipantCount(data.count));
        this.stateManager.on('participant_removed', (data) => this._updateParticipantCount(data.count));
        this.stateManager.on('duration_updated', (data) => this._updateDuration(data.duration));
    }

    /**
     * Show preview modal
     */
    showPreview(stream) {
        if (this.elements.previewVideo && stream) {
            this.elements.previewVideo.srcObject = stream;
        }
        
        if (this.elements.previewModal) {
            this.elements.previewModal.classList.remove('hidden');
        }
    }

    /**
     * Hide preview modal
     */
    hidePreview() {
        if (this.elements.previewModal) {
            this.elements.previewModal.classList.add('hidden');
        }
    }

    /**
     * Show local video
     */
    showLocalVideo(stream) {
        if (this.elements.localVideo && stream) {
            this.elements.localVideo.srcObject = stream;
            this.elements.localVideo.muted = true;
            this.elements.localVideo.play().catch(console.error);
        }
    }

    /**
     * Add remote video
     */
    addRemoteVideo(peerId, stream, participantName) {
        // Remove existing if present
        this.removeRemoteVideo(peerId);

        const videoTile = document.createElement('div');
        videoTile.id = `video-${peerId}`;
        videoTile.className = 'video-tile';
        videoTile.innerHTML = `
            <video id="remote-video-${peerId}" autoplay playsinline></video>
            <div class="video-overlay">
                <div class="participant-name">${participantName || 'Participant'}</div>
                <div class="connection-status"></div>
                <div class="audio-indicator"></div>
            </div>
        `;

        if (this.elements.videoGrid) {
            this.elements.videoGrid.appendChild(videoTile);
        }

        const video = document.getElementById(`remote-video-${peerId}`);
        if (video) {
            video.srcObject = stream;
            video.play().catch(console.error);
        }

        // Setup audio visualization
        this._setupAudioVisualization(peerId, stream);
    }

    /**
     * Remove remote video
     */
    removeRemoteVideo(peerId) {
        const videoTile = document.getElementById(`video-${peerId}`);
        if (videoTile) {
            videoTile.remove();
        }
    }

    /**
     * Update participant video state
     */
    updateParticipantVideo(peerId, videoEnabled) {
        const videoTile = document.getElementById(`video-${peerId}`);
        if (!videoTile) return;

        if (!videoEnabled) {
            videoTile.classList.add('video-disabled');
            // Show avatar or placeholder
        } else {
            videoTile.classList.remove('video-disabled');
        }
    }

    /**
     * Update participant audio state
     */
    updateParticipantAudio(peerId, audioEnabled) {
        const audioIndicator = document.querySelector(`#video-${peerId} .audio-indicator`);
        if (audioIndicator) {
            if (!audioEnabled) {
                audioIndicator.innerHTML = '<i class="fas fa-microphone-slash"></i>';
                audioIndicator.classList.add('muted');
            } else {
                audioIndicator.innerHTML = '';
                audioIndicator.classList.remove('muted');
            }
        }
    }

    /**
     * Update call status text
     */
    updateCallStatus(status) {
        if (this.elements.callStatus) {
            this.elements.callStatus.textContent = status;
        }
    }

    /**
     * Update participant count
     */
    _updateParticipantCount(count) {
        if (this.elements.participantCount) {
            this.elements.participantCount.textContent = count;
        }
    }

    /**
     * Update call duration
     */
    _updateDuration(duration) {
        if (this.elements.callDuration) {
            this.elements.callDuration.textContent = this.stateManager.getFormattedDuration();
        }
    }

    /**
     * Update network quality indicator
     */
    updateNetworkQuality(quality) {
        if (!this.elements.networkQuality) return;

        const qualityConfig = {
            good: { text: 'Good', color: 'text-green-500', icon: 'signal' },
            fair: { text: 'Fair', color: 'text-yellow-500', icon: 'signal' },
            poor: { text: 'Poor', color: 'text-red-500', icon: 'signal' }
        };

        const config = qualityConfig[quality] || qualityConfig.good;
        
        this.elements.networkQuality.innerHTML = `
            <i class="fas fa-${config.icon} ${config.color}"></i>
            <span class="${config.color}">${config.text}</span>
        `;
    }

    /**
     * Show error modal
     */
    showError(message, type = 'error') {
        const errorHtml = `
            <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-[9999]">
                <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 max-w-md mx-4 shadow-2xl">
                    <div class="text-center">
                        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full ${type === 'error' ? 'bg-red-100' : 'bg-yellow-100'} mb-4">
                            <i class="fas fa-${type === 'error' ? 'exclamation-triangle' : 'info-circle'} text-2xl ${type === 'error' ? 'text-red-600' : 'text-yellow-600'}"></i>
                        </div>
                        <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-2">
                            ${type === 'error' ? 'Call Error' : 'Notice'}
                        </h3>
                        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">${message}</p>
                        <button onclick="this.closest('.fixed').remove()" 
                                class="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-semibold">
                            OK
                        </button>
                    </div>
                </div>
            </div>
        `;

        const div = document.createElement('div');
        div.innerHTML = errorHtml;
        document.body.appendChild(div);
    }

    /**
     * Show reconnecting overlay
     */
    showReconnecting() {
        if (this.elements.reconnectingOverlay) {
            this.elements.reconnectingOverlay.classList.remove('hidden');
        }
    }

    /**
     * Hide reconnecting overlay
     */
    hideReconnecting() {
        if (this.elements.reconnectingOverlay) {
            this.elements.reconnectingOverlay.classList.add('hidden');
        }
    }

    /**
     * Handle state changes
     */
    _handleStateChange(data) {
        const { to, reason } = data;

        switch (to) {
            case 'preview':
                this.updateCallStatus('Preview - Check your camera and microphone');
                break;
            case 'connecting':
                this.updateCallStatus('Connecting...');
                this.hidePreview();
                break;
            case 'ringing':
                this.updateCallStatus('Calling...');
                break;
            case 'connected':
                this.updateCallStatus('Connected');
                this.hideReconnecting();
                break;
            case 'reconnecting':
                this.updateCallStatus('Reconnecting...');
                this.showReconnecting();
                break;
            case 'ended':
                this.updateCallStatus(reason ? `Call ended: ${reason}` : 'Call ended');
                this._handleCallEnd();
                break;
            case 'failed':
                this.updateCallStatus(reason ? `Call failed: ${reason}` : 'Call failed');
                this.showError(this._getFailureMessage(reason));
                break;
        }
    }

    /**
     * Handle call end
     */
    _handleCallEnd() {
        setTimeout(() => {
            // Redirect or close
            window.location.href = '/';
        }, 3000);
    }

    /**
     * Get user-friendly failure message
     */
    _getFailureMessage(reason) {
        const messages = {
            'connection_timeout': 'Could not connect to the call. Please check your internet connection and try again.',
            'permission_denied': 'Camera or microphone access was denied. Please allow access in your browser settings.',
            'no_devices': 'No camera or microphone found. Please connect a device and try again.',
            'device_in_use': 'Your camera or microphone is being used by another application.',
            'network_error': 'Network error occurred. Please check your connection and try again.',
            'all_participants_left': 'All participants have left the call.'
        };

        return messages[reason] || 'An error occurred during the call. Please try again.';
    }

    /**
     * Setup audio visualization
     */
    _setupAudioVisualization(peerId, stream) {
        const audioTracks = stream.getAudioTracks();
        if (audioTracks.length === 0) return;

        if (!this.audioContext) {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        }

        const source = this.audioContext.createMediaStreamSource(stream);
        const analyser = this.audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        source.connect(analyser);

        const bufferLength = analyser.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const checkAudioLevel = () => {
            analyser.getByteFrequencyData(dataArray);
            const average = dataArray.reduce((a, b) => a + b) / bufferLength;
            
            const audioIndicator = document.querySelector(`#video-${peerId} .audio-indicator`);
            if (audioIndicator && average > 30) {
                audioIndicator.classList.add('speaking');
            } else if (audioIndicator) {
                audioIndicator.classList.remove('speaking');
            }

            requestAnimationFrame(checkAudioLevel);
        };

        checkAudioLevel();
    }

    /**
     * Toggle button state
     */
    toggleButton(button, enabled, enabledClass, disabledClass) {
        if (!button) return;

        if (enabled) {
            button.classList.remove(disabledClass);
            button.classList.add(enabledClass);
        } else {
            button.classList.remove(enabledClass);
            button.classList.add(disabledClass);
        }
    }

    /**
     * Update mute button
     */
    updateMuteButton(isMuted) {
        this.toggleButton(
            this.elements.muteBtn,
            !isMuted,
            'bg-white/20',
            'bg-red-500'
        );
        
        if (this.elements.muteBtn) {
            const icon = this.elements.muteBtn.querySelector('i');
            if (icon) {
                icon.className = isMuted ? 'fas fa-microphone-slash' : 'fas fa-microphone';
            }
        }
    }

    /**
     * Update video button
     */
    updateVideoButton(isVideoOn) {
        this.toggleButton(
            this.elements.videoBtn,
            isVideoOn,
            'bg-white/20',
            'bg-red-500'
        );
        
        if (this.elements.videoBtn) {
            const icon = this.elements.videoBtn.querySelector('i');
            if (icon) {
                icon.className = isVideoOn ? 'fas fa-video' : 'fas fa-video-slash';
            }
        }
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CallStateManager, CallUIController };
}
