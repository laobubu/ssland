/// <reference path="../../typings/vue/vue.d.ts" />
/// <reference path="../../typings/jquery/jquery.d.ts" />

var app = {
    "users": [
        {
            "id": 1,
            "username": "test",
            "port": 1234,
            "suspended": 0,
            "salted_password": "xxxxx",
            "sskey": "test",
            "since": 0,
            "meta": {
                "limit": [
                    { "amount": 0, "since": "2016-05-01 00:00:00", "type": "time" }
                ]
            }
        }
    ],
    "app": {
        uindex: 0,
        limit: [],
        stat: [],
        stat_scale: 100,
        stat_filter: ''
    }
};
app = new Vue({
    el: '#main-ptl',
    data: app,
    methods: {
        suspend: function (i,ev) {
            var u = app.users[i];
            var reason = (!u.suspended && !ev.ctrlKey) ? prompt("Reason to suspend?\n (Click the button with Ctrl to skip this)") : "";
            if (reason === null) return;
            api('user/suspend', { 
                username: u.username, 
                suspend: u.suspended ? 0 : 1,
                reason: reason 
            }, function (rtn) { u.suspended = rtn.suspended ? true : false })
        },
        user_del: function (i) {
            var u = app.users[i];
            if (!confirm('Delete user ' + u.username + '?')) return false;
            api('user/del', { username: u.username }, function (rtn) { app.users.splice(i, 1); })
        },
        lim_open: function (i,ev) {
            app.app.uindex = i;
            app.app.limit = (app.users[i].meta.limit || []).slice();
            var ref = $(ev.target.parentElement.parentElement);
            if (ref[0].nextElementSibling == limEditor[0]) limEditor.toggle();
            else {
                limEditor.insertAfter(ref);
                limEditor.show();
            }
        },
        tiblur: function (ev, obj, par) {
            ev.target.value = obj[par]
        },
        ticonfirm: function (ev, obj, par, apiName, pl) {
            if (ev.keyCode != 13) return;
            ev.preventDefault();
            pl = pl || {};
            pl.value = ev.target.value;
            api(apiName, pl, function() {
                obj[par] = ev.target.value;
                ev.target.blur();
            });
        },
        humanFileSize: function (bytes, si) {
            var thresh = si ? 1000 : 1024;
            if(Math.abs(bytes) < thresh) {
                return bytes + ' B';
            }
            var units = si
                ? ['kB','MB','GB','TB','PB','EB','ZB','YB']
                : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
            var u = -1;
            do {
                bytes /= thresh;
                ++u;
            } while(Math.abs(bytes) >= thresh && u < units.length - 1);
            return bytes.toFixed(1)+' '+units[u];
        },
        sumAmount: function(arr, filter) {
            return arr.reduce(function(prev,i){
                if (filter && !i.title.match(filter)) return prev;
                return (i.amount||0) + prev
            }, 0)
        }
    }
});

var SALT = "";

function api(name, payload, callback) {
    var uri = '/admin/' + name;
    if (callback) $.post(uri, payload, callback);
    else $.post(uri, payload);
}

function reload_users() { api('user/list', function (rtn) { app.users = rtn.list }) }

function _cli_callback(rtn) {
    var result = rtn.output;
    if (rtn.retval) result = "Exited with code " + rtn.retval + "\n\n" + result;
    $('#cli pre').text(result);
}

$('#cli').submit(function () {
    $('#cli pre').text('Loading...');
    api('cli', { cmd: $('#cli input').val() }, _cli_callback);
    return false;
})

function _passwd_callback(rtn) {
    UIkit.modal("#passwd").hide();
    $('#passwd [name=password]').val('');
    UIkit.notify("Password for " + $('#passwd [name=username]').val() + " changed.");
}
$('#passwd form').submit(function () {
    api('user/passwd', {
        password: $('#passwd [name=password]').val(),
        username: $('#passwd [name=username]').val()
    }, _passwd_callback);
    return false;
})


function new_user_gen() {
    setTimeout(function() {
        $('#user_add [name=username]').focus();
        $('#user_add [name=sskey]').val(md5(Math.random()));
    }, 100);
}
$('#user_add').submit(function () {
    var un = $('#user_add [name=username]').val();
    if (app.users.some(function(ck) {return ck.username == un})) {
        alert('User exists');
        return false;
    }
    
    api('user/add', {
        sskey: $('#user_add [name=sskey]').val(),
        username: un,
        password: $('#user_add [name=password]').val()
    }, function(){
        UIkit.notify('User created. Please apply to SS');
        $('#user_add [name=password]').val('');
        $('#useradd').hide('');
        reload_users();
    });
    return false;
})


$('#traffic-view').submit(function() {
    var $frm = $('#traffic-view');
    app.app.stat = [ { title: "Loading", data: [] } ]
    api('tx/query', {
        from: $('[name=from]', $frm).val(),
        to: $('[name=to]', $frm).val()
    }, function(data) {
        app.app.stat = data;
    })
    return false;
})

var limEditor = $('#lim-editor').hide();

var limSinceFormat = /^(this-(week|month)|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$/;
$('#lim-editor-submit').click(function() {
    var u = app.users[app.app.uindex];
    
    if (!app.app.limit.every(function(r){
        r.amount = parseInt(r.amount);
        return (limSinceFormat.test(r.since));
    })) {
        alert("A rule has invalid time param!");
        return false;
    }
    
    api('user/limit', {
        username: u.username,
        limit: JSON.stringify(app.app.limit)
    }, function(){
        UIkit.notify('Restriction rules are confirmed.');
        u.meta.limit = app.app.limit.slice();
    })
    return false;
})

function sys_restart() {
    api('restart',function(rsp){UIkit.notify('System will restart in '+rsp.time+' sec.')})
}

reload_users();
api('basic', function (rsp) {
    SALT = rsp.user_salt;
})
