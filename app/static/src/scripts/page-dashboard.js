"use strict";

/**
 * 后台脚本
 */

var $ = require('jquery');
var common = require('./utils/common');
//scrollbar plugin
var Ps = require('perfect-scrollbar');
//Markdown 解析器
var mdParser = require('markdown').markdown;
//加载指示器
var loader = require('./utils/loader').loaderIndicator;
//Token 监视器
var tokenMonitor = require('./utils/token-monitor');
//图片上传
var upload = require('./utils/upload');

//监视 token
$(function () {
   tokenMonitor();
});

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

//浏览器滚动条
$(function () {
    $('.ps-container').each(function (i, el) {
        Ps.initialize(el);
    });
});

//折叠边栏等
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

//回到顶部
$(function () {
   $('a[rel="go-top"]').on('click', function () {
      $('html, body').animate({scrollTop: 0}, 1000);
   });
});

//外观 - 顶部导航
//删除导航项目
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

//添加导航设置输入框
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

//提交导航菜单设置
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

//外观 - 底部链接菜单
//删除链接条目
$(function () {
   $('button.link-delete').on('click', function () {
      var delLink = $(this).parent('.link-item');
      delLink.remove();
   });
});

//添加链接设置输入框
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

//提交链接设置
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
       //console.log(links);
       $('#setting-value').val(links);
       form.submit();
   }) ;
});

//文章
//文章编辑 - 自动生成预览
$(function () {
   if (!$('body').hasClass('dashboard-post-edit')) return;
   var mdTextarea = $('.entry-markdown textarea'),
       previewArea = $('.entry-preview .rendered-markdown'),
       countBoard = $('.entry-word-count'),
       md, html;
    function parseMarkdown() {
        md = mdTextarea.val();
        html = mdParser.toHTML(md);
        //console.log(html);
        previewArea.html(html);
        countBoard.text(previewArea.text().length.toString() + '个字');
    }
    parseMarkdown();
    mdTextarea.keyup(parseMarkdown);
});

//发布按钮下拉框
$(function () {
   $('button.dropdown-toggle').on('click', function () {
       if ($(this).hasClass('closed')){
           $(this).removeClass('closed').addClass('open');
           $(this).next().removeClass('fade-out closed').addClass('fade-in-scale open');
       }else{
           $(this).removeClass('open').addClass('closed');
           $(this).next().removeClass('fade-in-scale open').addClass('fade-out closed');
       }
   }) ;

   $('ul.dropdown-menu>li').on('click', function () {
       var $this = $(this),
           action = $this.data('action');
       $this.siblings().removeClass('active').end().addClass('active').closest('.splitbtn').children().first()
           .text($this.text()).toggleClass('btn-info btn-danger').data('action', action).next().toggleClass('btn-info btn-danger').trigger('click');
   });
});

//发布或保存文章
$(function () {
    $('.publish-button').on('click', function () {
       var btn = $(this),
           action = btn.data('action'),
           titleInput = $('#entry-title'),
           title = titleInput.val(),
           markdown = $('.entry-markdown textarea').val();
        if(title == ''){
            titleInput.focus();
            return;
        }


    });
});

//侧滑文章选项面板
$(function () {
    if($('button.post-settings').length > 0){
        var postSettingPannelTrigger = $('button.post-settings');
            //closeSettingPannelTrigger = $('.post-settings-menu button.close');
        postSettingPannelTrigger.on('click', function (e) {
            $('body').removeClass('post-setting-menu-expanded').addClass('post-setting-menu-expanded');
            e.stopPropagation();
        });
        //closeSettingPannelTrigger.on('click', function () {
        //   $('body').removeClass('post-setting-menu-expanded');
        //});
        $('body').on('click', '.page-container, .post-settings-menu button.close', function () {
            $('body').removeClass('post-setting-menu-expanded');
        });
    }

});

//文章选项面板博文地址预览
$(function () {
   $('input[name="post-setting-slug"]').keyup(function () {
       var slug = $(this).val();
       var previewDiv = $(this).parent().next();
       previewDiv.text(common.getSiteUrl() + '/' + encodeURIComponent(slug));
   }) ;
});

//文章选项面板标签处理
$(function () {
    var select = $('#tag-input');
    var itemsWrap = $('.selectize-items');
    var tags = [];
    var updateSelectOptions = function(){
        select.html('');
        tags = [];
        itemsWrap.children('.item').each(function () {
            select.append('<option value="' + $(this).data('value') + '" selected="selected">' + $(this).text().replace('×', '') + '</option>');
            tags.push($(this).text().replace('×', ''));
        })
    };
    updateSelectOptions();

    itemsWrap.on('click', 'a.remove', function () {
       $(this).parent().remove();
        updateSelectOptions();
    });
    itemsWrap.children('input').keyup(function (e) {
        var $this = $(this);
        var newTag;
        if(e.keyCode==13 && $this.val()){
            if(tags.indexOf($this.val()) != -1 ){
                alert('请勿重复添加标签');
            }else{
                $.ajax({
                    url: common.getSiteUrl()+'/api/v1.0/tags/' + $this.val(),
                    method: 'put',
                    dataType: 'json',
                    beforeSend: function(xhr){
                        xhr.setRequestHeader('Authorization', "Bearer "+common.getStoredAccessToken());
                    },
                    success: function(data){
                        console.log(data);
                        if(!data.success && data.message) alert(data.message);
                        if(!data.success || !data.tagId) return;
                        newTag = '<div data-value="' + data.tagId + '" class="item">' + $this.val() + '<a href="javascript:void(0)" class="remove" tabindex="-1" title="移除">×</a></div>';
                        $this.before(newTag);
                        $this.val('');
                        updateSelectOptions();
                    },
                    error: function(data){
                        console.log('error');
                    }
                })
            }

        }
    });
});

//提交文章
$(function () {
    var submitBtn = $('.dashboard-post-edit button.publish-button');
    var title, markdown, pidToken, slug, metaTitle, metaDescription, thumbUrl, postType, tags, action;

    function updatePostData(){
        title = $('input#entry-title').val() || 'Untitled';
        markdown = $('#entry-markdown-content textarea').val();
        pidToken = $('input#entry-pid-token').val();
        thumbUrl = $('img.js-upload-target').attr('src');
        slug = $('input[name="post-setting-slug"]').val();
        slug = encodeURIComponent(slug);
        metaTitle = $('#meta-title').val();
        metaDescription = $('#meta-descrition').val();
        postType = $('input#static-page').is(':checked') ? 'page':'post';
        tags = $('select#tag-input').val();
        action = submitBtn.data('action') == 'publish' ? 'publish':'draft';
    }

    if(submitBtn){
        submitBtn.on('click', function () {
            updatePostData();
            $.ajax({
                url: common.getAPIUrl + '/posts',
                method: 'post',
                dataType: 'json',
                data: {
                    title: title,
                    markdown: markdown,
                    pidToken: pidToken,
                    thumbUrl: thumbUrl,
                    slug: slug,
                    metaTitle: metaTitle,
                    metaDescription: metaDescription,
                    postType: postType,
                    tags: tags,
                    action: action
                },
                beforeSend: function(xhr){
                    xhr.setRequestHeader('Authorization', "Bearer "+common.getStoredAccessToken());
                },
                success: function(data){

                },
                error: function(data){

                }
            })
        })
    }
});
