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
        limit: []
    }
};
app = new Vue({
    el: '#main-ptl',
    data: app,
    methods: {
        suspend: function (i) {
            var u = app.users[i];
            api('user/suspend', { username: u.username, suspend: u.suspended ? 0 : 1 }, function (rtn) { u.suspended = rtn.suspended ? true : false })
        },
        user_del: function (i) {
            var u = app.users[i];
            if (!confirm('Delete user ' + u.username + '?')) return false;
            api('user/del', { username: u.username }, function (rtn) { app.users.splice(i, 1); })
        },
        lim_open: function (i) {
            app.app.uindex = i;
            app.app.limit = (app.users[i].meta.limit || []).slice();
            setTimeout(function() { UIkit.switcher('#main-ptl').show(1); }, 100);
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

function _sskey_callback(rtn) {
    UIkit.modal("#sskey").hide();
    app.users[app.app.uindex].sskey = $('#sskey [name=sskey]').val();
}
$('#sskey form').submit(function () {
    api('user/sskey', {
        sskey: $('#sskey [name=sskey]   ').val(),
        username: $('#sskey [name=username]').val()
    }, _sskey_callback);
    return false;
})

$('#user_add').submit(function () {
    var un = $('#user_add [name=username]').val();
    if (app.users.some(function(ck) {return ck.username == un})) return false;
    
    api('user/add', {
        sskey: $('#user_add [name=sskey]   ').val(),
        username: un,
        password: $('#user_add [name=password]').val()
    }, reload_users);
    return false;
})


$('#traffic-view').submit(function() {
    alert('Not implemented yet')
    return false;
})

var limSinceFormat = /^(this-(week|month)|\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})$/;
$('#lim-editor-submit').click(function() {
    var u = app.users[app.app.uindex];
    
    if (!app.app.limit.every(function(r){
        return (limSinceFormat.test(r.since));
    })) {
        alert("A rule has invalid time param!");
        return false;
    }
    
    api('user/limit', {
        username: u.username,
        limit: JSON.stringify(app.app.limit)
    }, function(){
        UIkit.notify('Modified');
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
