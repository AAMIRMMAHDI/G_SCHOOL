// templates/sw.js
self.addEventListener('push', function(event) {
    let data = {};
    if (event.data) {
        try {
            data = event.data.json();
        } catch (e) {
            data = {
                head: 'نوتیفیکیشن جدید',
                body: event.data.text()
            };
        }
    }

    const title = data.head || 'اعلان جدید';
    const options = {
        body: data.body || 'پیام جدیدی دریافت کردید.',
        icon: '/static/images/icon-192x192.png',  // بعداً ایکون اضافه کن
        badge: '/static/images/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        }
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});