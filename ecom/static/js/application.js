function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Show the targeted section
    const target = document.getElementById(sectionId);
    if (target) {
        target.style.display = 'block';
    }
}

function toggleJobDesc(appId) {
    const container = document.getElementById(`desc-${appId}`);
    const button = document.querySelector(`#app-${appId} .btn-details-toggle`);
    
    // Toggle the Active class
    container.classList.toggle('active');
    button.classList.toggle('active');
    
    // Update button text
    if (container.classList.contains('active')) {
        button.innerHTML = `Hide Description <i class="fas fa-chevron-down"></i>`;
    } else {
        button.innerHTML = `View Description <i class="fas fa-chevron-down"></i>`;
    }
}