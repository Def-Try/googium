// Update clock and date
function updateDateTime() {
    const now = new Date();
    const timeOptions = { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    
    document.getElementById('clock').textContent = now.toLocaleTimeString('en-GB', timeOptions);
    document.getElementById('date').textContent = now.toLocaleDateString('en-US', dateOptions);
}

setInterval(updateDateTime, 1000);
updateDateTime();

// Bookmarks functionality
let bookmarks = JSON.parse(localStorage.getItem('bookmarks')) || [
    { name: 'Google', url: 'https://www.google.com', icon: 'https://www.google.com/favicon.ico' },
    { name: 'YouTube', url: 'https://www.youtube.com', icon: 'https://www.youtube.com/favicon.ico' },
    { name: 'Wikipedia', url: 'https://www.wikipedia.org', icon: 'https://www.wikipedia.org/favicon.ico' },
    { name: 'GitHub', url: 'https://github.com', icon: 'https://github.com/favicon.ico' },
    { name: 'Stack Overflow', url: 'https://stackoverflow.com', icon: 'https://stackoverflow.com/favicon.ico' },
    { name: 'Discord', url: 'https://discord.com/app', icon: 'https://cdn.prod.website-files.com/6257adef93867e50d84d30e2/62fddf0fde45a8baedcc7ee5_847541504914fd33810e70a0ea73177e%20(2)-1.png' },
];

function saveBookmarks() {
    localStorage.setItem('bookmarks', JSON.stringify(bookmarks));
}

function renderBookmarks() {
    const bookmarksContainer = document.getElementById('bookmarks');
    bookmarksContainer.innerHTML = '';
    
    bookmarks.forEach((bookmark, index) => {
        const bookmarkElement = document.createElement('a');
        bookmarkElement.href = bookmark.url;
        bookmarkElement.className = 'bookmark';
        bookmarkElement.innerHTML = `
            <img src="${bookmark.icon}" alt="${bookmark.name} icon" width="32" height="32">
            <div>${bookmark.name}</div>
            <button class="edit-bookmark" data-index="${index}">✏️</button>
        `;
        bookmarksContainer.appendChild(bookmarkElement);
    });

    const addBookmarkButton = document.createElement('div');
    addBookmarkButton.className = 'add-bookmark bookmark';
    addBookmarkButton.innerHTML = `
        <div class="bookmark-icon">➕</div>
        <div>Add Bookmark</div>
    `;
    addBookmarkButton.addEventListener('click', () => openEditModal(-1));
    bookmarksContainer.appendChild(addBookmarkButton);

    document.querySelectorAll('.edit-bookmark').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            openEditModal(parseInt(button.dataset.index));
        });
    });
}

// Edit modal functionality
const modal = document.getElementById('editModal');
const editNameInput = document.getElementById('editName');
const editUrlInput = document.getElementById('editUrl');
const editIconInput = document.getElementById('editIcon');
const saveEditButton = document.getElementById('saveEdit');
const deleteBookmarkButton = document.getElementById('deleteBookmark');
const cancelEditButton = document.getElementById('cancelEdit');

let currentEditIndex = -1;

function openEditModal(index) {
    currentEditIndex = index;
    if (index === -1) {
        editNameInput.value = '';
        editUrlInput.value = '';
        editIconInput.value = '';
        deleteBookmarkButton.style.display = 'none';
    } else {
        const bookmark = bookmarks[index];
        editNameInput.value = bookmark.name;
        editUrlInput.value = bookmark.url;
        editIconInput.value = bookmark.icon;
        deleteBookmarkButton.style.display = 'inline-block';
    }
    modal.style.display = 'block';
}

function closeEditModal() {
    modal.style.display = 'none';
}

saveEditButton.addEventListener('click', () => {
    const newBookmark = {
        name: editNameInput.value,
        url: editUrlInput.value,
        icon: editIconInput.value
    };
    if (currentEditIndex === -1) {
        bookmarks.push(newBookmark);
    } else {
        bookmarks[currentEditIndex] = newBookmark;
    }
    saveBookmarks();
    renderBookmarks();
    closeEditModal();
});

deleteBookmarkButton.addEventListener('click', () => {
    if (currentEditIndex !== -1) {
        bookmarks.splice(currentEditIndex, 1);
        saveBookmarks();
        renderBookmarks();
        closeEditModal();
    }
});

cancelEditButton.addEventListener('click', closeEditModal);

renderBookmarks();

// Theme toggle functionality
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

function setThemeIcon() {
    const lightIcon = themeToggle.querySelector('.light-icon');
    const darkIcon = themeToggle.querySelector('.dark-icon');
    if (body.classList.contains('dark-mode')) {
        lightIcon.style.display = 'inline';
        darkIcon.style.display = 'none';
    } else {
        lightIcon.style.display = 'none';
        darkIcon.style.display = 'inline';
    }
}

function toggleTheme() {
    body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
    setThemeIcon();
}

themeToggle.addEventListener('click', toggleTheme);

// Check for saved theme preference
const savedDarkMode = localStorage.getItem('darkMode');

if (savedDarkMode === 'true') {
    body.classList.add('dark-mode');
}

setThemeIcon();

// Edit mode toggle functionality
const editModeToggle = document.getElementById('editModeToggle');
let editMode = false;

function toggleEditMode() {
    editMode = !editMode;
    editModeToggle.style.opacity = editMode ? '1' : '0.5';
    document.querySelectorAll('.edit-bookmark').forEach(button => {
        button.style.display = editMode ? 'block' : 'none';
    });
    document.querySelector('.add-bookmark').style.display = editMode ? 'block' : 'none';
}

editModeToggle.addEventListener('click', toggleEditMode);