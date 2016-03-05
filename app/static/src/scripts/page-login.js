"use strict";

/**
 * 登录页脚本
 */

var $ = require('jquery');
var common = require('./utils/common');

var siteUrl = window.location.protocol + '//' + window.location.host,
    loginApiUrl = siteUrl + '/api/v1.0/login';

//validate

var usernameInput = $('input#username'),
    passInput = $('input#password'),
    //autofillPassInput = $('input#password:-webkit-autofill'),
    submitBtn = $('button#login-btn');

function validateUsername(name){
    var reg = /^[A-Za-z][A-Za-z0-9_]{4,}$/; //用户名以字母开头,只能包含英文/数字/下划线,长度5及5以上
    return reg.test(name);
}

function validatePass(password){
    var reg = /^[\S]{6,}$/;
    return reg.test(password);
}

function checkAll(){
    if(!validateUsername(usernameInput.val())){
        usernameInput.focus();
        console.log('username invalid');
        return false;
    }
    if(!validatePass(passInput.val())){
        //passInput.focus();
        console.log('password invalid');
        return false;
    }
    return true;
}

$(function(){
    $.each([usernameInput, passInput], function(){
          $(this).keyup(function(){
                if(checkAll()){
                    submitBtn.prop('disabled', false);
                }else{
                    submitBtn.prop('disabled', true);
                }
          });
    });
});

$(document).ready(function(){
    setTimeout(function () {
        passInput.val('');//清除自动填充的密码等
    }, 100);
});


//Ajax login request
$(function () {
   submitBtn.on('click', function () {
     var username = usernameInput.val(),
         password = passInput.val();
       $.ajax({
           method: 'POST',
           url: loginApiUrl,
           data: {username: username, password: password},
           dataType: 'json',
           timeout: 30000,
           beforeSend: function(){
             submitBtn.prop('disabled', true).text('登录中...');
           },
           error: function(){
             passInput.val('');
             submitBtn.text('登录').prop('disabled', true);
           },
           success: function(data){
               console.log(data);
               console.log(common.getUrlPara('redirect'));
             if(data.success && data.success==1){
                  submitBtn.text('登录成功');
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
                  setTimeout(function () {
                      var href = common.getUrlPara('redirect') ? (decodeURIComponent(common.getUrlPara('redirect')).indexOf("http") == 0 ? decodeURIComponent(common.getUrlPara('redirect')) : common.getSiteUrl() + decodeURIComponent(common.getUrlPara('redirect'))) : common.getSiteUrl();
                      //console.log(href);
                      window.location.href = href;
                  }, 1500);
             }else{
                 passInput.val('');
                 submitBtn.text('登录').prop('disabled', true);
                 alert(data.message);
             }
           }
       }).done(function () {
           submitBtn.text('登录');
       });
   });
});
