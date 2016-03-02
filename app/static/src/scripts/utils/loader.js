"use strict";

//加载指示器

var $ = require('jquery');

exports.loaderIndicator = function (loaderImg, text, backLayer) {
    this.backLayer = backLayer || '<div class="loader-background"></div>';
    this.loaderImg = loaderImg || '/static/dist/images/loader.gif';
    this.text = text || '';
    this.isShowing = false;
    this.show = function () {
        if(this.isShowing) return;
        $('body').append(this.backLayer.substr(0, this.backLayer.length-6) + '<div class="loader">' + '<img class="loader-img" src="' + this.loaderImg + '">' + '<div class="loader-text">' + this.text + '</div>' + '</div>' + '</div>');
        this.isShowing = true;
    };
    this.hide = function () {
      if($('.loader').length > 0){
          $('.loader').remove();
          this.isShowing = false;
      }
    };
};