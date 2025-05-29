// Improved JavaScript for fingerprint scanner integration 
// For use with HID DigitalPersona 4500 Fingerprint Reader

document.addEventListener('DOMContentLoaded', function() {
    // Get UI elements
    const scanBtn = document.getElementById('scanBtn');
    const fingerprintScanner = document.getElementById('fingerprintScanner');
    const fingerStatus = document.getElementById('fingerStatus');
    const successMessage = document.getElementById('successMessage');
    const saveBtn = document.getElementById('saveBtn');
    const fingerprintData = document.getElementById('fingerprintData');
    const fingerprintImage = document.getElementById('fingerprintImage');
    
    // Hide success message initially
    if (successMessage) {
        successMessage.style.display = 'none';
    }
    
    // Track scanning state
    let isScanning = false;
    
    // Mock Digital Persona SDK integration
    // In a real implementation, you would use the actual SDK
    class DigitalPersonaSDK {
        constructor() {
            console.log("Initializing DigitalPersona SDK");
            this.initialized = true;
            this.connected = false;
            
            // Try to connect to the device
            this.connect();
        }
        
        connect() {
            console.log("Attempting to connect to fingerprint reader");
            // In a real implementation, this would actually connect to the hardware
            setTimeout(() => {
                this.connected = true;
                console.log("Connected to fingerprint reader");
            }, 500);
        }
        
        startCapture(options) {
            if (!this.initialized) {
                if (options.onFailure) {
                    options.onFailure({
                        code: "NOT_INITIALIZED",
                        message: "SDK not initialized"
                    });
                }
                return;
            }
            
            if (!this.connected) {
                console.log("Reconnecting to device...");
                this.connect();
                if (options.onFailure) {
                    options.onFailure({
                        code: "DEVICE_NOT_CONNECTED",
                        message: "Fingerprint reader not connected"
                    });
                }
                return;
            }
            
            console.log("Starting fingerprint capture");
            
            // In a real implementation, this would actually capture from the hardware
            // For now, we'll simulate the capture process
            
            // Simulate capture delay
            setTimeout(() => {
                // Create mock fingerprint data
                // In a real implementation, this would be the actual fingerprint data
                const mockFingerprint = this.generateMockFingerprint();
                
                // Call the success callback
                if (options.onSuccess) {
                    options.onSuccess({
                        success: true,
                        quality: 85,
                        templateBase64: mockFingerprint
                    });
                }
            }, 2000);
        }
        
        generateMockFingerprint() {
            // Create a mock fingerprint template
            // In a real implementation, this would be the actual template from the SDK
            
            // Generate 512 random bytes
            const array = new Uint8Array(512);
            for (let i = 0; i < array.length; i++) {
                array[i] = Math.floor(Math.random() * 256);
            }
            
            // Convert to Base64
            return btoa(String.fromCharCode.apply(null, array));
        }
    }
    
    // Initialize the SDK
    let dpSDK;
    try {
        // In a real implementation, you would use the actual SDK
        dpSDK = new DigitalPersonaSDK();
        console.log("DigitalPersona SDK initialized successfully");
    } catch (e) {
        console.error("Failed to initialize DigitalPersona SDK:", e);
        if (fingerStatus) {
            fingerStatus.textContent = "Error: Could not initialize fingerprint device";
            fingerStatus.classList.add("text-danger");
        }
    }
    
    // Add click handler for scan button
    if (scanBtn) {
        scanBtn.addEventListener('click', function() {
            if (isScanning) {
                // Already scanning, ignore
                return;
            }
            
            // Update UI
            isScanning = true;
            if (fingerStatus) {
                fingerStatus.textContent = "Scanning... Place finger on the scanner";
                fingerStatus.className = "finger-status mt-3 text-primary";
            }
            if (fingerprintScanner) {
                fingerprintScanner.classList.add("scanning");
            }
            
            // Update button text
            scanBtn.textContent = "Scanning...";
            scanBtn.disabled = true;
            
            // Start the actual capture
            if (dpSDK) {
                dpSDK.startCapture({
                    onSuccess: function(result) {
                        console.log("Fingerprint captured successfully");
                        
                        // Update UI
                        isScanning = false;
                        if (fingerprintScanner) {
                            fingerprintScanner.classList.remove("scanning");
                        }
                        if (fingerStatus) {
                            fingerStatus.textContent = "Fingerprint captured successfully!";
                            fingerStatus.className = "finger-status mt-3 text-success";
                        }
                        
                        // Reset button
                        scanBtn.textContent = "Scan Again";
                        scanBtn.disabled = false;
                        
                        // Show success message
                        if (successMessage) {
                            successMessage.style.display = "block";
                        }
                        
                        // Enable save button
                        if (saveBtn) {
                            saveBtn.disabled = false;
                        }
                        
                        // Set fingerprint data
                        if (fingerprintData) {
                            fingerprintData.value = result.templateBase64;
                        }
                        
                        // Update fingerprint image to show success
                        if (fingerprintImage) {
                            fingerprintImage.src = "/static/img/fingerprint-success.png";
                        }
                    },
                    onFailure: function(error) {
                        console.error("Failed to capture fingerprint:", error);
                        
                        // Update UI
                        isScanning = false;
                        if (fingerprintScanner) {
                            fingerprintScanner.classList.remove("scanning");
                        }
                        if (fingerStatus) {
                            fingerStatus.textContent = "Failed to capture fingerprint: " + error.message;
                            fingerStatus.className = "finger-status mt-3 text-danger";
                        }
                        
                        // Reset button
                        scanBtn.textContent = "Try Again";
                        scanBtn.disabled = false;
                        
                        // Update fingerprint image to show failure
                        if (fingerprintImage) {
                            fingerprintImage.src = "/static/img/fingerprint-error.png";
                        }
                    }
                });
            } else {
                // No SDK, fallback to simulation
                console.log("Using fallback simulator");
                simulateFingerprintScan();
            }
        });
    }
    
    // Fallback simulator
    function simulateFingerprintScan() {
        setTimeout(() => {
            // Simulate fingerprint capture
            if (Math.random() > 0.2) { // 80% success rate for demo
                // Success
                isScanning = false;
                if (fingerprintScanner) {
                    fingerprintScanner.classList.remove("scanning");
                }
                if (fingerStatus) {
                    fingerStatus.textContent = "Fingerprint captured successfully!";
                    fingerStatus.className = "finger-status mt-3 text-success";
                }
                
                // Reset button
                scanBtn.textContent = "Scan Again";
                scanBtn.disabled = false;
                
                // Show success message
                if (successMessage) {
                    successMessage.style.display = "block";
                }
                
                // Enable save button
                if (saveBtn) {
                    saveBtn.disabled = false;
                }
                
                // Set fingerprint data
                if (fingerprintData) {
                    // Generate random base64 data
                    const randomData = new Uint8Array(512);
                    window.crypto.getRandomValues(randomData);
                    fingerprintData.value = btoa(String.fromCharCode.apply(null, randomData));
                }
                
                // Update fingerprint image
                if (fingerprintImage) {
                    fingerprintImage.src = "/static/img/fingerprint-success.png";
                }
            } else {
                // Failure
                isScanning = false;
                if (fingerprintScanner) {
                    fingerprintScanner.classList.remove("scanning");
                }
                if (fingerStatus) {
                    fingerStatus.textContent = "Failed to capture fingerprint. Please try again.";
                    fingerStatus.className = "finger-status mt-3 text-danger";
                }
                
                // Reset button
                scanBtn.textContent = "Try Again";
                scanBtn.disabled = false;
                
                // Update fingerprint image
                if (fingerprintImage) {
                    fingerprintImage.src = "/static/img/fingerprint-error.png";
                }
            }
        }, 3000);
    }
    
    // Form validation
    const fingerprintForm = document.getElementById('fingerprintForm');
    if (fingerprintForm) {
        fingerprintForm.addEventListener('submit', function(e) {
            if (!fingerprintData.value) {
                e.preventDefault();
                alert('Please capture a fingerprint before saving.');
                return false;
            }
            return true;
        });
    }
});