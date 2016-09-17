function forEachSelector(selector, func) {
    [].forEach.call(document.querySelectorAll(selector), func)
}

function getScrollXY() {
    var x = (window.pageXOffset !== undefined)
        ? window.pageXOffset
        : (document.documentElement || document.body.parentNode || document.body).scrollLeft;
    var y = (window.pageYOffset !== undefined)
        ? window.pageYOffset
        : (document.documentElement || document.body.parentNode || document.body).scrollTop;
    return { x: x, y: y }
}

function genPassword() {
    return (Math.random().toString(36).slice(-8)) + (Math.random().toString(36).slice(-8))
}

function user_gen(input_ids) {
    var ps = genPassword()
    input_ids.forEach(function(id){
        var e=document.getElementById(id)
        e.value = ps
        e.type = 'text'
    })
}

function showRandomPassword() {
    prompt('Copy and paste into the field.', genPassword())
}

+ function () {
    function flick_handler() {
        var xy = getScrollXY()
        localStorage['yuck__flick'] = JSON.stringify({
            url: window.location.href, x: xy.x, y: xy.y
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

    forEachSelector('a.flick', function (link) {
        link.addEventListener('click', flick_handler, false)
    })
} ();

+ function () {
    //smart date input notify

    var inited = 0, div, input;
    function init() {
        if (inited) return

        var today = new Date()

        div = document.createElement('div')
        div.id = 'smartdate-box'
        div.className = 'yuck-absolute'
        div.classList.add('hidden')
        div.innerHTML = [
            '<p>input the date like <code class="use-this">' + today.getFullYear() + '-' + (1+today.getMonth()) + '-' + today.getDate() + '</code></p>',
            '<p>or an expression relative to <b>last trigged time</b></p>', 
            '<ul>',
            '<li><code class="use-this">next month</code> <code class="use-this">next week</code> <code class="use-this">next day</code></li>',
            '<li><code class="use-this">+2month 15days</code> <code class="use-this">+7d</code></li>',
            '</ul>' 
        ].join('')

        document.body.appendChild(div)

        function usethis(ev) {
            var e=ev.target
            input.value=e.getAttribute('data-data')||e.textContent
            input.focus()
        }
        forEachSelector('#smartdate-box .use-this', function(e) {
            e.addEventListener('click', usethis, false)
        })

        inited = !0
    }

    function show(e) {
        var b = e.target.getBoundingClientRect(), xy = getScrollXY()
        init()
        input = e.target
        div.style.left = (b.left + xy.x) + 'px'
        div.style.top = (b.bottom + xy.y) + 'px'
        div.classList.remove('hidden')
    }

    var hiding = 0
    function hide(e) {
        if (!hiding) clearTimeout(hiding)
        hiding = setTimeout(hide2, 200)
    }

    function hide2() {
        var ae = document.activeElement;
        hiding = 0
        if (ae.matches('input[data-smartdate], #smartdate-box, #smartdate-box *')) return
        div.classList.add('hidden')
    }

    forEachSelector('input[data-smartdate]', function (input) {
        input.addEventListener('focus', show, false)
        input.addEventListener('blur', hide, false)
    })
} ();
