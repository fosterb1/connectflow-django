/**
 * Production-Grade WebRTC Client
 * Handles peer-to-peer video/audio with robust error handling, 
 * adaptive quality, and network resilience.
 * 
 * Features:
 * - Automatic reconnection
 * - Adaptive bitrate
 * - Network quality monitoring
 * - Echo cancellation
 * - Graceful degradation
 */

class WebRTCClient {
    constructor(config = {}) {
        this.config = {
            iceServers: config.iceServers || [
                { urls: 'stun:stun.l.google.com:19302' },
                { urls: 'stun:stun1.l.google.com:19302' }
            ],
            maxReconnectAttempts: 5,
            reconnectDelay: 2000,
            connectionTimeout: 15000,
            statsInterval: 2000,
            ...config
        };

        // State
        this.localStream = null;
        this.peerConnections = new Map();
        this.connectionStates = new Map();
        this.reconnectAttempts = new Map();
        this.statsIntervals = new Map();
        this.eventHandlers = new Map();
        
        // Network quality
        this.networkQuality = 'good'; // good, fair, poor
        this.lastBitrateAdjustment = Date.now();
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
                console.error(`Event handler error for ${event}:`, err);
            }
        });
    }

    /**
     * Initialize local media with best practices
     */
    async initializeLocalMedia(constraints = {}) {
        const defaultConstraints = {
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                sampleRate: 48000,
                channelCount: 1
            },
            video: {
                width: { ideal: 1280, max: 1920 },
                height: { ideal: 720, max: 1080 },
                frameRate: { ideal: 30, max: 30 },
                facingMode: 'user'
            }
        };

        const mergedConstraints = this._mergeDeep(defaultConstraints, constraints);

        try {
            this.emit('media_initializing', { constraints: mergedConstraints });
            
            this.localStream = await navigator.mediaDevices.getUserMedia(mergedConstraints);
            
            this.emit('media_initialized', { 
                stream: this.localStream,
                audioTracks: this.localStream.getAudioTracks().length,
                videoTracks: this.localStream.getVideoTracks().length
            });

            return this.localStream;

        } catch (error) {
            this.emit('media_error', { 
                error,
                type: this._categorizeMediaError(error)
            });
            throw error;
        }
    }

    /**
     * Create peer connection with proper configuration
     */
    createPeerConnection(peerId, options = {}) {
        if (this.peerConnections.has(peerId)) {
            console.warn(`Peer connection already exists for ${peerId}`);
            return this.peerConnections.get(peerId);
        }

        const pcConfig = {
            iceServers: this.config.iceServers,
            iceCandidatePoolSize: 10,
            bundlePolicy: 'max-bundle',
            rtcpMuxPolicy: 'require',
            iceTransportPolicy: 'all' // 'all' or 'relay' for TURN-only
        };

        const pc = new RTCPeerConnection(pcConfig);
        this.peerConnections.set(peerId, pc);
        this.connectionStates.set(peerId, 'new');
        this.reconnectAttempts.set(peerId, 0);

        // Add local tracks
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => {
                pc.addTrack(track, this.localStream);
            });
        }

        // Event handlers
        pc.onicecandidate = (event) => this._handleIceCandidate(peerId, event);
        pc.ontrack = (event) => this._handleTrack(peerId, event);
        pc.oniceconnectionstatechange = () => this._handleIceConnectionStateChange(peerId, pc);
        pc.onconnectionstatechange = () => this._handleConnectionStateChange(peerId, pc);
        pc.onsignalingstatechange = () => this._handleSignalingStateChange(peerId, pc);
        pc.onicegatheringstatechange = () => this._handleIceGatheringStateChange(peerId, pc);
        pc.onnegotiationneeded = () => this._handleNegotiationNeeded(peerId, pc, options);

        // Start monitoring connection quality
        this._startStatsMonitoring(peerId, pc);

        this.emit('peer_connection_created', { peerId, state: 'new' });

        return pc;
    }

    /**
     * Create and send offer
     */
    async createOffer(peerId, options = {}) {
        const pc = this.peerConnections.get(peerId);
        if (!pc) {
            throw new Error(`No peer connection for ${peerId}`);
        }

        try {
            const offerOptions = {
                offerToReceiveAudio: true,
                offerToReceiveVideo: true,
                iceRestart: options.iceRestart || false
            };

            const offer = await pc.createOffer(offerOptions);
            await pc.setLocalDescription(offer);

            this.emit('offer_created', { peerId, offer });

            return offer;

        } catch (error) {
            this.emit('offer_error', { peerId, error });
            throw error;
        }
    }

    /**
     * Handle incoming offer
     */
    async handleOffer(peerId, offer, options = {}) {
        let pc = this.peerConnections.get(peerId);
        
        if (!pc) {
            pc = this.createPeerConnection(peerId, options);
        }

        try {
            await pc.setRemoteDescription(new RTCSessionDescription(offer));
            
            const answer = await pc.createAnswer();
            await pc.setLocalDescription(answer);

            this.emit('answer_created', { peerId, answer });

            return answer;

        } catch (error) {
            this.emit('answer_error', { peerId, error });
            throw error;
        }
    }

    /**
     * Handle incoming answer
     */
    async handleAnswer(peerId, answer) {
        const pc = this.peerConnections.get(peerId);
        if (!pc) {
            console.error(`No peer connection for ${peerId}`);
            return;
        }

        try {
            await pc.setRemoteDescription(new RTCSessionDescription(answer));
            this.emit('answer_received', { peerId });

        } catch (error) {
            this.emit('answer_error', { peerId, error });
            console.error('Error setting remote description:', error);
        }
    }

    /**
     * Handle ICE candidate
     */
    async handleIceCandidate(peerId, candidate) {
        const pc = this.peerConnections.get(peerId);
        if (!pc) {
            console.error(`No peer connection for ${peerId}`);
            return;
        }

        try {
            await pc.addIceCandidate(new RTCIceCandidate(candidate));
        } catch (error) {
            console.error('Error adding ICE candidate:', error);
        }
    }

    /**
     * Toggle audio
     */
    toggleAudio(enabled) {
        if (!this.localStream) return false;

        const audioTracks = this.localStream.getAudioTracks();
        audioTracks.forEach(track => {
            track.enabled = enabled;
        });

        this.emit('audio_toggled', { enabled });
        return enabled;
    }

    /**
     * Toggle video
     */
    toggleVideo(enabled) {
        if (!this.localStream) return false;

        const videoTracks = this.localStream.getVideoTracks();
        videoTracks.forEach(track => {
            track.enabled = enabled;
        });

        this.emit('video_toggled', { enabled });
        return enabled;
    }

    /**
     * Switch camera (mobile)
     */
    async switchCamera() {
        if (!this.localStream) return;

        const videoTrack = this.localStream.getVideoTracks()[0];
        if (!videoTrack) return;

        const currentFacingMode = videoTrack.getSettings().facingMode;
        const newFacingMode = currentFacingMode === 'user' ? 'environment' : 'user';

        try {
            const newStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: newFacingMode },
                audio: false
            });

            const newVideoTrack = newStream.getVideoTracks()[0];
            
            // Replace track in all peer connections
            this.peerConnections.forEach(pc => {
                const sender = pc.getSenders().find(s => s.track?.kind === 'video');
                if (sender) {
                    sender.replaceTrack(newVideoTrack);
                }
            });

            // Stop old track and update local stream
            videoTrack.stop();
            this.localStream.removeTrack(videoTrack);
            this.localStream.addTrack(newVideoTrack);

            this.emit('camera_switched', { facingMode: newFacingMode });

        } catch (error) {
            this.emit('camera_switch_error', { error });
            console.error('Error switching camera:', error);
        }
    }

    /**
     * Close peer connection
     */
    closePeerConnection(peerId) {
        const pc = this.peerConnections.get(peerId);
        if (pc) {
            pc.close();
            this.peerConnections.delete(peerId);
            this.connectionStates.delete(peerId);
            this.reconnectAttempts.delete(peerId);
            
            // Stop stats monitoring
            const interval = this.statsIntervals.get(peerId);
            if (interval) {
                clearInterval(interval);
                this.statsIntervals.delete(peerId);
            }

            this.emit('peer_connection_closed', { peerId });
        }
    }

    /**
     * Close all connections
     */
    closeAll() {
        // Stop all peer connections
        this.peerConnections.forEach((pc, peerId) => {
            this.closePeerConnection(peerId);
        });

        // Stop local stream
        if (this.localStream) {
            this.localStream.getTracks().forEach(track => track.stop());
            this.localStream = null;
        }

        this.emit('all_connections_closed');
    }

    /**
     * ICE candidate handler
     */
    _handleIceCandidate(peerId, event) {
        if (event.candidate) {
            this.emit('ice_candidate', {
                peerId,
                candidate: event.candidate
            });
        }
    }

    /**
     * Track handler
     */
    _handleTrack(peerId, event) {
        this.emit('track_received', {
            peerId,
            track: event.track,
            streams: event.streams
        });
    }

    /**
     * ICE connection state change handler
     */
    _handleIceConnectionStateChange(peerId, pc) {
        const state = pc.iceConnectionState;
        console.log(`ICE connection state for ${peerId}: ${state}`);

        this.emit('ice_connection_state_change', { peerId, state });

        switch (state) {
            case 'connected':
            case 'completed':
                this.reconnectAttempts.set(peerId, 0);
                this.connectionStates.set(peerId, 'connected');
                break;

            case 'failed':
                this._handleConnectionFailure(peerId, pc);
                break;

            case 'disconnected':
                this._handleDisconnection(peerId, pc);
                break;

            case 'closed':
                this.closePeerConnection(peerId);
                break;
        }
    }

    /**
     * Connection state change handler
     */
    _handleConnectionStateChange(peerId, pc) {
        const state = pc.connectionState;
        console.log(`Connection state for ${peerId}: ${state}`);

        this.connectionStates.set(peerId, state);
        this.emit('connection_state_change', { peerId, state });

        if (state === 'failed') {
            this._handleConnectionFailure(peerId, pc);
        }
    }

    /**
     * Signaling state change handler
     */
    _handleSignalingStateChange(peerId, pc) {
        const state = pc.signalingState;
        this.emit('signaling_state_change', { peerId, state });
    }

    /**
     * ICE gathering state change handler
     */
    _handleIceGatheringStateChange(peerId, pc) {
        const state = pc.iceGatheringState;
        this.emit('ice_gathering_state_change', { peerId, state });
    }

    /**
     * Negotiation needed handler
     */
    async _handleNegotiationNeeded(peerId, pc, options) {
        if (options.isInitiator) {
            try {
                await this.createOffer(peerId);
            } catch (error) {
                console.error('Negotiation failed:', error);
            }
        }
    }

    /**
     * Handle connection failure
     */
    async _handleConnectionFailure(peerId, pc) {
        const attempts = this.reconnectAttempts.get(peerId) || 0;

        if (attempts < this.config.maxReconnectAttempts) {
            console.log(`Attempting to reconnect to ${peerId} (attempt ${attempts + 1})`);
            
            this.reconnectAttempts.set(peerId, attempts + 1);
            this.emit('reconnecting', { peerId, attempt: attempts + 1 });

            // Wait before reconnecting
            await new Promise(resolve => setTimeout(resolve, this.config.reconnectDelay));

            // ICE restart
            try {
                await this.createOffer(peerId, { iceRestart: true });
            } catch (error) {
                console.error('Reconnection failed:', error);
                this.emit('reconnect_failed', { peerId, error });
            }

        } else {
            console.error(`Max reconnect attempts reached for ${peerId}`);
            this.emit('connection_failed', { peerId });
            this.closePeerConnection(peerId);
        }
    }

    /**
     * Handle disconnection
     */
    _handleDisconnection(peerId, pc) {
        this.emit('peer_disconnected', { peerId });
        
        // Wait a bit to see if it reconnects
        setTimeout(() => {
            if (pc.iceConnectionState === 'disconnected') {
                this._handleConnectionFailure(peerId, pc);
            }
        }, 5000);
    }

    /**
     * Start stats monitoring for connection quality
     */
    _startStatsMonitoring(peerId, pc) {
        const interval = setInterval(async () => {
            if (!pc || pc.connectionState === 'closed') {
                clearInterval(interval);
                return;
            }

            try {
                const stats = await pc.getStats();
                const quality = this._analyzeStats(stats);
                
                if (quality !== this.networkQuality) {
                    this.networkQuality = quality;
                    this.emit('network_quality_change', { peerId, quality });
                    
                    // Adjust bitrate if needed
                    this._adjustBitrate(peerId, pc, quality);
                }

            } catch (error) {
                console.error('Stats error:', error);
            }

        }, this.config.statsInterval);

        this.statsIntervals.set(peerId, interval);
    }

    /**
     * Analyze WebRTC stats for quality metrics
     */
    _analyzeStats(stats) {
        let packetsLost = 0;
        let packetsReceived = 0;
        let jitter = 0;
        let rtt = 0;

        stats.forEach(report => {
            if (report.type === 'inbound-rtp') {
                packetsLost += report.packetsLost || 0;
                packetsReceived += report.packetsReceived || 0;
                jitter += report.jitter || 0;
            }
            if (report.type === 'candidate-pair' && report.state === 'succeeded') {
                rtt = report.currentRoundTripTime || 0;
            }
        });

        const packetLossRate = packetsReceived > 0 
            ? (packetsLost / (packetsLost + packetsReceived)) 
            : 0;

        // Determine quality
        if (packetLossRate > 0.05 || jitter > 0.1 || rtt > 0.3) {
            return 'poor';
        } else if (packetLossRate > 0.02 || jitter > 0.05 || rtt > 0.15) {
            return 'fair';
        } else {
            return 'good';
        }
    }

    /**
     * Adjust bitrate based on network quality
     */
    async _adjustBitrate(peerId, pc, quality) {
        const now = Date.now();
        if (now - this.lastBitrateAdjustment < 5000) {
            return; // Don't adjust too frequently
        }

        const sender = pc.getSenders().find(s => s.track?.kind === 'video');
        if (!sender) return;

        const parameters = sender.getParameters();
        if (!parameters.encodings || parameters.encodings.length === 0) {
            parameters.encodings = [{}];
        }

        // Adjust based on quality
        switch (quality) {
            case 'poor':
                parameters.encodings[0].maxBitrate = 250000; // 250kbps
                parameters.encodings[0].maxFramerate = 15;
                break;
            case 'fair':
                parameters.encodings[0].maxBitrate = 500000; // 500kbps
                parameters.encodings[0].maxFramerate = 24;
                break;
            case 'good':
                parameters.encodings[0].maxBitrate = 2500000; // 2.5Mbps
                parameters.encodings[0].maxFramerate = 30;
                break;
        }

        try {
            await sender.setParameters(parameters);
            this.lastBitrateAdjustment = now;
            this.emit('bitrate_adjusted', { peerId, quality, parameters });
        } catch (error) {
            console.error('Error adjusting bitrate:', error);
        }
    }

    /**
     * Categorize media errors
     */
    _categorizeMediaError(error) {
        if (error.name === 'NotAllowedError' || error.name === 'PermissionDeniedError') {
            return 'permission_denied';
        } else if (error.name === 'NotFoundError' || error.name === 'DevicesNotFoundError') {
            return 'no_devices';
        } else if (error.name === 'NotReadableError' || error.name === 'TrackStartError') {
            return 'device_in_use';
        } else if (error.name === 'OverconstrainedError') {
            return 'constraints_not_satisfied';
        } else if (error.name === 'TypeError') {
            return 'invalid_constraints';
        } else if (error.name === 'NotSupportedError') {
            return 'not_supported';
        } else {
            return 'unknown';
        }
    }

    /**
     * Utility: Deep merge objects
     */
    _mergeDeep(target, source) {
        const output = { ...target };
        if (this._isObject(target) && this._isObject(source)) {
            Object.keys(source).forEach(key => {
                if (this._isObject(source[key])) {
                    if (!(key in target)) {
                        Object.assign(output, { [key]: source[key] });
                    } else {
                        output[key] = this._mergeDeep(target[key], source[key]);
                    }
                } else {
                    Object.assign(output, { [key]: source[key] });
                }
            });
        }
        return output;
    }

    _isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = WebRTCClient;
}
