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
        uindex: 0
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

reload_users();
api('basic', function (rsp) {
    SALT = rsp.user_salt;
})
