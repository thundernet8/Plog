"use strict";
var $ = require('jquery');

$(function () {
    //跳转登录页添加 redirect 链接
   $('a.login-link').on('click', function (e) {
        e.preventDefault();
        var loginLink = $(this).attr('href');
        loginLink = loginLink + '?redirect=' + encodeURIComponent(window.location.pathname);
        window.location.href = loginLink;
    });

    //输入框等聚焦提示
    $('[data-focus]').on('focus', function () {
        $($(this).data('focus')).slideDown();
    }).on('blur', function () {
        $($(this).data('focus')).slideUp();
    });
});

//获取 url 中的 get 参数
exports.getUrlPara = function (name ,url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
    var regexS = "[\\?&]" + name + "=([^&#]*)";
    var regex = new RegExp(regexS);
    var results = regex.exec(url);
    return results == null ? null : results[1];
};