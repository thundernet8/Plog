"use strict";
var $ = require('./libs/jquery/2.2.0/jquery.js');

var siteUrl = window.location.protocol + '//' + window.location.host,
    loginApiUrl = siteUrl + '/api/v1.0/register';

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
    }, 300);
});

