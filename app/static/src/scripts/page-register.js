"use strict";
var $ = require('./libs/jquery/2.2.0/jquery.js');

var siteUrl = window.location.protocol + '//' + window.location.host,
    registerApiUrl = siteUrl + '/api/v1.0/register';

//validate

var usernameInput = $('input#username'),
    emailInput = $('input#email'),
    passInput = $('input#password'),
    pass2Input = $('input#password2'),
    submitBtn = $('button#register-btn'),
    successTip = $('p#success-tip');

function validateUsername(name){
    var reg = /^[A-Za-z][A-Za-z0-9_]{4,}$/; //用户名以字母开头,只能包含英文/数字/下划线,长度5及5以上
    return reg.test(name);
}

function validateEmail(email){
    var reg = /^([a-zA-Z0-9_-])+@([a-zA-Z0-9_-])+(.[a-zA-Z0-9_-])+$/;
    return reg.test(email);
}

function validatePass(password){
    var reg = /^[\S]{6,}$/;
    return reg.test(password);
}

function checkAll(){
    if(!validateUsername(usernameInput.val())){
        usernameInput.focus();
        return false;
    }
    if(!validateEmail(emailInput.val())){
        //emailInput.focus();
        return false;
    }
    if(!validatePass(passInput.val())){
        //passInput.focus();
        return false;
    }
    if(!validatePass(pass2Input.val())){
        //pass2Input.focus();
        return false;
    }
    if(passInput.val() !== pass2Input.val()){
        //pass2Input.focus();
        return false;
    }
    return true;
}

$(function(){
    $.each([usernameInput, emailInput, passInput, pass2Input], function(){
          $(this).keyup(function(){
                if(checkAll()){
                    submitBtn.prop('disabled', false);
                }else{
                    submitBtn.prop('disabled', true);
                }
          });
    });
});


//ajax register

$(function () {
   submitBtn.on('click', function () {
       var username = usernameInput.val(),
           email = emailInput.val(),
           password = passInput.val();
       $.ajax({
           method: 'POST',
           url: registerApiUrl,
           data: {username: username, email: email, password: password},
           dataType: 'json',
           timeout: 60,
           beforeSend: function(){
               submitBtn.prop('disabled', true).text('注册中...');
           },
           success: function(data){
               if(data.success && data.success==1){
                   alert('注册成功');
                   window.location.href = siteUrl;
               }else{
                   passInput.val('');
                   pass2Input.val('');
                   alert(data.message);
               }
           },

       }).done(function(){
           submitBtn.text('发送注册邮件');
       })

   }) ;
});
