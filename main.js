/**
 * Student Management System — Frontend Controller
 */

// Toggle password visibility in Login Form
function togglePasswordVisibility(inputId, btn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    if (input.type === 'password') {
        input.type = 'text';
        btn.style.color = '#4f46e5';
    } else {
        input.type = 'password';
        btn.style.color = '';
    }
}

// Show Toast Message
function showToast(message, type = 'success') {
    const toast = document.getElementById('toastNotification');
    const toastMsg = document.getElementById('toastMsg');
    const toastIcon = document.getElementById('toastIcon');

    if (!toast || !toastMsg) return;

    toastMsg.textContent = message;
    
    // Icon based on type
    if (type === 'success') {
        toastIcon.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>`;
    } else if (type === 'error') {
        toastIcon.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>`;
    } else {
        toastIcon.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#3b82f6" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>`;
    }

    toast.classList.add('show');
    clearTimeout(window.__toastTimeout);
    window.__toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, 3500);
}

// Handle Roll Number Link Generation via AJAX
async function handleGenerateLink(e) {
    e.preventDefault();
    const rollInput = document.getElementById('rollNumberInput');
    const btnGenerate = document.getElementById('btnGenerate');
    const container = document.getElementById('generatedLinkContainer');
    const linkInput = document.getElementById('generatedLinkText');
    const openBtn = document.getElementById('btnOpenLink');
    const statusBadge = document.getElementById('linkStatusBadge');

    const rollNo = rollInput.value.trim();
    if (!rollNo) {
        showToast('Please enter a roll number.', 'error');
        return;
    }

    btnGenerate.disabled = true;
    btnGenerate.innerHTML = `<span>Generating...</span>`;

    try {
        const response = await fetch('/api/generate_link', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ roll_no: rollNo })
        });

        const data = await response.json();

        if (response.ok && data.success) {
            linkInput.value = data.full_link;
            openBtn.href = data.relative_link;
            
            if (data.exists) {
                statusBadge.textContent = "Existing Profile Found";
                statusBadge.style.background = "#eef2ff";
                statusBadge.style.color = "#4338ca";
            } else {
                statusBadge.textContent = "New Link Created";
                statusBadge.style.background = "#ecfdf5";
                statusBadge.style.color = "#065f46";
            }

            container.style.display = 'block';
            container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            showToast(`Link generated for Roll No: ${data.roll_no}!`);
        } else {
            showToast(data.error || 'Failed to generate link', 'error');
        }
    } catch (err) {
        console.error(err);
        showToast('Network error while generating link.', 'error');
    } finally {
        btnGenerate.disabled = false;
        btnGenerate.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="13 17 18 12 13 7"></polyline>
                <polyline points="6 17 11 12 6 7"></polyline>
            </svg>
            <span>Generate Link</span>
        `;
    }
}

// Copy Generated Link to Clipboard
function copyGeneratedLink() {
    const linkInput = document.getElementById('generatedLinkText');
    if (!linkInput || !linkInput.value) return;

    copyLinkToClipboard(linkInput.value);

    const copyBtnText = document.getElementById('copyBtnText');
    if (copyBtnText) {
        const orig = copyBtnText.textContent;
        copyBtnText.textContent = "Copied!";
        setTimeout(() => {
            copyBtnText.textContent = orig;
        }, 2000);
    }
}

// Universal Clipboard Copy helper
function copyLinkToClipboard(url) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(url).then(() => {
            showToast('Link copied to clipboard!');
        }).catch(() => {
            fallbackCopy(url);
        });
    } else {
        fallbackCopy(url);
    }
}

function fallbackCopy(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    try {
        document.execCommand('copy');
        showToast('Link copied to clipboard!');
    } catch (err) {
        showToast('Could not copy link automatically. Please copy manually.', 'error');
    }
    document.body.removeChild(textArea);
}

// Live Search Filter for Students Table
function filterStudentsTable() {
    const query = (document.getElementById('searchStudentsInput')?.value || '').toLowerCase().trim();
    const rows = document.querySelectorAll('.student-row');
    let visibleCount = 0;

    rows.forEach(row => {
        const searchData = row.getAttribute('data-search') || '';
        if (searchData.includes(query)) {
            row.style.display = '';
            visibleCount++;
        } else {
            row.style.display = 'none';
        }
    });

    const emptyRow = document.getElementById('emptyTableRow');
    if (emptyRow) {
        emptyRow.style.display = (visibleCount === 0 && rows.length > 0) ? '' : 'none';
    }
}

// Confirmation Dialog for Record Deletion
function confirmDelete(rollNo) {
    return confirm(`Are you sure you want to delete student Roll No: ${rollNo}?\nThis will remove their individual ${rollNo}.xlsx file and update the master Excel file.`);
}
