/* DraftedCV Digital CV – interactions. Data comes from cv-data.json via build.py. */
(function () {
    'use strict';
    var root = document.documentElement, body = document.body;
    var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    var page = document.getElementById('page');
    function setInert(on) { if (page) { if (on) page.setAttribute('inert', ''); else page.removeAttribute('inert'); } }
    var FOCUSABLE = 'a[href]:not([hidden]):not([style*="display: none"]), button:not([disabled]), [tabindex]:not([tabindex="-1"])';

    /* ---------- Theme: Dark / Light (follows the device until the visitor chooses) ---------- */
    function applyTheme(t) {
        body.classList.remove('mountain', 'traditional'); body.classList.add(t);
        root.setAttribute('data-theme', t);
        var light = t === 'traditional';
        document.querySelectorAll('.js-theme').forEach(function (b) {
            b.setAttribute('aria-pressed', String(light));
            b.setAttribute('aria-label', light ? 'Switch to dark theme' : 'Switch to light theme');
            var i = b.querySelector('.js-theme-icon'), l = b.querySelector('.js-theme-label');
            if (i) { i.classList.toggle('fa-sun', !light); i.classList.toggle('fa-moon', light); }
            if (l) l.textContent = light ? 'Dark' : 'Light';
        });
    }
    applyTheme(root.getAttribute('data-theme') || 'mountain');
    document.querySelectorAll('.js-theme').forEach(function (b) {
        b.addEventListener('click', function () {
            var t = body.classList.contains('traditional') ? 'mountain' : 'traditional';
            applyTheme(t); try { localStorage.setItem('cvTheme', t); } catch (e) {}
        });
    });

    /* ---------- Mobile menu ---------- */
    var menu = document.getElementById('mobileMenu'), menuBtn = document.getElementById('menuBtn'), burger = document.getElementById('hamburgerIcon');
    function setMenu(open) {
        if (!menu) return;
        menu.classList.toggle('hidden', !open);
        menuBtn.setAttribute('aria-expanded', String(open));
        menuBtn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
        burger.classList.toggle('fa-bars', !open); burger.classList.toggle('fa-xmark', open);
    }
    if (menuBtn) menuBtn.addEventListener('click', function () { setMenu(menu.classList.contains('hidden')); });
    if (menu) menu.addEventListener('click', function (e) { if (e.target.closest('a, button')) setMenu(false); });

    /* ---------- Scroll fade-in ---------- */
    var els = document.querySelectorAll('.scroll-animate');
    if (reduce || !('IntersectionObserver' in window)) els.forEach(function (el) { el.classList.add('visible'); });
    else {
        var io = new IntersectionObserver(function (entries) {
            entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('visible'); io.unobserve(en.target); } });
        }, { threshold: 0.1 });
        els.forEach(function (el) { io.observe(el); });
    }

    /* ---------- Dialog helper: focus trap, Esc, focus return ---------- */
    function trap(container, e) {
        if (e.key !== 'Tab') return;
        var f = Array.prototype.filter.call(container.querySelectorAll(FOCUSABLE), function (el) { return el.offsetParent !== null; });
        if (!f.length) { e.preventDefault(); return; }
        var first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }

    /* ---------- Project modal ---------- */
    var projects = window.CV_PROJECTS || [];
    var modal = document.getElementById('projectModal'), lastFocus = null;
    function onModalKey(e) { if (e.key === 'Escape') { e.preventDefault(); hideModal(); } else trap(modal, e); }
    function showModal(i) {
        var p = projects[i]; if (!p) return;
        lastFocus = document.activeElement;
        document.getElementById('modalTitle').textContent = p.title;
        document.getElementById('modalDescription').textContent = p.description;
        var tc = document.getElementById('modalTech'); tc.innerHTML = '';
        (p.tech || []).forEach(function (t) { var s = document.createElement('span'); s.className = 'tech-tag'; s.textContent = t; tc.appendChild(s); });
        var ok = function (u) { return u && u !== '#'; };
        var live = document.getElementById('modalLiveLink'), gh = document.getElementById('modalGithubLink');
        live.hidden = !ok(p.live); if (ok(p.live)) live.href = p.live;
        gh.hidden = !ok(p.github); if (ok(p.github)) gh.href = p.github;
        document.getElementById('modalNoLinks').hidden = ok(p.live) || ok(p.github);
        modal.classList.remove('hidden'); modal.classList.add('flex');
        setInert(true); root.classList.add('modal-open');
        document.addEventListener('keydown', onModalKey);
        document.getElementById('modalClose').focus();
    }
    function hideModal() {
        modal.classList.add('hidden'); modal.classList.remove('flex');
        setInert(false); root.classList.remove('modal-open');
        document.removeEventListener('keydown', onModalKey);
        if (lastFocus && lastFocus.focus) lastFocus.focus();
    }
    document.querySelectorAll('[data-project]').forEach(function (c) {
        c.addEventListener('click', function () { showModal(+c.getAttribute('data-project')); });
    });
    if (modal) {
        modal.addEventListener('click', function (e) { if (e.target === modal) hideModal(); });
        document.getElementById('modalClose').addEventListener('click', hideModal);
    }
    window.showProjectModal = showModal; window.hideProjectModal = hideModal;

    /* ---------- QR welcome screen ---------- */
    var w = document.getElementById('welcome'), wb = document.getElementById('welcomeBtn'), wFocus = null;
    function onWelcomeKey(e) {
        if (e.key === 'Escape' || ((e.key === 'Enter' || e.key === ' ') && document.activeElement === wb)) { e.preventDefault(); closeWelcome(); }
        else if (e.key === 'Tab') { e.preventDefault(); wb.focus(); }
    }
    function openWelcome(fromUser) {
        if (!w) return;
        wFocus = fromUser ? document.activeElement : null;
        w.hidden = false; w.classList.remove('welcome-hide');
        root.classList.remove('no-welcome'); root.classList.add('welcome-open');
        setInert(true); document.addEventListener('keydown', onWelcomeKey);
        wb.focus({ preventScroll: true });
    }
    function closeWelcome() {
        if (!w || w.classList.contains('welcome-hide')) return;
        w.classList.add('welcome-hide'); root.classList.remove('welcome-open');
        setInert(false); document.removeEventListener('keydown', onWelcomeKey);
        setTimeout(function () { w.hidden = true; }, reduce ? 0 : 350);
        if (wFocus && wFocus.focus) wFocus.focus(); else { var m = document.getElementById('main'); if (m) m.focus({ preventScroll: true }); }
    }
    if (w) {
        /* Tap anywhere except the QR itself (so long-press to share the QR still works) */
        w.addEventListener('click', function (e) { if (!e.target.closest('.welcome-qr')) closeWelcome(); });
        if (root.classList.contains('no-welcome')) { w.hidden = true; w.classList.add('welcome-hide'); }
        else openWelcome(false);
    }
    document.querySelectorAll('.js-show-qr').forEach(function (b) { b.addEventListener('click', function () { openWelcome(true); }); });

    /* ---------- PWA: offline support + home-screen install ---------- */
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function () { navigator.serviceWorker.register('sw.js').catch(function () {}); });
    }
})();
