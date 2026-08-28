document.addEventListener('DOMContentLoaded', function() {
    // 1. Notification Dropdown Toggle & AJAX Fetch
    const notifBtn = document.getElementById('notifBellBtn');
    const notifDropdown = document.getElementById('notifDropdown');

    if (notifBtn && notifDropdown) {
        notifBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notifDropdown.classList.toggle('active');
            if (notifDropdown.classList.contains('active')) {
                fetchNotifications();
            }
        });

        document.addEventListener('click', function(e) {
            if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
                notifDropdown.classList.remove('active');
            }
        });
    }

    function fetchNotifications() {
        fetch('/api/notifications')
            .then(res => res.json())
            .then(data => {
                const badge = document.getElementById('notifBadgeCount');
                if (badge) {
                    if (data.unread_count > 0) {
                        badge.textContent = data.unread_count;
                        badge.style.display = 'inline-block';
                    } else {
                        badge.style.display = 'none';
                    }
                }

                const list = document.getElementById('notifList');
                if (list) {
                    if (data.notifications.length === 0) {
                        list.innerHTML = '<div style="padding: 16px; text-align: center; color: #64748b; font-size: 0.85rem;">No notifications found</div>';
                        return;
                    }
                    list.innerHTML = data.notifications.map(n => `
                        <a href="${n.link}" class="notif-item ${n.is_read ? 'read' : 'unread'}" style="display: flex; flex-direction: column; padding: 12px 16px; border-bottom: 1px solid #e2e8f0; ${n.is_read ? '' : 'background-color: #f0fdf4;'}">
                            <span style="font-size: 0.85rem; color: #0f172a; font-weight: ${n.is_read ? '500' : '600'};">${n.message}</span>
                            <span style="font-size: 0.72rem; color: #64748b; margin-top: 4px;">${n.created_at}</span>
                        </a>
                    `).join('');
                }
            })
            .catch(err => console.error('Error fetching notifications:', err));
    }

    const markReadBtn = document.getElementById('markAllReadBtn');
    if (markReadBtn) {
        markReadBtn.addEventListener('click', function() {
            fetch('/api/notifications/read-all', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        fetchNotifications();
                    }
                });
        });
    }

    // 2. Global Search Modal
    const searchTrigger = document.getElementById('globalSearchTrigger');
    const searchModal = document.getElementById('globalSearchModal');
    const searchInput = document.getElementById('globalSearchInput');
    const searchResults = document.getElementById('globalSearchResults');

    if (searchTrigger && searchModal) {
        searchTrigger.addEventListener('click', function() {
            searchModal.classList.add('active');
            if (searchInput) searchInput.focus();
        });

        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                searchModal.classList.add('active');
                if (searchInput) searchInput.focus();
            }
            if (e.key === 'Escape' && searchModal.classList.contains('active')) {
                searchModal.classList.remove('active');
            }
        });

        const closeModalBtn = searchModal.querySelector('.close-modal');
        if (closeModalBtn) {
            closeModalBtn.addEventListener('click', function() {
                searchModal.classList.remove('active');
            });
        }
    }

    if (searchInput && searchResults) {
        let debounceTimer;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            const query = this.value.trim();
            if (query.length < 2) {
                searchResults.innerHTML = '<div style="padding: 20px; text-align: center; color: #64748b; font-size: 0.9rem;">Type at least 2 characters to search...</div>';
                return;
            }

            searchResults.innerHTML = '<div style="padding: 20px; text-align: center; color: #64748b;"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';

            debounceTimer = setTimeout(() => {
                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        if (!data.results || data.results.length === 0) {
                            searchResults.innerHTML = '<div style="padding: 20px; text-align: center; color: #64748b;">No matching results found</div>';
                            return;
                        }

                        searchResults.innerHTML = data.results.map(r => `
                            <a href="${r.url}" class="search-result-item" style="display: flex; align-items: center; gap: 14px; padding: 12px 16px; border-bottom: 1px solid #e2e8f0; border-radius: 8px; margin-bottom: 4px; transition: background 0.2s;">
                                <div style="width: 36px; height: 36px; border-radius: 8px; background: #e0e7ff; color: #4f46e5; display: flex; align-items: center; justify-content: center;">
                                    <i class="fas ${r.icon}"></i>
                                </div>
                                <div style="flex: 1;">
                                    <div style="font-weight: 600; font-size: 0.9rem; color: #0f172a;">${r.title} <span style="font-size: 0.75rem; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; color: #475569; font-weight: 700;">${r.code}</span></div>
                                    <div style="font-size: 0.78rem; color: #64748b;">${r.subtitle} • <span style="color: #4f46e5; font-weight: 600;">${r.type}</span></div>
                                </div>
                            </a>
                        `).join('');
                    });
            }, 300);
        });
    }

    // 3. Auto-hide Toast Notifications
    const toasts = document.querySelectorAll('.toast-alert');
    toasts.forEach(toast => {
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(20px)';
            setTimeout(() => toast.remove(), 300);
        }, 4500);
    });
});
