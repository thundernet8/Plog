"use strict";
var $ = require('./libs/jquery/2.2.0/jquery.js');

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
        emailInput.focus();
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


