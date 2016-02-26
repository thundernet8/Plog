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

    $("#main-menu>li.has-sub").each(function () {
       if($(this).hasClass('active')){
           $(this).addClass("expanded");
       }
    });
});

//scrollbar
$(function () {
    $('.ps-container').each(function (i, el) {
        Ps.initialize(el);
    });
});

//collapse sidebar/others
$(function () {
   $('a[data-toggle]').on('click', function () {
      var targetPrefix = $(this).data('toggle'),
          targetName = '.' + targetPrefix + '-menu';
       //console.log(targetName);
       //sidebar
       if(targetPrefix == 'sidebar'){
           $(targetName).toggleClass('collapsed');
       }
   });
});

//scroll top
$(function () {
   $('a[rel="go-top"]').on('click', function () {
      $('html, body').animate({scrollTop: 0}, 1000);
   });
});
