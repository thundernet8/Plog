"use strict";

var $ = require('jquery');

var siteUrl = window.location.protocol + '//' + window.location.host,
    refreshTokenUrl = siteUrl + '/api/v1.0/authentication/refresh',
    loginUrl = siteUrl + '/login.do';

//监听 token 等用于授权的信息
module.exports = function () {
    var secureInfo, access_token, refresh_token, expires_at, time;

    function checkTokenStatus(){
        console.log('check token status');
        secureInfo = JSON.parse(localStorage.getItem('Plog:Token'));
        access_token = secureInfo.access_token || '';
        refresh_token = secureInfo.refresh_token || '';
        expires_at = secureInfo.expires_at || 0;
        time = parseInt(new Date().getTime()/1000);
        if(!access_token || !refresh_token) return;
        if(parseInt(expires_at)-time>300) return;
        refreshToken(refresh_token);
    }

    function refreshToken(refresh_token){
        $.ajax({
            url: refreshTokenUrl,
            method: 'post',
            dataType: 'json',
            data: {
                refresh_token: refresh_token
            },
            success: function(data){
                if(!data.access_token){
                    location.href = loginUrl;
                    return;
                }
                //存储 token 到 localStorage
                  var secureInfo = {
                    plog_authenticator: 'password_grant',
                    access_token: data.access_token,
                    expires_in: data.expires_in,
                    expires_at: data.expires_at,
                    refresh_token: data.refresh_token,
                    token_type: data.token_type
                  };
                 localStorage.setItem('Plog:Token', JSON.stringify(secureInfo));
            }
        })
    }

    setInterval(checkTokenStatus, 60000);
};