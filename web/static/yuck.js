+function () {
    function flick_handler() {
        var x = (window.pageXOffset !== undefined)
            ? window.pageXOffset
            : (document.documentElement || document.body.parentNode || document.body).scrollLeft;
        var y = (window.pageYOffset !== undefined)
            ? window.pageYOffset
            : (document.documentElement || document.body.parentNode || document.body).scrollTop;

        localStorage['yuck__flick'] = JSON.stringify({
            url: window.location.href, x: x, y: y
        })
    }

    try {
        var last_flick = JSON.parse(localStorage['yuck__flick'])
        if (last_flick.url === window.location.href) {
            window.scrollTo(last_flick.x, last_flick.y)
            localStorage['yuck__flick'] = ''
        }
    } catch (err) {
    }

    [].forEach.call(document.querySelectorAll('a.flick'), function (link) {
        link.addEventListener('click', flick_handler, false)
    })
}()
