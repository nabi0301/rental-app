// Enable tooltips everywhere
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize registration form validation
    validateRegistrationForm();
    
    // Initialize map if it exists on the page
    initSearchMap();
});

// Map functionality for property search
let searchMap = null;
let searchMarker = null;

function initSearchMap() {
    const mapElement = document.getElementById('searchMap');
    if (!mapElement) return;

    // Initialize the map
    searchMap = L.map('searchMap').setView([40.7128, -74.0060], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(searchMap);

    // Try to load existing coordinates from hidden inputs
    const lat = document.getElementById('search_lat').value;
    const lng = document.getElementById('search_lng').value;
    if (lat && lng) {
        setSearchLocation(lat, lng);
    }

    // Add click event to map
    searchMap.on('click', function(e) {
        setSearchLocation(e.latlng.lat, e.latlng.lng);
    });
}

function setSearchLocation(lat, lng) {
    // Update hidden inputs
    document.getElementById('search_lat').value = lat;
    document.getElementById('search_lng').value = lng;

    // Update or add marker
    if (searchMarker) {
        searchMarker.setLatLng([lat, lng]);
    } else {
        searchMarker = L.marker([lat, lng]).addTo(searchMap);
    }

    // Center map on new location
    searchMap.setView([lat, lng], 13);
}

function getUserLocation() {
    if (!navigator.geolocation) {
        alert('Geolocation is not supported by your browser');
        return;
    }

    navigator.geolocation.getCurrentPosition(
        function(position) {
            setSearchLocation(position.coords.latitude, position.coords.longitude);
        },
        function(error) {
            let message = 'Error getting your location: ';
            switch(error.code) {
                case error.PERMISSION_DENIED:
                    message += 'Permission denied';
                    break;
                case error.POSITION_UNAVAILABLE:
                    message += 'Position unavailable';
                    break;
                case error.TIMEOUT:
                    message += 'Timeout';
                    break;
                default:
                    message += 'Unknown error';
            }
            alert(message);
        }
    );
}

// Image preview for property uploads
function previewImages(input) {
    const container = document.getElementById('imagePreviewContainer');
    container.innerHTML = '';
    
    if (input.files) {
        Array.from(input.files).forEach((file, index) => {
            const reader = new FileReader();
            reader.onload = function(e) {
                const col = document.createElement('div');
                col.className = 'col-md-4 mb-2';
                
                const img = document.createElement('img');
                img.src = e.target.result;
                img.className = 'img-thumbnail';
                img.style.maxHeight = '200px';
                
                if (index === 0) {
                    const badge = document.createElement('span');
                    badge.className = 'badge bg-primary position-absolute top-0 end-0';
                    badge.textContent = 'Primary';
                    col.appendChild(badge);
                }
                
                col.appendChild(img);
                container.appendChild(col);
            };
            reader.readAsDataURL(file);
        });
    }
}

// Registration form validation
function validateRegistrationForm() {
    const form = document.querySelector('form');
    if (!form) return;

    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirm_password');
    
    confirmPassword.addEventListener('input', function() {
        if (password.value !== confirmPassword.value) {
            confirmPassword.setCustomValidity("Passwords do not match");
        } else {
            confirmPassword.setCustomValidity("");
        }
    });

    password.addEventListener('input', function() {
        let message = [];
        if (password.value.length < 8) {
            message.push("Password must be at least 8 characters long");
        }
        if (!/[A-Z]/.test(password.value)) {
            message.push("Password must contain at least one uppercase letter");
        }
        if (!/[a-z]/.test(password.value)) {
            message.push("Password must contain at least one lowercase letter");
        }
        if (!/\d/.test(password.value)) {
            message.push("Password must contain at least one number");
        }
        password.setCustomValidity(message.join("\n"));
    });
}

// Price range validation
function validatePriceRange() {
    const minPrice = document.getElementById('min_price');
    const maxPrice = document.getElementById('max_price');
    
    if (minPrice && maxPrice && minPrice.value && maxPrice.value) {
        if (parseInt(minPrice.value) > parseInt(maxPrice.value)) {
            alert('Minimum price cannot be greater than maximum price');
            return false;
        }
    }
    return true;
}
