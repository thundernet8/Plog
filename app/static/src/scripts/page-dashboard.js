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

//appearance - navigations
//delete nav item
$(function () {
   $('button.nav-delete').on('click', function () {
      var delNav = $(this).parent('.nav-item');
      if (delNav.hasClass('primary-nav')){
          delNav.nextAll().each(function () {
             if($(this).hasClass('sub-nav')){
                 $(this).remove();
             } else {
                 return false;
             }
          });
          delNav.remove();
      } else {
        delNav.remove();
      }
   });
});

//add nav item input field
$(function () {
   $('button.nav-add').on('click', function () {
      var currentNavItem = $(this).parent('.nav-item'),
          copyNavItem = currentNavItem.clone(true),
          blankInput = false;
      currentNavItem.find('input').each(function () {
          if (!$(this).val()){
              blankInput = true;
          }
      }) ;
      if (!blankInput){
          currentNavItem.find('.nav-add').remove();
          copyNavItem.find('input').each(function () {
             $(this).val('');
          });
          //copyNavItem.find('.nav-add').remove();
          currentNavItem.after(copyNavItem);
      }
   });
});

//submit nav setting
$(function () {
   $('#setting-navigations #submit').on('click', function () {
       //e.preventDefault();
       var form = $('#setting-navigations'),
           navi = {"navigations": []},
           hasPrimary = false,
           name, url, item, currentSub;
       form.find('.nav-item').each(function () {
           name = $(this).find('input').first().val();
           url = $(this).find('input').last().val();
           if (!name || !url) return true;
           item = {};
           item[name] = url;
           if($(this).hasClass('primary-nav') || !hasPrimary){
               hasPrimary = true;
               navi["navigations"].push({
                   "primary": item
               });
           } else {
               currentSub = navi["navigations"][navi["navigations"].length-1]['sub'];
               if (currentSub && currentSub instanceof Array){
                   currentSub.push(item);
               }else{
                   currentSub = [item];
               }
               navi["navigations"][navi["navigations"].length-1]['sub'] = currentSub;
           }
       });
       navi = JSON.stringify(navi);
       //console.log(navi);
       $('#setting-value').val(navi);
       form.submit();
   }) ;
});

//appearance - links
//delete link item
$(function () {
   $('button.link-delete').on('click', function () {
      var delLink = $(this).parent('.link-item');
      delLink.remove();
   });
});

//add link item input field
$(function () {
   $('button.link-add').on('click', function () {
      var currentLinkItem = $(this).parent('.link-item'),
          copyLinkItem = currentLinkItem.clone(true),
          blankInput = false;
      currentLinkItem.find('input').each(function () {
          if (!$(this).val()){
              blankInput = true;
          }
      }) ;
      if (!blankInput){
          currentLinkItem.find('.link-add').remove();
          copyLinkItem.find('input').each(function () {
             $(this).val('');
          });
          currentLinkItem.after(copyLinkItem);
      }
   });
});

//submit link setting
$(function () {
   $('#setting-links #submit').on('click', function () {
       //e.preventDefault();
       var form = $('#setting-links'),
           links = {"links": []},
           name, url, item;
       form.find('.link-item').each(function () {
           name = $(this).find('input').first().val();
           url = $(this).find('input').last().val();
           if (!name || !url) return true;
           item = {};
           item[name] = url;
           links["links"].push(item);
       });
       links = JSON.stringify(links);
       console.log(links);
       $('#setting-value').val(links);
       form.submit();
   }) ;
});