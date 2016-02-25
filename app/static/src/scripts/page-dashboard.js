"use strict";

/**
 * 后台脚本
 */

var $ = require('jquery');

//scrollbar plugin
var Ps = require('perfect-scrollbar');

var siteUrl = window.location.protocol + '//' + window.location.host;


//边栏二级菜单展开
$(function () {
    $("#main-menu>li.has-sub").on('click', function () {
       $(this).toggleClass('expanded');
    });
});

//scrollbar
$(function () {
    $('.ps-container').each(function (i, el) {
        Ps.initialize(el);
    });
});