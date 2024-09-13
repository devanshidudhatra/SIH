// Getting the drop zone and file input elements
const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');

// Prevent default behavior (Prevent file from being opened)
['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, preventDefaults, false)
})

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Highlight the drop zone when dragging files over it
['dragenter', 'dragover'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.add('highlight');
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    dropZone.addEventListener(eventName, () => {
        dropZone.classList.remove('highlight');
    }, false);
});

// Handle dropped files
dropZone.addEventListener('drop', handleDrop, false);

function handleDrop(e) {
    let dt = e.dataTransfer;
    let files = dt.files;
    handleFiles(files);
}

function handleFiles(files) {
    [...files].forEach(uploadFile);
    [...files].forEach(displayFile);
}

function uploadFile(file) {
    // You can implement this function to send the file to a server
    console.log('File uploaded: ', file.name);
}

function displayFile(file) {
    const fileElement = document.createElement('p');
    fileElement.innerHTML = `File: ${file.name}`;
    fileList.appendChild(fileElement);
}

// Open file dialog when clicking on drop zone
dropZone.addEventListener('click', () => {
    fileInput.click();
});

// Handle manual file input
fileInput.addEventListener('change', (e) => {
    const files = e.target.files;
    handleFiles(files);
});
