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
//$(function () {
//   $("a[data-toggle='dropdown']").on('click blur', function () {
//       var toggle = $(this).data('toggle');
//      $(this).closest('.'+toggle).toggleClass('open');
//   });
//});
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

//获取 localStorage 中的 access_token
exports.getStoredAccessToken = function () {
    var secureInfo = localStorage.getItem('Plog:Token');
    secureInfo = JSON.parse(secureInfo);
    return secureInfo.access_token || '';
};

//获取站点 url
exports.getSiteUrl = function () {
    return window.location.protocol + '//' + window.location.host;
};

//获取站点API url
exports.getAPIUrl = function () {
    return window.location.protocol + '//' + window.location.host + '/api/v1.0';
};

//获取后台 url
exports.getDashUrl = function () {
    return window.location.protocol + '//' + window.location.host + '/dashboard';
};