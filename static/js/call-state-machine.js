/**
 * Call State Machine - Production-Grade
 * Manages call lifecycle with strict state transitions
 * 
 * States:
 * - IDLE: No call
 * - INITIATING: Creating call
 * - RINGING: Outgoing call, waiting for answer
 * - INCOMING: Incoming call, not answered yet
 * - CONNECTING: Call accepted, establishing connection
 * - CONNECTED: Active call with media
 * - RECONNECTING: Temporary connection loss
 * - ENDING: Call teardown in progress
 * - ENDED: Call terminated
 */

class CallStateMachine {
    constructor() {
        this.state = 'IDLE';
        this.previousState = null;
        this.stateHistory = [];
        this.stateStartTime = Date.now();
        this.callDuration = 0;
        this.durationInterval = null;
        
        // Call metadata
        this.callId = null;
        this.callType = null; // 'audio' | 'video'
        this.participants = new Map();
        this.initiator = null;
        this.localParticipant = null;
        
        // State transition callbacks
        this.stateTransitions = new Map();
        this.stateEntryCallbacks = new Map();
        this.stateExitCallbacks = new Map();
        
        // Valid state transitions
        this.validTransitions = {
            'IDLE': ['INITIATING', 'INCOMING'],
            'INITIATING': ['RINGING', 'ENDED'],
            'RINGING': ['CONNECTING', 'ENDED'],
            'INCOMING': ['CONNECTING', 'ENDED'],
            'CONNECTING': ['CONNECTED', 'RECONNECTING', 'ENDED'],
            'CONNECTED': ['RECONNECTING', 'ENDING'],
            'RECONNECTING': ['CONNECTED', 'ENDING'],
            'ENDING': ['ENDED'],
            'ENDED': ['IDLE']
        };
        
        this.setupDefaultCallbacks();
    }

    /**
     * Setup default state callbacks
     */
    setupDefaultCallbacks() {
        // CONNECTED state entry
        this.onEnter('CONNECTED', () => {
            this.startCallTimer();
        });

        // CONNECTED state exit
        this.onExit('CONNECTED', () => {
            this.stopCallTimer();
        });

        // ENDED state entry
        this.onEnter('ENDED', () => {
            this.stopCallTimer();
        });
    }

    /**
     * Transition to new state
     */
    transition(newState, metadata = {}) {
        // Validate transition
        if (!this.isValidTransition(newState)) {
            console.error(`Invalid state transition: ${this.state} -> ${newState}`);
            return false;
        }

        // Store previous state
        this.previousState = this.state;
        
        // Calculate time in current state
        const timeInState = Date.now() - this.stateStartTime;
        
        // Add to history
        this.stateHistory.push({
            state: this.state,
            duration: timeInState,
            timestamp: Date.now(),
            metadata
        });

        // Exit current state
        this.executeExitCallbacks(this.state);

        // Update state
        this.state = newState;
        this.stateStartTime = Date.now();

        console.log(`State transition: ${this.previousState} -> ${this.state}`, metadata);

        // Enter new state
        this.executeEntryCallbacks(newState);

        // Execute transition callbacks
        this.executeTransitionCallbacks(this.previousState, newState);

        return true;
    }

    /**
     * Check if transition is valid
     */
    isValidTransition(newState) {
        const allowedStates = this.validTransitions[this.state] || [];
        return allowedStates.includes(newState);
    }

    /**
     * Get current state
     */
    getState() {
        return this.state;
    }

    /**
     * Check if in specific state
     */
    is(state) {
        return this.state === state;
    }

    /**
     * Check if call is active
     */
    isActive() {
        return ['CONNECTING', 'CONNECTED', 'RECONNECTING'].includes(this.state);
    }

    /**
     * Check if can accept media
     */
    canAcceptMedia() {
        return ['CONNECTING', 'CONNECTED', 'RECONNECTING'].includes(this.state);
    }

    /**
     * Initialize call
     */
    initiate(callId, callType, participants, initiatorId, localUserId) {
        if (!this.transition('INITIATING', { callId, callType })) {
            return false;
        }

        this.callId = callId;
        this.callType = callType;
        this.initiator = initiatorId;
        this.localParticipant = localUserId;
        
        participants.forEach(p => {
            this.participants.set(p.userId, {
                userId: p.userId,
                username: p.username,
                status: 'invited',
                joinedAt: null
            });
        });

        return true;
    }

    /**
     * Start ringing (outgoing call)
     */
    startRinging() {
        return this.transition('RINGING');
    }

    /**
     * Receive incoming call
     */
    receiveCall(callId, callType, initiatorId, localUserId) {
        if (!this.transition('INCOMING', { callId, callType, initiatorId })) {
            return false;
        }

        this.callId = callId;
        this.callType = callType;
        this.initiator = initiatorId;
        this.localParticipant = localUserId;

        return true;
    }

    /**
     * Accept call
     */
    acceptCall() {
        if (!['RINGING', 'INCOMING'].includes(this.state)) {
            return false;
        }

        return this.transition('CONNECTING');
    }

    /**
     * Call connected
     */
    connected() {
        if (!this.transition('CONNECTED')) {
            return false;
        }

        return true;
    }

    /**
     * Start reconnection
     */
    startReconnection() {
        if (!['CONNECTED'].includes(this.state)) {
            return false;
        }

        return this.transition('RECONNECTING');
    }

    /**
     * Reconnection successful
     */
    reconnected() {
        if (!this.transition('CONNECTED')) {
            return false;
        }

        return true;
    }

    /**
     * End call
     */
    endCall() {
        if (!['RINGING', 'INCOMING', 'CONNECTING', 'CONNECTED', 'RECONNECTING'].includes(this.state)) {
            return false;
        }

        this.transition('ENDING');
        
        // Automatically transition to ENDED after cleanup
        setTimeout(() => {
            this.transition('ENDED');
        }, 100);

        return true;
    }

    /**
     * Reset to idle
     */
    reset() {
        this.transition('IDLE');
        this.callId = null;
        this.callType = null;
        this.participants.clear();
        this.initiator = null;
        this.localParticipant = null;
        this.callDuration = 0;
    }

    /**
     * Add participant
     */
    addParticipant(userId, username) {
        this.participants.set(userId, {
            userId,
            username,
            status: 'invited',
            joinedAt: null
        });
    }

    /**
     * Update participant status
     */
    updateParticipantStatus(userId, status) {
        const participant = this.participants.get(userId);
        if (participant) {
            participant.status = status;
            if (status === 'joined' && !participant.joinedAt) {
                participant.joinedAt = Date.now();
            }
        }
    }

    /**
     * Remove participant
     */
    removeParticipant(userId) {
        this.participants.delete(userId);
    }

    /**
     * Get active participants
     */
    getActiveParticipants() {
        return Array.from(this.participants.values()).filter(p => 
            ['joined', 'connected'].includes(p.status)
        );
    }

    /**
     * Start call timer
     */
    startCallTimer() {
        if (this.durationInterval) return;

        this.durationInterval = setInterval(() => {
            this.callDuration++;
        }, 1000);
    }

    /**
     * Stop call timer
     */
    stopCallTimer() {
        if (this.durationInterval) {
            clearInterval(this.durationInterval);
            this.durationInterval = null;
        }
    }

    /**
     * Get formatted call duration
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
     * Register state transition callback
     */
    onTransition(fromState, toState, callback) {
        const key = `${fromState}->${toState}`;
        if (!this.stateTransitions.has(key)) {
            this.stateTransitions.set(key, []);
        }
        this.stateTransitions.get(key).push(callback);
    }

    /**
     * Register state entry callback
     */
    onEnter(state, callback) {
        if (!this.stateEntryCallbacks.has(state)) {
            this.stateEntryCallbacks.set(state, []);
        }
        this.stateEntryCallbacks.get(state).push(callback);
    }

    /**
     * Register state exit callback
     */
    onExit(state, callback) {
        if (!this.stateExitCallbacks.has(state)) {
            this.stateExitCallbacks.set(state, []);
        }
        this.stateExitCallbacks.get(state).push(callback);
    }

    /**
     * Execute transition callbacks
     */
    executeTransitionCallbacks(fromState, toState) {
        const key = `${fromState}->${toState}`;
        const callbacks = this.stateTransitions.get(key) || [];
        
        callbacks.forEach(callback => {
            try {
                callback({ from: fromState, to: toState });
            } catch (error) {
                console.error('Error in transition callback:', error);
            }
        });
    }

    /**
     * Execute entry callbacks
     */
    executeEntryCallbacks(state) {
        const callbacks = this.stateEntryCallbacks.get(state) || [];
        
        callbacks.forEach(callback => {
            try {
                callback(state);
            } catch (error) {
                console.error('Error in entry callback:', error);
            }
        });
    }

    /**
     * Execute exit callbacks
     */
    executeExitCallbacks(state) {
        const callbacks = this.stateExitCallbacks.get(state) || [];
        
        callbacks.forEach(callback => {
            try {
                callback(state);
            } catch (error) {
                console.error('Error in exit callback:', error);
            }
        });
    }

    /**
     * Get state history
     */
    getStateHistory() {
        return this.stateHistory;
    }

    /**
     * Get state info
     */
    getStateInfo() {
        return {
            current: this.state,
            previous: this.previousState,
            timeInState: Date.now() - this.stateStartTime,
            callDuration: this.callDuration,
            formattedDuration: this.getFormattedDuration(),
            callId: this.callId,
            callType: this.callType,
            participants: this.getActiveParticipants().length,
            isActive: this.isActive()
        };
    }
}

// Export
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CallStateMachine;
}
