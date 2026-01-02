/* ================= SIDEBAR ================= */

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (window.innerWidth > 768) {
        sidebar.classList.toggle('collapsed');
    } else {
        sidebar.classList.toggle('active');
    }
}

function showSection(id) {
    document.querySelectorAll('.content-section').forEach(s => s.style.display = 'none');
    document.getElementById(id).style.display = 'block';

    if (window.innerWidth <= 768) {
        document.getElementById('sidebar').classList.remove('active');
    }

    document.querySelectorAll('.nav-links a').forEach(a => a.classList.remove('active'));
}

/* ================= PROFILE MENU ================= */

window.addEventListener("click", () => {
    document.querySelectorAll(".profile-dropdown").forEach(d => d.classList.remove("show"));
});

function toggleProfileMenu(event, id) {
    event.stopPropagation();
    document.getElementById(id).classList.toggle("show");
}

/* ================= JOB TOGGLE ================= */

function toggleJob(id) {
    const el = document.getElementById("job-" + id);
    const icon = el.previousElementSibling.querySelector("i");

    if (el.style.display === "block") {
        el.style.display = "none";
        icon.classList.remove("rotate");
    } else {
        el.style.display = "block";
        icon.classList.add("rotate");
    }
}

/* ================= APPLY MODAL ================= */

let selectedJobId = null;

function openApplyPopup(jobId, jobTitle) {
    selectedJobId = jobId;

    document.getElementById("modalJobTitle").innerText =
        "Apply for " + jobTitle;

    // Resume
    const resumeLink = document.getElementById("modalResumeLink");
    if (window.__PROFILE_RESUME_URL) {
        resumeLink.href = window.__PROFILE_RESUME_URL;
        resumeLink.style.display = "inline";
    } else {
        resumeLink.style.display = "none";
    }

    // Profile warning
    document.getElementById("profileIncompleteMsg").style.display =
        window.__PROFILE_INCOMPLETE ? "block" : "none";

    document.getElementById("applyLoader").style.display = "none";
    document.getElementById("applyResult").style.display = "none";

    document.getElementById("applyModal").style.display = "flex";
}
document.addEventListener('DOMContentLoaded', function () {
    const params = new URLSearchParams(window.location.search);
    const jobId = params.get('find_job');

    if (jobId) {
        const targetJob = document.getElementById('job-card-' + jobId);

        if (targetJob) {
            // 1. Scroll the job into the middle of the screen
            targetJob.scrollIntoView({ behavior: 'smooth', block: 'center' });

            // 2. Add the highlight color class
            targetJob.classList.add('highlight-job');

            // 3. Optional: Remove highlight after 5 seconds
            setTimeout(() => {
                targetJob.classList.remove('highlight-job');
            }, 5000);
        }
    }
});
function closeApplyPopup() {
    document.getElementById("applyModal").style.display = "none";
}

/* ================= APPLY CONFIRM ================= */
function confirmApply() {
    const loader = document.getElementById("applyLoader");
    const result = document.getElementById("applyResult");
    const btn = document.getElementById("confirmApplyBtn");
    if (!selectedJobId) return;

    loader.style.display = "block";
    result.style.display = "none";
    btn.disabled = true;

    // prepare form data
    const form = new FormData();
    const fileInput = document.getElementById('newResumeInput');
    if (fileInput && fileInput.files && fileInput.files.length > 0) {
        form.append('resume', fileInput.files[0]);
    }

    fetch(`/apply-job/${selectedJobId}/`, {
        method: "POST",
        headers: {
            "X-CSRFToken": getCookie("csrftoken")
        },
        body: form,
        credentials: 'same-origin'
    })
        .then(res => res.json())
        .then(data => {
            loader.style.display = "none";
            btn.disabled = false;

            // ❌ Profile incomplete
            if (data.status === "incomplete") {
                alert("Please complete your profile first.");
                window.location.href = data.redirect;
                return;
            }

            // 🔒 Already applied
            if (data.status === "already_applied") {
                alert("⚠ You already applied for this job.");
                closeApplyPopup();
                return;
            }

            // ✅ Success
            if (data.status === "success") {
                alert("🎉 Application submitted successfully!");
                closeApplyPopup();

                // 🔥 Change Apply button instantly
                const applyBtn = document.querySelector(
                    `button[onclick*="'${selectedJobId}'"]`
                );
                if (applyBtn) {
                    applyBtn.innerText = "✔ Applied";
                    applyBtn.disabled = true;
                    applyBtn.classList.add("btn-applied");
                }
            }
        })
        .catch(() => {
            loader.style.display = "none";
            btn.disabled = false;
            alert("Network error. Please try again.");
        });
}

/* ================= CSRF ================= */

function getCookie(name) {
    const el = document.querySelector('[name=csrfmiddlewaretoken]');
    if (el) return el.value;

    let match = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return match ? match.pop() : '';
}

// Auto-open apply modal when redirected back from profile completion
function tryAutoOpenFromURL() {
    const params = new URLSearchParams(window.location.search);
    const jobId = params.get('open_apply');
    if (!jobId) return;

    let title = '';
    const details = document.getElementById('job-' + jobId);
    if (details) {
        const header = details.previousElementSibling;
        const titleEl = header.querySelector('.job-title');
        if (titleEl) title = titleEl.innerText;
    }

    openApplyPopup(jobId, title);

    const url = new URL(window.location);
    url.searchParams.delete('open_apply');
    window.history.replaceState({}, '', url);
}

document.addEventListener('DOMContentLoaded', tryAutoOpenFromURL);

