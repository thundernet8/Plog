"use strict";
var $ = require('jquery');

$(function () {
    //跳转登录页添加 redirect 链接
   $('.bind-redirect').on('click', function (e) {
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

//dropdown菜单
$(function () {
   $("a[data-toggle='dropdown']").on('click', function () {
       var toggle = $(this).data('toggle');
      $(this).closest('.'+toggle).toggleClass('open');
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